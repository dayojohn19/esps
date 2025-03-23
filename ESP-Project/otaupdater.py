import gc
from configs.configs import files_to_update
import os
import json
import time
import urequests
from machine import reset   
from textwriter import  textWriter

class OTAUpdater:
    gc.collect()
    # ledlight.start(100)
    # giturl = "https://github.com/dayojohn19/esp_supermini/"
    # giturl = "https://github.com/dayojohn19/esp_supermini/"
    giturl = "https://github.com/dayojohn19/esps/"
    def __init__(self, repo_url=giturl, filenames=files_to_update):
        self.filenames = filenames
        print('\n\n     ', repo_url)
        self.repo_url = repo_url
        if "www.github.com" in self.repo_url :
            print(f"Updating {repo_url} to raw.githubusercontent")
            self.repo_url = self.repo_url.replace("www.github","raw.githubusercontent")
        elif "github.com" in self.repo_url:
            print(f"Updating {repo_url} to raw.githubusercontent'")
            self.repo_url = self.repo_url.replace("github","raw.githubusercontent")            
        self.version_url = self.repo_url + 'main/version.json'
        print(f"version url is: {self.version_url}")
        if 'version.json' in os.listdir():    
            gc.collect()
            with open('version.json') as f:
                self.current_version = int(json.load(f)['version'])
                f.close()
            print(f"Current device firmware version is '{self.current_version}'")
        else:
            self.current_version = 0
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)
                f.close()
            gc.collect()
        self.download_and_install_update_if_available()
        
    def fetch_latest_code(self,firmware_url)->bool:
        time.sleep(1)
        response = urequests.get(firmware_url,timeout=14)
        gc.collect()
        if response.status_code == 200:
            print(f'\n Fetched latest {firmware_url}\n')
            gc.collect()
            self.latest_code = response.text
            gc.collect()
            return True
        elif response.status_code == 404:
            print(f'File not found  \n           {firmware_url}')
            pass

    def update_no_reset(self):
        time.sleep(1)
        with open('latest_code.py', 'w') as f:
            f.write(self.latest_code)
        self.current_version = self.latest_version
        self.latest_code = None
        return

    def update_and_reset(self,filename):
        time.sleep(1)
        print('         saving latest ',filename)
        os.rename('latest_code.py', filename)  
        return

    def check_for_updates(self):
        time.sleep(1)
        """ Check if updates are available."""
        response = urequests.get(self.version_url)
        try:
            if '404' in response.text:
                print('Cant found version URL 404')
                return
            data = json.loads(response.text)
            self.latest_version = int(data['version'])
            print(f'        Latest: {self.latest_version}\n         Current: {self.current_version}')    
            return True if self.current_version < self.latest_version else False
        except Exception as e:
            print('Error: ',e)
            self.latest_version = 2
            self.current_version = 1
            textWriter('error.txt',f'Error in checking for updates: {e}')
    
    def download_and_install_update_if_available(self):
        time.sleep(1)
        gc.collect()
        try:
            if self.check_for_updates():
                print('Updating Latest')
                self.firmware_urls = []
                for filename in self.filenames:
                    print(f'         {filename} Updating', end='')
                    time.sleep(0.1)
                    gc.collect()
                    url = self.repo_url + 'main/ESP-Project/' + filename
                    print(f'              {url}')
                    self.firmware_urls.append(url)
                ct = 0 
                for c in self.firmware_urls:
                    ct+=1
                for i in range(ct):
                    time.sleep(1)
                    gc.collect()
                    time.sleep(1)
                    try:
                        if self.fetch_latest_code(self.firmware_urls[i]):
                            gc.collect()
                            time.sleep(1)
                            self.update_no_reset() 
                            gc.collect()
                            time.sleep(1)
                            self.update_and_reset(self.filenames[i]) 
                            gc.collect()
                            time.sleep(1)
                            print('Done ++ Updating ', self.filenames[i])
                    except Exception as e:
                        print('Cant Update: ',self.filenames[i], "\n                        reason: ",e)
                        textWriter('error.txt',f'Error in updating: {self.filenames[i]} {e}')
                    time.sleep(1)
                with open('version.json', 'w') as f:
                    json.dump({'version': self.current_version}, f)
                print('Restarting device 5')
                for i in range(5):
                    time.sleep(1)
                    print(f'{5-i}')
                # sleep(5)
                print("\n\n         Applying Updates and Restarting \n\n")
                reset()  
            else:
                print('No new updates available.')
                time.sleep(2)
            return True
        except Exception as e:
            print('Cant download and update: ',e)

