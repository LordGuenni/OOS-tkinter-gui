"""Dieses Modul stellt das backEnd für den gui_audiorecorder da."""

import datetime
import sqlite3
import threading
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse

from tabulate import tabulate

DATABASE_NAME = "recordings.db"

class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect(DATABASE_NAME)
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
        rows = c.fetchall()
        list_of_recordings = tabulate(
            rows, headers=("URL", "Filename", "Duration", "Created"), tablefmt="heavy_outline"
        )
        print(list_of_recordings)
        return list_of_recordings


def record_audio(url, filename, duration, block_size):
    start_time = time.time()
    try:
        print(f"Recording {filename}.mp3 from {url}...")
        with urllib.request.urlopen(url) as response:
            with open(f"{filename}.mp3", "wb") as f:
                while time.time() - start_time < duration:
                    f.write(response.read(block_size))
        end_time = time.time()
        print(f"Recording finished. Duration: {end_time - start_time} seconds")
        return filename
    except (urllib.error.URLError, IOError) as e:
        print(f"An error occurred while recording: {e}")
        return None


def add_recording_to_database(url, filename, duration):
    creation_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = filename + ".mp3" 
    with DatabaseConnection() as c:
        c.execute("SELECT COUNT(*) FROM recordings WHERE filename = ?", (filename,))
        count = c.fetchone()[0]
        if count > 0:
            # If a recording with the same filename already exists, delete it
            c.execute("DELETE FROM recordings WHERE filename = ?", (filename,))
        c.execute("INSERT INTO recordings (url, filename, duration, creation_time) VALUES (?, ?, ?, ?)", 
                  (url[:30], filename, duration, creation_time))


def record(url, filename, duration, block_size):
    recorded_filename = record_audio(url, filename, duration, block_size)
    if recorded_filename:
        add_recording_to_database(url, recorded_filename, duration)
    else:
        print("Recording could not be added to the database.")


def start_download(url, filename, duration, block_size):
    if not validate_url(url):
        raise ValueError("Invalid URL")
    threading.Thread(target=record, args=(url, filename, duration, block_size)).start()
