# ClockConfig

The `ClockConfig` class provides an easy way to configure and manage the DS3231 RTC module on an ESP32 or similar microcontroller. It includes methods for setting up the I2C interface, configuring pins, enabling the 32kHz output, setting alarms, and synchronizing the RTC with the DS3231.

## Features

- Initialize and configure the DS3231 RTC module
- Set up pins for SQW and 32kHz outputs
- Enable or disable the 32kHz output
- Set the frequency of the SQW output
- Set daily alarms
- Synchronize the RTC with the DS3231
- Get the current date and time

## Installation

1. Copy the `clockconfig.py` file to your project directory.
2. Ensure you have the necessary dependencies installed, such as `machine` and `time`.

## Usage

If it reaches the Alarm it will Enable 32khz Output

### Example


```python
from clockconfig import ClockConfig

# Initialize the clock configuration
clock_config = ClockConfig( sqw_pin=13, scl_pin=14, sda_pin=12, handler_alarm=todo_when_alarm , i2c_freq=50000)  # Set I2C frequency to 50kHz to save energy

# Enable 32kHz output
clock_config.enable_32kHz_output(False)

# Set SQW frequency to 1Hz to save energy
clock_config.set_sqw_frequency(1)

# Set alarms
clock_config.set_alarm_everyday(7, 30)  # Set the first alarm for 7:30 AM
clock_config.set_alarm2_everyday(17, 30)  # Set the second alarm for 5:30 PM

# Get the current date and time
current_time = clock_config.get_time()
print(f"Current Date: {current_time[0]}")
print(f"Current Time: {current_time[1]}")


```

Methods
__init__(self, sqw_pin=13, scl_pin=14, sda_pin=12, k32_pin=15, i2c_freq=100000)
Initializes the ClockConfig class with the specified pin numbers and I2C frequency.

setup_pins(self)
Sets up the pins for SQW and 32kHz outputs and attaches interrupt handlers.

enable_32kHz_output(self, enable=True)
Enables or disables the 32kHz output.

set_sqw_frequency(self, freq)
Sets the frequency of the SQW output. Valid frequencies are 1, 1024, 4096, and 8192 Hz.

alarm_handler(self, pin)
Handles interrupts from the SQW pin.



set_alarm_everyday(self, hrs, min, sec=0)
Sets a daily alarm at the specified time.

set_alarm2_everyday(self, hrs=1, min=1, day=1)
Sets a second daily alarm at the specified time.

sync_rtc_with_ds3231(self)
Synchronizes the RTC with the DS3231.

get_time(self)
Returns the current date and time as a list in the format [date, time].

License
This project is licensed under the MIT License.