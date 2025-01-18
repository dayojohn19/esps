import os
import subprocess
import sys

def compile_file(file_path):
    if not file_path.endswith(".py"):
        print("Error: The file is not a Python (.py) file.")
        return

    # Run mpy-cross on the specified file
    subprocess.run(["mpy-cross", file_path])
    
    # Get the base filename without extension
    basename = os.path.basename(file_path).replace(".py", ".mpy")
    
    # Move the .mpy file to the test folder
    test_dir = "/Users/nhoj/Desktop/garden/ESP_/testfolder"
    mpy_file = os.path.join(os.path.dirname(file_path), basename)
    subprocess.run(["mv", mpy_file, test_dir])
    
    print(f"Processed and moved {basename} to {test_dir}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python compile_current_file.py <path_to_current_file>")
    else:
        compile_file(sys.argv[1])

