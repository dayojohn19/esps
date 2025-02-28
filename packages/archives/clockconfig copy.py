from machine import Pin, I2C, RTC 
from mpy import clock
import time


# When alarm it will set the 32kHz output



class ClockConfig:
    def __init__(self, sqw_pin=13, scl_pin=14, sda_pin=12, handler_alarm=None, i2c_freq=100000 ):
        from machine import RTC
        self.handler_alarm = handler_alarm
        self.clock_sqw = sqw_pin  # D7
        self.clock_scl = scl_pin  # D5
        self.clock_sda = sda_pin  # D6
        # self.clock_k32 = k32_pin  # D8
        self.clock_i2c = I2C(scl=Pin(self.clock_scl), sda=Pin(self.clock_sda), freq=i2c_freq)  # Example with GPIO14 and GPIO12 SDA=D6 SCL=D5
        self.clock = clock.DS3231(self.clock_i2c)
        self.enable_32kHz_output(False)
        self.rtc = RTC()
        self.setup_pins()
        self.sync_rtc_with_ds3231()

    def sync_rtc_with_ds3231(self):
        print('Syncing RTC with DS3231')
        time.sleep(3)  # Wait for the RTC to stabilize
        self.rtc.datetime(self.clock.datetime())

    def get_time(self):
        date = "{}/{}/{}".format(self.rtc.datetime()[1], self.rtc.datetime()[2], self.rtc.datetime()[0])
        time = "{}:{}:{}".format(self.rtc.datetime()[4], self.rtc.datetime()[5], self.rtc.datetime()[6])
        return [date, time]


    def setup_pins(self):
        self.sqw_pin = Pin(self.clock_sqw, Pin.IN, Pin.PULL_UP)
        # self.k32_pin = Pin(self.clock_k32, Pin.IN, Pin.PULL_DOWN)
        self.sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.handler_SQW)
        # self.k32_pin.irq(trigger=Pin.IRQ_RISING, handler=self.handler_32k)

    def enable_32kHz_output(self, enable=False):
        self.clock.output_32kHz(enable)
        return enable

    def handler_SQW(self, pin):
        self.enable_32kHz_output(True)
        print(f" \n {self.clock.datetime()} SQW Interrupt Triggered by PIN:", pin)
        self.handler_alarm()
        self.clock.check_alarm(1)
        self.clock.check_alarm(2)
        print('\n')

    # def handler_32k(self, pin):
    #     print("32kHz Interrupt Triggered by PIN:", pin)
    #     print(self.clock.datetime())
    #     print('\n')

    def set_alarm_everyday(self, hrs, min, sec=0):
        self.clock.alarm1((sec, min, hrs), match=self.clock.AL1_MATCH_HMS)
        print(f"Alarm Set for {hrs}h : {min}m : {sec}s")

    def set_alarm2_everyday(self, hrs=1, min=1, day=1):
        self.clock.alarm2((min, hrs, day), match=self.clock.AL2_MATCH_HM)
        print(f"Everyday Alarm {hrs} : {min}m")

# Example usage
if __name__ == "__main__":
    clock_config = ClockConfig(i2c_freq=50000) # set to 50000 to save energy
    clock_config.enable_32kHz_output(True)
    clock_config.set_alarm_everyday(7, 30)  # Set the first alarm for 7:30 AM
    clock_config.set_alarm2_everyday(17, 30)