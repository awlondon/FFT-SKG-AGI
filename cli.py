"""Command line interface for symbolic token processing."""

import sys

from skg_engine import SKGEngine
import config


def process_token(token: str) -> dict:
    engine = SKGEngine(config.GLYPH_OUTPUT_DIR)
    return engine.process_token(token)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli.py <token>")
        sys.exit(1)
    process_token(sys.argv[1])
