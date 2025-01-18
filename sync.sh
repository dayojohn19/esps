# Get the last modified .py file if no input is provided
if [ -z "$1" ]; then
    file_to_convert=$(ls -t *.py | head -n 1)
else
    file_to_convert="${1}.py"
fi
# Ensure the script is run with the environment
source env/bin/activate
echo "File to convert: $file_to_convert"

# Compile Python script
mpy-cross "$file_to_convert" -o testfolder/"${file_to_convert%.py}.mpy"
echo $(pwd)
file_name="$1"
# Combine the directory and file name to get the full path
file_path="${current_dir}/${file_name}"
echo "------------------${file_path}------------------"
sleep 1
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
