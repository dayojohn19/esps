import time
from machine import ADC, PWM, Pin, RTC , reset_cause, Timer, deepsleep, UART,reset
import _thread
from configs.configs import groundPin, doorservoPin
from servoModule import Servo
from SimModule import Sim
from configs.configs import sim_tx, clock_scl, clock_sda, clock_sqw, alarm , scanStart, scanEnd,daytimeEnd, daytimeStart,feederpin, buzzerPin, rdm6300Pin
from led_signal import LEDSignal
import gc
from clockModule import Clock, updateClock
from settings import Settings
# from rdm6300 import RDM6300
from textwriter import textWriter
import json
import select

# mode= 'toss' #TODO add func changing mode when texted
textfiles = ['feed','alarm','error']

Pin(clock_scl, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
p  = Pin(clock_sqw, Pin.OUT, Pin.PULL_UP) # Because its powering RTC 3v 
p.value(1)
Pin(clock_sda, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 


def timeChecker(pin=None):
    if RTC().datetime()[0] < 2023:
        clock = Clock()
    ch = RTC().datetime()[4]
    try:
        af.gnd.on
        s = Sim()
        s.receiveSMS()
    except:
        print(' no AF')
    # print(f'Time(2) if {ch} >= {daytimeEnd} scanEnd')
    # print('\n   ------- Daytime Cheker  --------    \n')
    if ch > daytimeEnd:
        print(f'\n\n Not Daytime now {ch} >= {daytimeEnd}')
        # print('Going Deepsleep \n\n')
        time.sleep(5)
        # deepsleep()
    return print('Still daytime')
timer = Timer(2)    
timer.init(period=60000, mode=Timer.PERIODIC, callback=timeChecker)
# timer.deinit() 

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



class Battery():
    def __init__(self):
        from configs.configs import batteryPin,BatteryMotorPin
        # print('     Building Battery',end='    ')
        self.BatteryMotorPin = BatteryMotorPin
        self.batteryPin = batteryPin
        print('run self.record to check battery')
    @property
    def record(self):
        bat = f'\nBattery\nMotor {self.motor}%\nModule {self.module}%'
        textWriter('battery.txt',bat)
        return bat

    @property
    def motor(self):
        return self.battery(self.BatteryMotorPin,atten=3,max_reading=4095,min_reading=2795)
    @property
    def module(self):
        return self.battery(self.batteryPin,3)
    def battery(self,pin, atten=3,max_reading=4095, min_reading=13):
        a = ADC(Pin(pin)) 
        a.atten(atten)
        def read(a):
            num_samples = 50  # Number of samples to average
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


class Feeder():
    
    def __init__(self,feederpin=feederpin, initFeed = 10):
        print('     Initiated Feeder()')
        instruction = """
        Feeder( feeder_pin  ,   initFeed)
        self.go
        self.slow
        self.finish
        self.back
        """ 
        # print('Instruciton: ',instruction)
        self.gnd = Power()
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
        self.gnd.on
        time.sleep(0.01)
        for s in range(5):
            time.sleep(0.1)
            self.servo.duty(self.backwward)
            time.sleep(0.1)
            self.servo.duty(self.stop)
            time.sleep(0.1)
            print(s)
        self.gnd.off
    def finish(self):
        try:
            self.servo.duty_u16(0)
        except:
            self.servo.duty(0)
        time.sleep(1)
        self.gnd.off
    @property
    def slow(self):
        self.gnd.on
        self.servo.duty(self.slowforward)
        time.sleep(1.4) # One Complete rev
        self.servo.duty(0)
    @property
    def go(self):
        self.gnd.on
        self.servo.duty(self.forward)
        # time.sleep(0.636) # One Complete Revolution
        time.sleep(0.16) # One Complete Revolution
        # time.sleep(0.32) # One Complete Revolution
        self.servo.duty(0)

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



class Buzzer():
    def __init__(self,pin=buzzerPin):
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


class FlyGate():
    from configs.configs import gatePin
    def __init__(self, flygatePin = gatePin):
        self.openAngle = 260
        self.closeAngle = 115
        self.gate = Servo(flygatePin)
        self.isOpen = False
        self.gnd = Power()
    @property
    def open(self):
        if self.isOpen:
            return
        self.isOpen = True
        self.gnd.on
        time.sleep(0.5)
        self.gate.move(self.openAngle)
        time.sleep(3)
        self.gnd.off
    @property
    def close(self):
        if self.isOpen:
            self.gnd.on
            time.sleep(0.5)
            self.gate.move(self.closeAngle)
            time.sleep(1)
            self.gnd.off
            self.isOpen = False
        return



# def extend_alarm(clock,addsec=15):
#     wake = Wake()
#     time.sleep(1)
#     ct = clock.get_time()
#     hr,min,sec =  map(int, ct[1].split(':'))
#     print('     Wake Reason: ',wake.reason)
#     print("         Wake time:              " , ct[1])
#     sec = sec+addsec
#     if sec >= 60:
#         sec = sec-60
#         min += 1
#         if min >= 60:
#             hr+=1
#             min=min-60
#     # print(f'Setting Alarm at {hr} {min} {sec}')
#     clock.alarm_daily(hr,min, sec)
#     time.sleep(2)
#     print('         Sleep Time:             ',clock.get_time()[1])





class Train():
    def __init__(self):
        self.gnd = Power()
        self.gnd.on
        self.flygate = FlyGate()
        print('Initiating Feeder')
        self.feeder = Feeder()
        print('Initiating LED')
        self.ledlight = LEDSignal()
        print('Initiating Buzzer')
        self.buzzer = Buzzer()
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
        self.gnd.on
        _thread.start_new_thread(self.flySignal,())
        time.sleep(1)
        self.flygate.open
        time.sleep(1)
        self.buzzer.twosec()
        time.sleep(1)
        # gnd.off
        for i in range(self.flyduration):
            time.sleep(1)
            print(f"Flying in {i+1}/{self.flyduration}")

    def rest(self):
        print('Resting')
        self.isflying = False
        self.flygate.close
        time.sleep(2)
    def feed(self,ftimes):
        print('Feeding')
        self.ledlight.on()
        self.gnd.on
        for i in range(ftimes):
            print(f'Feeding in {i+1}/{ftimes}')
            time.sleep(0.5)
            self.feeder.go
        time.sleep(2)
        self.ledlight.off()
    def session(self, nsession=1,flysec=60,feedtime=10):
        print('     Starting Session')
        self.flyduration = flysec
        for i in range(nsession):
            print(f'        Session in {i}/{nsession}')
            time.sleep(1)
            self.feed(ftimes=feedtime)
            
            for i in range(30):
                time.sleep(1)
                print(f"Waiting after feeding {i+1}/30")
            self.fly()
            print('      Done Flying')
            time.sleep(1)
            print('     Resting')
            self.rest()
            print('Feeding')
            self.feed(feedtime)
            print(f'Session {nsession} / {nsession} finished')
        return True




class AutoFeeder():
    def __init__(self, ic=None): 
        instruction = """
        AutoFeeder( ic=None ) Internet_connection
        """
        print('Starting Auto Feeder')
        print(instruction)
        # self.moduleSleepTime = 30* 60 
        self.alarm = alarm
        self.wake = Wake()
        self.ic  = ic
        self.moduleSleepTime = 7200000 # 2hrs
        self.gnd = Power()
        self.gnd.on
        time.sleep(1)
        self.battery = Battery()
        self.sim = Sim()
        # self.smsReceived = self.sim.receiveSMS()
        self.clock = None
        self.mode = Settings('mode')
        self.clock = Clock()
        self.ch = self.clock.clock.datetime()[4]        
        # self.run()

    def isDaytime(self):
        print('     Checking Datetime', end='')
        try: 
            print('         Clock',end='')
            print(f'             Alarm Time {alarm}')
            try: 
                gc.collect()
                updateClock(self.clock.clock , self.sim)
                if RTC().datetime()[0] < 2024:
                    self.clock = Clock()
                # updateClock(RTC() , self.clock, True)
            except Exception as e:
                print("Isdaytime Error : ",e)                
                textWriter('error.txt',f'Error in isDaytime: {e}')
            print(f'isDaytime:     Daytime {daytimeStart}-{daytimeEnd} \n       Current Hour: {self.ch} ')
            if daytimeStart <= self.ch < daytimeEnd: 
                return True
        # try: self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
        except Exception as e:
            print('Error isDaytime Func  reason: ',e)
            textWriter('error.txt',e)
        return False


    def run(self):
        dayHour = self.isDaytime()
        print('IsDaytime: ',dayHour)
        gc.collect()
        if dayHour:
            if self.mode.get == 'toss':
                print(f'Toss Mode \n     Scanning {scanStart} until {scanEnd} current Time: {self.ch}')
                if scanStart <= self.ch < scanEnd:
                    print(f'Scanning until {scanEnd} current time is {self.ch}')
                print('    ++++    Starting to Receive RFID ++\n')
                print('turning off wifi start scanning')
                time.sleep(5)
                self.gnd.off
                try:
                    print('Disconnecting from Internet')
                    self.ic.disconnect()
                    self.ic.active(False)
                except:
                    print('     No Internet Connection Given')                 
                time.sleep(1)
                self.scan = RDM6300()
                self.scan.scan()            
            elif self.mode.get == 'session':
                if self.wake.reason == 'deepsleep':
                    print('Wake Reason DeepSleep Start Training')
                    # self.fly = FlyGate(gatePin) #2
                    # self.door = DoorGate(doorPin, doorservoPin)
                    # self.feed = Feeder(feederpin) # 9
                    self.train = Train()
                    # self.train.session()
                    self.train.session(1,60,10)   
                    try:
                        b = self.battery.record
                        try: 
                            self.gnd.on
                            time.sleep(3)
                            ts = self.sim.datetime()  
                            self.sim.sendSMS(message=f'{ts} finished Session {b}')
                        except Exception as e:
                            ts = e
                            textWriter('error.txt',f'Error in sim.datetime: {e}')
                            print('Error in sim.datetime: ',e)
                        toLogString = f' {b} Sim Datetime {ts}  '
                        textWriter('log.txt',toLogString)
                        print(toLogString)
                    except Exception as e:
                        print('Error Logging Runtime: ',e)
                        textWriter('log.txt', f'Error Logging Runtime  {RTC.datetime()} -  {e}')
                    print('Sleeping Again for ', self.moduleSleepTime)
                    self.gnd.off
                    time.sleep(5)
                    p  = Pin(clock_sqw, Pin.OUT, Pin.PULL_UP) # Because its powering RTC 3v 
                    deepsleep(self.moduleSleepTime)
                else:
                    print('Need Wake Reason == deepsleep to start session')
                    for i in range(5):
                        print(f'Sleeping in {i+1}/5')
                        time.sleep(1)
                    p  = Pin(clock_sqw, Pin.OUT, Pin.PULL_UP) # Because its powering RTC 3v     
                    deepsleep(5000)
        if dayHour == False:
            print("Create a Func TODO")
            print('deepsleep and wait for alarm')
            print('     Daytime False sleeping in 10')
            for i in range(10):
                print(f'{i+1} ', end=' ')
                time.sleep(1)
            time.sleep(2)
            p  = Pin(clock_sqw, Pin.OUT, Pin.PULL_UP) # Because its powering RTC 3v 
            deepsleep()                    
                # self.train = Train()
                # self.train.session(1,60,30)                    
                # if self.moduleSleepTime == 0:
                #     self.moduleSleepTime = 60000            
                # print('     Run Session')
                # self.gnd.off
                
class RDM6300:
    def __init__(self, file_path=None):
        if RTC().datetime()[0] < 2022:
            time.sleep(1)
            print('Updating Datetime()')
            self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=None,alarm_time=alarm)
            updateClock(RTC(), self.clock.clock, ismachine=True)        
        if file_path is None:
            file_path = 'rdm6300.json'
        self.file_path = file_path
        self.light = LEDSignal(doorservoPin)
        self.gothread = True
        self.rxPin = rdm6300Pin
        self.gnd = Power()
        self.sending = False
        self.t = Train()
        time.sleep(1)
        try:
            self.data = self.read()
        except:
            self.data = {}
            self.save
            self.data = self.read()
        self.processing = []

        
        # self.timer.init(period=3600000, mode=Timer.PERIODIC, callback=self.selftimer)


    def hasData(self): # not used
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
        time_tuple=RTC().datetime()
        month_names = ["January", "February", "March", "April", "May", "June",  "July", "August", "September", "October", "November", "December"]
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


    def add(self, rf_id, initial_count=1):
        print('Adding: ',rf_id)
        self.light.wink(0.5)
        rf_id = str(rf_id)
        """Add new card or update existing card in JSON file"""
        try:
            if rf_id in self.processing:
                print("passing multiple same id ")
                return
            else:
                self.processing.append(rf_id)
                self.gnd.on
                time.sleep(3)
            print('Processing: ',rf_id)
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
            time.sleep(1)
            gc.collect()
            self.save
            time.sleep(1)
            d = self.data[rf_id]
            gc.collect()
            time.sleep(1)
            ec = 0
            for _ in d["entries"]:
                ec+=1
            b = Battery()
            b = b.record
            s = f'{d["id"]} arrived: {d["last_seen"]} count {ec} \n {b}'
            gc.collect()
            print('send sms')
            _thread.start_new_thread(self.t.feed,(15,))
            if self.sendSMS(message=s) == True:
                print('SMS Sent!!', s)
            else:
                
                print('Trying to send SMS again')
                self.sendSMS(message=s)
            gc.collect()
            try:
                self.processing.remove(d["id"])
                time.sleep(1)
                if self.processing == []:
                    self.gnd.off
                    print(' \n\n No more processing\n')
                print(f"processed {d["id"]}")
            except Exception as e:
                print('cant finish process ',e)
            gc.collect()
            return True
            # return self.inform(self.data[rf_id])
        except Exception as e:
            # self.processing = []
            print(f"Error adding card: {e}")
            textWriter('error.txt',f'Error in adding card: {e}')
            return False
            

    def sendSMS(self,message="messageTemplate", number=639568543802, receive = False): #working now         
        self.gnd.on
        self.sim = Sim()
        self.sim.sendSMS(message=message , number=number)
        # time.sleep(5)
        # st = time.time()
        # self.sending = True
        # while self.sending:
        #     if time.time() -st >= 60:
        #         print('Cant Send')
        #         break
        #     print('             Waiting to finish sending')
        #     time.sleep(1)
        #     try:
        #         print('sending sms')
        #         # self.uart.write("AT+IPR=9600\r\n")
        #         time.sleep(1)
        #         self.uart.write("AT\r\n") # Hand Shake
        #         time.sleep(1)
        #         # self.uart.write('AT+CREG=1\r\n')
        #         time.sleep(1)
        #         # self.uart.write('AT+CSQ\r\n')
        #         time.sleep(1)
        #         self.uart.write("AT+CMGF=1\r\n") # Put to Text Mode
        #         gc.collect()
        #         time.sleep(1)
        #         # return True
        #         self.uart.write(f'AT+CMGS=\"+{number}\"\r\n')
        #         time.sleep(1)
        #         self.uart.write(message)
        #         time.sleep(1)
        #         self.uart.write(bytes([26])) # stop the SIM Module for SMS
        #         gc.collect()
        #         textWriter('sms.txt',f'message')
        #         self.sending = False
        #         return True
        #     except Exception as e:
        #         print('cant send: ',e)
        #         textWriter('error.txt',f'Error in sending SMS: {e}')
        #         return False
        
    def scan(self):
        self.gnd.off
        with open('tags.json', 'r') as file:
            self.tagProfile = json.load(file)        
        # resetPin()
        gc.collect()
        print('\n     Starting scan.\n\n')
        time.sleep(1)
        self.uart = UART(1, baudrate=9600, rx=self.rxPin, tx=sim_tx,timeout=10)  # Reduced timeout
        self.uart.flush()        
        self.light.wink(0.3)
        time.sleep(0.3)
        self.light.wink(0.3)
        while True:
            if self.gothread:
                print('True Again')
                tt = ''
                lt = ''
                poll = select.poll()
                poll.register(self.uart,select.POLLIN)        
                while self.gothread:
                    e = poll.poll(1000)
                    for f, ee in e:
                        if ee & select.POLLIN:
                            try:
                                # tag = self.uart2.read()[:13].decode('utf-8').strip() # latest code 
                                tag = self.uart.read().decode('utf-8').strip()
                                tag = "".join(filter(lambda x: 32 <= ord(x) <= 126, tag))
                                if tag == lt:
                                    print(f'.', end='')
                                    self.light.wink(0.1)
                                    continue
                                elif tag in self.tagProfile:
                                    if tt == tag:
                                        self.light.wink(0.1)
                                        print('_',end='')
                                        continue
                                    lt = tag
                                    tt = tag
                                    print('New Tag: ',tag,)
                                    tag = self.tagProfile[tag]
                                    _thread.start_new_thread(self.add,(tag,))
                                    gc.collect()
                                    # self.add,(tag,)
                                    print('r', end='')
                                    print(f'New: {tag}')                    
                                    self.light.wink(0.3)
                                else:
                                    lt = tag
                                    print(tag)
                                    self.light.wink(0.1)
                            except:
                                print('Got Error in Pollin')
                                pass
                    time.sleep(0.05)       
                print('Thread goes false')         
            else:
                i=0
                while self.gothread == False:
                    i+=2
                    print("                                           waiting thread", i)
                    time.sleep(2)



