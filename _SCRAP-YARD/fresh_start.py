# fresh_start.py
import os
import json
import shutil
import time
from datetime import datetime
import logging
from typing import Dict, List, Set

# Configure logging with a timestamped log file
def setup_logging():
    log_filename = f"fresh_start_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()

# Configuration
AGENCY_GATES: List[Dict[str, str]] = [
    {
        "gate": "confirm_fresh_start",
        "question": "Are you sure you want a fresh start?",
        "glyphs": "🜁🜄"
    },
    {
        "gate": "confirm_delete_all",
        "question": "Are you SURE you want to delete all accumulated SKG data structures?",
        "glyphs": "🜂🝓"
    }
]

SKG_PATHS: Dict[str, str] = {
    "tokens": "derived",
    "glyphs": "derived",
    "glyph_images": "derived",
    "glyphs/fft": "derived",
    "glyphs/fft_raw": "derived",
    "glyphs/dbRw": "critical",
    "phrase_audio": "derived",
    "tokens_fft": "derived",
    "tokens_fft_img": "derived",
    "tokens_audio": "derived",
    "intermodal": "derived",
    "avatar_slots": "derived",
    "skg_output": "derived",
    "skg_output_stream.jsonl": "log",
    "gate_decision_log.jsonl": "log",
    "gate_reflections.jsonl": "log",
    "symbolic_reflection_log.jsonl": "log",
    "phrase_candidates.jsonl": "semi-critical",
    "emergent_tokens": "derived",
    "emergent_tokens.jsonl": "derived",
    "hlsf_frame_log.jsonl": "log",
    "avatar_window_debug.log": "log",
    "agency_log.jsonl": "log"
}

CAPSULE_DIR = "symbolic_capsules"
PRESERVE_DIRS = True  # Option to preserve directory structure vs. full deletion

def ask_agency_gate(gate: Dict[str, str]) -> bool:
    """Prompt the user to confirm an agency gate decision."""
    print(f"\n🧠 {gate['question']}")
    print(f"   Glyph Sequence: {gate['glyphs']}")
    response = input("Type YES to proceed (anything else to abort): ").strip().upper()
    confirmed = response == "YES"
    logger.info(f"Gate '{gate['gate']}': User response = {response}, Confirmed = {confirmed}")
    return confirmed

def timestamped_folder() -> str:
    """Create a timestamped folder for the memory capsule."""
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    capsule_path = os.path.join(CAPSULE_DIR, f"capsule_{now}")
    os.makedirs(capsule_path, exist_ok=True)
    logger.info(f"Created capsule directory: {capsule_path}")
    return capsule_path

def backup_all(target_dir: str, paths: Dict[str, str]) -> None:
    """Backup all SKG paths to the target capsule directory."""
    logger.info(f"[⏳] Saving memory capsule to {target_dir}")
    print(f"[⏳] Backing up SKG data to {target_dir}...")
    for path, tag in paths.items():
        if os.path.exists(path):
            dest_path = os.path.join(target_dir, os.path.basename(path))
            try:
                if os.path.isdir(path):
                    shutil.copytree(path, dest_path, dirs_exist_ok=True)
                else:
                    shutil.copy2(path, dest_path)
                logger.info(f" - Backed up: {path} -> {dest_path}")
            except Exception as e:
                logger.error(f"Failed to back up {path}: {e}")
                print(f"[⚠️] Failed to back up {path}: {e}")
        else:
            logger.debug(f" - Skipped (does not exist): {path}")

def truncate_file(path: str) -> None:
    """Truncate a file to empty its contents while preserving the file."""
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write("")  # Explicitly write empty string for clarity
        logger.info(f" - Truncated: {path}")
    except Exception as e:
        logger.error(f"Failed to truncate {path}: {e}")
        print(f"[⚠️] Failed to truncate {path}: {e}")

def clear_directory(path: str, preserve_files: Set[str]) -> None:
    """
    Clear non-preserved files in a directory, optionally preserving the directory itself.

    Args:
        path: The directory path to clear.
        preserve_files: Set of file paths to preserve (e.g., log files).
    """
    if not os.path.isdir(path):
        return

    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if item_path in preserve_files:
            continue
        try:
            if os.path.isfile(item_path):
                os.remove(item_path)
                logger.info(f" - Removed file: {item_path}")
            elif os.path.isdir(item_path) and not PRESERVE_DIRS:
                shutil.rmtree(item_path)
                logger.info(f" - Removed directory: {item_path}")
        except Exception as e:
            logger.error(f"Failed to remove {item_path}: {e}")
            print(f"[⚠️] Failed to remove {item_path}: {e}")

def delete_path(path: str, preserve_files: Set[str]) -> None:
    """
    Delete a path unless it's a file to preserve, in which case truncate it.

    Args:
        path: The path to delete or truncate.
        preserve_files: Set of file paths to preserve (e.g., log files).
    """
    if not os.path.exists(path):
        return

    if path in preserve_files:
        truncate_file(path)
    elif os.path.isdir(path):
        clear_directory(path, preserve_files)
        if not PRESERVE_DIRS:
            try:
                shutil.rmtree(path)
                logger.info(f" - Removed directory: {path}")
            except Exception as e:
                logger.error(f"Failed to remove directory {path}: {e}")
                print(f"[⚠️] Failed to remove {path}: {e}")
    else:
        try:
            os.remove(path)
            logger.info(f" - Removed: {path}")
        except Exception as e:
            logger.error(f"Failed to remove {path}: {e}")
            print(f"[⚠️] Failed to remove {path}: {e}")

def run_fresh_start(paths: Dict[str, str] = SKG_PATHS, agency_gates: List[Dict[str, str]] = AGENCY_GATES) -> None:
    """Run the fresh start protocol, preserving logging files and optionally directories."""
    print("[SYSTEM] Initiating symbolic fresh start protocol...")
    logger.info("Starting fresh start protocol")

    # Define preservation rules
    preserve_files = {path for path, tag in paths.items() if tag == "log"}
    critical_files = {path for path, tag in paths.items() if tag == "critical"}

    # Display plan
    print("\n⚠️ Planned actions:")
    print(" - Log files (*.jsonl tagged 'log') will be truncated but preserved.")
    print(" - Critical files (tagged 'critical') will be preserved as-is.")
    if PRESERVE_DIRS:
        print(" - Directories will be preserved, but non-preserved contents will be deleted.")
    else:
        print(" - Directories and their contents will be deleted unless tagged 'log' or 'critical'.")
    print(" - Other files will be deleted.")

    print("\nPaths to process:")
    for path, tag in paths.items():
        exists = os.path.exists(path)
        status = "[✓]" if exists else "[ ]"
        action = ("truncate" if path in preserve_files else
                  "preserve" if path in critical_files else
                  "clear contents" if os.path.isdir(path) and PRESERVE_DIRS else
                  "delete")
        print(f"  {status} {path}  (type: {tag}, action: {action})")

    # Handle dynamic skg_ folders
    skg_dirs = [d for d in os.listdir() if d.startswith("skg_") and os.path.isdir(d)]
    if skg_dirs:
        print("\nDynamic SKG folders detected:")
        for d in skg_dirs:
            print(f"  [✓] {d}  (action: delete)")
        if not ask_agency_gate({"gate": "confirm_skg_dirs", "question": "Delete dynamic skg_* folders?", "glyphs": "🜃🝔"}):
            print("[INFO] Skipping deletion of dynamic skg_ folders.")
            skg_dirs = []
        else:
            for d in skg_dirs:
                try:
                    shutil.rmtree(d)
                    logger.info(f"Deleted dynamic folder: {d}")
                    print(f"[🗑️] Deleted: {d}")
                except Exception as e:
                    logger.error(f"Failed to delete {d}: {e}")
                    print(f"[⚠️] Failed to delete {d}: {e}")

    # Run agency gates
    for gate in agency_gates:
        if not ask_agency_gate(gate):
            print(f"[ABORTED] Fresh start cancelled at gate '{gate['gate']}'.")
            logger.info(f"Fresh start aborted at gate: {gate['gate']}")
            return

    # Backup data
    capsule_path = timestamped_folder()
    backup_all(capsule_path, paths)

    # Execute wipe
    print("\n[WIPING] Modifying SKG data structures...")
    logger.info("Executing fresh start wipe")
    for path in paths:
        if path not in critical_files:  # Skip critical files
            delete_path(path, preserve_files)

    print(f"\n[✅] Symbolic memory reset complete.")
    print(f"[💾] Memory capsule saved at: {capsule_path}")
    logger.info("Fresh start completed. Capsule saved at: %s", capsule_path)

if __name__ == "__main__":
    try:
        run_fresh_start()
    except KeyboardInterrupt:
        print("\n[ABORTED] Fresh start interrupted by user.")
        logger.info("Fresh start interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\n[ERROR] Unexpected error during fresh start: {e}")
        logger.error(f"Unexpected error: {e}", exc_info=True)
