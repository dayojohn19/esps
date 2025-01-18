#!/bin/bash

# Directory to watch
WATCH_DIR="/path/to/your/python/files"
# Directory to move .mpy files to
TEST_DIR="/path/to/test/folder"

# Ensure inotify-tools is installed
if ! command -v inotifywait &> /dev/null
then
    echo "inotifywait could not be found, please install inotify-tools"
    exit
fi

# Function to run the script in a new terminal window
run_in_new_terminal() {
    osascript <<EOF
tell application "Terminal"
    do script "$1"
end tell
EOF
}

# Watch for changes in .py files
inotifywait -m -e close_write --format '%w%f' "$WATCH_DIR" | while read FILE
do
    if [[ "$FILE" == *.py ]]; then
        # Run mpy-cross on the changed file
        mpy-cross "$FILE"
        
        # Get the base filename without extension
        BASENAME=$(basename "$FILE" .py)
        
        # Move the .mpy file to the test folder
        mv "${WATCH_DIR}/${BASENAME}.mpy" "$TEST_DIR"
        
        echo "Processed and moved ${BASENAME}.mpy to $TEST_DIR"
        
        # Run the .mpy file in a new terminal window
        run_in_new_terminal "python ${TEST_DIR}/${BASENAME}.mpy"
    fi
done