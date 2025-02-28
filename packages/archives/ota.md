# ota.py

>   it takes **arguments wifi ssid, password, giturl, [ list_of_files   ]
>
>   Over the Air update
>
>   Accepts github repo path
>
>   list of file path is the list you want to update

sample_url= `https://github.com/dayojohn19/esp12f/` <small>should put "/" at the end </small>

sample_file_path = [`file/path/first.txt,   file/path/second.txt`]


```
x = OTAUpdater(SSID,PASSWORD,sample_url,sample_file_path)

x.download_and_install_update_if_available()   
``` 

<hr>

`veersion.json` will be created, you can do version.json auto update on push on github actions
create a file in this path on your github, you just create Actions  >   New Workflow    >   Automation  >   Manual Automation    

then copy the code

 <strong>`.github/workflows/increment-version.yml`</string>

```
name: Increment Version on Push

on:
  push:
    branches:
      - main  # Change to your default branch name if it's different (e.g., 'master')

jobs:
  increment-version:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v2

      - name: Increment Version and Add Human-readable Timestamp
        run: |
          # Check if version.json exists, else initialize version to 0
          if [ -f version.json ]; then
            # Read the current version from version.json
            VERSION=$(jq '.version' version.json)
          else
            VERSION=0
          fi

          VERSION=$((VERSION + 1))

          TIMESTAMP=$(date +"%b %d %H:%M:%S %Y")

          echo "{\"version\": $VERSION, \"timestamp\": \"$TIMESTAMP\"}" > version.json

          echo "New version: $VERSION, Timestamp: $TIMESTAMP"

      - name: Commit and Push Changes
        run: |
          git config --global user.email "github-actions[bot]@users.noreply.github.com"
          git config --global user.name "GitHub Actions"
          git add version.json
          git commit -m "Increment version to $VERSION and add timestamp $TIMESTAMP"
          git push
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```          