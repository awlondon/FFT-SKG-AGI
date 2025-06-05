⚙️ FFT-SKG-AGI
FFT-SKG-AGI is an experimental symbolic cognition engine that combines frequency-domain analysis with symbolic token processing. It recursively explores relationships between tokens, assigns glyphs via agency gates, and expands each token into multi-modal representations like:

🧠 Symbolic glyphs

🎧 Audio + FFTs

🖼️ Visual glyph images

📈 Log-based thought traces

The system acts as a sandbox for symbolic knowledge graph emergence using recursive agency, OpenAI-driven context generation, and offline modality synthesis.

🚀 Running the Engine
Run the interactive engine with:

bash
Copy
Edit
python main.py
On first run, main.py will auto-create folders under modalities/, glyph_memory/, and logs/.

Each token you enter is:

Assigned a glyph

Passed through the agency gate pipeline

Optionally externalized via FFT or image/audio generation

📊 Visualizing Thought Logs
To inspect agency gate behavior over time:

bash
Copy
Edit
python graph_cli.py path/to/gate_decision_log.jsonl
This parses decision logs and visualizes relationships between tokens, adjacencies, and symbolic gate triggers.

🔧 Requirements
Install dependencies with:

bash
Copy
Edit
pip install -r requirements.txt
Required Python Packages:
openai

requests

numpy

scipy

matplotlib

Pillow

pyttsx3

Note: You’ll need valid environment variables for:

OPENAI_API_KEY

SERPAPI_API_KEY

🎯 Project Goals
This project is designed to:

Simulate agentic symbolic cognition

Assign unique glyphs to token streams

Use adjacency + frequency to recursively generate symbolic knowledge graphs

Produce audio-visual externalizations via FFT + TTS

Enable log-based introspection of symbolic reasoning paths

It’s intended as a foundation for self-evolving AGI cognition based on recursive symbolic structures.