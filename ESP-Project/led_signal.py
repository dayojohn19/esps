import machine
from time import sleep
from utime import ticks_ms
from machine import Pin

import time
class LEDSignal:
    def __init__(self, pin):
        self.pin=pin
        self.led = Pin(pin, Pin.OUT)
        self.timer = None
        self.startTime = 0
        self.expireTime = 0
        self.isOn = False

        self.dot = 0.2
        self.dash = 0.6
        self.space = 0.2  # Space between symbols in the same letter
        self.letter_space = 0.6  # Space between letters

    def blink_sos(self):
        # SOS is " ... --- ... "
        for _ in range(3):  # Repeat for "..."
            self.led.on()
            time.sleep(self.dot)
            self.led.off()
            time.sleep(self.space)
        
        time.sleep(self.letter_space)  # Space between letters

        for _ in range(3):  # Repeat for "---"
            self.led.on()
            time.sleep(self.dash)
            self.led.off()
            time.sleep(self.space)

        time.sleep(self.letter_space)  # Space between letters

        for _ in range(3):  # Repeat for "..."
            self.led.on()
            time.sleep(self.dot)
            self.led.off()
            time.sleep(self.space)



    def wink(self,ms=0.3):
        self.led.on()
        sleep(ms)
        self.led.off()
            


    def blink(self, timer=None):        
        if self.isOn == False:
            self.led.on()
            self.isOn = True
        else:
            self.led.off()
            self.isOn = False
        # self.led.value(not self.led.value())
        if self.expireTime != 0:
            ct = ticks_ms() - self.startTime
            if ct >= self.expireTime:
                self.led.off()
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

# class LEDSignal:
#     def __init__(self, pin=2):
#         self.pin=pin
#         self.led = machine.Pin(pin, machine.Pin.OUT, machine.Pin.PULL_DOWN, hold=True)
#         self.timer = None
#         self.startTime = 0
#         self.expireTime = 0

#     def blink(self, timer=None):        
#         self.led = machine.Pin(self.pin, machine.Pin.OUT, machine.Pin.PULL_DOWN, hold=False)
#         if self.expireTime != 0:
#             ct = ticks_ms() - self.startTime
#             if ct >= self.expireTime:
#                 self.off()
#                 self.stop()

#                 self.expireTime = 0
#         self.led.on()
#         sleep(1.5)
#         self.led.value(not self.led.value())

#     def start(self, speed=500, expireTime=0):
#         self.startTime = ticks_ms()
#         self.expireTime = expireTime*1000
#         # startTime = ticks_ms()
#         # endTime = until*1000
#         # while True:
            
#         # if until is not None:


#         if self.timer is None:
#             self.timer = machine.Timer(0)
#             self.timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=self.blink)
#         else:
#             self.timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=self.blink)


#     def stop(self):
#         if self.timer is not None:
#             self.timer.deinit()
#             self.timer = None
#             # self.led.value(1)
#             self.led.off()
#         self.led = machine.Pin(self.pin, machine.Pin.OUT, machine.Pin.PULL_DOWN, hold=True)
#     def off(self):
#         self.led.off()

#     def on(self):
#         self.led.off()
            

# # Example usage
# # if __name__ == "__main__":
# #     led_signal = LEDSignal(pin=2)
# #     print('Led working')
# #     led_signal.start(speed=100) 
# #     sleep(2)
# #     led_signal.stop()