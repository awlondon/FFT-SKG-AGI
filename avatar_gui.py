diff --git a//dev/null b/avatar_gui.py
index 0000000000000000000000000000000000000000..c7e402f7724deee23c4bf91fc5dd6248b4ce181c 100644
--- a//dev/null
+++ b/avatar_gui.py
@@ -0,0 +1,81 @@
+import os
+import math
+import queue
+import tkinter as tk
+from typing import Optional
+
+
+class AvatarGUI:
+    """Minimal Tkinter interface showing glyphs, FFT images and adjacency graph."""
+
+    def __init__(self, engine) -> None:
+        self.engine = engine
+        self.root = tk.Tk()
+        self.root.title("Avatar GUI")
+        self.update_queue: queue.Queue = queue.Queue()
+        self.images: dict[str, tk.PhotoImage] = {}
+        # glyph display
+        self.glyph_label = tk.Label(self.root, text="Glyph", width=256, height=256)
+        self.glyph_label.grid(row=0, column=0, padx=5, pady=5)
+        # adjacency canvas
+        self.graph_canvas = tk.Canvas(self.root, width=256, height=256, bg="white")
+        self.graph_canvas.grid(row=0, column=1, padx=5, pady=5)
+        # audio/image FFT
+        self.audio_fft_label = tk.Label(self.root, text="Audio FFT", width=256, height=256)
+        self.audio_fft_label.grid(row=1, column=0, padx=5, pady=5)
+        self.image_fft_label = tk.Label(self.root, text="Image FFT", width=256, height=256)
+        self.image_fft_label.grid(row=1, column=1, padx=5, pady=5)
+        self.last_token: Optional[str] = None
+
+    def run(self) -> None:
+        self.root.after(200, self.process_queue)
+        self.root.mainloop()
+
+    def process_queue(self) -> None:
+        while not self.update_queue.empty():
+            glyph = self.update_queue.get()
+            self._update_display(glyph)
+        self.root.after(200, self.process_queue)
+
+    def update_from_token(self, glyph: dict) -> None:
+        self.update_queue.put(glyph)
+
+    def _set_image(self, label: tk.Label, path: Optional[str], key: str) -> None:
+        if path and os.path.exists(path):
+            try:
+                photo = tk.PhotoImage(file=path)
+                label.configure(image=photo, text="")
+                self.images[key] = photo
+            except Exception:
+                label.configure(text="(image error)", image="")
+        else:
+            label.configure(text="No image", image="")
+
+    def _update_display(self, glyph: dict) -> None:
+        self.last_token = glyph.get("token")
+        visual = glyph.get("modalities", {}).get("visual", {})
+        audio_mod = glyph.get("modalities", {}).get("audio", {})
+        self._set_image(self.glyph_label, visual.get("symbolic_image"), "glyph")
+        self._set_image(self.audio_fft_label, audio_mod.get("fft_audio"), "audio")
+        img_fft = visual.get("fft_from_image") or visual.get("fft_visual")
+        self._set_image(self.image_fft_label, img_fft, "imgfft")
+        self._update_graph()
+
+    def _update_graph(self) -> None:
+        self.graph_canvas.delete("all")
+        token = self.last_token
+        if not token:
+            return
+        center_x = center_y = 128
+        radius = 90
+        self.graph_canvas.create_oval(center_x-20, center_y-20, center_x+20, center_y+20, fill="lightblue")
+        self.graph_canvas.create_text(center_x, center_y, text=token)
+        adjs = list(self.engine.get_adjacencies_for_token(token).keys())[:6]
+        for i, adj in enumerate(adjs):
+            angle = math.radians(i * (360/len(adjs))) if adjs else 0
+            x = center_x + radius * math.cos(angle)
+            y = center_y + radius * math.sin(angle)
+            self.graph_canvas.create_line(center_x, center_y, x, y)
+            self.graph_canvas.create_oval(x-15, y-15, x+15, y+15, fill="white")
+            self.graph_canvas.create_text(x, y, text=adj, font=("Arial", 8))
+
