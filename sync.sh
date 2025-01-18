#!/bin/bash
read "file"
# Ensure the script is run with the environment
source env/bin/activate


# Compile Python script
mpy-cross test1.py

# Get the remote URL
url=$(git remote get-url origin)
echo "Saving to $url"
sleep 1

# Commit and push changes
git add .
git commit -am 'Auto Commit'
git push
sleep 5
echo "Changes have been committed."

# Update version file
VERSION_FILE="version.json"
if [ ! -f "$VERSION_FILE" ]; then
    echo "$VERSION_FILE not found. Creating a new file with version 0."
    echo '{"version": 0}' > "$VERSION_FILE"
    VERSION=0
else
    VERSION=$(jq '.version' "$VERSION_FILE")
fi
NEW_VERSION=$((VERSION + 1))
jq ".version = $NEW_VERSION" "$VERSION_FILE" > temp.json && mv temp.json "$VERSION_FILE"
echo "Version updated to: $NEW_VERSION"
