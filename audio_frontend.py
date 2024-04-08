"""Dieses Modul stellt das frontend für den gui_audiorecorder da."""

import tkinter as tk
from tkinter import ttk, messagebox
import click
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
        value = min(BLOCK_SIZES, key=lambda x: abs(x - int(value)))
        self.blocksize_slider.set(value)  #

    def setup_ui(self):
        self.root.title("Florian Stamer Audio Downloader")

        self.url_entry = self.create_input_field("URL:")
        self.filename_entry = self.create_input_field("Filename:")

        self.duration_slider = self.create_slider("Duration:", DURATION_MIN, DURATION_MAX)
        
        self.blocksize_slider = self.create_slider("Blocksize:", BLOCK_SIZE_MIN, BLOCK_SIZE_MAX)
        self.blocksize_slider.config(command=lambda value: self.on_slider_move(value))  
        
        self.create_button("List", self.display_recordings)
        self.create_button("Start", self.button_start)

        self.output_text = tk.Text(self.root, wrap='word')
        self.output_text.pack(fill='x')
        self.output_text.pack_forget()
        
        self.progress_frame = tk.Frame(self.root)
        self.progress_frame.pack(side="bottom", fill="x")

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
        self.output_text.delete(1.0, tk.END)
        list_of_recordings = list_recordings()
        
        if list_of_recordings:
            self.output_text.insert(tk.END, list_of_recordings)
            self.output_text.pack(fill='x')
        else:
            self.output_text.pack_forget()


    def update_progress_bar(self, duration):
        progress = ttk.Progressbar(self.progress_frame, length=200, mode='determinate', maximum=duration, value=0)
        progress.pack(fill='x')
        self.root.after(1000, self.countdown, duration, progress)
        self.root.update_idletasks()

    def countdown(self, time_left, progress):
        if time_left > 0:
            progress['value'] = progress['maximum'] - time_left
            progress.pack(fill='x')
            self.root.after(1000, self.countdown, time_left - 1, progress)
        else:
            messagebox.showinfo("Erfolg", "Download Abgeschlossen!")
            progress['value'] = progress['maximum']

@click.command()
@click.argument("url", required=False)
@click.option("--filename", "-f", default="myRadio", help="Name of recording")
@click.option("--duration", "-d", default=30, help="Duration of recording in seconds")
@click.option("--blocksize", "-b", default=64, help="Block size for read/write in bytes")
@click.option("--list", "-l", is_flag=True, help="List all recordings")

def main(url=None, filename="myRadio", duration=30, blocksize=64, list=False):
    if not any([url, list]):
        root = tk.Tk()
        app = AudioDownloaderApp(root)
        root.mainloop()
    elif list:
        list_of_recordings = list_recordings()
        if list_of_recordings:
            for recording in list_of_recordings:
                click.echo(recording)
        else:
            click.echo("No recordings available.")
    else:
        try:
            start_download(url, filename, duration, blocksize)
        except ValueError as e:
            click.echo(f"Error: {e}")

if __name__ == "__main__":
    main()