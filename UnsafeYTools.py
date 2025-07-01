import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import threading
import os
import shutil
import sys
import re

BG_COLOR = "#0f0f0f"  # black
FG_COLOR = "#a259ff"  # purple 
ACTIVE_BG = "#5f0fff"  # purple but more purple
FONT_NAME = "Consolas"

class UnsafeYToolsApp:
    def __init__(self, root):
        self.root = root
        root.title("UnsafeYTools")
        root.geometry("600x500")
        root.configure(bg=BG_COLOR)

        self.filepath = None
        self.token_seed = ""

        root.grid_rowconfigure(3, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.upload_btn = tk.Button(root, text="Select MP4 File", command=self.select_file,
                                    bg=FG_COLOR, fg="white", activebackground=ACTIVE_BG,
                                    relief="flat", font=(FONT_NAME, 12), cursor="hand2")
        self.upload_btn.grid(row=0, column=0, pady=(15, 5), padx=10, sticky="ew")

        self.file_label = tk.Label(root, text="No file selected", bg=BG_COLOR, fg="white",
                                   font=(FONT_NAME, 10))
        self.file_label.grid(row=1, column=0, pady=5, padx=10, sticky="ew")

        self.send_btn = tk.Button(root, text="Send (Run BAT on MP4)", command=self.run_process,
                                  bg=FG_COLOR, fg="white", activebackground=ACTIVE_BG,
                                  relief="flat", font=(FONT_NAME, 12), cursor="hand2")
        self.send_btn.grid(row=2, column=0, pady=5, padx=10, sticky="ew")

        self.output_text = tk.Text(root, height=15, bg="#2c003e", fg="white",
                                   font=(FONT_NAME, 10), state="disabled", wrap="word")
        self.output_text.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")

        self.token_frame = tk.Frame(root, bg=BG_COLOR)
        self.token_frame.grid(row=4, column=0, pady=10, padx=10, sticky="ew")

        self.token_label = tk.Label(self.token_frame, text="Token Seed: None", bg=BG_COLOR,
                                    fg="white", font=(FONT_NAME, 10))
        self.token_label.pack(side="left", padx=5)

        self.copy_token_btn = tk.Button(self.token_frame, text="Copy Token Seed",
                                        command=self.copy_token,
                                        bg=FG_COLOR, fg="white", activebackground=ACTIVE_BG,
                                        relief="flat", font=(FONT_NAME, 10), cursor="hand2")
        self.copy_token_btn.pack(side="left", padx=5)

        self.download_btn = tk.Button(self.token_frame, text="Open Result Folder",
                                      command=self.download_file,
                                      bg=FG_COLOR, fg="white", activebackground=ACTIVE_BG,
                                      relief="flat", font=(FONT_NAME, 10), cursor="hand2")
        self.download_btn.pack(side="left", padx=5)

    def select_file(self):
        filename = filedialog.askopenfilename(title="Select MP4 File", filetypes=[("MP4 files", "*.mp4")])
        if filename:
            self.filepath = filename
            self.file_label.config(text=os.path.basename(filename))
            self.log(f"✅ File selected: {filename}")
        else:
            self.log("No file selected.")

    def run_process(self):
        if not self.filepath:
            messagebox.showerror("Error", "Please select an MP4 file first.")
            return

        self.send_btn.config(state="disabled")
        self.upload_btn.config(state="disabled")
        self.log("Starting process...\n")

        threading.Thread(target=self.run_bat_process).start()

    def run_bat_process(self):
        try:
            base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
            dest_path = os.path.join(base_dir, os.path.basename(self.filepath))
            shutil.copy2(self.filepath, dest_path)
            self.log(f"Copied file to script directory: {dest_path}")

            run_bat_path = os.path.join(base_dir, "run.bat")
            if not os.path.exists(run_bat_path):
                self.log(f"❌ run.bat not found in {base_dir}")
                self.enable_buttons()
                return

            process = subprocess.Popen(
                [run_bat_path, os.path.basename(dest_path)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.log(line.strip())
                    match = re.search(r'Token \(Seed\):\s*([A-Z0-9]+)', line)
                    if match:
                        self.token_seed = match.group(1)
                        self.update_token_label()

            process.wait()
            self.log("\nProcess finished.")

        except Exception as e:
            self.log(f"Error: {e}")

        self.enable_buttons()

    def log(self, text):
        self.output_text.config(state="normal")
        self.output_text.insert("end", text + "\n")
        self.output_text.see("end")
        self.output_text.config(state="disabled")

    def update_token_label(self):
        self.token_label.config(text=f"Token Seed: {self.token_seed}")

    def copy_token(self):
        if self.token_seed:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.token_seed)
            messagebox.showinfo("Copied", "Token seed copied to clipboard.")
        else:
            messagebox.showwarning("No Token", "No token seed to copy.")

    def download_file(self):
        base_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(base_dir):
            os.startfile(base_dir)
        else:
            messagebox.showerror("Error", "Result folder not found.")

    def enable_buttons(self):
        self.send_btn.config(state="normal")
        self.upload_btn.config(state="normal")

if __name__ == "__main__":
    root = tk.Tk()
    app = UnsafeYToolsApp(root)
    root.mainloop()
