from machine import TouchPad,Pin, I2C, ADC, deepsleep, RTC,PWM
import machine
from time import sleep
import time
from clockModule import Clock
from SimModule import Sim
import math
import utime
from utime import ticks_ms

powerpin= 0
feederpin = 2
doorServoPin = 5
clock_scl = 12
clock_sqw = 13
clock_sda   = 14
gatePin = 15
doorPin = 18
ledsignalPin =  19         
sim_tx = 32 #blue
sim_rx = 33
sim_uart = 1

alarm = {'am':9,'pm':15,'min':30}

textfiles = ['feed','alarm','error']
feedblink = 119
flyblink = 419
pressed_time = 0

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




class LEDSignal:
    def __init__(self, pin):
        self.pin=pin
        self.led = Pin(pin, Pin.OUT)
        self.timer = None
        self.startTime = 0
        self.expireTime = 0
        self.isOn = False
    def blink(self, timer=None):        
        if self.isOn == False:
            self.on()
            self.isOn = True
        else:
            self.off()
            self.isOn = False
        # self.led.value(not self.led.value())
        if self.expireTime != 0:
            ct = ticks_ms() - self.startTime
            if ct >= self.expireTime:
                self.off()
                self.stop()
                self.expireTime = 0
    def start(self, speed=500, expireTime=0):
        self.startTime = ticks_ms()
        self.expireTime = expireTime*1000
        if self.timer is None:
            self.timer = machine.Timer(0)
            self.timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=self.blink)
        else:
            self.timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=self.blink)
    def stop(self):
        if self.timer is not None:
            self.timer.deinit()
            self.timer = None
            # self.led.value(1)
            self.led.off()
        # self.led = machine.Pin(self.pin, machine.Pin.OUT, machine.Pin.PULL_DOWN, hold=True)
    def off(self):
        self.led.off()
    def on(self):
        self.led.on()
            
class Power:
    def __init__(self,pin):
        self.pin = Pin(pin,Pin.OUT)
        self.on()
    def on(self):
        self.pin.value(0)
    def off(self):
        self.pin.value(1)

class Feeder():
    def __init__(self,servoPin):
        self.servo_pin = Pin(servoPin)
        self.servo = PWM(self.servo_pin)
        self.servo.freq(50)
        self.backwward = 23
        self.stop = 0
        self.forward = 110
        self.slowforward = 90
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
    def go(self, initFeed= 30):
        print(' \n  Starting Feeding')
        print('First Feed for first comer')
        sleep(0.01)
        self.servo.duty(self.forward)
        sleep(2)
        self.servo.duty(self.slowforward)
        print('     End')
        sleep(2)
        for i in range(initFeed):
            print(f'Initial Feeding in {i+1}/{initFeed}')
            sleep(0.4)
            self.servo.duty(self.forward)
            sleep(0.05)
            self.servo.duty_u16(self.stop)
            sleep(0.4)
        sleep(0.1)
        self.servo.duty_u16(0)

class Servo:
    __servo_pwm_freq = 50
    __min_u10_duty = 26 - 0 # offset for correction
    __max_u10_duty = 123- 0  # offset for correction
    min_angle = 0
    max_angle = 180
    current_angle = 0.001
    def __init__(self, pin):
        self.__initialise(pin)
    def update_settings(self, servo_pwm_freq, min_u10_duty, max_u10_duty, min_angle, max_angle, pin):
        self.__servo_pwm_freq = servo_pwm_freq
        self.__min_u10_duty = min_u10_duty
        self.__max_u10_duty = max_u10_duty
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.__initialise(pin)
    def move(self, angle):
        # round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
        angle = round(angle, 2)
        # do we need to move?
        if angle == self.current_angle:
            return
        self.current_angle = angle
        # calculate the new duty cycle and move the motor
        duty_u10 = self.__angle_to_u10_duty(angle)
        self.__motor.duty(duty_u10)
    def __angle_to_u10_duty(self, angle):
        return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u10_duty
    def __initialise(self, pin):
        self.current_angle = -0.001
        self.__angle_conversion_factor = (self.__max_u10_duty - self.__min_u10_duty) / (self.max_angle - self.min_angle)
        self.__motor = PWM(Pin(pin))
        self.__motor.freq(self.__servo_pwm_freq)


class DoorGate(): 
    def __init__(self, doorPin, doorServoPin):
        self.closeAngle = 180
        self.openAngle = 0
        self.doorbuttonpinobj = doorPin
        self.doorservopinobj = doorServoPin
        self.isOpen = True
        self.setUp()
    def touch(self,pin=None):
        global pressed_time
        new_time = ticks_ms()
        if (new_time - pressed_time) < 500:
            return
        pressed_time = new_time
        if self.isOpen == True:
            self.close()
            self.isOpen = False
        else:
            self.open()
            self.isOpen = True
        return
    def setUp(self):
        self.doorbutton = Pin(self.doorbuttonpinobj, Pin.IN, Pin.PULL_UP)
        self.doorbutton.irq(trigger=Pin.IRQ_FALLING, handler=self.touch)  
        servo = Servo(self.doorservopinobj)
        self.servo = servo
    def close(self):
        self.setpos(self.closeAngle)
        return
    def open(self):
        self.isOpen == True
        start_time = time.time()
        self.setpos(self.openAngle)
        while (time.time() - start_time) < 5:
            pass
        self.close()
        return
    def setpos(self, pos):
        self.servo.move(pos)
        # def map_range(value, old_min, old_max, new_min, new_max):
        #     return (value - old_min) * (new_max - new_min) / (old_max - old_min) + new_min
        # old_min = -4
        # old_max = 30
        # new_min = 0
        # new_max = 180
        # pos = map_range(pos, new_min, new_max, old_min, old_max)
        # self.pos = int(pos)
        # duty = int((pos/360) * (self.max_duty - self.min_duty) + self.min_duty)
        # self.servo.duty(duty)
        return


class Train():
    def __init__(self, feeder,clock):
        self.openAngle = 200
        self.closeAngle = -10
        self.light = LEDSignal(ledsignalPin)
        self.gate = Servo(gatePin)
        self.ground = Pin(powerpin,Pin.OUT)
        self.power = Power(powerpin)
        self.power.on()        
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
        



def textWriter(fileName=None, toWrite=None):
    try:
        with open(fileName, "a") as myfile:
            myfile.write(f"\n{toWrite}    [ {RTC().datetime()} ]")
            myfile.flush()
        print(f"Log written successfully:\n    {toWrite}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error while writing to log: {e}")        

def alarm_handler():
    try:
        try:
            global af
            if af is not None:
                pass
        except:
            af = AutoFeeder()                  
            newTime = af.sim.datetime()
            updatedt = date_to_tuple(newTime)            
        if confirm_alarm(af.clock.clock.datetime()) == True:
            textWriter('alarm.txt',f'[ {RTC().datetime()} ] Alarm Started')
            print(f'[ {RTC().datetime()} ] Started')
            stamp = str(af.sim.datetime())
            af.sim.sendSMS(639568543802,f'Alarm Started: {stamp}')
            power = Power(powerpin)
            power.on()
            af.train.train(1,300)
            textWriter('alarm.txt',f'[ {RTC().datetime()} ]         Alarm Ended')
            print('Alarm Ended')            
        else:
            print("alarm Triggered at wrong time")
            textWriter('alarm.txt',f'[ {RTC().datetime()} ] Alarm Triggered not time')
    except Exception as e:
        textWriter('alarm.txt',f'[ {RTC().datetime()} ] Alarm Triggered not time {e}')
        print('         Failed to execute alarm ', e)
        time.sleep(2)
    for i in range(10):
        print(f'Sleeping in {i+1}/10')
        time.sleep(1)
    deepsleep()

class AutoFeeder():
    def __init__(self): 
        time.sleep(3)
        
        try: self.power = Power(powerpin)
        except: pass    
        try: self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
        except:
            try:
                self.clock = Clock(sqw_pin=clock_sqw,scl_pin=clock_scl,sda_pin=clock_sda,handler_alarm=alarm_handler,alarm_time=alarm)
            except:
                print('Error Cant import clock')
                textWriter('error.txt','Clock Error')
        try: self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
        except:
            try:
                 self.sim = Sim(uart_num=sim_uart, tx=sim_tx,rx=sim_rx)
            except:
                print('Error CAnt import sim')
                textWriter('error.txt',' Sim Error')
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

        self.door = DoorGate(doorPin, doorServoPin)
        self.feed = Feeder(feederpin)
        self.train = Train(self.feed,clock=self.clock)
try:
    af = AutoFeeder()
except:
    try:
        af = AutoFeeder()
    except:
        textWriter('error.txt','Cant create auto feeder')

for i in range(2):
    time.sleep(1)
    af.train.open()
    time.sleep(1)
    af.train.close()
    time.sleep(1)
time.sleep(1)
af.train.close()    
power = Power(powerpin)
power.off()
for i in range(5):
    time.sleep(1)
    print(f'Sleeping in {i+1}/5')

deepsleep()



