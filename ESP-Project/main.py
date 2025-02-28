

# for bare11
from machine import Pin, I2C, RTC , DEEPSLEEP,SoftI2C

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
Pin(clock_scl, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
Pin(clock_sqw, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
Pin(clock_sda, Pin.OUT, Pin.PULL_DOWN) # Because its powering RTC 3v 
alarm = {'am':7,'pm':15,'min':30}
pressed_time = 0
textfiles = ['feed','alarm','error']
feedblink = 119
flyblink = 419
ledlight = LEDSignal(ledsignalPin)
ledlight.wink()
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
            return 'unknown'
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
feeder = Feeder()


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

def alarm_handler():
    try:
        sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
        ts = sim.datetime()
        sim.sendSMS(message=f'{ts} Alarm Is Triggered ')
    except:
        try:
            sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
            ts = sim.datetime()
            sim.sendSMS(message=f'{ts}Alarm Is Triggered')
        except:
            print('cant send message')
    print('\n  +++++ Alarm Pass Function Triggered! ++++\n')

 


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
                    self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
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
                self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
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
                clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
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
                clock_i2c = SoftI2C(scl=Pin(clock_scl), sda=Pin(clock_sda))
                self.clock = DS3231(clock_i2c)
                try: 
                    if self.clock.OSF():
                        newTime = self.sim.datetime()
                        updatedt = date_to_tuple(newTime)
                        self.clock.datetime((updatedt))
                        print('+++ Time Updated ++++')
                    else:
                        print('Time is Correct')
                except Exception as e:
                    print("Error : ",e)                
                ch = self.clock.datetime()[4]
                if 7 <= ch < 17: 
                    if self.moduleSleepTime == 0:
                        self.moduleSleepTime = 60000
                    print('Daytime True')
                    return True

            
            # try: self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
            except:
                print('Error Cant import clock')
                textWriter('error.txt','Clock Error')

            return False
    

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



print('\n----------- \n  ')


try:
    ic = connect_or_create_wifi()
except: print("Error COnnecting to network")
# gnd.on
time.sleep(1)
af = AutoFeeder()
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




