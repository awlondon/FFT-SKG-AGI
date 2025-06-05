# replay_thought_loop.py
import os
import json
import time
import logging
import signal
import sys
from typing import Optional, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("thought_loop_reentry.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

THOUGHT_STREAM_PATH = "skg_output_stream.jsonl"

class ThoughtLoopReentry:
    def __init__(self, engine, delay: float = 0.5):
        """
        Initialize the ThoughtLoopReentry class for reentrant cognition.

        Args:
            engine: The SKGEngine instance to process tokens.
            delay (float): Delay between reprocessing tokens (in seconds).
        """
        self.engine = engine
        self.delay = delay
        self.seen_ids = set()
        self.running = True
        self.file_position = 0  # Track position in the file for tailing

        # Validate engine
        if not hasattr(self.engine, "id_map") or not hasattr(self.engine, "process_token"):
            logger.error("Engine validation failed: Missing 'id_map' or 'process_token' attributes")
            raise ValueError("Engine must have 'id_map' and 'process_token' attributes")
        logger.info("Engine validation successful")

        # Set up signal handling for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info("Received shutdown signal. Stopping thought loop reentry...")
        self.running = False

    def initialize(self):
        """Initialize the reentry process, validate engine, and prepare state."""
        if not os.path.exists(THOUGHT_STREAM_PATH):
            logger.warning(f"Output stream file not found: {THOUGHT_STREAM_PATH}")
            return False

        logger.info("[🌀] Beginning recursive reentry into thought loop...")
        return True

    def start(self):
        """Start the reentrant thought loop process."""
        if not self.initialize():
            return

        while self.running:
            self.reenter_once()
            time.sleep(1.0)  # Avoid tight looping

        logger.info("Thought loop reentry stopped.")

    def reenter_once(self):
        """Perform a single iteration of the reentry loop."""
        try:
            new_tokens = self._read_new_lines()
            logger.info(f"Read {len(new_tokens)} new tokens from the stream")
            self._process_tokens(new_tokens)
        except Exception as e:
            logger.error(f"Error during reentry loop: {e}")
            time.sleep(1.0)  # Wait before retrying

    def _read_new_lines(self) -> list[Tuple[Optional[str], Optional[str]]]:
        """
        Read new lines from the thought stream file using tailing.

        Returns:
            List of (token, tid) tuples for new tokens.
        """
        new_tokens = []

        try:
            with open(THOUGHT_STREAM_PATH, "r", encoding="utf-8") as f:
                # Seek to the last known position
                f.seek(self.file_position)
                lines = f.readlines()
                # Update position to the end of the file
                self.file_position = f.tell()

            logger.info(f"Read {len(lines)} lines from the thought stream file")

            for line in lines:
                try:
                    data = json.loads(line.strip())
                    tid = data.get("token")
                    if tid and tid not in self.seen_ids:
                        token = self.engine.id_map.get(tid)
                        if token:
                            new_tokens.append((token, tid))
                            self.seen_ids.add(tid)
                            logger.debug(f"New token added: {token} ({tid})")
                except json.JSONDecodeError as e:
                    logger.error(f"Malformed line in stream: {line.strip()} - {e}")
                except Exception as e:
                    logger.error(f"Error processing line: {e}")

        except FileNotFoundError:
            logger.warning(f"Thought stream file disappeared: {THOUGHT_STREAM_PATH}")
            self.file_position = 0  # Reset position if file is recreated
        except IOError as e:
            logger.error(f"IO error while reading thought stream: {e}")

        return new_tokens

    def _process_tokens(self, new_tokens: list[Tuple[str, str]]):
        """
        Process new tokens by reentering them into the engine.

        Args:
            new_tokens: List of (token, tid) tuples to process.
        """
        for token, tid in new_tokens:
            if not self.running:
                logger.info("Processing stopped due to shutdown signal")
                break

            # Optional: Add symbolic filtering or gate checks
            if not self.engine.should_reenter_token(tid):
                logger.info(f"[SKIP] Token {tid} did not pass gate checks")
                continue

            logger.info(f"[↻] Reentering token: {token} ({tid})")
            try:
                # Fallback to load token from disk if not in id_map
                if not token:
                    token = self.engine.load_token_text_from_disk(tid)

                # Handle multimodal tokens
                modality = self.engine.get_token_modality(tid)
                if modality == "text":
                    self.engine.process_token(token, tid)
                elif modality == "image":
                    self.engine.process_image_token(token, tid)
                elif modality == "audio":
                    self.engine.process_audio_token(token, tid)
                else:
                    logger.warning(f"Unknown modality for token {tid}: {modality}")

                logger.info(f"Successfully reprocessed token: {token} ({tid})")
                time.sleep(self.delay)
            except Exception as e:
                logger.error(f"Error reprocessing token {tid}: {e}")

# Example usage:
# from skg_engine import SKGEngine
# engine = SKGEngine(...)
# reentry = ThoughtLoopReentry(engine)
# reentry.start()