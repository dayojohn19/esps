from machine import Pin, I2C, RTC , DEEPSLEEP,SoftI2C
import time
from utime import ticks_ms
triggered_time = 0

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
        print('                                                             (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])')
        if datetime is None:
            try:
                self.i2c.readfrom_mem_into(self.addr, DATETIME_REG, self._timebuf)
            except Exception as e:
                print('Error in reading time',e)
                return
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
                print(f"WARNING: Oscillator stop flag set. Time may not be accurate.\n run clock.datetime()  (0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])\n {year, month, day, weekday, hour, minutes, seconds, 0}")

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

    def alarm1(self, time=None, match=AL1_MATCH_DHMS, int_en=True, weekday=True):
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

    def alarm2(self, time=None, match=AL2_MATCH_DHM, int_en=True, weekday=True):
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


from configs.configs import clock_scl,clock_sda,clock_sqw, alarm, alarm_handler
class Clock:
    def __init__(self, sqw_pin=clock_sqw, scl_pin=clock_scl, sda_pin=clock_sda, handler_alarm=alarm_handler,alarm_time=alarm ,i2c_freq=100000 ):
        if sqw_pin == None:
            print('Please set SCL SDA SQW Pin and alarm handler function !!')

        self.amhr=alarm_time['am']
        self.pmhr=alarm_time['pm']
        self.min=alarm_time['min']
        self.i2c_freq = i2c_freq
        self.passed_handler_alarm = handler_alarm
        self.clock_sqw = sqw_pin  # D7
        self.clock_scl = scl_pin  # D5
        self.clock_sda = sda_pin  # D6
        # self.clock_k32 = k32_pin  # D8
        self.clock_i2c = SoftI2C(scl=Pin(self.clock_scl), sda=Pin(self.clock_sda), freq=i2c_freq)  # Example with GPIO14 and GPIO12 SDA=D6 SCL=D5
        # self.clock_i2c = SoftI2C(scl=Pin(clock_scl), sda=Pin(clock_sda))  # Example with GPIO14 and GPIO12 SDA=D6 SCL=D5
        self.clock = DS3231(self.clock_i2c)
        self.enable_32kHz_output(False)
        self.rtc = RTC()
        
        # print("Manually Checking Alarm")
        print('\n\n --- Manual Checking ALARM -- ', end=' ')
        if self.clock.check_alarm(1):
            self.check_handler(self.clock_sqw)
        #     print('\n       ALARM 1 True')
        #     self.clock.check_alarm(1)
        #     self.passed_handler_alarm()
        if self.clock.check_alarm(2):
            self.check_handler(self.clock_sqw)
        #     self.clock.check_alarm(2)
        #     self.passed_handler_alarm()
        #     print('\n   ALARM 2 True')
        # time.sleep(5)
        # print('ALARMS Manually Reviewed  ',self.get_time() )
        self.alarm_daily(self.amhr,self.min)
        self.alarm2_daiy(self.pmhr,self.min)        
        self.setup_pins()
        self.sync_rtc_with_ds3231()
        print(' ***  Clock DONE  +++ \n')

    def sync_rtc_with_ds3231(self):
        print('Syncing RTC with DS3231')
        time.sleep(2)  # Wait for the RTC to stabilize
        self.rtc.datetime(self.clock.datetime())

    def get_time(self):
        date = "{}/{}/{}".format(self.clock.datetime()[1], self.clock.datetime()[2], self.clock.datetime()[0])
        time = "{}:{}:{}".format(self.clock.datetime()[4], self.clock.datetime()[5], self.clock.datetime()[6])
        return [date, time]
    def real_time(self):
        time_tuple = self.clock.datetime()
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

    def setup_pins(self):
        import esp32
        # self.sqw_pin = Pin(self.clock_sqw, Pin.IN, Pin.PULL_DOWN)
        self.sqw_pin = Pin(self.clock_sqw, Pin.IN, Pin.PULL_UP)
        # esp32.wake_on_ext0(self.clock_sqw, level= esp32.WAKEUP_ALL_LOW)
        # esp32.wake_on_ext1(pins = (self.clock_sqw,), level= esp32.WAKEUP_ANY_HIGH)
        esp32.wake_on_ext1(pins = (self.clock_sqw,), level= esp32.WAKEUP_ALL_LOW)
        self.sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=self.check_handler)

        # self.k32_pin = Pin(self.clock_k32, Pin.IN, Pin.PULL_DOWN)
        # self.k32_pin.irq(trigger=Pin.IRQ_RISING, handler=self.handler_32k)

    def enable_32kHz_output(self, enable=False):
        self.clock.output_32kHz(enable)
        return enable

    # def handler_SQW(self, pin):
    def check_handler(self, pin):
        global triggered_time
        new_time = ticks_ms()
        if (new_time - triggered_time) < 500:
            return        
        triggered_time = new_time
        isgoing = False
        if (self.clock.check_alarm(1)):
            print('alarm1: True')
            isgoing = True
        elif (self.clock.check_alarm(2)):
            print('alarm2:  True')
            isgoing = True
        if isgoing == False:
            print('No Alarm Saw')
            return
        def confirm_alarm(currentdate, alarm_min):
            print('Confirming Alarm')
            """
            Check if alarm was triggered near the alarm set
            """
            time_tuple = currentdate
            hour = 1
            alarm_hour = 1
            minute = time_tuple[5] 
            time_in_minutes = hour * 60 + minute
            alarm_time_in_minutes = alarm_hour * 60 + alarm_min
            print(f'Alarm Set Time: {alarm_hour} {alarm_min} ')
            print(f'Alarm Current Time: {hour} {minute}')
            minute_diff = abs(time_in_minutes - alarm_time_in_minutes)
            print('  -----   Alarm Diff: ',minute_diff)
            if minute_diff <= 10:
                print("         The alarm time is within ±10 minutes of the given Minutes.")
                print('Confirmed')
                return True
            else:
                print('Not Confirmed')

                return minute_diff
                
        if  confirm_alarm(self.clock.datetime(), self.min) != True:
            print('     Sorry Alarm Pin Triggered at wrong Time')
            return
        time.sleep(2)
        print('Alarming     Pin Trigger handler_SQL()')
        print(f"[ {self.get_time()[1]} ]SQW Interrupt Triggered by PIN:", pin)
        self.enable_32kHz_output(True)

        # if self.clock.check_alarm(1):
        #     print('\n       ALARM 1 ')
        #     self.passed_handler_alarm()
        # if self.clock.check_alarm(2):
        #     self.passed_handler_alarm()
        #     print('\n   ALARM 2')
        time.sleep(2)
        self.alarm_daily(self.amhr,self.min)
        self.alarm2_daiy(self.pmhr,self.min)
        self.enable_32kHz_output(False)
        self.passed_handler_alarm()
        print('Alarm Reset\n')

    # def handler_32k(self, pin):
    #     print("32kHz Interrupt Triggered by PIN:", pin)
    #     print(self.clock.datetime())
    #     print('\n')

    def alarm_daily(self, hrs, min, sec=0):
        self.hrs = hrs
        self.min = min
        self.clock.alarm1((sec, min, hrs), match=self.clock.AL1_MATCH_HMS)
        print(f"        Alarm1 Set          {hrs}:{min}:{sec}" , end='')

    def alarm2_daiy(self, hrs=1, min=1, day=1):
        self.hrs = hrs
        self.min = min
        self.clock.alarm2((min, hrs, day), match=self.clock.AL2_MATCH_HM)
        print(f"        Alarm2 Set          {hrs}:{min}:0")
        # print(f"Alarm2 Set {hrs} : {min}m")



def date_to_tuple(datestr, ismachineRTC=False):
    instruction = """
    from sim.datetime() to updating ds3231 time
    """
    print('Instruction: ',instruction)
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
    if ismachineRTC:
        date_tuple = (year, month, day, 0, hour, minute, second, 0)
    else:   
        date_tuple = (year, month, day, hour, minute, second, 0)
    return date_tuple #(0-year, 1-month, 2-day, 3-hour, 4-minutes[, 5-seconds[, 6-weekday]])


def updateClock(c,s, ismachine=False):
    instruction = """
    updateClock(    clock_to_update ,   clock_origin   )
    clock_to_update.datetime(clock_origin.datetime())
        if ismachine means the clock is machine.RTC() else it is clock.clock
    """
    # print('Instruction: \n', instruction)
    try:
        if c.datetime()[0] < 2024:
            try:
                c.datetime()
            except:
                c.clock.datetime()
                c = c.clock
            # if c.OSF():
            newTime = s.datetime()
            print(f'        Clock Time not Updated {c.datetime()}')
            updatedt = date_to_tuple(newTime, ismachineRTC=ismachine)
            c.datetime((updatedt))
            print('             Updated Clock')
    except:
        newTime = s.clock.datetime()
    if c.datetime()[0] < 2022:
        print('Cant Update Sim no SIgnal')
        time.sleep(3)
        return False
    return True


# Example usage
if __name__ == "__main__":
    clock_config = Clock(i2c_freq=50000) # set to 50000 to save energy
    clock_config.enable_32kHz_output(False)
    clock_config.alarm_daily(7, 30)  # Set the first alarm for 7:30 AM
    clock_config.alarm2_daiy(17, 30)