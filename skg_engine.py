import os
import json
import pickle
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Any

from engine_comm import write_message, subscribe_to_stream
import config

from superknowledge_graph import SuperKnowledgeGraph
from agency_gate import process_agency_gates
from skg_thought_tracker import SKGThoughtTracker
from glyph_builder import build_glyph_if_needed
try:
    from tts_engine import speak
except Exception:
    speak = None  # type: ignore
try:
    from gesture_engine import display_gesture
except Exception:
    display_gesture = None  # type: ignore


@dataclass
class AgencyGateDecision:
    gate: str
    decision: str
    confidence: float = 0.0


class SKGEngine:
    """
    Core symbolic knowledge graph engine.  This class manages the mapping of
    tokens to glyphs, records adjacency information between tokens and their
    glyphs and executes recursive thought loops.  It handles persistence of
    memory to disk so that state can be restored between runs.

    Parameters
    ----------
    memory_path : str
        Directory used to persist token and adjacency maps.  If the
        directory does not exist it will be created.
    glyph_path : Optional[str]
        Optional path to a JSON file containing a list of unicode glyphs to
        select from.  If omitted or invalid a default pool containing a
        single placeholder glyph ("□") is used.
    comm_enabled : bool, optional
        If True the engine will broadcast externalized tokens to a stream file
        and process tokens received from subscribed engines.
    """

    def __init__(
        self,
        memory_path: str,
        glyph_path: Optional[str] = "glossary/extended_glyph_pool.json",
        *,
        binary: bool = False,
        encrypt_key: Optional[bytes] = None,
        comm_enabled: bool = False,
    ):
        self.comm_enabled = comm_enabled
        self.comm_out_file = os.path.join(memory_path, "engine_stream.jsonl")
        self._subscriptions: list = []
        self.memory_path = memory_path
        self.glyph_list_path = glyph_path
        self.binary = binary
        self.encrypt_key = encrypt_key
        self.token_map: dict[str, dict] = {}
        self.adjacency_map: dict[str, dict[str, int]] = {}
        self.glyph_pool: List[str] = []
        self.graph = SuperKnowledgeGraph()
        self.thought_tracker = SKGThoughtTracker()
        self.thought_history: List[str] = []
        self.externalized_last: bool = False
        self.last_modality: str = "speak"
        # Runtime toggle flags controlled via the GUI
        self.speech_enabled: bool = True
        self.gesture_enabled: bool = True
        self.recursion_enabled: bool = True

        # Load glyph pool and persisted state
        self._load_glyph_pool(self.glyph_list_path)
        self._load_state()

        from glyph_decision_engine import AGIDecision
        self.glyph_decider = AGIDecision(self.glyph_pool)

        # Setup logging paths
        self.log_dir = os.path.join(self.memory_path, "logs")
        os.makedirs(self.log_dir, exist_ok=True)
        self.adj_log = os.path.join(self.log_dir, "adjacency_walk.log")
        self.weight_log = os.path.join(self.log_dir, "weight_updates.log")

    def enable_communication(self, enabled: bool = True) -> None:
        """Toggle engine-to-engine communication."""
        self.comm_enabled = enabled

    def subscribe_to_engine(self, stream_path: str) -> None:
        """Subscribe to another engine's output stream."""
        if not self.comm_enabled:
            return
        t = subscribe_to_stream(stream_path, lambda tok: self.recursive_thought_loop(tok))
        self._subscriptions.append(t)

    def _log(self, log_path: str, entry: dict) -> None:
        """Append a JSON log entry to the specified file."""
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def _encrypt(self, data: bytes) -> bytes:
        """XOR encrypt data with the configured key."""
        if not self.encrypt_key:
            return data
        key = self.encrypt_key
        return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

    def _decrypt(self, data: bytes) -> bytes:
        """XOR decrypt data with the configured key."""
        return self._encrypt(data)

    def _load_glyph_pool(self, path: Optional[str]) -> None:
        """Load the list of available glyphs from a JSON file."""
        # Ensure we have a fallback glyph
        self.glyph_pool = []
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    glyphs = json.load(f)
                if isinstance(glyphs, list) and glyphs:
                    self.glyph_pool = glyphs
            except Exception:
                # On failure leave pool empty and fall back later
                pass
        if not self.glyph_pool:
            self.glyph_pool = ["□"]

    def _load_state(self) -> None:
        """Load token and adjacency maps from persistent storage if they exist."""
        ext = "pkl" if self.binary else "json"
        token_path = os.path.join(self.memory_path, f"token_map.{ext}")
        adj_path = os.path.join(self.memory_path, f"adjacency_map.{ext}")
        if os.path.exists(token_path):
            try:
                mode = "rb" if self.binary or self.encrypt_key else "r"
                with open(token_path, mode) as f:
                    data = f.read()
                if mode == "rb":
                    data = self._decrypt(data)
                    if self.binary:
                        self.token_map = pickle.loads(data)
                    else:
                        self.token_map = json.loads(data.decode("utf-8"))
                else:
                    self.token_map = json.loads(data)
            except Exception:
                self.token_map = {}
        if os.path.exists(adj_path):
            try:
                mode = "rb" if self.binary or self.encrypt_key else "r"
                with open(adj_path, mode) as f:
                    data = f.read()
                if mode == "rb":
                    data = self._decrypt(data)
                    if self.binary:
                        self.adjacency_map = pickle.loads(data)
                    else:
                        self.adjacency_map = json.loads(data.decode("utf-8"))
                else:
                    self.adjacency_map = json.loads(data)
            except Exception:
                self.adjacency_map = {}

    def save_state(self) -> None:
        """Persist token and adjacency maps to disk."""
        os.makedirs(self.memory_path, exist_ok=True)
        ext = "pkl" if self.binary else "json"
        token_path = os.path.join(self.memory_path, f"token_map.{ext}")
        adj_path = os.path.join(self.memory_path, f"adjacency_map.{ext}")
        mode = "wb" if self.binary or self.encrypt_key else "w"
        try:
            data: Any
            if self.binary:
                data = pickle.dumps(self.token_map)
            else:
                json_str = json.dumps(self.token_map, indent=2)
                data = json_str.encode("utf-8") if mode == "wb" else json_str
            if mode == "wb":
                with open(token_path, mode) as f:
                    f.write(self._encrypt(data))
            else:
                with open(token_path, mode, encoding="utf-8") as f:
                    f.write(data)
        except Exception:
            pass
        try:
            if self.binary:
                data = pickle.dumps(self.adjacency_map)
            else:
                json_str = json.dumps(self.adjacency_map, indent=2)
                data = json_str.encode("utf-8") if mode == "wb" else json_str
            if mode == "wb":
                with open(adj_path, mode) as f:
                    f.write(self._encrypt(data))
            else:
                with open(adj_path, mode, encoding="utf-8") as f:
                    f.write(data)
        except Exception:
            pass

    def update_glyph_weight(self, glyph: dict) -> dict:
        """Increment the text weight for a glyph and log the update."""
        if not isinstance(glyph, dict):
            return glyph
        old_weight = glyph.get("modalities", {}).get("text", {}).get("weight", 0)
        glyph.setdefault("modalities", {}).setdefault("text", {})["weight"] = old_weight + 1
        glyph["last_updated"] = datetime.utcnow().isoformat() + "Z"
        self._log(self.weight_log, {
            "timestamp": glyph["last_updated"],
            "token": glyph.get("token"),
            "glyph_id": glyph.get("glyph_id"),
            "old_weight": old_weight,
            "new_weight": glyph["modalities"]["text"]["weight"],
        })
        return glyph

    def _deterministic_index(self, token: str) -> int:
        """
        Deterministically map a token to an index into the glyph pool by hashing
        the token.  This avoids purely random glyph assignment while still
        distributing tokens across the pool.  A simple sum-of-ordinals hash
        provides sufficient variability.
        """
        if not self.glyph_pool:
            return 0
        return sum(ord(c) for c in token) % len(self.glyph_pool)

    def assign_glyph_to_token(self, token: str, adjacency: Optional[list] = None) -> dict:
        """Assign (or retrieve) a glyph for the given token and update its weight."""
        if token in self.token_map:
            glyph = self.token_map[token]
        else:
            glyph_id = self.select_glyph_for_token(token, adjacency)
            now = datetime.utcnow().isoformat() + "Z"
            glyph = {
                "glyph_id": glyph_id,
                "token": token,
                "created_on": now,
                "last_updated": now,
                "modalities": {"text": {"weight": 0}},
            }
            self.token_map[token] = glyph
        glyph = self.update_glyph_weight(glyph)
        self.save_state()
        return glyph

    def select_glyph_for_token(self, token: str, adjacency: Optional[list] = None) -> str:
        """
        Select a glyph for a token using a deterministic hash of the token.
        If no glyph pool is available the placeholder glyph is returned.
        """
        if not self.glyph_pool:
            return "□"
        return self.glyph_decider.choose(token, adjacency)

    def update_adjacency_map(self, token: str, adjacencies: list) -> None:
        """Merge a list of adjacency tokens into the internal adjacency map."""
        mapping = self.adjacency_map.setdefault(token, {})
        for adj in adjacencies:
            adj_token = adj.get("token", adj) if isinstance(adj, dict) else adj
            weight = adj.get("weight", 1) if isinstance(adj, dict) else 1
            mapping[adj_token] = mapping.get(adj_token, 0) + weight
            # Add an edge in the superknowledge graph
            self.graph.connect("global", token, adj_token)
        self.save_state()

    def get_adjacencies_for_token(self, token: str) -> dict:
        return self.adjacency_map.get(token, {})

    def recursive_thought_loop(self, token: str, depth: int = 0, max_depth: int = 5, parent: Optional[str] = None) -> list:
        """
        Recursively traverse adjacent tokens up to a maximum depth.  At each
        level the agency gate is evaluated to determine whether exploration
        should continue, reevaluation should occur or the token should be
        externalized.  The function returns a list of glyph objects
        encountered during the traversal.
        """
        if depth >= max_depth:
            return []

        # If the token is new and we came from a parent, log the expansion
        if token not in self.token_map and parent is not None:
            origin_glyph = self.token_map.get(parent)
            self.thought_tracker.log_expansion(parent, token, origin_glyph)

        current_glyph = self.assign_glyph_to_token(token)
        self.thought_history.append(token)
        # Keep thought history bounded
        if len(self.thought_history) > 20:
            self.thought_history = self.thought_history[-20:]

        gate, modality, _ = self.evaluate_agency_gate(token)
        if gate == "externalize":
            self.externalize_token(token, modality)
            self.thought_tracker.log_thought_loop(token, depth, [current_glyph], True)
            self.thought_tracker.reset()
            return [current_glyph]

        adjacents = self.get_adjacencies_for_token(token)
        self.thought_tracker.log_convergence([token] + list(adjacents.keys()), len(adjacents), 0)

        result = [current_glyph]
        for slot_index, adj_token in enumerate(adjacents.keys()):
            self.thought_tracker.log_adjacency(token, adj_token, slot_index, weight_delta=adjacents[adj_token])
            result.extend(self.recursive_thought_loop(adj_token, depth + 1, max_depth, parent=token))
        return result

    def evaluate_agency_gate(self, token: str) -> tuple[str, str, float]:
        """
        Determine which agency gate should fire for the given token.  A simple
        heuristic is used: tokens with low weight and few adjacencies tend to
        explore, tokens with moderate weight reevaluate, and tokens with high
        weight externalize.  If none of these conditions apply a random gate
        is chosen to introduce variability.
        """
        glyph = self.token_map.get(token, {})
        weight = glyph.get("modalities", {}).get("text", {}).get("weight", 1) if isinstance(glyph, dict) else 1
        adj_count = len(self.adjacency_map.get(token, {}))
        token_data = {"frequency": weight, "weight": weight}
        decisions: list[dict] = process_agency_gates(token, token_data, adj_count)
        modality_decision = next(
            (d for d in decisions if d.get("gate") == "expression"),
            {"gate": "expression", "decision": "speak", "confidence": 0.5},
        )

        # Determine a preferred gate based on simple heuristics
        if weight <= 1 and adj_count <= 0:
            return "explore", modality_decision.get("decision", "speak"), modality_decision.get("confidence", 0.5)
        if weight <= 2 and adj_count <= 2:
            return "reevaluate", modality_decision.get("decision", "speak"), modality_decision.get("confidence", 0.5)
        if weight >= 3:
            return "externalize", modality_decision.get("decision", "speak"), modality_decision.get("confidence", 0.5)
        # Otherwise pick the first affirmative decision or fall back to random
        for d in decisions:
            if d.get("decision") == "YES":
                return d.get("gate", "explore"), modality_decision.get("decision", "speak"), modality_decision.get("confidence", 0.5)
        return random.choice([d.get("gate", "explore") for d in decisions]), modality_decision.get("decision", "speak"), modality_decision.get("confidence", 0.5)

    def externalize_token(self, token: str, modality: str = "speak") -> None:
        """Output a token's glyph using speech or gesture."""
        glyph = self.token_map.get(token)
        display = glyph.get("glyph_id", glyph) if isinstance(glyph, dict) else glyph
        weight = glyph.get("modalities", {}).get("text", {}).get("weight") if isinstance(glyph, dict) else None
        print(f"[SKGEngine] Externalizing '{token}' → '{display}' (weight: {weight if weight is not None else 'N/A'}, modality: {modality})")
        if modality == "speak" and speak and self.speech_enabled:
            speak(token)
        elif modality == "gesture" and display_gesture and self.gesture_enabled:
            display_gesture(token)
        self.externalized_last = True
        self.last_modality = modality
        if self.comm_enabled:
            write_message(self.comm_out_file, token, display)

    def add_glyph_to_pool(self, glyph: str) -> None:
        self.glyph_pool.append(glyph)
        if hasattr(self, "glyph_decider"):
            self.glyph_decider.glyph_pool = self.glyph_pool

    def traverse_superknowledge(self, start_token: str, steps: int = 5) -> list:
        return self.graph.traverse(start_token, max_steps=steps)

    def generate_space_field(self, token: str, radius: float = 1.0) -> dict:
        """
        Create a simple radial layout of the token and its adjacencies using the
        hlsf_adapter.  If the adapter is not available a fallback layout is
        returned where adjacencies are placed around the origin at equal
        angles.
        """
        try:
            from hlsf_adapter import generate_vertices  # noqa
        except Exception:
            # Fallback: evenly distribute points on a circle
            def generate_vertices(center, rad, sides):
                import math
                return [(center[0] + rad * math.cos(2 * math.pi * i / sides),
                         center[1] + rad * math.sin(2 * math.pi * i / sides))
                        for i in range(sides)]
        field = {token: (0.0, 0.0)}
        adjacents = self.get_adjacencies_for_token(token)
        adjacency_tokens = list(adjacents.keys())
        sides = max(len(adjacency_tokens), 1)
        vertices = generate_vertices((0.0, 0.0), radius, sides)
        for idx, adj_token in enumerate(adjacency_tokens):
            field[adj_token] = vertices[idx % sides]
        return field

    def process_token(self, token: str) -> dict:
        """High level pipeline for CLI use."""
        glyph = build_glyph_if_needed(token)
        self.update_adjacency_map(token, glyph.get("adjacents", []))
        result = self.assign_glyph_to_token(token, glyph.get("adjacents", []))
        fft_image = glyph.get("modalities", {}).get("visual", {}).get("fft_visual")
        info = {
            "token": token,
            "glyph": result.get("glyph_id"),
            "fft_image": fft_image,
        }
        log_dir = os.path.join(self.memory_path, config.LOG_DIR)
        os.makedirs(log_dir, exist_ok=True)
        log_path = os.path.join(log_dir, config.SYMBOLIC_STREAM_LOG)
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "token": token,
            "glyph": result.get("glyph_id"),
            "decision": "externalized",
            "fft_image": os.path.basename(fft_image) if fft_image else None,
        }
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
        print(info)
        return info
