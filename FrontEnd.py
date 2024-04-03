"""Dieses Modul stellt das FrontEnd für den gui_audiorecorder da."""

import tkinter as tk

from tkinter import ttk
from tkinter import messagebox

from audio_backend import list_recordings, start_download 


DURATION_MIN = 30
DURATION_MAX = 300
BLOCK_SIZE_MIN = 64
BLOCK_SIZE_MAX = 512

def create_url_input(root):
    url_label = tk.Label(root, text="URL:")
    url_label.pack(fill='x')
    url_entry = tk.Entry(root)
    url_entry.pack(fill='x')
    return url_entry

def create_filename_input(root):
    filename_label = tk.Label(root, text="Dateiname:")
    filename_label.pack(fill='x')
    filename_entry = tk.Entry(root)
    filename_entry.pack(fill='x')
    return filename_entry

def create_duration_slider(root):
    duration_label = tk.Label(root, text="Dauer:")
    duration_label.pack(fill='x')
    duration_slider = tk.Scale(root, from_=DURATION_MIN, to=DURATION_MAX, orient='horizontal')
    duration_slider.pack(fill='x')
    return duration_slider

def create_blocksize_slider(root, on_change):
    blocksize_label = tk.Label(root, text="Blockgröße:")
    blocksize_label.pack(fill='x')
    blocksize_slider = tk.Scale(root, from_=BLOCK_SIZE_MIN, to=BLOCK_SIZE_MAX, orient='horizontal', command=on_change)
    blocksize_slider.pack(fill='x')
    return blocksize_slider

def main():
    
    root = tk.Tk()
    root.title("Florian Stamer Audio Downloader")
    progress_bars = []
    
    def button_start():
        duration = int(duration_slider.get())
        url = str(url_entry.get())
        filename = filename_entry.get()
        if filename == "":
            filename = "myRadio" 
        block_size = int(blocksize_slider.get())
        try:
            start_download(url, filename, duration, block_size)
            update_progress_bar(duration, progress_bars, root)
        except ValueError as e:
            messagebox.showerror("Fehler", str(e))
        
    def on_blocksize_slider_changed(value):        
        sizes = [64, 128, 256, 512]
        blocksize_slider.set(min(sizes, key=lambda x:abs(x-float(value))))

    url_entry = create_url_input(root)
    filename_entry = create_filename_input(root)
    duration_slider = create_duration_slider(root)
    blocksize_slider = create_blocksize_slider(root, on_blocksize_slider_changed)
    
    list_button = tk.Button(root, text="List", command=lambda: display_recordings())
    list_button.pack(fill='x')

    start_button = tk.Button(root, text="Start",command=button_start)
    start_button.pack(fill='x')

    output_text = tk.Text(root, wrap=tk.NONE)
    output_text.pack(fill='x')
    output_text.pack_forget()
    
    def display_recordings():
        recordings = list_recordings()
        if recordings:
            output_text.pack(fill='x')  
            output_text.delete(1.0, tk.END)  
            max_length = 0
            for recording in recordings:
                text = f"Url: {recording['url']} , File: {recording['filename']}, Duration: {recording['duration']} seconds, Created: {recording['creation_time']}\n"
                output_text.insert(tk.END, text)
                max_length = max(max_length, len(text))
            output_text.config(state='disabled')  
            root.update_idletasks()  
            width = max(root.winfo_width(), max_length * 8) + 50  
            root.geometry(f"{width}x{root.winfo_height() + output_text.winfo_height()}") 
        else:
            output_text.pack_forget()

    def countdown(time_left, progress_index):
        if time_left > 0:
            progress_bars[progress_index]['value'] = progress_bars[progress_index]['maximum'] - time_left
            root.after(1000, countdown, time_left - 1, progress_index)
        else:
            messagebox.showinfo("Erfolg", "Download Abgeschlossen!")
            progress_bars[progress_index]['value'] = progress_bars[progress_index]['maximum']
        
    def update_progress_bar(duration, progress_bars, root):
        progress = ttk.Progressbar(root, length=200, mode='determinate')
        progress.pack(fill='x')
        progress_bars.append(progress)
        progress['maximum'] = duration
        progress['value'] = 0
        countdown(duration, len(progress_bars) - 1)  

    root.mainloop()

if __name__ == "__main__":
    main()
    


