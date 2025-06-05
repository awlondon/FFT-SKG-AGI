⚙️ FFT-SKG-AGI
FFT-SKG-AGI is an experimental symbolic cognition engine that transforms input tokens into glyph-based representations, explores their adjacency relationships via recursive agency gates, and produces multimodal outputs including:

🧠 Symbolic glyphs

🎧 Audio + FFTs

🖼️ Visual glyph images

📈 Log-based thought trace logs

This project is a sandbox for emergent symbolic knowledge graphs driven by open-ended token streams and recursive symbolic agency.

🚀 Running the Engine
Start the interactive engine:

bash
Copy
Edit
python main.py
On first run, it will automatically create folders under modalities/, glyph_memory/, and logs/.

Each token entered is:

Assigned a unique symbolic glyph

Passed through an agency gate pipeline

Optionally externalized via FFT, image, or audio

📊 Visualizing Thought Logs
You can inspect agency gate behavior over time using:

bash
Copy
Edit
python graph_cli.py path/to/gate_decision_log.jsonl
This renders relationships between tokens, agency gates, and decisions based on adjacency and frequency.

🖋️ Using Symbola for Unicode Glyphs
Some features rely on the Symbola font to properly render advanced Unicode glyphs (e.g. 🜂, ⚚, 🜁).

🔽 Download Instructions
Download Symbola.ttf from a trusted source like Font Library.

Place it in a known directory, e.g.:

bash
Copy
Edit
mkdir _fonts
mv /path/to/Symbola.ttf _fonts/
🧱 Usage Example
To generate a glyph image using the font:

python
Copy
Edit
from glyph_visualizer import generate_glyph_image

image_path = generate_glyph_image("🜂", font_path="_fonts/Symbola.ttf")
If no font_path is given and the default path fails, it falls back to a generic system font via Pillow.

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

Environment Variables:
OPENAI_API_KEY

SERPAPI_API_KEY (for image search)

🎯 Project Goals
This project aims to:

Simulate recursive agentic symbolic cognition

Assign unique glyphs to tokens via adjacency/context

Generate multi-modal outputs (FFT, image, audio)

Track and visualize symbolic reasoning loops

Build toward self-evolving AGI cognition