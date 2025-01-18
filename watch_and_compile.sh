import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import subprocess

WATCH_DIR = os.getcwd()
TEST_DIR = "/path/to/test/folder"

class Watcher:
    def __init__(self, directory_to_watch):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                time.sleep(5)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_modified(event):
        if event.is_directory:
            return None
        elif event.src_path.endswith(".py"):
            # Run mpy-cross on the changed file
            subprocess.run(["mpy-cross", event.src_path])
            
            # Get the base filename without extension
            basename = os.path.basename(event.src_path).replace(".py", ".mpy")
            
            # Move the .mpy file to the test folder
            mpy_file = os.path.join(WATCH_DIR, basename)
            subprocess.run(["mv", mpy_file, TEST_DIR])
            
            print(f"Processed and moved {basename} to {TEST_DIR}")
            
            # Run the .mpy file in a new terminal window
            subprocess.run(["osascript", "-e", f'tell application "Terminal" to do script "python {os.path.join(TEST_DIR, basename)}"'])

if __name__ == '__main__':
    w = Watcher(WATCH_DIR)
    w.run()