# echo "Enter commit message:"
# read COMMIT_MSG

# Ask for destination path

# echo "Sync from $SOURCE to $DEST completed."
url=$(git remote get-url origin)
echo "Saving to $url"
sleep 1
git add .
git commit -am 'Auto Commit' 
# git push --force
sleep 1
echo "Changes have been committed with message: $COMMIT_MSG"

# rsync -avz /Users/nhoj/Desktop/garden/ESP_/synctest /Users/nhoj/Desktop/garden/esp32/synctest
# # Perform the rsync operation
# rsync -avz "$SOURCE" "$DEST"



sleep 1
VERSION_FILE="version.json"
if [ ! -f "$VERSION_FILE" ]; then
    echo "$VERSION_FILE not found. Creating a new file with version 0."
    echo '{"version": 0}' > "$VERSION_FILE"
    VERSION=0
else
    # Read the current version using jq
    VERSION=$(jq '.version' "$VERSION_FILE")
fi
NEW_VERSION=$((VERSION + 1))
jq ".version = $NEW_VERSION" "$VERSION_FILE" > temp.json && mv temp.json "$VERSION_FILE"
echo "Version updated to: $NEW_VERSION"
