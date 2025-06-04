import os
import json
import time


BASE_DIR = "skg_sp01"
OUTPUT_STREAM = os.path.join(BASE_DIR, "skg_output_stream.jsonl")
DBRW_DIR = os.path.join(BASE_DIR, "dbRw")
TOKENS_DIR = os.path.join(BASE_DIR, "tokens")

class ReplayAnalyzer:
    def __init__(self):
        print("[REPLAY] Waiting for output stream...")
        time.sleep(5)  # Delay to allow the engine to write initial tokens
        self.token_ids = self.load_token_ids()
        self.analysis = []
        self.run_analysis()

    def load_output_stream(self, stream_path):
        if not os.path.exists(stream_path):
            print(f"Output stream file not found: {stream_path}")
            return []
        
        with open(stream_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        if not lines:
            print(f"Output stream file is empty: {stream_path}")
            return []
        
        print(f"Loaded output stream with {len(lines)} entries.")
        return [line.strip() for line in lines]

    def load_token_ids(self):
        timeout = 30
        check_interval = 1
        waited = 0

        # If stream doesn't exist yet, create and wait
        if not os.path.exists(OUTPUT_STREAM):
            print(f"[REPLAY] Output stream not found — creating blank stream at {OUTPUT_STREAM}")
            os.makedirs(os.path.dirname(OUTPUT_STREAM), exist_ok=True)
            with open(OUTPUT_STREAM, "w", encoding="utf-8") as f:
                f.write("")

        print("[REPLAY] Waiting for token output...")
        while waited < timeout:
            token_ids = self.load_output_stream(OUTPUT_STREAM)
            if token_ids:
                print(f"[REPLAY] Detected {len(token_ids)} token(s) in stream.")
                return token_ids

            time.sleep(check_interval)
            waited += check_interval

        print(f"[REPLAY] No tokens found after {timeout}s — continuing with empty stream.")
        return []

    def get_token_text(self, token_id):
        for length_dir in os.listdir(TOKENS_DIR):
            path = os.path.join(TOKENS_DIR, length_dir, f"{token_id}.txt")
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
        return "?"

    def analyze_token(self, token_id):
        db_path = os.path.join(DBRW_DIR, f"{token_id}_dbRw.jsonl")
        if not os.path.exists(db_path):
            return

        with open(db_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        token = self.get_token_text(token_id)
        top_slots = []

        for slot, rels in data.items():
            if slot.startswith("_"):
                continue
            for glyph, weight in rels.items():
                top_slots.append((slot, glyph, weight))

        top_slots.sort(key=lambda x: -x[2])
        self.analysis.append({
            "id": token_id,
            "token": token,
            "top_slots": top_slots[:5]
        })

    def run_analysis(self):
        for tid in self.token_ids:
            self.analyze_token(tid)

    def print_summary(self):
        for entry in self.analysis:
            print(f"\n[{entry['token']} | #{entry['id']}]")
            for slot, glyph, weight in entry['top_slots']:
                print(f"  {slot} → {glyph} ({weight})")

if __name__ == "__main__":
    analyzer = ReplayAnalyzer()
    analyzer.print_summary()
