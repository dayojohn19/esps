
def alarm_handler(pin):
    print("Importine Servo: ",pin)
    # alarmclock.check_alarm(2)
    alarmclock.check_alarm(1)
    print(alarmclock.datetime())
    print('\n')

def alarm_handler2(pin):
    print("SECOND Square wave detected - interrupt triggered! by PIN: ",pin)
    print(alarmclock.datetime())
    print('\n')

def set_alarm_everyday(hrs,min,sec=0):
    alarmclock.alarm1((sec, min, hrs), match=alarmclock.AL1_MATCH_HMS)
    print(f"Alarm Set for {hrs}h : {min}m : {sec}s")

def set_alarm2_everyday(hrs=1,min=1,day=1):
    alarmclock.alarm2((min, hrs, day),match=alarmclock.AL2_MATCH_HM)
    print(f"Everyday Alarm {hrs} : {min}  ")

from machine import Pin, I2C
import clock
from configs.configs import *
# To Set Change Time
# datetime : tuple, (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])"""
# ds.datetime((2025,1,4,18,57,1,6))
alarmclock = clock.ds
# alarmclock.output_32kHz() # Enable 32 kHz output
alarmclock.output_32kHz(False)

# sqw_pin = Pin(clock_sqw, Pin.IN, Pin.PULL_UP) #D7
# sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=alarm_handler)

# k32_pin = Pin(clock_k32, Pin.IN, Pin.PULL_UP) # D8
# k32_pin.irq(trigger=Pin.IRQ_FALLING, handler=alarm_handler2)

# Set alarm 1 for 16:10:15 every day
# alarmclock.alarm1((15, 10, 16), match=alarmclock.AL1_MATCH_S)


# machine.sleep(60000)
# print('WakeUp')