# agency_gate_manager.py

import os
import json
import time
import logging
import numpy as np  # Ensure NumPy is available for FFT

from glyph_utils import BASE_DIR
from hierarchical_tokenizer import hierarchical_tokenization_tree
logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)



from collections import defaultdict

class AgencyGateManager:
    def __init__(self):
        self.gate_path = os.path.join(BASE_DIR, "agency_gates.json")
        self.log_path = os.path.join(BASE_DIR, "gate_decision_log.jsonl")
        self.reflection_path = os.path.join(BASE_DIR, "gate_reflections.jsonl")
        self.gates = self._load_gates()
        self._gate_usage = defaultdict(int)
        self.callbacks = {}  # Optional callbacks for gate triggers
        self._active_gate = None

    def set_active_gate(self, gate_name):
        self._active_gate = gate_name

    def get_active_gate(self):
        return self._active_gate

    def _load_gates(self):
        try:
            with open("agency_gates.json", "r", encoding="utf-8") as f:
                self.gates = json.load(f)
            logging.info(f"[INFO] Loaded agency gates from: {os.path.abspath('agency_gates.json')}")
        except Exception as e:
            logging.error(f"[ERROR] Failed to load agency gates: {e}")
            self.gates = {}

    def evaluate_gate_meaning(self, glyph_list):
        """
        Evaluates the meaning of a glyph list and returns a confidence score and interpretation.
        This method should be overridden by the actual implementation in the engine.
        """
        if not glyph_list:
            logging.warning("[WARNING] Empty glyph list provided for evaluation.")
            return 0.0, {}

        try:
            # Placeholder logic for evaluating glyphs
            confidence = min(1.0, max(0.0, 0.85))  # Ensure confidence is within [0.0, 1.0]
            interpretation = {
                "meaning": "example interpretation",
                "glyph_count": len(glyph_list),
                "glyphs": glyph_list
            }

            # In a real implementation, this would analyze the glyphs and return actual values
            logging.debug(f"[DEBUG] Evaluated glyphs: {glyph_list}, Confidence: {confidence}, Interpretation: {interpretation}")
            return confidence, interpretation

        except Exception as e:
            logging.error(f"[ERROR] Failed to evaluate gate meaning: {e}")
            return 0.0, {}

    def process_input(self, engine, input_data):
        """
        Tokenizes the input, maps adjacency, and applies FFT.
        :param input_data: The input string or glyph sequence to process.
        :return: Processed FFT result and tokenized data.
        """
        try:
            # Tokenize the input hierarchically
            levels = hierarchical_tokenization_tree(input_data)  # Simple tokenization (character-level)
            logging.debug(f"[DEBUG] Tokens: {levels}")
            
            engine.tokenize_levels(levels)
            
            for level in levels:
                # Apply FFT (convert tokens to numerical values for FFT)
                token_values = [ord(token) for token in level]  # Convert tokens to ASCII values
                fft_result = np.fft.fft(token_values)
                logging.debug(f"[DEBUG] FFT Result: {fft_result}")

            return fft_result, levels

        except Exception as e:
            logging.error(f"[ERROR] Failed to process input: {e}")
            return None, []

    def evaluate_gate(self, gate_name, token_id, engine):
        """
        Evaluate a gate by processing its glyphs and question, then combining them for evaluation.
        """
        logging.debug(f"[DEBUG] Evaluating gate: {gate_name}")
        if not self.gates or gate_name not in self.gates:
            logging.error(f"[ERROR] Gate '{gate_name}' not found in agency_gates.json")
            return False, 0.0, []  # Return default values for missing gates

        gate = self.gates[gate_name]
        glyph_seq = gate.get("glyphs", "")
        question = gate.get("question", "")

        # Process the glyph sequence
        glyph_fft, glyph_tokens = self.process_input(glyph_seq, engine)
        if glyph_fft is None:
            logging.error(f"[ERROR] Failed to process glyphs for gate '{gate_name}'")
            return False, 0.0, []

        # Process the question
        question_fft, question_tokens = self.process_input(question, engine)
        if question_fft is None:
            logging.error(f"[ERROR] Failed to process question for gate '{gate_name}'")
            return False, 0.0, []

        # Log the processed inputs
        logging.debug(f"[DEBUG] Processed Glyphs: {glyph_tokens}, FFT: {glyph_fft}")
        logging.debug(f"[DEBUG] Processed Question: {question_tokens}, FFT: {question_fft}")

        # Combine glyphs and question tokens for evaluation
        combined_tokens = glyph_tokens + question_tokens
        logging.debug(f"[DEBUG] Combined Tokens: {combined_tokens}")

        # Evaluate the gate meaning
        try:
            confidence, interpretation = self.evaluate_gate_meaning(combined_tokens)
        except Exception as e:
            logging.error(f"[ERROR] Failed to evaluate gate meaning: {e}")
            return False, 0.0, []

        decision = confidence > 0.75

        self._log_decision(gate_name, token_id, decision, confidence, glyph_seq, interpretation)

        if gate_name in self.callbacks:
            try:
                self.callbacks[gate_name](decision, confidence, {"token_id": token_id, "interpretation": interpretation})
            except Exception as e:
                logging.error(f"[ERROR] Gate callback failed for {gate_name}: {e}")

        return decision, confidence, interpretation

    def _log_decision(self, gate_name, token_id, decision, confidence, glyphs, interpretation):
        entry = {
            "timestamp": time.time(),
            "gate": gate_name,
            "token_id": token_id,
            "decision": "allow" if decision else "block",
            "confidence": round(confidence, 4),
            "glyphs": glyphs,
            "interpretation": interpretation,
            "reason": "recursive-symbolic-matching"
        }

        try:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logging.error(f"[ERROR] Failed to log gate decision: {e}")

        try:
            with open(self.reflection_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logging.error(f"[ERROR] Failed to log gate reflection: {e}")

    def get_gate(self, name):
        return self.gates.get(name)

    def agency_callback(self, decision, confidence, context):
        """
        Callback function to interact with AGIDecidor.
        Processes the decision and performs actions based on the context.
        """
        try:
            token_id = context.get("token_id", "unknown")
            interpretation = context.get("interpretation", {})
            logging.info(f"[CALLBACK] Decision: {decision}, Confidence: {confidence}, Token ID: {token_id}, Interpretation: {interpretation}")

            if decision:
                logging.info(f"[CALLBACK] Gate decision passed for Token ID: {token_id}.")
                # Perform actions for a positive decision
            else:
                logging.info(f"[CALLBACK] Gate decision failed for Token ID: {token_id}.")
                # Perform actions for a negative decision

        except Exception as e:
            logging.error(f"[ERROR] Failed in agency_callback: {e}")
