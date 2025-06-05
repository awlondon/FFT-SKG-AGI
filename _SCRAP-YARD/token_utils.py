# token_utils.py

from collections import defaultdict
import logging
import os
import json
import time

from fft_generator import generate_signal_fft_image_for_token
from glyph_utils import BASE_DIR, DEFAULT_GLYPH, generate_fft_image_for_token
from relationship_types import RELATIONSHIP_TYPES
from symbolic_constants import GLYPH_IMAGE_SIZE
from skg_thought_tracker import SKGThoughtTracker


class TokenUtils:
    def __init__(self, thought_tracker=None):
        self.base_dir = BASE_DIR
        self.token_counter = 1
        self.token_map = {}
        self.id_map = {}
        self.token_freq = {}
        self.initialize()  # Initialize the token maps and frequency tracker
        self.thought_tracker = thought_tracker or SKGThoughtTracker()
        from emergent_token_utils import EmergentTokenTracker
        from agency_gate_manager import AgencyGateManager
        from glyph_decision_engine import AGIDecidor

        # Ensure proper initialization of agency_manager and agi_decidor
        self.emergent_tracker = EmergentTokenTracker()
        self.agency_manager = AgencyGateManager()
        if not hasattr(self.agency_manager, 'agency_callback'):
            logging.error("[ERROR] AgencyGateManager is missing 'agency_callback'. Initialization failed.")
        self.agi_decidor = AGIDecidor(agi_callback=getattr(self.agency_manager, 'agency_callback', None), agency_manager=self.agency_manager)
        if not self.agi_decidor:
            logging.error("[ERROR] AGIDecidor initialization failed.")

        self.total_tokens = 0
        self.input_token_ids = set()
        self.token_fatigue = defaultdict(int)
        self.recent_tokens = []
        self.token_weights = {}
        self.token_to_glyph = {}  # Mapping of token IDs to glyphs
        self.current_sigil = "🜁"
        self.walk_trace = []
        self.confidence_log = []
        self.use_tts = True  # Enable TTS by default, can be overridden by the caller
        from text_to_speech_engine import TextToSpeechEngine
        self.text_to_speech_engine = TextToSpeechEngine()

    def initialize(self):
        tokens_dir = os.path.join(self.base_dir, "tokens")
        if not os.path.exists(tokens_dir):
            os.makedirs(tokens_dir)

        token_files = [f for f in os.listdir(tokens_dir) if f.endswith(".txt")]
        if token_files:
            max_id = max(int(f.split('.')[0]) for f in token_files)
            self.token_counter = max_id + 1

        for f in token_files:
            token_id = int(f.split('.')[0])
            with open(os.path.join(tokens_dir, f), "r", encoding="utf-8") as file:
                token = file.read().strip()
                self.token_map[token] = token_id
                self.id_map[token_id] = token
                self.token_freq[token_id] = 1

    def _create_token(self, token, source_file=None, context_tokens=None, is_glossary_token=False, glyph=None):
        """
        Create a token and save it to the appropriate directory.
        """
        # Generate a unique token ID
        token_id = str(hash(token) % 1000000)

        # Determine the save directory
        if is_glossary_token:
            if not glyph or not isinstance(glyph, str):
                logging.warning(f"[WARNING] Invalid glyph: {glyph}. Falling back to default glyph.")
                glyph = DEFAULT_GLYPH  # Use a fallback glyph
            save_dir = os.path.join(self.base_dir, "glossary_tokens", glyph)
        else:
            save_dir = os.path.join(self.base_dir, "dbRw")

        os.makedirs(save_dir, exist_ok=True)

        # Create the token data
        token_data = {
            "_id": token_id,
            "_token": token,
            "_source": source_file,
            "_context": context_tokens if not is_glossary_token else None,
            "_glyph": glyph if is_glossary_token else None,
        }

        # Save the token data to a JSON file
        token_file_path = os.path.join(save_dir, f"{token_id}.json")
        with open(token_file_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

        # Process only the first-level characters of the token
        from render_glyph import render_token
        from glyph_utils import generate_fft_image_for_token

        for char in token:
            # Render the character into an image
            img_path = os.path.join(self.base_dir, "tokens_fft_img", f"{char}_{token_id}.png")
            if not os.path.exists(img_path):
                render_token(char, size=int(GLYPH_IMAGE_SIZE[0]), output_path=img_path)
                logging.info(f"[INFO] Image generated for character '{char}' at {img_path}")

            # Generate the FFT for the character
            fft_path = os.path.join(self.base_dir, "tokens_fft", f"{char}_{token_id}_fft.png")
            if not os.path.exists(fft_path):
                generate_fft_image_for_token(char, token_id)  # Use the token ID for association
                logging.info(f"[INFO] FFT generated for character '{char}' at {fft_path}")

            # Update the dbRw file for the token
            dbRw_path = os.path.join(self.base_dir, "dbRw", f"{token_id}.json")
            if os.path.exists(dbRw_path):
                with open(dbRw_path, "r", encoding="utf-8") as f:
                    db_data = json.load(f)
            else:
                db_data = {"_id": token_id, "_token": token, "_frequency": 0, "_slots": {}}

            db_data["image_path"] = img_path
            db_data["fft_path"] = fft_path

            with open(dbRw_path, "w", encoding="utf-8") as f:
                json.dump(db_data, f, indent=2)

        logging.info(f"[INFO] Token '{token}' created with ID '{token_id}' and saved to {token_file_path}")
        return token_id

    def create_token_with_thought_loop(self, token, level=None, glossary=None, engine=None):
        """
        Create a token and process its first-level characters.
        """
        if token in self.token_map:
            token_id = self.token_map[token]
            self.recursive_walk(token_id)
            return token_id

        # Process the token
        glyph = None
        if glossary:
            if isinstance(glossary, dict):
                glyph = glossary.get("glyph")
                if not glyph or not isinstance(glyph, str):
                    logging.warning(f"[WARNING] Invalid glossary glyph: {glyph}. Falling back to default glyph.")
                    glyph = DEFAULT_GLYPH  # Use a fallback glyph
            elif isinstance(glossary, str):
                glyph = glossary
            else:
                raise TypeError(f"Invalid glossary type: {type(glossary)}. Expected dict or str.")
        else:
            glyph = DEFAULT_GLYPH  # Use a fallback glyph if no glossary is provided

        token_id = self._create_token(token, is_glossary_token=bool(glossary), glyph=glyph)

        # Process first-level characters only
        for char in token:
            self._create_token(char, is_glossary_token=False)

        return token_id

    def _add_relationship(self, source_id, target_id, relation_type=None, weight=1):
        """
        Add a symbolic relationship between two token IDs in a named slot (relation_type).
        Logs glyphs for source, relationship type, and target to symbolic_reflection_log.jsonl.
        """
        if source_id == target_id:
            return  # Skip self-references

        # Get glyphs for source and target tokens
        from glyph_utils import get_glyph_for_token, process_glyph_impression
        source_glyph = get_glyph_for_token(source_id)
        target_glyph = get_glyph_for_token(target_id)

        # Determine the relationship type
        if relation_type is None:
            distance = abs(int(source_id) - int(target_id))
            relation_type = f"distance_{distance}"

        # Validate relationship type
        if relation_type not in RELATIONSHIP_TYPES:
            logging.warning(f"[WARNING] Invalid relationship type: {relation_type}. Skipping.")
            return

        # Get glyph for relationship type
        relation_glyph = get_glyph_for_token(relation_type) or ">"  # Fallback glyph

        # Log the adjacency sequence
        if source_glyph and relation_glyph and target_glyph:
            logging.info(f"[RELATE] {source_glyph} -> {relation_glyph} -> {target_glyph}")
            process_glyph_impression(source_glyph)
            process_glyph_impression(relation_glyph)
            process_glyph_impression(target_glyph)

        # Add the relationship
        self.relationships[source_id][relation_type].setdefault("tokens", []).append(target_id)
        self.relationships[source_id][relation_type]["weight"] = (
            self.relationships[source_id][relation_type].get("weight", 0) + weight
        )
        self._update_dbRw_file(source_id)

    def gate_decision(self, gate_name, token_id):
        decision, confidence, _ = self.agency_manager.evaluate_gate(gate_name, self, token_id)
        return decision

    def load_token_data(self, token_id):
        """Load token data from the dbRw directory."""
        path = os.path.join(self.base_dir, "dbRw", f"{token_id}.json")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def recursive_walk(self, token_id, depth=0, max_depth=10, visited=None, parent=None):
        """
        Recursively traverse token adjacency slots with agency-based decisions while logging symbolic cognition.
        Prevents infinite recursion by maintaining a set of visited tokens.
        """
        from glyph_utils import get_glyph_for_token, process_glyph_impression

        if visited is None:
            visited = set()

        if depth >= max_depth or token_id in visited:
            return  # Stop recursion if max depth is reached or token is already visited

        visited.add(token_id)  # Mark the current token as visited

        if token_id not in self.id_map and parent is not None:
            self.thought_tracker.log_expansion(parent, token_id, None)

        token_data = self.load_token_data(token_id)
        glyph = get_glyph_for_token(token_id)
        if glyph:
            process_glyph_impression(glyph)  # Log the glyph
        self.thought_tracker.log_thought_loop(token_id, depth, [glyph] if glyph else [], False)

        slots = token_data.get("s", {})  # Get sigil slots
        self.thought_tracker.log_convergence([token_id] + list(slots.keys()), len(slots), len(slots))

        for slot_id in sorted(slots.keys()):  # Traverse each slot
            adj_map = slots[slot_id].get("a", {})  # Adjacency map for the slot
            sorted_tokens = sorted(adj_map.items(), key=lambda x: -x[1])  # Sort by weight

            for candidate_token, weight in sorted_tokens:
                # Enforce fatigue
                if self.token_fatigue[candidate_token] > 3:
                    continue
                self.token_fatigue[candidate_token] += 1

                # Log the glyph for the candidate token
                candidate_glyph = get_glyph_for_token(candidate_token)
                if candidate_glyph:
                    process_glyph_impression(candidate_glyph)

                self.thought_tracker.log_adjacency(token_id, candidate_token, slot_id, weight_delta=weight)
                if candidate_token not in self.id_map:
                    self.thought_tracker.log_expansion(token_id, candidate_token, candidate_glyph)

                # Make an agency-based decision
                if not self.gate_decision("continue_slot", candidate_token):
                    continue

                decision = self.agency_binary_decision(token_id, candidate_token, slot_id, weight, depth)
                if decision:
                    self.recursive_walk(candidate_token, depth + 1, max_depth, visited, parent=token_id)

    def agency_binary_decision(self, current_token, candidate_token, slot_id, weight, depth):
        """
        Make a binary decision to continue traversal or not.
        """
        # Example decision logic
        if weight < 0.1:  # Skip low-weight connections
            return False
        if depth > 5 and weight < 0.5:  # Avoid deep traversal of weak connections
            return False
        if self.has_seen_token(candidate_token):  # Avoid revisiting tokens
            return False

        # Optional: Add logic for slot switching or glyph jumping
        if self.should_switch_slot(current_token, slot_id):
            return False

        return True

    def evaluate_gate(self, gate_name, token_id):
        """
        Evaluate a gate using the AgencyGateManager and log the decision.
        """
        if not (self.agency_manager and self.agi_decidor):
            logging.warning("[⚠️] Missing gate engine — skipping evaluations.")
            return False, 0, None

        decision, confidence, interpretation = self.agency_manager.evaluate_gate(
            gate_name=gate_name,
            engine=self,
            token_id=token_id
        )
        logging.info(f"Gate '{gate_name}' decision: {decision}, Confidence: {confidence}, Interpretation: {interpretation}")
        return decision, confidence, interpretation

    def react_to_audio(self, interpretation):
        """
        React to audio based on the provided gate interpretation.

        Logs the interpretation, checks symbolic gate reactions, and optionally triggers
        reflective or expressive behavior.
        """
        print(f"[AUDIO] Reacting to interpreted input: {interpretation}")

        # Example symbolic decision logic
        if "question_self" in interpretation:
            self.trigger_agency_gate("question_self")
        elif "suppress_output" in interpretation:
            self.trigger_agency_gate("suppress_output")
        else:
            self.log_audio_reaction(interpretation)

    def speak_this_thought(self, thought):
        """
        Speak a given thought with symbolic context.
        """
        print(f"[THOUGHT] {thought}")
        tts_result = None
        if self.use_tts and self.text_to_speech_engine:
            try:
                tts_result = self.text_to_speech_engine.speak(thought)
            except Exception as e:
                logging.error(f"[ERROR] TTS engine failed: {e}")
        else:
            logging.warning("[TTS] Text-to-speech is disabled or uninitialized.")

        self.log_expressed_thought(thought, tts_result)

    def log_expressed_thought(self, thought, tts_result=None):
        """
        Log and optionally save an expressed thought along with its TTS result.
        """
        print(f"[LOG] Expressed thought: {thought}")

        # Ensure the expressed_thoughts directory exists
        expressed_thoughts_dir = os.path.join(self.base_dir, "expressed_thoughts")
        os.makedirs(expressed_thoughts_dir, exist_ok=True)

        # Save the thought to a text file
        thought_file_path = os.path.join(expressed_thoughts_dir, f"{hash(thought)}.txt")
        with open(thought_file_path, "w", encoding="utf-8") as f:
            f.write(thought)

        # Save the TTS result (audio file) if provided
        if tts_result:
            audio_file_path = os.path.join(expressed_thoughts_dir, f"{hash(thought)}.wav")
            with open(audio_file_path, "wb") as f:
                f.write(tts_result)

        logging.info(f"[INFO] Expressed thought logged: {thought}")
        if tts_result:
            logging.info(f"[INFO] TTS result saved to: {audio_file_path}")

    def process_gate_triggered_behavior(self, gate_name, token_id):
        """
        Trigger specific behaviors based on gate decisions.
        """
        decision, confidence, interpretation = self.evaluate_gate(gate_name, token_id)
        if decision:
            print(f"[INFO] Gate Trigger] Gate '{gate_name}' passed with confidence {confidence}. Interpretation: {interpretation}")
            # Example behavior: React to audio
            self.react_to_audio(interpretation)
        else:
            print(f"[INFO] Gate Trigger] Gate '{gate_name}' blocked with confidence {confidence}.")
            # Example behavior: Speak a thought
            self.speak_this_thought("Access denied.")

    def stream_to_visualizer(self, token, token_id, slot_index=0, mode="internal_thought"):
        from glyph_utils import get_glyph_for_token
        weight = self.token_weights.get(token_id, 1.0)
        glyph = get_glyph_for_token(token_id)
        fft_path = os.path.join(self.base_dir, "tokens_fft_img", f"{token_id}.png")

        # Ensure FFT image is generated
        if not os.path.exists(fft_path):
            print(f"[WARNING] Generating missing FFT image for token: {token} ({token_id})")
            generate_signal_fft_image_for_token(token_id, token)

        # Commenting out visualization stream calls
        # if not self.visualizer:
        #     logging.warning("Visualizer is not available. Skipping visualization.")
        #     return

        # if not hasattr(self.visualizer, "stream_token_to_visualizer"):
        #     logging.error(f"Visualizer does not support 'stream_token_to_visualizer'. Visualizer type: {type(self.visualizer)}")
        #     return

        # self.visualizer.stream_token_to_visualizer(
        #     token_id=token_id,
        #     glyph=glyph,
        #     fft_path=fft_path,
        #     slot_index=slot_index,
        #     weight=weight,
        #     mode=mode
        # )

    def append_to_output_stream(self, token_id):
        """
        Append a token ID to the output stream file.
        """
        stream_file = os.path.join(self.base_dir, "skg_output_stream.jsonl")
        log_entry = {"token_id": token_id, "timestamp": time.time()}

        # Ensure the output stream file exists
        if not os.path.exists(stream_file):
            with open(stream_file, "w", encoding="utf-8") as f:
                f.write("")

        # Append the log entry to the file
        try:
            with open(stream_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry) + "\n")
            logging.info(f"[INFO] Appended token ID {token_id} to output stream.")
        except Exception as e:
            logging.error(f"[ERROR] Failed to append to output stream: {e}")

    def walk_token_adjacency_horizon(self, token_index, tokens):
        """
        Traverse the adjacency horizon for a given token and preserve slot-specific relationships.
        Log glyphs for the current token, relationship type, and slotted tokens in weighted rank-order.
        """
        current_token = tokens[token_index]
        adjacency_window = tokens[token_index: token_index + 51]

        slot_map = {}
        for slot, adj_token in enumerate(adjacency_window, 1):
            # If the token already exists in a slot, do not overwrite or merge
            if any(adj_token in slot_data["adjacency_tokens"] for slot_data in slot_map.values()):
                logging.debug(f"[INFO] Token '{adj_token}' already exists in another slot. Skipping merge.")
                continue

            # Preserve the token in its original slot
            slot_map[slot] = {"adjacency_tokens": {adj_token: 1.0}}

        # Cache token data to reduce repeated file reads
        if not hasattr(self, "_token_data_cache"):
            self._token_data_cache = {}

        self.token_id = current_token

        if self.token_id in self._token_data_cache:
            token_data = self._token_data_cache[self.token_id]
        else:
            path = os.path.join(self.base_dir, "tokens", f"{self.token_id}.json")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    token_data = json.load(f)
                    self._token_data_cache[self.token_id] = token_data
            else:
                token_data = {}

        self.update_token_weight(self.token_id, token_data)

        # Log glyphs for the current token, relationship type, and slotted tokens
        current_glyph = get_glyph_for_token(self.token_id)
        from glyph_utils import get_glyph_for_token, process_glyph_impression
        process_glyph_impression(current_glyph)

        for slot, slot_data in slot_map.items():
            for adj_token, weight in slot_data["adjacency_tokens"].items():
                adj_glyph = get_glyph_for_token(adj_token)
                if adj_glyph:
                    process_glyph_impression(adj_glyph)

                # Log relationship type glyph if applicable
                relation_type_glyph = get_glyph_for_token(f"relation_{slot}")
                if relation_type_glyph:
                    process_glyph_impression(relation_type_glyph)

        return slot_map

    def _save_slot_mapping(self, token_id, slot_map):
        """
        Save the slot mapping for a token to the database or file system.
        """
        dbRw_dir = os.path.join(self.base_dir, "dbRw")
        os.makedirs(dbRw_dir, exist_ok=True)  # Ensure the directory exists

        # Construct the full file path
        db_path = os.path.join(dbRw_dir, f"{token_id}.json")

        # Load existing token data if available
        token_data = self.load_token_data(token_id)

        # Update the slots with the new mapping and adjust weights if necessary
        if "_slots" not in token_data:
            token_data["_slots"] = {}

        for slot, data in slot_map.items():
            if slot in token_data["_slots"]:
                # Update weight if the slot is already taken
                existing_weight = token_data["_slots"][slot].get("weight", 0)
                token_data["_slots"][slot]["weight"] = max(existing_weight, data.get("weight", 0))
            else:
                token_data["_slots"][slot] = data

        # Save the updated token data
        with open(db_path, "w", encoding="utf-8") as f:
            json.dump(token_data, f, indent=2)

    def update_token_weight(self, token_id, token_data):
        """
        Update the weight of a token based on its metadata or other criteria.
        """
        # Default weight if no specific data is available
        default_weight = 1.0

        # Extract weight from token data if available
        weight = token_data.get("_frequency", default_weight)

        # Apply additional logic to adjust weight (e.g., based on token fatigue or other metrics)
        fatigue_penalty = self.token_fatigue.get(token_id, 0) * 0.1
        adjusted_weight = max(weight - fatigue_penalty, 0.1)  # Ensure weight doesn't drop below 0.1

        # Update the token weight in the internal map
        self.token_weights[token_id] = adjusted_weight

        logging.info(f"[INFO] Updated weight for token '{token_id}': {adjusted_weight}")

    def think_about(self, token_id):
        """
        Unified method to process a token symbolically.
        """
        self.recursive_walk(token_id)
        self.process_gate_triggered_behavior("react_to_audio", token_id)
        self.stream_to_visualizer(self.id_map[token_id], token_id)
        self.append_to_output_stream(token_id)
        self.thought_tracker.reset()
