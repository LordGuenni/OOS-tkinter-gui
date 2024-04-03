"""Dieses Modul stellt das FrontEnd für den gui_audiorecorder da."""

import tkinter as tk
from tkinter import ttk, messagebox
from audio_backend import list_recordings, start_download

DURATION_MIN = 30
DURATION_MAX = 300
BLOCK_SIZE_MIN = 64
BLOCK_SIZE_MAX = 512
BLOCK_SIZES = [64, 128, 256, 512]

class AudioDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.setup_ui()

    def on_slider_move(self, value):
        # Round the value to the nearest valid block size
        value = min(BLOCK_SIZES, key=lambda x: abs(x - int(value)))
        self.blocksize_slider.set(value)  # Assuming self.blocksize_slider is the correct reference

            
    def setup_ui(self):
        self.root.title("Florian Stamer Audio Downloader")

        self.url_entry = self.create_input_field("URL:")
        self.filename_entry = self.create_input_field("Filename:")

        self.duration_slider = self.create_slider("Duration:", DURATION_MIN, DURATION_MAX)
        
        self.blocksize_slider = self.create_slider("Blocksize:", BLOCK_SIZE_MIN, BLOCK_SIZE_MAX)
        self.blocksize_slider.config(command=lambda value: self.on_slider_move(value))  # Passing value to on_slider_move
        
        self.create_button("List", self.display_recordings)
        self.create_button("Start", self.button_start)

        self.output_text = tk.Text(self.root, wrap=tk.NONE)
        self.output_text.pack(fill='x')
        self.output_text.pack_forget()

    def create_input_field(self, label_text):
        label = tk.Label(self.root, text=label_text)
        label.pack(fill='x')
        entry = tk.Entry(self.root)
        entry.pack(fill='x')
        return entry

    def create_slider(self, label_text, min_val, max_val, resolution=None):
        label = tk.Label(self.root, text=label_text)
        label.pack(fill='x')
        if resolution:
            slider = tk.Scale(self.root, from_=min_val, to=max_val, orient='horizontal', resolution=resolution)
        else:
            slider = tk.Scale(self.root, from_=min_val, to=max_val, orient='horizontal')
        slider.pack(fill='x')
        return slider

    def create_button(self, text, command):
        button = tk.Button(self.root, text=text, command=command)
        button.pack(fill='x')

    def button_start(self):
        duration = int(self.duration_slider.get())
        url = str(self.url_entry.get())
        filename = self.filename_entry.get() or "myRadio"
        block_size = int(self.blocksize_slider.get())
        try:
            start_download(url, filename, duration, block_size)
            self.update_progress_bar(duration)
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
        
    def display_recordings(self):
        list_of_recordings = list_recordings()
        if list_of_recordings:
            self.output_text.pack(fill='x')  
            self.output_text.delete(1.0, tk.END)  
            self.output_text.insert(tk.END, list_of_recordings)
            self.output_text.config(state='disabled')  
            self.root.update_idletasks()  
            width = self.output_text.winfo_width() + 20  
            self.root.geometry(f"{width}x{self.root.winfo_height()}")  
        else:
            self.output_text.pack_forget()

    def update_progress_bar(self, duration):
        progress = ttk.Progressbar(self.root, length=200, mode='determinate', maximum=duration, value=0)
        progress.pack(fill='x')
        self.root.after(1000, self.countdown, duration, progress)

    def countdown(self, time_left, progress):
        if time_left > 0:
            progress['value'] = progress['maximum'] - time_left
            self.root.after(1000, self.countdown, time_left - 1, progress)
        else:
            messagebox.showinfo("Erfolg", "Download Abgeschlossen!")
            progress['value'] = progress['maximum']

def main():
    root = tk.Tk()
    app = AudioDownloaderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()