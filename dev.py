import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process_args):
        self.process_args = process_args
        self.process = None
        self.start_process()

    def start_process(self):
        if self.process:
            self.process.terminate()
        print(f"Starting process: {' '.join(self.process_args)}")
        self.process = subprocess.Popen(self.process_args)

    def on_modified(self, event):
        if event.src_path.endswith(".py"):
            print(f"File changed: {event.src_path}. Restarting...")
            self.start_process()

if __name__ == "__main__":
    path = "."
    command = [sys.executable, "main.py"]
    
    event_handler = ReloadHandler(command)
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
