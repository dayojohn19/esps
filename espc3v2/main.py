

from configs.configs import wifiSSID ,wifipassword, doorservoPin, doorPin
from configs.configs import batteryPin,BatteryMotorPin
from configs.configs import ledsignalPin
from machine import Pin, I2C, RTC   ,SoftI2C, reset,   UART,  ADC, sleep, deepsleep,   lightsleep, PWM, reset_cause, Timer
from led_signal import LEDSignal
import network
import time


from configs.configs import clock_scl, clock_sda, clock_sqw, alarm 
from clockModule import Clock, DS3231
import _thread
import socket

import gc
import os
import json
import urequests
from SimModule import Sim

import ujson










scanUntil = 18
alarm = {'am':7,'pm':15,'min':30}

pressed_time = 0
textfiles = ['feed','alarm','error']
files_to_update=["main.py", "version.json"]

ledlight = LEDSignal(ledsignalPin)
ledlight.start(100,3)

def textWriter(fileName=None, toWrite=None):
    try:
        with open(fileName, "a") as myfile:
            myfile.write(f"\n{toWrite}    [ {RTC().datetime()} ]")
            myfile.flush()
        print(f"Log written successfully:\n     {fileName} ---  {toWrite}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error while writing to log: {e}")        


class Battery():
    def __init__(self):
        
        print('Building Battery')
        self.BatteryMotorPin = BatteryMotorPin
        self.batteryPin = batteryPin
        self.record
    @property
    def record(self):
        bat = f'Motor: {self.motor}% \nModule: {self.module}%'
        textWriter('battery.txt',bat)
        return bat

    @property
    def motor(self):
        return self.battery(self.BatteryMotorPin,3,4095,min_reading=13)
    @property
    def module(self):
        return self.battery(self.batteryPin,3)
    def battery(self,pin, atten=3,max_reading=4095, min_reading=13):
        a = ADC(Pin(pin)) 
        a.atten(atten)
        def read(a):
            num_samples = 100  # Number of samples to average
            total = 0 
            for _ in range(num_samples):
                total += a.read()
                time.sleep(0.01)     
            v = total / num_samples        
            return v 
        def percent(value, bn=min_reading, bm=max_reading, new_min=0, new_max=100):
            return int(((value - bn) / (bm - bn)) * (new_max - new_min) + new_min    )
        raw = read(a)
        bat = percent(raw)
        print(f'{bat} %     Reading: {raw}')
        return bat
baty = Battery()
class Wake():
    @property
    def reason(self):
        print("Wake Reason:")
        cause = reset_cause()
        if cause == 4:
            print("     deepsleep")
            return 'deepsleep'
        else:
            print('     unknwon')
            return cause
wake = Wake()
class Buzzer():
    def __init__(self,pin=doorservoPin):
        self.buzz = Pin(pin, Pin.OUT,Pin.PULL_DOWN)
    @property
    def on(self):
        self.buzz.value(1)
    @property
    def off(self):
        self.buzz.value(0)
    def twosec(self):
        self.buzz.value(1)
        time.sleep(20)
        self.buzz.value(0)
        return        
    @property
    def signal(self):
        _thread.start_new_thread(self.twosec,())

buzzer = Buzzer()



def resetPin():
    pins = [20, 21, 4, 7, 6,5,10]
    for i in range(2):
        time.sleep(0.1)
        gc.collect
        time.sleep(0.1)
        for pin_num in pins:
            time.sleep(0.1)
            try:
                pin = Pin(pin_num, Pin.IN)  # Set the pin to input mode
                pin.irq(handler=None)
                pin.value(0)  # Ensure the pin value is reset to low (0)
                print(f"GPIO{pin_num} reset to input mode with low value")
            except ValueError:
                # Some pins might not be available or might be reserved for special functions
                print(f"GPIO{pin_num} is not available or cannot be reset")

def real_time(time_tuple=RTC().datetime()):
    # time_tuple = self.clock.datetime()
    month_names = ["January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"]
    year = time_tuple[0]
    month = time_tuple[1]
    day = time_tuple[2]
    hour = time_tuple[4]
    minute = time_tuple[5]
    second = time_tuple[6]
    if hour >= 12:
        period = "PM"
        if hour > 12:
            hour -= 12
    else:
        period = "AM"
        if hour == 0:
            hour = 12  # Midnight case
    formatted_time = '{} {}, {} {:02}:{:02}:{:02} {}'.format(
        month_names[month - 1], day, year, hour, minute, second, period)
    return formatted_time


 
def alarm_handler():
    print('\n  +++++ Alarm Pass Function Triggered! ++++\n')




class RFIDReader:
    def __init__(self, file_path=None):

        if file_path is None:
            file_path = 'rdm6300.json'
        self.file_path = file_path
        self.light = LEDSignal(doorservoPin)
        self.gothread = True
        self.rxPin = doorPin
        try:
            self.data = self.read()
        except:
            self.data = {}
            self.save
            self.data = self.read()
        self.processing = None
        if RTC().datetime()[0] < 2022:
            print('Nedd Updating sim.datetime()')
        self.timer = Timer(2)
        # self.timer.init(period=3600000, mode=Timer.PERIODIC, callback=self.selftimer)
        self.timer.init(period=1800000, mode=Timer.PERIODIC, callback=self.selftimer)
    def selftimer(self, timer=None):
        print('Checking Time 2')
        try:
            pass
            # bat = Battery()
            # bat.record
            # print('Battery: ',bat)
        except:
            pass
        
        ch = RTC().datetime()[4]
        if ch >= scanUntil:
            print('selftimer() time is 12 noon stopping RFID Reading')
            self.gothread = False
            self.timer.deinit()
            time.sleep(2)
            deepsleep(5000)

        print('To Start reading run scan()')
    def hasData(self):
        if not bool(self.data):
            print("The dictionary is empty.")
            return False
        else:
            print("The dictionary is not empty.")
            return True
    @property
    def save(self):
        try:
            with open(self.file_path, 'w') as file:
                json.dump(self.data, file)
            print(f"Successfully wrote to {self.file_path}")
            
            return True
        except Exception as e:
            print(f"Error writing JSON: {e}")
            return True
            
    def read(self):
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
        except FileNotFoundError:
            print('creating file')
            default_data = {}
            with open(self.file_path, 'w') as file:
                json.dump(default_data if default_data is not None else {}, file, indent=4)
                data = default_data if default_data is not None else {}
        return data            

    def add_maker(self):
        return real_time(RTC().datetime())

    def add(self, rf_id, initial_count=1):
        self.light.wink(0.5)
        rf_id = str(rf_id)
        print('Saving: ',rf_id)
        print('Current Data: ',self.data)

        """Add new card or update existing card in JSON file"""
        try:
            if self.processing == rf_id:
                print("passing multiple same id ")
                return
            self.processing = rf_id     
            print('Processing: ',rf_id)
            # _thread.start_new_thread(self.add_maker, ())
            if rf_id not in self.data:
                self.data[rf_id] = {
                    "id": rf_id,
                    "entry_count": initial_count,
                    "entries": {initial_count: self.add_maker()},
                    "last_seen": self.add_maker(),
                    "inside": True

                }
            else:
                self.data[rf_id]["entry_count"] += 1
                self.data[rf_id]["entries"].update({self.data[rf_id]["entry_count"]: self.add_maker()})
                self.data[rf_id]["last_seen"] = self.add_maker()
                self.data[rf_id]["inside"] = True
            time.sleep(1)
            gc.collect()
            time.sleep(1)
            self.save
            time.sleep(1)
            gc.collect()
            time.sleep(1)
            # return
            return self.inform(self.data[rf_id])
        except Exception as e:
            self.processing = None
            print(f"Error adding card: {e}")
            
            return False


    def inform(self,d):
        gc.collect()
        # if d['id']  in rfidTags:
        #     # TODO ADD FUNC TO confirm tag
        time.sleep(1)
        # print(f"informed RFID: {d['id']} \n")

        ec = 0
        for _ in d["entries"]:
            ec+=1
        # b = Battery()
        # b = b.record

        # s = f'{d["id"]} arrived: {d["last_seen"]} count {ec} {b}'
        time.sleep(1)
        # self.gothread = False # Before Resetting the pins
        time.sleep(2)
        # resetPin()
        time.sleep(2)
        gc.collect()
        # self.sim = isim()
        # self.sim.sendSMS(message=s)
        # time.sleep(1)
        # self.sim.receiveSMS()
        time.sleep(1)
        gc.collect()
        time.sleep(1)
        # self.gothread = True
        time.sleep(1)
        # for i in range(15):
            # feeder.go
            # print(f'Feeding in {i+1}/15')
            # time.sleep(0.1)
        time.sleep(1)
        # print(f"Prcessing {self.processing}  current {d['id']}")
        if self.processing == d['id']:
            self.processing = None
        return

    def whenTrue(self): # Reading RFID
        print('True Again')
        sc = 0
        lt = ''
        msdelay = 1 # from 25 reduced to 19
        while self.gothread:
            if self.rfid1.any() >13:  # Check if data available
                time.sleep(0.1)
                rt = self.rfid1.read()[1:13]
                try:
                    tag= rt.decode()
                except:
                    print('RT error', rt)
                    tag = None
                if tag:
                    if tag == lt:
                        sc += 1
                        print(f'.', end='')
                        self.light.wink(0.1)
                    else:
                        lt = tag
                        _thread.start_new_thread(self.add,(tag,))
                        print('r', end='')
                        sc = 0
                        print(f'\nThreading Add TAG: {tag}')
            time.sleep_ms(msdelay)  # Reduced sleep time        
        print('Thread goes false')
        return
    def whenFalse(self):
        i=0
        while self.gothread == False:
            i+=2
            print("                                           waiting thread", i)
            time.sleep(2)
        return
    def scan(self):
        # resetPin()
        gc.collect()
        print('\n     Starting scan....\n\n')
        self.light.wink(0.3)
        time.sleep(0.3)
        self.light.wink(0.3)


        self.rfid1 = UART(1, baudrate=9600, rx=self.rxPin, timeout=1)  # Reduced timeout
        self.rfid1.flush()
        while True:
            if self.gothread:
                self.whenTrue()
            else:
                self.whenFalse()
                print('Re Initiating Scan')
                return  self.scan()




class OTAUpdater:
    gc.collect()
    # ledlight.start(100)
    giturl = "https://github.com/dayojohn19/esp_supermini/"
    def __init__(self, repo_url=giturl, filenames=files_to_update):
        self.filenames = filenames
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
        response = urequests.get(firmware_url,timeout=7)
        if response.status_code == 200:
            print(f'Fetched latest firmware code, status: {response.status_code}')
            self.latest_code = response.text
            return True
        elif response.status_code == 404:
            print(f'File not found at \n     {firmware_url}')
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
        print('renaming latest_code.py to ',filename)
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
    
    def download_and_install_update_if_available(self):
        time.sleep(1)
        gc.collect()
        if self.check_for_updates():
            print('Updating Latest...')
            self.firmware_urls = []
            for filename in self.filenames:
                print(f'        Updating: {filename}')
                time.sleep(0.1)
                gc.collect()
                url = self.repo_url + 'main/' + filename
                print(f'            {url}')
                self.firmware_urls.append(url)
            for i in range(len(self.firmware_urls)):
                time.sleep(1)
                gc.collect()
                time.sleep(1)
                try:
                    if self.fetch_latest_code(self.firmware_urls[i]):
                        self.update_no_reset() 
                        self.update_and_reset(self.filenames[i]) 
                        print('Done ', i)
                except Exception as e:
                    print('Cant Update: ',i, "reason: ",e)
                time.sleep(1)
            with open('version.json', 'w') as f:
                json.dump({'version': self.current_version}, f)
            print('Restarting device... 5')
            for i in range(5):
                time.sleep(1)
                print(f'{5-i}')
            # sleep(5)
            print("\n\n         Applying Updates and Restarting \n\n")
            reset()  
        else:
            ledlight.stop()
            print('No new updates available.')
            time.sleep(2)
        return True












def connect_or_create_wifi():
    def wait_for_change(check_func, timeout_ms, *args, **kwargs):
        start_time = time.ticks_ms()
        last_value = check_func(*args, **kwargs)  # Get the initial value
        print("waiting")
        while True:
            time.sleep(1)
            print('.',end="")
            current_value = check_func(*args, **kwargs)  # Check the value again
            if current_value != last_value:  # Check if the value has changed
                print("Value changed!")
                return current_value  # Return the new value
            if time.ticks_ms() - start_time > timeout_ms:
                print("Timeout reached, no change in value.")
                return False  # Timeout, return None
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(wifiSSID, wifipassword)
    print("Connecting to: ",wifiSSID)
    wifiConnection =  wait_for_change(wifi.isconnected, 7000)
    try:
        if wifiConnection == False:
            wifi.active(False)
            time.sleep(2)
            ic = network.WLAN(network.AP_IF)
            ic.active(True)        
            ic.config(essid=str('HGW-5DF528'),password='dayosfamily')
            print("Created Hotspot")
            print('Web REPL on : ',ic.ifconfig())
        else:
            ic = network.WLAN(network.AP_IF)
            ic.active(False)
            print('Web REPL on : ',wifi.ifconfig())
    except Exception as e:
        print('Error in wifi connection: ',e)
        textWriter('error.txt',f'Error in wifi connection: {e}')
    return ic












print('\n----------- \n  ')


try:
    connect_or_create_wifi()
    # x = RFIDReader()
    # x.scan()


except Exception as e: 
    print("Error Main", "   Reason: ",e)
    print('Resetting in 10')
    for i in range(10):
        time.sleep(1)
    reset()

# gnd.on
time.sleep(1)
print('sleeping in 3')


