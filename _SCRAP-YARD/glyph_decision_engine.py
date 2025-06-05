# filename: glyph_decision_engine.py

import json
import logging
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

import os
from collections import defaultdict
from agency_gate_manager import AgencyGateManager
from symbolic_constants import GLYPH_DIR

# Configuration
AGENCY_LOG_PATH = "agency_log.jsonl"
THRESHOLD = 5.0
LOW_CONFIDENCE = 1.0
MAX_RECURSION_DEPTH = 3
CONFIRMATION_THRESHOLD = 3
REJECTION_COOLDOWN = 1
FALLBACK_GLYPH = "🜁"

# Logging function
def log_agency_event(token_id, accepted, rejected, decision_type, depth):
    entry = {
        "token_id": token_id,
        "accepted": accepted,
        "rejected": rejected,
        "decision_type": decision_type,
        "recursion_depth": depth
    }
    with open(AGENCY_LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# Retrieve all glyphs associated with a token
def get_all_glyphs_associated_with(token_id, dbRw):
    glyphs = []
    for glyph, slots in dbRw.get("_slots", {}).items():
        if token_id in slots:
            glyphs.append({"glyph": glyph, "weight": slots[token_id], "source": "slot"})
    return sorted(glyphs, key=lambda g: g["weight"], reverse=True)

# Thresholding logic
def should_accept_glyph(token_id, glyph, weight):
    if weight > THRESHOLD:
        return True
    if weight < LOW_CONFIDENCE:
        return False
    return True

# Recursive exploration
def explore_token_adjacent_slots(token_id, dbRw_dict, depth=1):
    if depth > MAX_RECURSION_DEPTH:
        return None
    db = dbRw_dict.get(token_id)
    if not db:
        return None
    candidates = get_all_glyphs_associated_with(token_id, db)
    for candidate in candidates:
        if should_accept_glyph(token_id, candidate["glyph"], candidate["weight"]):
            return {"glyph": candidate["glyph"], "depth": depth}
        for sub_token_id in db.get("_slots", {}).get(candidate["glyph"], {}):
            result = explore_token_adjacent_slots(sub_token_id, dbRw_dict, depth+1)
            if result:
                return result
    return None

# AGIDecidor
class AGIDecidor:
    def __init__(self, agi_callback, agency_manager):
        if not isinstance(agency_manager, AgencyGateManager):
            raise TypeError("agency_manager must be an instance of AgencyGateManager")
        self.agi_callback = agi_callback
        self.agency_manager = agency_manager

        self.available_glyphs = []
        # Load available glyphs from the GLYPH_DIR
        for filename in os.listdir(GLYPH_DIR):
            if os.path.isfile(os.path.join(GLYPH_DIR, filename)) and len(filename) == 1:
                self.available_glyphs.append(filename)
        self.available_glyphs.sort()  # Sort to ensure consistent orderof glyphs

        gates_path = os.path.join(os.path.dirname(__file__), "agency_gates.json")
        self.gates = {}
        if os.path.exists(gates_path):
            with open(gates_path, "r", encoding="utf-8") as f:
                self.gates = json.load(f)

    def decide(self, gate_name, token_id):
        decision, confidence, interpretation = self.agency_manager.evaluate_gate(gate_name, None, token_id)
        self.agi_callback(decision, confidence, {"token_id": token_id, "interpretation": interpretation})

    def make_glyph_decision(self, token_id, glyph, engine=None):
        gate_name = "decide_glyph"
        while True:
            if gate_name not in self.gates:
                fallback = self.gates.get("evaluate_fallback_glyph")
                if fallback:
                    gate_name = "evaluate_fallback_glyph"
                    glyph = self.assign_glyph()  # Get fallback glyph from assign_glyph function
                else:
                    logging.warning(f"[AGENCY] No decision gate found for glyph '{glyph}'")
                    return "No"

            decision, confidence, interpretation = self.agency_manager.evaluate_gate(gate_name, engine, token_id)
            if decision:
                self.agi_callback(decision, confidence, {
                    "token_id": token_id,
                    "glyph": glyph,
                    "interpretation": interpretation
                })
                return "Yes"
            else:
                logging.info(f"[AGENCY] Decision for glyph '{glyph}' was 'No'. Trying next glyph.")
                glyph = self.assign_glyph()  # Assign a new glyph and retry
                if not glyph:
                    logging.error("[AGENCY] No more glyphs available to assign.")
                    return "No"
    
    
    def assign_glyph(self):
        """
        Assign a unique glyph from the pool and remove it.
        """
        try:
            if self.available_glyphs:
                glyph = self.available_glyphs.pop(0)  # Remove and return the first glyph
                logging.info(f"[GLYPH] Assigned glyph: {glyph}")
                return glyph
            else: 
                logging.error("[ERROR] No more glyphs available for assignment.")
                return None
        except Exception as e:
            logging.error(f"[ERROR] Failed to assign glyph: {e}")
            return None

# Global glyph tracking
token_to_glyph_map = defaultdict(lambda: {"attempts": defaultdict(int), "confirmed_glyph": None})

# Main logic
def decide_glyph_for_token(token_id, agi_decision, engine=None, glossary=None):
    glyph_data = token_to_glyph_map[token_id]

    if glyph_data["confirmed_glyph"]:
        return glyph_data["confirmed_glyph"]

    if glossary:
        possible_glyphs = [
            glyph for glyph in glossary
            if glyph != FALLBACK_GLYPH and len(glyph) == 1
        ]
    else:
        possible_glyphs = [
            glyph for glyph in os.listdir(GLYPH_DIR)
            if os.path.isfile(os.path.join(GLYPH_DIR, glyph))
            and glyph != FALLBACK_GLYPH
            and len(glyph) == 1
        ]

    for glyph in possible_glyphs:
        if glyph_data["attempts"][glyph] >= CONFIRMATION_THRESHOLD:
            continue

        decision = agi_decision.make_glyph_decision(token_id, glyph, engine)
        if decision == "Yes":
            glyph_data["attempts"][glyph] += 1

            if glyph_data["attempts"][glyph] >= CONFIRMATION_THRESHOLD:
                glyph_data["confirmed_glyph"] = glyph
                log_agency_event(
                    token_id=token_id,
                    accepted=glyph,
                    rejected=[],
                    decision_type="decide_glyph",
                    depth=1
                )
                return glyph

        # Log rejections
        rejected = [glyph for glyph in possible_glyphs if glyph_data["attempts"][glyph] > 0]
        log_agency_event(
            token_id=token_id,
            accepted=None,
            rejected=rejected,
            decision_type="decide_glyph",
            depth=1
        )

        logging.info(f"[GLYPH] Attempts for token {token_id}: {dict(glyph_data['attempts'])}")

    return None
