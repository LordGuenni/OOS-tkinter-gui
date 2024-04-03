"""Dieses Modul stellt das Backend für den gui_audiorecorder da."""

import datetime
import sqlite3
from threading import Thread
from urllib.parse import urlparse
import urllib.request
import time


class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect("recordings.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS recordings
                     (url TEXT, filename TEXT, duration INTEGER, creation_time TEXT)"""
        )
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.conn.close()
        

def validate_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False
                
def list_recordings():
    with DatabaseConnection() as c:
        print("List of recordings:")
        c.execute("SELECT * FROM recordings")
        recordings = []
        for row in c.fetchall():
            url, filename, duration, creation_time = row
            print(
                f"Url: {url} , File: {filename}, Duration: {duration} seconds, Created: {creation_time}"
            )
            recordings.append({
                'url': url,
                'filename': filename,
                'duration': duration,
                'creation_time': creation_time
            })
        return recordings


def record(url, filename, duration, blocksize):
    """Records audio from a Defined URL and saves it to a file."""
    try:
        print(f"Recording {filename}.mp3 from {url}...")
        start_time = time.time()
        
        with urllib.request.urlopen(url) as response:
            with open(f"{filename}.mp3", "wb") as f:
                while time.time() - start_time < duration:
                    f.write(response.read(blocksize))

        end_time = time.time()
        with DatabaseConnection() as c:
            c.execute("DELETE FROM recordings WHERE filename=?", (filename + ".mp3",))
            creation_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute(
                    "INSERT INTO recordings (url, filename, duration, creation_time) VALUES (?, ?, ?, ?)",
                    (url, filename + ".mp3", duration, creation_time),
                )   
        print(f"Recording finished. Duration: {end_time - start_time} seconds")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        

def start_download(url, filename, duration, block_size):
    if not validate_url(url):
        raise ValueError("Ungültige URL")
    Thread(target=record, args=(url, filename, duration, block_size)).start()
   
    
        
        
            



