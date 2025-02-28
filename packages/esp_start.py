import json
import network
import gc
import time
import socket
import ure
import esp  
import urequests
import os
import machine
from time import sleep
import uasyncio as asyncio
from configs.configs import essid,password,server_addr,giturl, files_to_update

timer = None
led = machine.Pin(2, machine.Pin.OUT)
def blink_led(timer):
    led.value(not led.value()) 

def start_blinking(speed=500):
    global timer
    if timer is None: 
        timer = machine.Timer(0)
        timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=blink_led)
def stop_blinking():
    global timer
    if timer is not None:
        timer.deinit() 
        timer = None 
        led.value(1)


async def dontwait(thelazyfunction,timeout=60):
    print('were not waiting you till you finish',timeout)
    time.sleep(2)
    try:
        # Run the function with a timeout of 3 seconds
        await asyncio.wait_for(thelazyfunction(), timeout)
        print("Function finished successfully.")
    except asyncio.TimeoutError:
        print("Function timed out.")


class OTAUpdater:
    print("OTA Updating")
    led.value(1)
    start_blinking(100)
    def __init__(self, essid=essid, password=password, repo_url=giturl, filenames=files_to_update):
        self.filenames = filenames
        self.ssid = essid
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
        self.download_and_install_update_if_available()
    # def connect_wifi(self):
    #     sta_if = network.WLAN(network.STA_IF)
    #     sta_if.active(True)
    #     if sta_if.isconnected():
    #         return
    #     else:
    #         sta_if.connect(self.ssid, self.password)
    #         while not sta_if.isconnected():
    #             print('.', end="")
    #             sleep(0.25)
    #         print(f'Connected to WiFi, IP is: {sta_if.ifconfig()[0]}')
    #         return
        
    def fetch_latest_code(self,firmware_url)->bool:
        response = urequests.get(firmware_url,timeout=7)
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
        
        # self.connect_wifi()
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
            print('Downloading latest code...')
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

            # print('Restarting device... 5')

            # sleep(5)
            print("\n\n         Applying Updates\n\n")
            time.sleep(3)
            machine.reset()  
        else:
            stop_blinking()
            print('No new updates available.')
            time.sleep(2)
        return True
# Initialize global variables

# Network configuration
wlan_ap = network.WLAN(network.AP_IF)
wlan_ap.active(True)
wlan_ap.config(essid=str(essid),password=str('123456789'))
wlan_sta = network.WLAN(network.STA_IF)
wlan_sta.active(False)
temp_server_timeout = 20
server_socket = None
start_time = None
# LED Blinking functions




def wait_to_connect(wlan_sta):
    gc.collect()
    startTime = time.time()
    while not wlan_sta.isconnected() and time.time() - startTime <= 10:
        print('connecting')
        time.sleep(0.8)

# HTTP response functions
def send_response(client, payload, status_code=200):
    client.sendall("HTTP/1.0 {} OK\r\n".format(status_code))
    client.sendall("Content-Type: text/html\r\n")
    client.sendall("Content-Length: {}\r\n".format(len(payload)))
    client.sendall("\r\n")
    if len(payload) > 0:
        client.sendall(payload)

def handle_root(client):
    print("scannning  wifi available")
    time.sleep(1)
    response_header = """
        <h1>Wi-Fi Client Setup</h1>
        <form action="configure" method="post">
          <label for="ssid">SSID</label>
          <select name="ssid" id="ssid">
    """
    response_variable = ""
    for ssid, *_ in wlan_sta.scan():
        response_variable += '<option value="{0}">{0}</option>'.format(ssid.decode("utf-8"))
    response_footer = """
           </select> <br/>
           Password: <input name="password" type="password"></input> <br />
           <input type="submit" value="Submit">
         </form>
    """
    gc.collect()
    send_response(client, response_header + response_variable + response_footer)

def handle_configure(client, request):
    print('Handling Configure')
    match = ure.search("ssid=([^&]*)&password=(.*)", request)
    if match is None:
        send_response(client, "Parameters not found", status_code=400)
        return
    ssid = match.group(1)
    password = match.group(2)
    if len(ssid) == 0:
        send_response(client, "SSID must be provided", status_code=400)
        return
    print(f"\n\n     Creating New Config for {ssid}")
    gc.collect()
    with open('configs/wifiSettings.json') as f:
        config = json.load(f)
    with open('configs/wifiSettings.json', 'w') as f:
        config["ssid"] = ssid
        config["ssid_password"] = password
        json.dump(config, f)
    wlan_sta.active(True)
    time.sleep(1)
    wlan_sta.connect(ssid, password)
    wait_to_connect(wlan_sta)
    print("is Connected: ",wlan_sta.isconnected())
    if wlan_sta.isconnected():    
        print('Handle Configure Connected')
        return True
    send_response(client, "CANT CONNECT {}".format(ssid))

def handle_not_found(client, url):
    send_response(client, "Path not found: {}".format(url), status_code=404)

def stop():
    global server_socket
    if server_socket:
        server_socket.close()

def handle_server(client, ntimeout):
    server_header = f"""
    <h2>Server Remaining runtime {ntimeout} of {temp_server_timeout}</h2>
    <h1>Files in Config</h1>
    <ul>
    """
    server_variable = ""
    directory = '/configs'
    files = os.listdir(directory)
    for file in files:
        pfile = directory + '/' + file
        if os.stat(pfile)[0] == 0x4000:
            print('its a path not file')
            pass
        else:
            server_variable += f"""<li><a href="/download?file={pfile}">
             {file}</a></li>
               """
    server_footer = """
    </ul>
    <a href="/exit"> EXIT </a>
    """
    send_response(client, server_header + server_variable + server_footer)

def extract_file_path(request):
    try:
        start_index = request.find('?file=') + 6
        if start_index > 5:
            end_index = request.find(' ', start_index)
            if end_index == -1:
                end_index = len(request)
            return request[start_index:end_index]
    except Exception as e:
        print(f"Error extracting file path: {e}")
    return None

def handle_download(client, fpath):
    if not os.stat(fpath):
        client.send('HTTP/1.1 404 Not Found\r\n')
        client.send('Content-Type: text/plain\r\n')
        client.send('Connection: close\r\n\r\n')
        client.send("File not found!")
        return
    client.send('HTTP/1.1 200 OK\r\n')
    client.send('Content-Type: application/octet-stream\r\n')
    client.send(f'Content-Disposition: attachment; filename="{fpath}"\r\n')
    client.send('Connection: close\r\n\r\n')
    with open(fpath, 'rb') as f:
        chunk = f.read(1024)
        while chunk:
            client.send(chunk)
            chunk = f.read(1024)

def temporary_server():
    addr = socket.getaddrinfo('192.168.4.1', 80)[0][-1]
    print("Starting Temporary Server",addr)
    global server_socket
    stop()
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    server_socket.setblocking(False)
    print('listening on', addr)
    global start_time
    start_time = time.time()
    while True:
        try:
            ntimeout = time.time() - start_time
            if ntimeout > temp_server_timeout:
                gc.collect()
                break
            client, addr = server_socket.accept()
            client.settimeout(5.0)
            print('client connected from', addr)
            start_time += 30
            request = b""
            try:
                while not "\r\n\r\n" in request:
                    request += client.recv(512)
            except OSError:
                pass
            if "HTTP" not in request:
                client.close()
                continue
            url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request.decode('ascii')).group(1).rstrip("/")
            if url == "":
                handle_server(client, ntimeout)
            if '/download' in request:
                request = request.decode('utf-8')
                file_path = extract_file_path(request)
                print('Found path: ', file_path)
                handle_download(client, file_path)
            if '/exit' in request:
                client.close()
                server_socket.close()
                gc.collect()
                break
        except OSError as e:
            if e.errno == 11: 
                print("No client connected, waiting...")
                time.sleep(1)
            else:
                print(f"Socket error: {e}")
                break
    gc.collect()
    # client.close()
    # server_socket.close()
    # return True

async def start(port=80):
    stop_blinking()
    led.value(0)
    addr = socket.getaddrinfo(server_addr, 80)[0][-1]
    global server_socket
    stop()
    server_socket = socket.socket()
    server_socket.bind(addr)
    server_socket.listen(1)
    server_socket.setblocking(False)
    print('Starting on', addr)
    wlan_sta.active(True)
    wlan_ap.active(True)
    start_time = time.time()
    while True:
        try:
            ntimeout = time.time() - start_time
            if ntimeout > temp_server_timeout:
                gc.collect()
                break
            client, addr = server_socket.accept()
            client.settimeout(5.0)
            print('client connected from', addr)
            request = b""
            try:
                while not "\r\n\r\n" in request:
                    request += client.recv(512)
            except OSError:
                pass
            
            if "HTTP" not in request:
                client.close()
                continue
            
            url = ure.search("(?:GET|POST) /(.*?)(?:\\?.*?)? HTTP", request.decode('ascii')).group(1).rstrip("/")
            print(f"URL is {url}")
            gc.collect()
            time.sleep(0.1)

            if url == "":
                handle_root(client)
            elif url == "configure":
                if handle_configure(client, request):
                    time.sleep(1)
                    if OTAUpdater():
                        print("OTA DONE")
                        break
                    machine.reset()   
            else:
                handle_not_found(client, url)
            print('Looping', wlan_sta.isconnected())
            client.close()
        except OSError as e:
            if e.errno == 11: 
                print("     connect to download config Files...")
                time.sleep(1)
            else:
                print(f"Socket error: {e}")
                break
        # return True
    # ap_if.active(False)

def connectWifi(wifiSSID=None, wifiPassword=None):
    wlan_ap.active(True)
    temporary_server()
    wlan_sta.active(True)
    # wlan = network.WLAN(network.STA_IF)
    time.sleep(1)
    gc.collect()
    time.sleep(1)
    esp.osdebug(None)
    time.sleep(1)
    print(f"\n\n     Fetching Wifi config for {wifiSSID}")
    if wifiSSID is None:
        with open('configs/wifiSettings.json') as f:
            config = json.load(f)
            wifiSSID = config['ssid']
            wifiPassword = config['ssid_password']
    else:
        print(f"\n\n     Creating New Config for {wifiSSID}")
        with open('configs/wifiSettings.json') as f:
            config = json.load(f)
        with open('configs/wifiSettings.json', 'w') as f:
            config["ssid"] = wifiSSID
            config["ssid_password"] = wifiPassword
            json.dump(config, f)
    time.sleep(1)
    print(f"     Connecting:  {wifiSSID} ")
    wlan_sta.connect(wifiSSID, wifiPassword)
    wait_to_connect(wlan_sta)
    time.sleep(1)
    if wlan_sta.isconnected():
        print('Connected to network turning wifi off')
        wlan_ap.active(False)
        if OTAUpdater():
            print("\nOTA Updated..\n\n")
            time.sleep(3)
            return True
        else:
            print("\n\n ****  Need to run New Update *****\n")
            time.sleep(3)
            machine.reset()
            # return False
        print("Cant Update OTA")
    else:
        gc.collect()
        time.sleep(1)
        print("Starting Config Server")
        asyncio.run(dontwait(start,60   ))

connectWifi()
print("Esp STARTED \n\n")
time.sleep(5)

server_socket.close()