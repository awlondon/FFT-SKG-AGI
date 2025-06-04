# file_selector.py
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

BASE_DIR = os.path.abspath(".")
TRAINING_DATA_DIR = os.path.join(BASE_DIR, "__TRAINING_DATA__")

def choose_training_files():
    def add_file_pairs(file_paths):
        results = []
        for path in file_paths:
            if not path.endswith(".txt"):
                continue
            base, _ = os.path.splitext(path)
            glossary_path = f"{base}_gg.json"
            glossary_exists = os.path.exists(glossary_path)
            results.append({
                "text": path,
                "gg": glossary_path if glossary_exists else None
            })
        return results

    def load_internal_files():
        tree.delete(*tree.get_children())
        for root_dir, _, files in os.walk(TRAINING_DATA_DIR):
            for fname in sorted(files):
                if fname.endswith(".txt"):
                    fpath = os.path.join(root_dir, fname)
                    tree.insert("", "end", values=(fpath,))

    def select_from_filesystem():
        file_paths = filedialog.askopenfilenames(
            title="Browse External Text Files",
            filetypes=[("Text Files", "*.txt")]
        )
        if file_paths:
            external_pairs = add_file_pairs(file_paths)
            for pair in external_pairs:
                tree.insert("", "end", values=(pair["text"],))

    def on_confirm():
        selected = []
        for item in tree.selection():
            txt_path = tree.item(item, "values")[0]
            if txt_path.endswith(".txt"):
                gg_path = txt_path.replace(".txt", "_gg.json")
                glossary_exists = os.path.exists(gg_path)
                selected.append({
                    "text": txt_path,
                    "gg": gg_path if glossary_exists else None
                })
        if not selected:
            messagebox.showwarning("⚠️ No Selection", "Please select at least one .txt training file.")
        else:
            nonlocal selected_pairs
            selected_pairs = selected
            root.destroy()

    selected_pairs = []

    root = tk.Tk()
    root.title("⟡ Symbolic Training File Selector ⟡")
    root.geometry("880x480")
    root.configure(bg="#111")

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Treeview",
        background="#111", foreground="#ccc", fieldbackground="#111",
        rowheight=26, font=("Consolas", 10))
    style.map("Treeview", background=[("selected", "#222")], foreground=[("selected", "#0f0")])
    style.configure("Treeview.Heading", font=("Consolas", 10, "bold"), background="#222", foreground="#aaa")

    frame = tk.Frame(root, bg="#111")
    frame.pack(fill="both", expand=True, padx=16, pady=(12, 4))

    tree = ttk.Treeview(frame, columns=("Path",), show="headings", selectmode="extended")
    tree.heading("Path", text="Training File Path")
    tree.column("Path", anchor="w")
    tree.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")

    btn_frame = tk.Frame(root, bg="#111")
    btn_frame.pack(pady=10)

    select_all_active = tk.BooleanVar(value=False)

    def toggle_select_all():
        if select_all_active.get():
            tree.selection_remove(*tree.get_children())
            select_all_active.set(False)
            select_all_btn.config(text="⟡ Select all __TRAINING_DATA__")
        else:
            tree.selection_set(*tree.get_children())
            select_all_active.set(True)
            select_all_btn.config(text="❎ Clear all selections")

    select_all_btn = tk.Button(
        btn_frame,
        text="⟡ Select all __TRAINING_DATA__",
        font=("Consolas", 10),
        command=toggle_select_all,
        bg="#333", fg="#eee",
        activebackground="#222",
        activeforeground="#0f0"
    )
    select_all_btn.pack(side="left", padx=10)

    tk.Button(btn_frame, text="🗀 Open File Explorer...", font=("Consolas", 10),
              command=select_from_filesystem, bg="#333", fg="#eee", activebackground="#222",
              activeforeground="#0f0").pack(side="left", padx=10)

    tk.Button(btn_frame, text="➤ Begin Symbolic Cognition", font=("Consolas", 10, "bold"),
              command=on_confirm, bg="#444", fg="#fff", activebackground="#111",
              activeforeground="#0f0").pack(side="left", padx=10)

    tk.Label(root, text="⟁ Only .txt files are shown. Glossary is matched automatically.",
             fg="#666", bg="#111", font=("Consolas", 9)).pack()

    load_internal_files()
    root.mainloop()
    return selected_pairs


# Optional standalone test
if __name__ == "__main__":
    results = choose_training_files()
    for pair in results:
        print(f"Text: {pair['text']} | Glossary: {pair.get('gg', 'None')}")
