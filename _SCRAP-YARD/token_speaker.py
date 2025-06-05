# token_speaker.py
import pyttsx3
import json
import os
import threading
import time
from silent_gate_engine import should_speak
from prune_engine import evaluate_slot_for_pruning

SPEECH_STREAM_PATH = "skg_output_stream.jsonl"
DBRW_PATH = "dbRw"
PHONEME_PATH = "glyph_phonemes.json"
SPOKEN_LOG_PATH = "spoken_stream.jsonl"

class TokenSpeaker:
    def __init__(self, stream_path=SPEECH_STREAM_PATH, poll_interval=2.0):
        self.stream_path = stream_path
        self.poll_interval = poll_interval
        self.last_position = 0  # Track file position for efficient reading
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.running = True
        self.phonemes = self.load_json(PHONEME_PATH)
        self.last_spoken_at = 0  # Track last spoken time for cooldown
        self.cooldown = 2.5  # Cooldown in seconds
        self.thread = threading.Thread(target=self.monitor_stream, daemon=True)

    def load_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"[WARNING] JSON file not found: {path}")
            return {}
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse JSON file: {path}")
            return {}

    def start(self):
        self.thread.start()

    def stop(self):
        self.running = False

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def log_spoken(self, token_id, token, glyph, spoken_text):
        entry = {
            "timestamp": time.time(),
            "token_id": token_id,
            "token": token,
            "glyph": glyph,
            "spoken": spoken_text,
            "type": "emergent"
        }
        with open(SPOKEN_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def get_token_text(self, token_id):
        path = f"tokens/{token_id}.txt"
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read().strip()
        return f"[Unknown token {token_id}]"

    def get_glyph_weight_map(self, token_id):
        path = f"dbRw/{token_id}.json"
        if not os.path.exists(path):
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                slots = data.get("_slots", {})
                return {glyph: sum(weights.values()) for glyph, weights in slots.items()}
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse glyph weights for token {token_id}")
            return {}

    def get_glyph_from_db(self, token_id):
        weights = self.get_glyph_weight_map(token_id)
        return max(weights, key=weights.get) if weights else None

    def prune_glyph_slot(self, glyph):
        print(f"[PRUNE] Initiating pruning for glyph slot: {glyph}")
        evaluate_slot_for_pruning(glyph)

    def monitor_stream(self):
        while self.running:
            if os.path.exists(self.stream_path):
                with open(self.stream_path, "r", encoding="utf-8") as f:
                    f.seek(self.last_position)
                    lines = f.readlines()
                    self.last_position = f.tell()

                for line in lines:
                    try:
                        entry = json.loads(line.strip())
                        self.handle_token(entry)
                    except json.JSONDecodeError:
                        print(f"[ERROR] Malformed line in stream: {line.strip()}")
                    except Exception as e:
                        print(f"[ERROR] Unexpected error: {e}")
            time.sleep(self.poll_interval)

    def handle_token(self, entry):
        token_id = entry.get("token_id")
        emergent = entry.get("is_emergent", False)
        weight = entry.get("weight", 0)

        if emergent and weight == 1:
            token_text = self.get_token_text(token_id)
            weights = self.get_glyph_weight_map(token_id)
            decision = should_speak(token_id, weights)

            if decision == "speak" and self.can_speak():
                glyph = self.get_glyph_from_db(token_id) or "∅"
                glyph_voice = self.phonemes.get(glyph, glyph)
                full_phrase = f"{token_text}, glyph {glyph_voice}"
                print(f"[SPEAK] {full_phrase}")
                self.speak(full_phrase)
                self.log_spoken(token_id, token_text, glyph, full_phrase)
                self.last_spoken_at = time.time()
            elif decision == "internal":
                print(f"[SILENT] {token_text} (internal reflection)")
            else:
                print(f"[BLOCKED] {token_text} (silent gate)")

    def can_speak(self):
        return (time.time() - self.last_spoken_at) >= self.cooldown