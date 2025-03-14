

# for bare11
from machine import Pin, I2C, RTC , DEEPSLEEP,SoftI2C

from configs.configs import sim_rx,sim_tx,sim_uart, wifiSSID ,wifipassword, groundPin, gatePin, doorPin,doorservoPin, ledsignalPin, BatteryMotorPin 
from machine import UART, Pin, ADC, RTC, sleep, deepsleep,lightsleep, PWM, reset_cause
from led_signal import LEDSignal
import network
import time
from servoModule import feedRun, Servo, feeder, feedRun2
from SimModule import Sim
from utime import ticks_ms
from configs.configs import clock_scl, clock_sda, clock_sqw, alarm 
from clockModule import Clock
pressed_time = 0
batteryPin=0
feederpin = 9
powerpin = 10
textfiles = ['feed','alarm','error']
feedblink = 119
flyblink = 419
startingNotif = LEDSignal(8)
startingNotif.start(500)
time.sleep(2)
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
# gnd.on
wake_reason = reset_cause()


def textWriter(fileName=None, toWrite=None):
    try:
        with open(fileName, "a") as myfile:
            myfile.write(f"\n{toWrite}    [ {RTC().datetime()} ]")
            myfile.flush()
        print(f"Log written successfully:\n    {toWrite}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error while writing to log: {e}")        


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
        time.sleep(0.1)  # Small delay to avoid tight loop, adjust if needed
    # blueLED.start(500)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    networklists = wifi.scan()    
    for n in networklists:
        nn = n[0]  # SSID (network name)
        rssi = n[3]  # RSSI (signal strength)
        print(f"SSID: {nn.decode()}, Signal Strength (RSSI): {rssi} dBm")
    wifi.connect(wifiSSID, wifipassword)
    # wifi.connect('Infinix HOT 10S', '123456789')
    # ic.config(essid=str('mywifi'),password='1234')
    # blueLED.start(1000)
    print("Connecting to: ",wifiSSID)
    wifiConnection =  wait_for_change(wifi.isconnected, 5000)
    if wifiConnection == False:
        wifi.active(False)
        # blueLED.start(100)
        time.sleep(2)
        ic = network.WLAN(network.AP_IF)
        ic.active(True)        
        ic.config(essid=str('DAYO_CONTROLLER'),password='123456789')
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
    return ic




time.sleep(2)
class Battery():
    def __init__(self):
        from configs.configs import batteryPin,BatteryMotorPin
        print('Building Battery')
        self.BatteryMotorPin = BatteryMotorPin
        self.batteryPin = batteryPin
        bat = f'Motor Battery: {self.motor}% \n         Module Battery: {self.module}%'
        textWriter('battery.txt',bat)
    @property
    def motor(self):
        print('        Motor Max Reading as of 2/19/2025 16:46:35 battery: 100 % 3898.71  ')
        textWriter('battery.txt',f' {af.sim.battery()}')
        return self.battery(self.BatteryMotorPin,2,3898,min_reading=2009)
    @property
    def module(self):
        print('        Module Max Reading as of 2/19/2025 16:46:7  battery: 90 % 3703.4  ')
        return self.battery(self.batteryPin,2)
    def battery(self,pin, atten=3,max_reading=4095, min_reading=100):
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



import _thread
srange=1000
def thread1():
    x = Servo(8)
    for i in range(srange):
        time.sleep(1)
        print(f'{8}Thread',i)
        x.move(180)
        time.sleep(2)
        x.move(0)
        time.sleep(2)
def thread2():
    x = Servo(7)
    for i in range(srange):
        time.sleep(1)
        print(f'{7}Thread',i)
        x.move(180)
        time.sleep(2)
        x.move(0)
        time.sleep(2)
def thread3():
    x = Servo(3)
    for i in range(srange):
        time.sleep(1)
        print(f'{3}Thread',i)
        x.move(180)
        time.sleep(2)
        x.move(0)
        time.sleep(2)
def thread4():
    x = Servo(5)
    for i in range(srange):
        time.sleep(1)
        print(f'{5}Thread',i)
        x.move(180)
        time.sleep(2)
        x.move(0)
        time.sleep(2)
def thread5():
    x = Servo(2)
    for i in range(srange):
        time.sleep(1)
        print(f'{5}Thread',i)
        x.move(180)
        time.sleep(2)
        x.move(0)
        time.sleep(2)
# _thread.start_new_thread(thread1,())
# _thread.start_new_thread(thread2,())
# _thread.start_new_thread(thread3,())
# _thread.start_new_thread(thread4,())
# _thread.start_new_thread(thread5,())

result = {'module': None}
threading = False
def import_task(module_name):
    try:
        globals()[module_name] = __import__(module_name)
        result['module'] = globals(__import__(module_name))
    except Exception as e:
        result['error':e]
def import_with_timeout(module_name, timeout=5):
    global result
    global threading
    threading = True
    result = {'module':None}
    _thread.start_new_thread(import_task,(module_name,))
    start_time = time.time()
    while time.time() - start_time <= timeout and threading == True:
        global threading
        if result['module'] is not None:
            return result['module']
        if 'error' in result:
            print('Error Importing')
            return None
        time.sleep(0.5)
    print(f'Timeou Failed to import {module_name}')
    return None
# import sys
# sys.modules.pop('long',None)


def alarm_handler():
    print('\n  +++++ Alarm Pass Function Triggered! ++++\n')

def extend_alarm(clock,addsec=15):
    time.sleep(2)
    ct = clock.get_time()
    hr,min,sec =  map(int, ct[1].split(':'))
    print('     Wake Reason: ',wake_reason)
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


print('\n----------- \n  ')





class DoorGate():
    # for ESO MAX settings 
    def __init__(self, doorbuttonpin=doorPin, doorservo=doorservoPin):
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
        self.doorbutton = Pin(self.doorbuttonpinobj, Pin.IN, Pin.PULL_UP)
        self.doorbutton.irq(trigger=Pin.IRQ_FALLING, handler=self.touch)  


        self.min_duty = 40
        self.max_duty = 1115        
        servo = PWM(Pin(self.doorservopinobj))
        servo.freq(50)
        self.servo = servo
        # self.setpos(90)
    def close(self):
        print('Close')
        self.setpos(self.closeAngle)
        return
    def open(self):
        print('Open')
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








class Train():
    def __init__(self, feeder,clock):
        self.openAngle = 200
        self.closeAngle = -10
        self.light = LEDSignal(ledsignalPin)
        self.gate = Servo(gatePin)
        self.ground = Pin(powerpin,Pin.OUT)
        self.power = Power(powerpin)
        self.power.on
        self.light.stop()
        self.feeder = feeder
        self.clock = clock
    def feed(self):
        self.ground.on()
        try:
            textWriter('feed.txt',f'Feed Done {' '.join(self.clock.get_time())}')
        except:pass
        self.light.start(feedblink,20)
        time.sleep(1.5)
        self.feeder.go() 
        time.sleep(3)
        self.light.stop()
    def open(self):
        time.sleep(0.5)
        self.gate.move(self.openAngle)
        time.sleep(1)
        self.light.start(500,2)
    def close(self):
        time.sleep(0.5)
        self.gate.move(self.closeAngle)
        time.sleep(1)
    def train(self,train=1, seconds=None):
        try:
            # ic.active(False)
            print('Turning Network OFF')
            global sim
            print('Turning Simcard off')
        except Exception as e:
            print('Not connected to anything',e)        
        if seconds == None:
            print('Please Add How Many times and Seconds train(2,60)')
            return
        print('Initial Feeding...')
        self.power.on()  
        self.light.start(feedblink)
        self.feeder.go()    
        print('     Waiting to Finish the feeds')
        self.light.stop()
        self.open()
        waitTime = 30
        for i in range(waitTime):
            sleep(1)
            print(f'            {i+1}/{waitTime} Waiting')
        self.close()
        for i in range(int(train)):
            print(f'Train {i}/{train} ')
            print('Starting Light in 1000')
            self.ground.on()
            time.sleep(1)
            self.light.start(flyblink)
            for ii in range(seconds):
                print(f'    flying for {ii+1}/{seconds} ')
                time.sleep(1)
            self.ground.on()    
            self.light.stop()
            time.sleep(2)
            self.close()
            self.light.start(feedblink,30)
            self.feed()
            # self.ground.off()  
            print(f'{i+1}/{train} End')
            time.sleep(1)
        


# # pwm_in2 = PWM(in2, freq=1000)
# def motor1_stop():
#     in1.value(0)
#     in2.value(0)

# def motor1_reverse():
#     in1.value(0)
#     in2.value(1)
#     time.sleep(0.15)
#     motor1_stop()

# def motor1_forward():
#     in1.value(1)
#     in2.value(0)
#     time.sleep(0.15)
#     motor1_stop()
# print('Gear Motor Pinned')


# blueLED = LEDSignal(pin=ledPin)
# blueLED.start(800)
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

    time_tuple = (year, month, day, hour, minute, second)
    # time_tuple = (2025, 2, 16, 11, 17, 30)
    # weekday = time.mktime(time_tuple)  # Convert to seconds since epoch
    # weekday = time.localtime(weekday).tm_wday  # tm_wday gives 0=Monday, 6=Sunday
    # Create the tuple in the desired format
    date_tuple = (year, month, day, hour, minute, second, 0)
    return date_tuple #(0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])


def confirm_alarm(currentdate):
    """
    Check if alarm was triggered near the alarm set
    """
    time_tuple = currentdate
    global alarm # {'am':8,'pm':15,'min':15}
    # hour = time_tuple[4]  
    hour = 1
    minute = time_tuple[5] 
    time_in_minutes = hour * 60 + minute
    if alarm['pm'] > 0:
        alarm_hour = alarm['pm']
    else:
        alarm_hour = alarm['am']
    alarm_hour = 1
    alarm_time_in_minutes = alarm_hour * 60 + alarm['min']
    print(f'Alarm Set Time: {alarm_hour} {alarm['min']} ')
    print(f'Alarm Current Time: {hour} {minute}')
    minute_diff = abs(time_in_minutes - alarm_time_in_minutes)
    print('  -----   Alarm Diff: ',minute_diff)
    if minute_diff <= 10:
        print("The alarm time is within ±10 minutes of the given time.")
        return True
    else:
        return minute_diff



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
class Feeder():
    def __init__(self,feederpin, initFeed = 20):
        self.servo_pin = Pin(feederpin)
        self.servo = PWM(self.servo_pin)
        self.servo.freq(50)
        self.backwward = 23
        self.stop = 0
        self.forward = 110
        self.slowforward = 90
        self.initFeed=initFeed
    def back(self):
        sleep(0.01)
        for s in range(10):
            sleep(0.1)
            self.servo.duty(self.backwward)
            sleep(0.1)
            self.servo.duty(self.stop)
            sleep(0.1)
            print(s)
    def stop(self):
        self.servo.duty_u16(0)
    def go(self):
        print(' \n  Starting Feeding')
        print('First Feed for first comer')
        sleep(0.01)
        self.servo.duty(self.slowforward)
        print('     End')
        sleep(3)
        for i in range(self.initFeed):
            print(f'Initial Feeding in {i+1}/{self.initFeed}')
            sleep(0.4)
            self.servo.duty(self.forward)
            sleep(0.05)
            self.servo.duty_u16(self.stop)
            sleep(0.4)
        sleep(0.1)
        self.servo.duty_u16(0)

try:    
    class AutoFeeder():
        def __init__(self): 
            time.sleep(3)
            try: 
                self.power = Power(groundPin)
                self.power.on
            except: pass    
            try: self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
            except:
                print('Error Cant import clock')
                textWriter('error.txt','Clock Error')
            try: 
                self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
                newCommand = self.sim.receiveSMS()
                if newCommand == None:
                    print('No New Command')
                else:
                    print("Create a Func that will create a Command")


            except Exception as e: print("Sim ERROR ",e)
                # try:
                #     self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
                # except:
                #     print('Error CAnt import sim')
                #     textWriter('error.txt',' Sim Error')
            try: 
                if self.clock.clock.OSF():
                    newTime = self.sim.datetime()
                    updatedt = date_to_tuple(newTime)
                    self.clock.clock.datetime((updatedt))
                    print('+++ Time Updated ++++')
                else:
                    print('Time is Correct')
            except Exception as e:
                print("Error : ",e)

        
            self.gate = Servo(gatePin)
            self.door = DoorGate(doorPin, doorservoPin)
            self.feed = Feeder(feederpin)
            self.train = Train(self.feed,clock=self.clock)

    # class AutomaticFeedMachine():
    #     def __init__(self):
    #         self.gnd_active = Pin(groundPin,Pin.OUT)
    #         self.gnd_active.on()
    #         time.sleep(1)
    #         self.importClock()
    #         self.importSim()
    #         # self.sim.power.off()
    #         try:
    #             self.sim.power.off()
    #         except:
    #             print('No Sim')
    #         # blueLED.start(100)

    #     def importSim(self):    
    #         try:
    #             from SimModule import Sim
    #             self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
    #         except Exception as e:
    #             textWriter('error.txt',e)
    #             print('Cant Import Sim Module First Try ',e)
    #             try:
    #                 print('Second Trial Importing sim module')
    #                 self.gnd_active.off()
    #                 time.sleep(2)
    #                 self.gnd_active.on()
    #                 time.sleep(2)
    #                 from SimModule import Sim
    #                 self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
    #             except:
    #                 textWriter('error.txt', 'importSim ')
    #         # from clockAlarm import set_alarm_everyday,set_alarm2_everyday, alarmclock
    #     def initiateTrain(self):
    #         try:
    #             ntrain = 3
    #             flySecond = 180
    #             sct= ' '.join(self.clock.get_time())
    #             textWriter('train.txt',f'[ {sct} ] ++ Started Training recursion: {ntrain} second: {20}\n')
    #             trainer = Train()
    #             trainer.train(ntrain,flySecond)
    #             ect= ' '.join(self.clock.get_time())
    #             textWriter('train.txt',f'[ {ect} ] ---- Ended Training \n')
    #         except Exception as e:
    #             textWriter('error.txt', 'initiateTrain ')
    #             print("\n\n    ",e)
    #     def importClock(self):
    #         try:
    #             from configs.configs import clock_scl, clock_sda, clock_sqw, alarm 
    #             from clockModule import Clock
    #             self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=self.alarm_handler,alarm_time=alarm)
    #             # clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,alarm_time=alarm)
    #             print("DONE Setting up Alarm")
    #         except Exception as e:
    #             textWriter('error.txt', f'importClock Error {e}')
    #             print('Cant import clock' ,e)
        
    #     def alarm_handler(self):
    #         tstamp = ''
    #         tstamp2 = ''
    #         try:
    #             # ic.active(False)
    #             pass
    #         except:
    #             print('No IC found!')
    #         self.gnd_active.on()
    #         try:
    #             tstamp= ' '.join(self.clock.get_time())
    #             textWriter('alarm.txt',f'[ {tstamp} ]  +++ Alarm Stared ')
    #         except:
    #             try:
    #                 print('Trying againd')
    #                 self.importClock()
    #                 time.sleep(2)
    #                 tstamp= ' '.join(self.clock.get_time())
    #                 textWriter('alarm.txt',f'[ {' '.join(self.clock.get_time())} ]  +++ Alarm Stared ')
    #             except:
    #                 print('Really Cant import self.clock')

    #         try:
    #             try:
    #                 addmessage = self.sim.battery()
    #             except:
    #                 try:
    #                     from SimModule import Sim
    #                     self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
    #                     addmessage = self.sim.battery()
    #                 except:
    #                     print('Really cant import Sim absrd')
    #             self.sim.sendSMS(number="639765514253",message=f'Alarm runs successfully at {addmessage}')
    #         except: print('Cant send text amessage')
    #         try:
    #             self.initiateTrain()
    #         except Exception as e:
    #             print('Erro training: ',e)
    #         try: # connect wo whatsapp
    #             addmessage = self.sim.battery()
    #             try:
    #                 addmessage += checkBattery()
    #             except:
    #                 print('cant include battery')
    #                 pass
    #             try:
    #                 self.sim.sendwhatsapp(f'Alarm runs successfully at {addmessage}')
    #             except:
    #                 pass
    #             try:
    #                 self.sim.sendSMS(message=f'Alarm runs successfully at {addmessage}')
    #             except: pass
    #             # try:
    #             #     sim.sendSMS(number="639765514253",message=f'Alarm runs successfully at {addmessage}')
    #             # except: pass
    #             pass
    #             tstamp2 = ' '.join(self.clock.get_time())
    #             textWriter('alarm.txt',f'[ {tstamp2} ]  --- Alarm Ended ')

    #         except Exception as e:
    #             textWriter('error.txt', 'alarmHandler '+str(e))
    #             print('Sending Message failed: ',e)    
    #         self.gnd_active.off()

except Exception as e:
    print('\n ++++++++++   Cant Create Automatic Feeder Machine    ',e)
    time.sleep(4)


# af = AutomaticFeedMachine()
ic = connect_or_create_wifi()
gnd.on
time.sleep(1)
if gnd.power:
    try:
        af = AutoFeeder()
    except Exception as e:
        print('Error')
else:
    startingNotif.start(150)
    for i in range(3):
        print('\n\n     Please type "gnd.on"  First to power up\n\n')
        time.sleep(2)

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




