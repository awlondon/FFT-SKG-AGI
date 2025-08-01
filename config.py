"""Global configuration options for the SKG engine and CLI."""

# Engine communication settings
ENABLE_ENGINE_COMM = False
SUBSCRIBE_STREAM = None

# Centralized file paths
GLYPH_OUTPUT_DIR = "./glyph_output"
ADJACENCY_SAMPLE_DIR = "./adjacency_samples"
OFFLINE_LOOKUP_FILE = "offline_lookup.json"

# Glyph decision thresholds
GLYPH_WEIGHT_THRESHOLD = 5.0
LOW_CONFIDENCE_THRESHOLD = 1.0
MAX_RECURSION_DEPTH = 3
CONFIRMATION_THRESHOLD = 3
REJECTION_COOLDOWN = 1

# Log directory for symbolic stream
LOG_DIR = "logs"
SYMBOLIC_STREAM_LOG = "symbolic_stream.jsonl"
