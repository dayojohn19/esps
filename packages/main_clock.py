from machine import Pin, I2C, RTC 
import time


DATETIME_REG    = const(0) # 7 bytes
ALARM1_REG      = const(7) # 5 bytes
ALARM2_REG      = const(11) # 4 bytes
CONTROL_REG     = const(14)
STATUS_REG      = const(15)
AGING_REG       = const(16)
TEMPERATURE_REG = const(17) # 2 bytes
# datetime = (2025,1 , 3, 2, 56, 30, 5) # OLD

# datetime : tuple, (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])"""
# ds.datetime((2025,1,4,3,46,0,6))
def dectobcd(decimal):
    """Convert decimal to binary coded decimal (BCD) format"""
    return (decimal // 10) << 4 | (decimal % 10)

def bcdtodec(bcd):
    """Convert binary coded decimal to decimal"""
    return ((bcd >> 4) * 10) + (bcd & 0x0F)


class DS3231:
    """ DS3231 RTC driver.

    Hard coded to work with year 2000-2099."""
    FREQ_1      = const(1)
    FREQ_1024   = const(2)
    FREQ_4096   = const(3)
    FREQ_8192   = const(4)
    SQW_32K     = const(1)

    AL1_EVERY_S     = const(15) # Alarm every second
    AL1_MATCH_S     = const(14) # Alarm when seconds match (every minute)
    AL1_MATCH_MS    = const(12) # Alarm when minutes, seconds match (every hour)
    AL1_MATCH_HMS   = const(8) # Alarm when hours, minutes, seconds match (every day)
    AL1_MATCH_DHMS  = const(0) # Alarm when day|wday, hour, min, sec match (specific wday / mday) (once per month/week)

    AL2_EVERY_M     = const(7) # Alarm every minute on 00 seconds
    AL2_MATCH_M     = const(6) # Alarm when minutes match (every hour)
    AL2_MATCH_HM    = const(4) # Alarm when hours and minutes match (every day)
    AL2_MATCH_DHM   = const(0) # Alarm when day|wday match (once per month/week)

    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self._timebuf = bytearray(7) # Pre-allocate a buffer for the time data
        self._buf = bytearray(1) # Pre-allocate a single bytearray for re-use
        self._al1_buf = bytearray(4)
        self._al2buf = bytearray(3)

    def datetime(self, datetime=None):
        """Get or set datetime
        Always sets or returns in 24h format, converts to 24h if clock is set to 12h format
        datetime : tuple, (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])"""
        if datetime is None:
            self.i2c.readfrom_mem_into(self.addr, DATETIME_REG, self._timebuf)
            # 0x00 - Seconds    BCD
            # 0x01 - Minutes    BCD
            # 0x02 - Hour       0 12/24 AM/PM/20s BCD
            # 0x03 - WDay 1-7   0000 0 BCD
            # 0x04 - Day 1-31   00 BCD
            # 0x05 - Month 1-12 Century 00 BCD
            # 0x06 - Year 0-99  BCD (2000-2099)
            seconds = bcdtodec(self._timebuf[0])
            minutes = bcdtodec(self._timebuf[1])

            if (self._timebuf[2] & 0x40) >> 6: # Check for 12 hour mode bit
                hour = bcdtodec(self._timebuf[2] & 0x9f) # Mask out bit 6(12/24) and 5(AM/PM)
                if (self._timebuf[2] & 0x20) >> 5: # bit 5(AM/PM)
                    # PM
                    hour += 12
            else:
                # 24h mode
                hour = bcdtodec(self._timebuf[2] & 0xbf) # Mask bit 6 (12/24 format)

            weekday = bcdtodec(self._timebuf[3]) # Can be set arbitrarily by user (1,7)
            day = bcdtodec(self._timebuf[4])
            month = bcdtodec(self._timebuf[5] & 0x7f) # Mask out the century bit
            year = bcdtodec(self._timebuf[6]) + 2000

            if self.OSF():
                print("WARNING: Oscillator stop flag set. Time may not be accurate.")

            return (year, month, day, weekday, hour, minutes, seconds, 0) # Conforms to the ESP8266 RTC (v1.13)

        # Set the clock
        try:
            self._timebuf[3] = dectobcd(datetime[6]) # Day of week
        except IndexError:
            self._timebuf[3] = 0
        try:
            self._timebuf[0] = dectobcd(datetime[5]) # Seconds
        except IndexError:
            self._timebuf[0] = 0
        self._timebuf[1] = dectobcd(datetime[4]) # Minutes
        self._timebuf[2] = dectobcd(datetime[3]) # Hour + the 24h format flag
        self._timebuf[4] = dectobcd(datetime[2]) # Day
        self._timebuf[5] = dectobcd(datetime[1]) & 0xff # Month + mask the century flag
        self._timebuf[6] = dectobcd(int(str(datetime[0])[-2:])) # Year can be yyyy, or yy
        self.i2c.writeto_mem(self.addr, DATETIME_REG, self._timebuf)
        self._OSF_reset()
        return True

    def square_wave(self, freq=None):
        """Outputs Square Wave Signal

        The alarm interrupts are disabled when enabling a square wave output. Disabling SWQ out does
        not enable the alarm interrupts. Set them manually with the alarm_int() method.
        freq : int,
            Not given: returns current setting
            False = disable SQW output,
            1 =     1 Hz,
            2 = 1.024 kHz,
            3 = 4.096 kHz,
            4 = 8.192 kHz"""
        if freq is None:
            return self.i2c.readfrom_mem(self.addr, CONTROL_REG, 1)[0]

        if not freq:
            # Set INTCN (bit 2) to 1 and both ALIE (bits 1 & 0) to 0
            self.i2c.readfrom_mem_into(self.addr, CONTROL_REG, self._buf)
            self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([(self._buf[0] & 0xf8) | 0x04]))
        else:
            # Set the frequency in the control reg and at the same time set the INTCN to 0
            freq -= 1
            self.i2c.readfrom_mem_into(self.addr, CONTROL_REG, self._buf)
            self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([(self._buf[0] & 0xe3) | (freq << 3)]))
        return True

    def alarm1(self, time=None, match=AL1_MATCH_DHMS, int_en=True, weekday=False):
        """Set alarm1, can match mday, wday, hour, minute, second

        time    : tuple, (second,[ minute[, hour[, day]]])
        weekday : bool, select mday (False) or wday (True)
        match   : int, match const
        int_en  : bool, enable interrupt on alarm match on SQW/INT pin (disables SQW output)"""
        if time is None:
            # TODO Return readable string
            self.i2c.readfrom_mem_into(self.addr, ALARM1_REG, self._al1_buf)
            return self._al1_buf

        if isinstance(time, int):
            time = (time,)

        a1m4 = (match & 0x08) << 4
        a1m3 = (match & 0x04) << 5
        a1m2 = (match & 0x02) << 6
        a1m1 = (match & 0x01) << 7

        dydt = (1 << 6) if weekday else 0 # day / date bit

        self._al1_buf[0] = dectobcd(time[0]) | a1m1 # second
        self._al1_buf[1] = (dectobcd(time[1]) | a1m2) if len(time) > 1 else a1m2 # minute
        self._al1_buf[2] = (dectobcd(time[2]) | a1m3) if len(time) > 2 else a1m3 # hour
        self._al1_buf[3] = (dectobcd(time[3]) | a1m4 | dydt) if len(time) > 3 else a1m4 | dydt # day (wday|mday)

        self.i2c.writeto_mem(self.addr, ALARM1_REG, self._al1_buf)

        # Set the interrupt bit
        self.alarm_int(enable=int_en, alarm=1)

        # Check the alarm (will reset the alarm flag)
        self.check_alarm(1)

        return self._al1_buf

    def alarm2(self, time=None, match=AL2_MATCH_DHM, int_en=True, weekday=False):
        """Get/set alarm 2 (can match minute, hour, day)

        time    : tuple, (minute[, hour[, day]])
        weekday : bool, select mday (False) or wday (True)
        match   : int, match const
        int_en  : bool, enable interrupt on alarm match on SQW/INT pin (disables SQW output)
        Returns : bytearray(3), the alarm settings register"""
        if time is None:
            # TODO Return readable string
            self.i2c.readfrom_mem_into(self.addr, ALARM2_REG, self._al2buf)
            return self._al2buf

        if isinstance(time, int):
            time = (time,)

        a2m4 = (match & 0x04) << 5 # masks
        a2m3 = (match & 0x02) << 6
        a2m2 = (match & 0x01) << 7

        dydt = (1 << 6) if weekday else 0 # day / date bit

        self._al2buf[0] = dectobcd(time[0]) | a2m2 if len(time) > 1 else a2m2 # minute
        self._al2buf[1] = dectobcd(time[1]) | a2m3 if len(time) > 2 else a2m3 # hour
        self._al2buf[2] = dectobcd(time[2]) | a2m4 | dydt if len(time) > 3 else a2m4 | dydt # day

        self.i2c.writeto_mem(self.addr, ALARM2_REG, self._al2buf)

        # Set the interrupt bits
        self.alarm_int(enable=int_en, alarm=2)

        # Check the alarm (will reset the alarm flag)
        self.check_alarm(2)

        return self._al2buf

    def alarm_int(self, enable=True, alarm=0):
        """Enable/disable interrupt for alarm1, alarm2 or both.

        Enabling the interrupts disables the SQW output
        enable : bool, enable/disable interrupts
        alarm : int, alarm nr (0 to set both interrupts)
        returns: the control register"""
        if alarm in (0, 1):
            self.i2c.readfrom_mem_into(self.addr, CONTROL_REG, self._buf)
            if enable:
                self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([(self._buf[0] & 0xfa) | 0x05]))
            else:
                self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([self._buf[0] & 0xfe]))

        if alarm in (0, 2):
            self.i2c.readfrom_mem_into(self.addr, CONTROL_REG, self._buf)
            if enable:
                self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([(self._buf[0] & 0xf9) | 0x06]))
            else:
                self.i2c.writeto_mem(self.addr, CONTROL_REG, bytearray([self._buf[0] & 0xfd]))

        return self.i2c.readfrom_mem(self.addr, CONTROL_REG, 1)

    def check_alarm(self, alarm):
        """Check if the alarm flag is set and clear the alarm flag"""
        self.i2c.readfrom_mem_into(self.addr, STATUS_REG, self._buf)
        if (self._buf[0] & alarm) == 0:
            # Alarm flag not set
            return False

        # Clear alarm flag bit
        self.i2c.writeto_mem(self.addr, STATUS_REG, bytearray([self._buf[0] & ~alarm]))
        return True

    def output_32kHz(self, enable=True):
        """Enable or disable the 32.768 kHz square wave output"""
        status = self.i2c.readfrom_mem(self.addr, STATUS_REG, 1)[0]
        if enable:
            self.i2c.writeto_mem(self.addr, STATUS_REG, bytearray([status | (1 << 3)]))
        else:
            self.i2c.writeto_mem(self.addr, STATUS_REG, bytearray([status & (~(1 << 3))]))

    def OSF(self):
        """Returns the oscillator stop flag (OSF).

        1 indicates that the oscillator is stopped or was stopped for some
        period in the past and may be used to judge the validity of
        the time data.
        returns : bool"""
        return bool(self.i2c.readfrom_mem(self.addr, STATUS_REG, 1)[0] >> 7)

    def _OSF_reset(self):
        """Clear the oscillator stop flag (OSF)"""
        self.i2c.readfrom_mem_into(self.addr, STATUS_REG, self._buf)
        self.i2c.writeto_mem(self.addr, STATUS_REG, bytearray([self._buf[0] & 0x7f]))

    def _is_busy(self):
        """Returns True when device is busy doing TCXO management"""
        return bool(self.i2c.readfrom_mem(self.addr, STATUS_REG, 1)[0] & (1 << 2))
# Set the machine datetime

# When alarm it will set the 32kHz output



class Clock:
    def __init__(self, sqw_pin=13, scl_pin=14, sda_pin=12, handler_alarm=None, i2c_freq=100000 ):
        self.hrs=0
        self.min=0
        self.i2c_freq = i2c_freq
        self.handler_alarm = handler_alarm
        self.clock_sqw = sqw_pin  # D7
        self.clock_scl = scl_pin  # D5
        self.clock_sda = sda_pin  # D6
        # self.clock_k32 = k32_pin  # D8
        self.clock_i2c = I2C(scl=Pin(self.clock_scl), sda=Pin(self.clock_sda), freq=i2c_freq)  # Example with GPIO14 and GPIO12 SDA=D6 SCL=D5
        self.clock = DS3231(self.clock_i2c)
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
        self.set_alarm_everyday(self.hrs,self.min)
        self.set_alarm2_everyday(self.hrs,self.min)
        print(f" \n {self.clock.datetime()} SQW Interrupt Triggered by PIN:", pin)
        self.handler_alarm()
        self.enable_32kHz_output(False)
        self.clock.check_alarm(1)
        self.clock.check_alarm(2)
        print('\n')

    # def handler_32k(self, pin):
    #     print("32kHz Interrupt Triggered by PIN:", pin)
    #     print(self.clock.datetime())
    #     print('\n')

    def set_alarm_everyday(self, hrs, min, sec=0):
        self.hrs = hrs
        self.min = min
        self.clock.alarm1((sec, min, hrs), match=self.clock.AL1_MATCH_HMS)
        print(f"Alarm Set for {hrs}h : {min}m : {sec}s")

    def set_alarm2_everyday(self, hrs=1, min=1, day=1):
        self.hrs = hrs
        self.min = min
        self.clock.alarm2((min, hrs, day), match=self.clock.AL2_MATCH_HM)
        print(f"Everyday Alarm {hrs} : {min}m")

# Example usage
if __name__ == "__main__":
    clock_config = Clock(i2c_freq=50000) # set to 50000 to save energy
    clock_config.enable_32kHz_output(True)
    clock_config.set_alarm_everyday(7, 30)  # Set the first alarm for 7:30 AM
    clock_config.set_alarm2_everyday(17, 30)