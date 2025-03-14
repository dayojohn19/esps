

# for bare11
from machine import Pin, I2C, RTC , DEEPSLEEP,SoftI2C, reset
from configs.configs import sim_rx,sim_tx,sim_uart, wifiSSID ,wifipassword, groundPin, gatePin, doorPin,doorservoPin, ledsignalPin, BatteryMotorPin , feederpin
from machine import UART, Pin, ADC, RTC, sleep, deepsleep,lightsleep, PWM, reset_cause
from led_signal import LEDSignal
import network
import time
from servoModule import feedRun, Servo, feeder, feedRun2
from SimModule import Sim
from utime import ticks_ms
from configs.configs import clock_scl, clock_sda, clock_sqw, alarm 
from clockModule import Clock, DS3231
import _thread
import socket

import ujson
import json
import os

class Feeder():
    def __init__(self,feederpin=feederpin, initFeed = 10):
        self.servo_pin = Pin(feederpin)
        self.servo = PWM(self.servo_pin)
        self.servo.freq(50)
        self.backwward = 23
        self.stop = 0
        self.forward = 110
        self.slowforward = 90
        self.initFeed=initFeed
        self.goCount = 3
        self.servo.duty(0)
    def back(self):
        gnd.on
        time.sleep(0.01)
        for s in range(5):
            time.sleep(0.1)
            self.servo.duty(self.backwward)
            time.sleep(0.1)
            self.servo.duty(self.stop)
            time.sleep(0.1)
            print(s)
        gnd.off
    def finish(self):
        try:
            self.servo.duty_u16(0)
        except:
            self.servo.duty(0)
        time.sleep(1)
        gnd.off
    @property
    def slow(self):
        gnd.on
        self.servo.duty(self.slowforward)
        time.sleep(1.4) # One Complete rev
        self.servo.duty(0)
    @property
    def go(self):
        gnd.on
        self.servo.duty(self.forward)
        # time.sleep(0.636) # One Complete Revolution
        time.sleep(0.16) # One Complete Revolution
        # time.sleep(0.32) # One Complete Revolution
        self.servo.duty(0)
feeder = Feeder()

def resetPin():
    pins = [20, 21, 4, 7, 6,5,10]
    for i in range(2):
        time.sleep(0.1)
        gc.collect
        time.sleep(0.1)
        for pin_num in pins:
            time.sleep(0.1)
            try:
                pin = Pin(pin_num, Pin.IN, Pin.PULL_DOWN)  # Set the pin to input mode
                pin.value(0)  # Ensure the pin value is reset to low (0)
                print(f"GPIO{pin_num} reset to input mode with low value")
            except ValueError:
                # Some pins might not be available or might be reserved for special functions
                print(f"GPIO{pin_num} is not available or cannot be reset")
    # try:
    #     len = 1
    #     del len
    # except Exception as e:
    #     print('Error in del len',e)

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


class Power:
    def __init__(self,pin = groundPin):
        self.pin = Pin(pin,Pin.OUT)
        self.power = False
    @property
    def on(self):
        self.pin.value(1)
        self.power = True
    @property
    def off(self):
        self.pin.value(0)
        self.power = False

gnd = Power(groundPin) # whole ground Pin
def isim():
    st = time.time()
    time.sleep(1)
    gnd = Power(groundPin) # whole ground Pin
    gnd.on
    while time.time() - st < 10:
        sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
        if sim is not None:
            break
    return sim
# try:
#     gnd.on
#     print('1st Time Sim Object')
#     time.sleep(2)
#     sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
# except Exception as e:
#     try:
#         print('2nd Time Importing Sim')
#         gnd.on
#         time.sleep(3)
#         sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
#     except Exception as e:
#         print('Error in Sim Object: ',e)
def alarm_handler():
    try:
        sim = sim
        ts = sim.datetime()
        sim.sendSMS(message=f'{ts} Alarm Is Triggered ')
    except:
        try:
            sim = sim
            ts = sim.datetime()
            sim.sendSMS(message=f'{ts}Alarm Is Triggered')
        except:
            print('cant send message')
    print('\n  +++++ Alarm Pass Function Triggered! ++++\n')

def updateClock(c,s):
    try:
        c.datetime()
    except:
        c.clock.datetime()
        c = c.clock
    # if c.OSF():
    newTime = s.datetime()
    updatedt = date_to_tuple(newTime)
    c.datetime((updatedt))
    print('+++ Time Updated ++++')
    # else:
    #     print('Time is Correct')
# try:
#     print('1st Time importing Clock Object')
#     clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
# except Exception as e:
#     try:
#         print('2nd Time importing Clock Object')
#         clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
#     except Exception as e:
#         print('Cant create Clock Reason: ',e)
# time.sleep(2)



class RFIDReader:
    def __init__(self, file_path=None):
        # resetPin()
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
        # try:
        #     self.sim = sim
        # except Exception as e:
        #     print('Error in sim object')
        #     self.sim = None
        # self.result = 0
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
            self.light.wink(0.5)
            return True
        except Exception as e:
            print(f"Error writing JSON: {e}")
            return True
    def add_maker(self):
        # return
        # self.result = self.sim.datetime()
        return real_time(RTC().datetime())
        # return self.result
        # if self.sim is not None:
        #     return self.sim.datetime()
        # try:
        #     return self.sim.datetime()
        # except:
        #     return 0
        # time.sleep(5)
        # return time.time()

    def add(self, rf_id, initial_count=1):
        """Add new card or update existing card in JSON file"""
        try:
            _thread.start_new_thread(self.add_maker, ())
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
            _thread.start_new_thread(self.inform, (self.data[rf_id],))
            # self.inform(self.data[rf_id])
        except Exception as e:
            print(f"Error adding card: {e}")
            return False

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
    def inform(self,d):
        time.sleep(1)
        print(f"informed RFID: {d} \n")
        self.gothread = False
        ec = 0
        for _ in d["entries"]:
            ec+=1
        s = f'{d["id"]} arrived: {d["last_seen"]} count {ec}\n'
        time.sleep(1)
        resetPin()
        self.sim = isim()
        # sms_json = ujson.dumps(d).encode()
        sms_json = s.encode()
        self.sim.sendSMS(message=sms_json)
        time.sleep(1)
        self.sim.receiveSMS()
        time.sleep(1)
        for i in range(15):
            feeder.go
            print(f'Feeding in {i+1}/15')
            time.sleep(0.1)
        # TODO ADD FUNC TO FEED
        time.sleep(1)
        self.gothread = True
        self.scan()

    def scan(self):
        resetPin()
        gc.collect()
        print('\n     Starting scan....\n\n')
        # self.sim.uart.deinit()
        time.sleep(2)
        self.rfid1 = UART(1, baudrate=9600, rx=self.rxPin, timeout=10)  # Reduced timeout
        self.rfid1.flush()
        lt = ''
        sc = 0
        msdelay = 25  # Reduced delay to 50ms
        def read_rfid_data(uart):
            if uart.any():  # Check if data available
                start = uart.read(1)
                if start == b'\x02':
                    data = uart.read(12)
                    end = uart.read(1)
                    try:
                        if data and len(data) == 12 and end == b'\x03':
                            tag_hex = data[0:10].decode()
                            return tag_hex[1:10]
                    except:
                        pass
                else:
                    try:
                        data = uart.read(20).decode()[:9]
                        if data and int(data[0]) >= 1 and len(data) <= 9 and ' ' not in data:
                            return data
                    except:
                        pass
            return None

        print('Scanning....')
        while self.gothread:
            # tag = read_rfid_data(self.rfid1)
            if self.rfid1.any() >10:  # Check if data available
                rt = self.rfid1.read()[:10]
                try:
                    tag= rt.decode()
                except:
                    print('RT error', rt)
                    tag = None
            #     start = self.rfid1.read(1)
            #     if start == b'\x02':
            #         data = self.rfid1.read(12)
            #         end = self.rfid1.read(1)
            #         try:
            #             if data and len(data) == 12 and end == b'\x03':
            #                 tag_hex = data[0:10].decode()
            #                 tag =  tag_hex[1:10]
            #         except:
            #             print('tag first err')
            #             tag = None
            #     else:
            #         try:
            #             # if type(len) == int:
            #             #     del len
            #             data = self.rfid1.read(20).decode()[:9]
            #             if data and int(data[0]) >= 1:
            #                 count = 0
            #                 for char in data:
            #                     count += 1
            #                     if count > 9:  # Exit early if the count exceeds 9
            #                         break
            #                 if count <= 9 and ' ' not in data:
            #                     tag =  data
            #                     # print("Conditions met!")
            #                 else:
            #                     pass
            #                     # print("Conditions not met!")
            #             else:
            #                 pass
            #                 # print("Conditions not met!")                        
            #             # if data and int(data[0]) >= 1 and len(data) <= 9 and ' ' not in data:
            #             #     tag =  data
                        
            #         except Exception as e: 
            #             # try:

            #             #     print('typerror del len')
            #             #     del len
            #             # except Exception as e:
            #             #     print('tag second err',e)
            #         # except Exception as e:
            #             # try:
            #             #     len=1
            #             #     del len
            #             # except Exception as e:
            #             #     print('not err on len',e)
            #             # print('tag second err',e)
            #             # try:
            #             #     if type(len) == int:
            #             #         del len
            #             # except NameError as e:
            #             #     print('UnboundLocalError: ',e)
            #             tag = None
            else:
                tag = None

            if tag:
                if tag == lt:
                    sc += 1
                    print(f'.', end='')
                    self.light.wink(0.1)
                else:
                    lt = tag
                    print(f'\nTAG: {tag}')
                    self.add(tag)
                    print('r', end='')
                    self.save
                    sc = 0
            time.sleep_ms(msdelay)  # Reduced sleep time
        print('Ending thread....')















Pin(clock_scl, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
Pin(clock_sqw, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
Pin(clock_sda, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
alarm = {'am':7,'pm':15,'min':30}
pressed_time = 0
textfiles = ['feed','alarm','error']
files_to_update=["main.py", "version.json"]
feedblink = 119
flyblink = 419
ledlight = LEDSignal(ledsignalPin)
ledlight.wink()







import gc
import os
import json
import urequests
# for i in range(4):
#     print(f'Updated from github v4{i}')
#     time.sleep(1)
class OTAUpdater:
    ledlight.start(100)
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
        response = urequests.get(firmware_url,timeout=7)
        if response.status_code == 200:
            print(f'Fetched latest firmware code, status: {response.status_code}')
            self.latest_code = response.text
            return True
        elif response.status_code == 404:
            print(f'File not found at \n     {firmware_url}')
            pass

    def update_no_reset(self):
        with open('latest_code.py', 'w') as f:
            f.write(self.latest_code)
        self.current_version = self.latest_version
        self.latest_code = None
        return

    def update_and_reset(self,filename):
        print('renaming latest_code.py to ',filename)
        os.rename('latest_code.py', filename)  
        return

    def check_for_updates(self):
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
                gc.collect()
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















# gnd.on

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

def textWriter(fileName=None, toWrite=None):
    try:
        with open(fileName, "a") as myfile:
            myfile.write(f"\n{toWrite}    [ {RTC().datetime()} ]")
            myfile.flush()
        print(f"Log written successfully:\n     {fileName} ---  {toWrite}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error while writing to log: {e}")        


def connect_or_create_wifi():
    def test_internet_connection():
        try:
            # Try to connect to Google's DNS server (8.8.8.8)
            addr = socket.getaddrinfo('8.8.8.8', 53)
            s = socket.socket()
            s.connect(addr[0][-1])
            print('Internet connected')
            s.close()
            return True
        except Exception as e:
            print('No internet connection:', e)
    
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
        time.sleep(0.1)  # Small delay to avoid tight loop, adjust if needed
    # blueLED.start(500)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    # networklists = wifi.scan()    
    # for n in networklists:
    #     nn = n[0]  # SSID (network name)
    #     rssi = n[3]  # RSSI (signal strength)
    #     print(f"SSID: {nn.decode()}, Signal Strength (RSSI): {rssi} dBm")
    wifi.connect(wifiSSID, wifipassword)
    # wifi.connect('Infinix HOT 10S', '123456789')
    # ic.config(essid=str('mywifi'),password='1234')
    # blueLED.start(1000)
    print("Connecting to: ",wifiSSID)
    wifiConnection =  wait_for_change(wifi.isconnected, 7000)
    try:
        if wifiConnection == False:
            wifi.active(False)
            # blueLED.start(100)
            time.sleep(2)
            ic = network.WLAN(network.AP_IF)
            ic.active(True)        
            ic.config(essid=str('HGW-5DF528'),password='dayosfamily')
            # ic.config(essid=str('mywifi'),password='1234')
            print("Created Hotspot")
            print('Web REPL on : ',ic.ifconfig())
            # blueLED.stop()
        else:
            ic = network.WLAN(network.AP_IF)
            ic.active(False)
            # blueLED.stop()
            print('Web REPL on : ',wifi.ifconfig())
            print("Connected Wifi")
    except Exception as e:
        print('Error in wifi connection: ',e)
        textWriter('error.txt',f'Error in wifi connection: {e}')
    if test_internet_connection():
        print("Connected to the internet")
    else:
        print('Connecting to internet via sim')
        sim.connectInternet()
        if test_internet_connection():
            print("\n       SIM     Connected to the internet")
        else:
            print("No internet connection")
            textWriter('error.txt','No internet connection')
            return False
    return ic




time.sleep(2)
class Battery():
    def __init__(self):
        from configs.configs import batteryPin,BatteryMotorPin
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
        return self.battery(self.BatteryMotorPin,3,4095,min_reading=2795)
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





def extend_alarm(clock,addsec=15):
    time.sleep(2)
    ct = clock.get_time()
    hr,min,sec =  map(int, ct[1].split(':'))
    print('     Wake Reason: ',wake.reason)
    print("         Wake time:              " , ct[1])
    sec = sec+addsec
    if sec >= 60:
        sec = sec-60
        min += 1
        if min >= 60:
            hr+=1
            min=min-60
    # print(f'Setting Alarm at {hr} {min} {sec}')
    clock.alarm_daily(hr,min, sec)
    time.sleep(2)
    print('         Sleep Time:             ',clock.get_time()[1])





class DoorGate():
    # for ESO MAX settings 
    def __init__(self, doorservo=doorservoPin, doorbuttonpin=doorPin):
        self.closeAngle = 180
        self.openAngle = 0
        # self.doorbutton = Pin(doorbuttonpin, Pin.IN, Pin.PULL_DOWN)
        self.doorbuttonpinobj = doorbuttonpin
        self.doorservopinobj = doorservo
        self.isOpen = True
        self.setUp()

    def touch(self,pin=None):
        global pressed_time
        new_time = ticks_ms()
        if (new_time - pressed_time) < 500:
            return
        pressed_time = new_time
        # if not self.irq_lock.acquire():
        #     return
        if self.isOpen == True:
            self.close()
            # self.setpos(180)
            # self.gnd_active.on()
            self.isOpen = False
        else:
            self.open()
            self.isOpen = True
        return
    def setUp(self):
        self.doorbutton = Pin(self.doorbuttonpinobj, Pin.IN, Pin.PULL_DOWN)
        self.doorbutton.irq(trigger=Pin.IRQ_RISING, handler=self.touch)  
        self.min_duty = 40
        self.max_duty = 1115        
        servo = PWM(Pin(self.doorservopinobj))
        servo.freq(50)
        self.servo = servo
        # self.setpos(90)
    @property
    def close(self):
        if self.isOpen:
            print('Close')
            gnd.on
            self.setpos(self.closeAngle)
            time.sleep(2)
            gnd.off
            self.isOpen == False
        return
    @property
    def open(self):
        print('Open')
        gnd.on
        if self.isOpen:
            return
        self.isOpen == True
        start_time = time.time()
        self.setpos(self.openAngle)
        while (time.time() - start_time) < 5:
            pass
        self.close()
        return
        

    def setpos(self, pos):
        def map_range(value, old_min, old_max, new_min, new_max):
            return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
        old_min = -4
        old_max = 30
        new_min = 0
        new_max = 180
        pos = map_range(pos, new_min, new_max, old_min, old_max)
        self.pos = int(pos)
        duty = int((pos/360) * (self.max_duty - self.min_duty) + self.min_duty)
        # duty = int((pos/180) * (new_max - new_min) + new_min)
        self.servo.duty(duty)
        return
# doorgate = DoorGate()
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

class FlyGate():
    from configs.configs import gatePin
    def __init__(self, flygatePin = gatePin):
        self.openAngle = 330
        self.closeAngle = 110
        self.gate = Servo(gatePin)
        self.isOpen = False
    @property
    def open(self):
        if self.isOpen:
            return
        self.isOpen = True
        gnd.on
        time.sleep(0.5)
        self.gate.move(self.openAngle)
        time.sleep(3)
        gnd.off
    @property
    def close(self):
        if self.isOpen:
            gnd.on
            time.sleep(0.5)
            self.gate.move(self.closeAngle)
            time.sleep(1)
            gnd.off
            self.isOpen = False
        return
flygate = FlyGate()

# def tester(ms=1):
#     feeder.servo.duty(feeder.forward)
#     time.sleep(ms)
#     feeder.servo.duty(0)
        # time.sleep(1)
        # time.sleep(1)
        # for i in range(10):
        #     print(f'Initial Feeding in {i+1}/{self.goCount}')
        #     time.sleep(0.4)
        #     self.servo.duty(self.forward)
        #     time.sleep(0.05)
        #     self.servo.duty_u16(self.stop)
        #     time.sleep(0.4)
        # time.sleep(0.1)
        # self.servo.duty_u16(0)



class Train():
    def __init__(self, feeder=feeder):
        global ledlight
        self.ledlight = ledlight
        self.power = Power(groundPin)
        self.power.on
        self.isflying = False
        self.flyduration=0
    def flySignal(self):
        if self.flyduration == 0:
            self.flyduration = float('inf')
        st = time.time()
        while self.isflying:
            cd = time.time()-st
            if  cd > self.flyduration:
                self.isflying = False
                break            
            # print(f'Train.fly in {cd}/{self.flyduration}')
            time.sleep(1.25)    
            self.ledlight.wink(0.025)
        return True
    def fly(self):
        self.isflying = True
        gnd.on
        _thread.start_new_thread(self.flySignal,())
        time.sleep(4)
        flygate.open
        time.sleep(3)
        buzzer.twosec()
        time.sleep(1)
        # gnd.off
        for i in range(self.flyduration):
            time.sleep(1)
            print(f"Flying in {i+1}/{self.flyduration}")

    def rest(self):
        self.isflying = False
        flygate.close
        time.sleep(2)
    def feed(self,ftimes):
        ledlight.on()
        for i in range(ftimes):
            print(f'Feeding in {i+1}/{ftimes}')
            time.sleep(1)
            feeder.go
        time.sleep(2)
        ledlight.off()
        gnd.off
    def session(self, nsession=1,flysec=60,feedtime=10):
        self.flyduration = flysec
        for i in range(nsession):
            print(f'        Session in {i}/{nsession}')
            time.sleep(1)
            print('Feeding')
            self.feed(ftimes=feedtime)
            print('     Done Feeding')
            for i in range(30):
                time.sleep(1)
                print(f"Waiting after feeding {i+1}/30")
            print('Flying')
            self.fly()
            print('      Done Flying')
            time.sleep(1)
            print('     Resting')
            self.rest()
            print('Feeding')
            self.feed(feedtime)
            print(f'Session {i+1} / {nsession} ended')
        return True
t = Train()
            



def date_to_tuple(datestr):
    """
    from sim.datetime() to updating ds3231 time
    """
    date_str = datestr
    month_map = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5,'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10,'November': 11, 'December': 12}
    date_parts = date_str.split(', ')
    month_name = date_parts[0]
    day, year = date_parts[1].split(' ')
    month = month_map[month_name]
    day = int(day)
    year = int(year)
    time_parts, am_pm = date_parts[2].split(' ')
    hour, minute, second = map(int, time_parts.split(':'))
    if am_pm == 'PM' and hour != 12:
        hour += 12
    elif am_pm == 'AM' and hour == 12:
        hour = 0
    date_tuple = (year, month, day, hour, minute, second, 0)
    return date_tuple #(0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])

 


def alert_user(alertmessage):
    textWriter('alert.txt',str(alertmessage))
    try:
        timestamp = RTC().datetime()
        try:
            af.sim.sendwhatsapp(f'{timestamp} -- {alertmessage}')
            print('Done sending')
        except:
            print('Cant send whatsapp')
        try:
            af.sim.sendSMS(message=f'{timestamp} -- {alertmessage}')
        except:
            print(' Cant Send sms')
    except Exception as e:
        textWriter('alert.txt',f'Cant alert {e}')

# def feed_servo(pin):
#     runServo()
#     time.sleep(1)

try:    
    class AutoFeeder():
        def __init__(self): 
            # self.moduleSleepTime = 30* 60 
            self.moduleSleepTime = 7200000 # 2hrs
            try: 
                self.power = Power(groundPin)
                self.power.on
            except: pass     
            try: 
                try:
                    time.sleep(2)
                    self.sim = sim
                except Exception as e:
                    print('Error first importing Sim: ',e)
                    # try: self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
                    # except: pass
                self.newCommand = self.sim.receiveSMS()
                if self.newCommand == None:
                    print('No New Command')
                else:
                    if "check battery" in self.newCommand[0].lower():
                        print('Requesting to check battery', self.newCommand)
                    print(f"Create a Func that will create a Command\n       {self.newCommand}")

            except Exception as e: print("Sim ERROR ",e)

            if self.isDaytime() == False:
            # if self.isDaytime() == True:
                self.clock = clock
                print('Going TO sleep')
                for i in range(10):
                    time.sleep(1)
                    print(f' Sleeping in {i}/10 Reason night Time')
                    print("Create a Func TODO")
                    import machine
                    print('deepsleep and wait for alarm')
                time.sleep(2)
                machine.deepsleep()
            self.buzzer = Buzzer()


            self.battery = Battery()

            if wake.reason == 'deepsleep':
                print('Wake Reason DeepSleep Start Training')
                # self.fly = FlyGate(gatePin) #2
                # self.door = DoorGate(doorPin, doorservoPin)
                # self.feed = Feeder(feederpin) # 9
                
                self.train = Train()
                self.train.session()
                print('Logging in log.txt')
                try:

                    gnd.off
                    time.sleep(2)
                    gnd.on
                    time.sleep(10)
                    
                    sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
                    try:
                        ts = sim.datetime()
                        try:
                            b = self.battery.record
                            sim.sendSMS(message=f'{ts} finished Recursions {b}')
                        except Exception as e:
                            textWriter('error.txt',f'{e}')
                    except Exception as e:
                        ts = e
                    bp = self.battery.module
                    toLogString = f' {bp} % Battery {ts}  -   Successful Session Rutime'
                    textWriter('log.txt',toLogString)
                except Exception as e:
                    textWriter('log.txt', f'Error Logging Runtime  {RTC.datetime()} -  {e}')
                clock = clock
                print('Sleeping Again for ', self.moduleSleepTime)
                time.sleep(5)
                gnd.off
                time.sleep(5)
                import machine
                machine.deepsleep(self.moduleSleepTime)
            else:
                print('Need Wake Reason == deepsleep to start training')
                print('Sleeping in module just been powered')
                time.sleep(2)
                import machine 
                machine.deepsleep(5000)


        def isDaytime(self):
            try: 
                self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
                # clock_i2c = SoftI2C(scl=Pin(clock_scl), sda=Pin(clock_sda))
                # self.clock = DS3231(clock_i2c)
                try: 
                    updateClock(self.clock.clock , self.sim)
                    # if self.clock.OSF():
                    #     newTime = self.sim.datetime()
                    #     updatedt = date_to_tuple(newTime)
                    #     self.clock.datetime((updatedt))
                    #     print('+++ Time Updated ++++')
                    # else:
                    #     print('Time is Correct')
                except Exception as e:
                    print("Error : ",e)                
                ch = self.clock.datetime()[4]
                if 11 <= ch < 17: 
                    if self.moduleSleepTime == 0:
                        self.moduleSleepTime = 60000
                    print('Daytime True')
                    return True
                if 7 <= ch < 11:
                    mode= 'toss'
                    if mode == 'toss':
                        print('Daytime True')
                        self.train = Train()
                        self.train.session(1,60,20)
                        print('\    ++++    nStarting to Receive RFID ++\n')

            
            # try: self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
            except:
                print('Error Cant import clock')
                textWriter('error.txt','Clock Error')

            return False
    


except Exception as e:
    print('\n ++++++++++   Cant Create Automatic Feeder Machine    ',e)
    time.sleep(4)



print('\n----------- \n  ')


try:
    print('trying to update')
    # af = AutoFeeder()
    gnd.on
    ic = connect_or_create_wifi()
    ou = OTAUpdater()

except Exception as e: print("Error COnnecting to network!", "   Reason: ",e)
# gnd.on
time.sleep(1)

# if gnd.power:
#     # try:
#     #     af = AutoFeeder()
#     # except Exception as e:
#     #     print('Error')
# else:
#     for i in range(3):
#         print('\n\n     Please type "gnd.on"  First to power up\n\n')
#         time.sleep(2)
gnd.off
print('sleeping in 3')

# adc = ADC(0)
# adc.atten(ADC.ATTN_11DB)   
# adc.read() # MAx 4095
# door = DoorGate()
# checkBattery()

# Initialize 
#  on GPIO 3 (or choose another pin like GPIO 34)
# print("Turning off everything")
# time.sleep(1)
# import webrepl
# webrepl.start()
 # internetconnection
# print('Turning Off Again')
# time.sleep(60)
# time.sleep(3)
# ic.active(False)
# blueLED.stop()
# self.gnd_active.off()
# deepsleep()



# uart1 = UART(1, baudrate=115200, tx=Pin(20), rx=Pin(21)) 
# while True:
#     uart1.write('AT\r\n')  # Basic AT command to check if ESP32 B responds
#     time.sleep(1)  # Wait for a second
    
#     if uart1.any():  # Check if there is a response
#         response = uart1.read()
#         print("Response from ESP32 B:", response.decode('utf-8'))
#     time.sleep(1)  # Wait for a second




