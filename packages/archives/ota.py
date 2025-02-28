import network
import urequests
import os
import json
import machine
from time import sleep
import gc

class OTAUpdater:
    def __init__(self, ssid, password, repo_url, filenames):
        self.filenames = filenames
        self.ssid = ssid
        self.password = password
        self.repo_url = repo_url
        if "www.github.com" in self.repo_url :
            print(f"Updating {repo_url} to raw.githubusercontent")
            self.repo_url = self.repo_url.replace("www.github","raw.githubusercontent")
        elif "github.com" in self.repo_url:
            print(f"Updating {repo_url} to raw.githubusercontent'")
            self.repo_url = self.repo_url.replace("github","raw.githubusercontent")            
        self.version_url = self.repo_url + 'main/version.json'
        print(f"version url is: {self.version_url}")
        self.firmware_urls = []
        
        for filename in self.filenames:
            url = self.repo_url + 'main/' + filename
            self.firmware_urls.append(url)

        
        if 'version.json' in os.listdir():    
            with open('version.json') as f:
                self.current_version = int(json.load(f)['version'])
            print(f"Current device firmware version is '{self.current_version}'")

        else:
            self.current_version = 0
            
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)
                return
            
    def connect_wifi(self):
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        if sta_if.isconnected():
            return
        else:
            sta_if.connect(self.ssid, self.password)
            while not sta_if.isconnected():
                print('.', end="")
                sleep(0.25)
            print(f'Connected to WiFi, IP is: {sta_if.ifconfig()[0]}')
            return
        
    def fetch_latest_code(self,firmware_url)->bool:
        response = urequests.get(firmware_url)
        if response.status_code == 200:
            print(f'Fetched latest firmware code, status: {response.status_code}')
            self.latest_code = response.text
            return True
        
        elif response.status_code == 404:
            print(f'Firmware not found - {firmware_url}.')
            pass

    def update_no_reset(self):
        with open('latest_code.py', 'w') as f:
            f.write(self.latest_code)
        self.current_version = self.latest_version
        self.latest_code = None
        return


    def update_and_reset(self,filename):
        os.rename('latest_code.py', filename)  
        return


        
    def check_for_updates(self):
        """ Check if updates are available."""
        
        self.connect_wifi()
        response = urequests.get(self.version_url)
        try:
            data = json.loads(response.text)
            self.latest_version = int(data['version'])
            print(f'latest version is: {self.latest_version}')
        except:
            self.latest_version = 2
            self.current_version = 1
        newer_version_available = True if self.current_version < self.latest_version else False
        
        print(f'Newer version available: {newer_version_available}')    
        return newer_version_available
    
    def download_and_install_update_if_available(self):
        if self.check_for_updates():
            for i in range(len(self.firmware_urls)):
                gc.collect()
                try:
                    if self.fetch_latest_code(self.firmware_urls[i]):
                        self.update_no_reset() 
                        self.update_and_reset(self.filenames[i]) 
                except:
                    print('Passing: ',self.firmware_urls[i])
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)
            print('Restarting device... 5')
            sleep(5)
            machine.reset()  
        else:
            print('No new updates available.')
        return