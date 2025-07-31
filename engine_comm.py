import os
import json
import threading
import time
from typing import Optional


def write_message(stream_path: str, token: str, glyph: str) -> None:
    """Append a token/glyph pair to the stream file as a JSON line."""
    os.makedirs(os.path.dirname(stream_path), exist_ok=True)
    with open(stream_path, "a", encoding="utf-8") as f:
        f.write(json.dumps({"token": token, "glyph": glyph}) + "\n")


def subscribe_to_stream(stream_path: str, callback, poll_interval: float = 1.0) -> threading.Thread:
    """Watch a stream file and invoke callback(token) for each new entry."""
    def monitor() -> None:
        # Wait for file to exist
        while not os.path.exists(stream_path):
            time.sleep(poll_interval)
        with open(stream_path, "r", encoding="utf-8") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(poll_interval)
                    continue
                try:
                    data = json.loads(line.strip())
                    token = data.get("token")
                    if token:
                        callback(token)
                except json.JSONDecodeError:
                    continue
    t = threading.Thread(target=monitor, daemon=True)
    t.start()
    return t
