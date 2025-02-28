


def run_manual_servo(pin):
    runServo()
    time.sleep(1)   
    return
def milliseconds_to_time(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)
    return hours, minutes, remaining_seconds
# Refactored textWriter function
def textWriter(fileName='text_logs/alarm_logs.txt', toWriteData=''):
    try:
        # Get the current timestamp using the getTime function from clock module
        from clock import getTime
        timeStamp = ' '.join(clock.getTime())
        # Open the file in append mode and write the log
        with open(fileName, "a") as myfile:
            myfile.write(f"\n[{timeStamp}] {toWriteData}")
            myfile.flush()
        print(f"Log written successfully:   {timeStamp} {toWriteData}")
    except Exception as e:
        print(f"Error while writing to log: {e}")
# 
def alarm_handler(pin):
    print('Alarming...')
    timeStamp = ' '.join(clock.getTime())
    logmessage = ''
    alarmclock.check_alarm(1) # renew the alarm
    alarmclock.check_alarm(2) # newnew alarm
    servorun = runServo(5)
    textWriter(toWriteData=f"\n [ {timeStamp} ] Alarm Servo Runs \n ")
    try:
        import SimModule
        atd = SimModule.AT_Device(tx=sim_tx,rx=sim_rx)       
        print('Openning Simcard')
        atd.write("AT+CMGF=1\r", cmdPurpose='Text Mode') # Put to Text Mode
        battery_level = atd.log_run_device(logSheet='text_logs/esp8266_feeder_runtime.txt')
        atd.sendSMS(message=f"{servorun} {battery_level}%")
        print('Done')
    except Exception as e:
        print("\n Simcard Error") 
        print(f"Error: {e} \n")
        logmessage += f"Error: {e} \n"    
    try:
        from wifiControl import connectWifi
        for i in range(3):
            time.sleep(1)
            wifiSetup = connectWifi()
        logmessage += wifiSetup[1]  # Store Wi-Fi setup result in log message
        if wifiSetup[0]:  # If Wi-Fi is connected successfully
            import whatsappControl
            ct = ' '.join(clock.getTime())
            whatsappControl.send_message(message=f"Device Run [ {ct} ]")
            # print("Wi-Fi is set up successfully. and Sent to Whatsapp")
    except Exception as e:
        print(f"Error: {e}")
        logmessage += f"Error: {e}"    
    import network
    network.WLAN().active(False)
    textWriter(toWriteData=f"Servo Runs {' '.join(clock.getTime())}")
    time.sleep(1)
    textWriter(toWriteData=f"{logmessage} Closing:")
def alertUser(battery_level):
    from wifiControl import connectWifi
    for i in range(3):
        time.sleep(1)
        wifiSetup = connectWifi()
    import whatsappControl
    ct = ' '.join(clock.getTime())
    whatsappControl.send_message(message=f"Battery Reading  {battery_level} [ {ct} ]")
    pass


# Function to read the battery voltage
from configs.configs import *
import time
from machine import Pin 
import machine 
adc = machine.ADC(analog_battery)
def read_battery_voltage():
    import time
    # Average ADC readings to reduce noise
    def scale_value(value, min_val=490, max_val=690, new_min=0, new_max=100):
        # Linear scaling formula
        return ((value - min_val) / (max_val - min_val)) * (new_max - new_min) + new_min

    # Define the parameters
    min_val = 460 # minimum Value
    max_val = 690 # max value
    new_min = 0    
    total = 0
    num_samples = 5  # Number of samples to average
    for _ in range(num_samples):
        total += adc.read()
        time.sleep(0.01)  # Delay between readings
    average_value = total / num_samples
    battery_percent = scale_value(average_value)
    print('AVERAGE READING: ',average_value)
    V_min = 3 # Map ADC value (0-1023) to battery voltage range (2.4V to 4.2V)
    V_max = 3.8
    battery_voltage = (average_value / 690) * (V_max - V_min) + V_min
    battery_percentage = ((battery_voltage - V_min) / (V_max - V_min)) * 100
    return [battery_voltage,battery_percentage , f" Reading: {average_value}  Battery {battery_percent} %    ",battery_percent, average_value]


# Main execution starts here
import clock
# from clockAlarm import time_to_alarm


from clockAlarm import set_alarm_everyday,set_alarm2_everyday, alarmclock
from servoControl import runServo

from machine import sleep,reset, RTC 

button = Pin(0, Pin.IN, Pin.PULL_UP)
button.irq(trigger=Pin.IRQ_FALLING, handler=run_manual_servo)




uptime_ms = time.ticks_ms()
uptime_sec = uptime_ms / 1000
hours = int(uptime_sec // 3600)
minutes = int((uptime_sec % 3600) // 60)
seconds = int(uptime_sec % 60)
runtime=f""
# Small delay to stabilize
time.sleep(1)
battery_reading = read_battery_voltage()
welcome_text = f"  {battery_reading[2]}  Uptime: {hours} hours, {minutes} minutes, {seconds} seconds ------"
textWriter(fileName='text_logs/battery_logs.txt', toWriteData=welcome_text)
led = Pin(2, Pin.OUT)
for i in range(10):
    print('sleepings in ',10-i)
    led.value(1)
    time.sleep(1)
    led.value(0)
    time.sleep(1)
led.value(0)

# Get current timestamp
# Write initial log entry
if int(battery_reading[4]) <=550 :
    alertUser(battery_reading[4])
print("Setting up Alarm")
# sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=alarm_handler)
set_alarm_everyday(alarm['am'],alarm['min'])
set_alarm2_everyday(alarm['pm'],alarm['min'])
print("DONE Setting up Alarm")
# Calculate the alarm time (using values from alarms configuration)
# alarmAt = time_to_alarm(alarms[0], alarms[1], alarms[2])  # Morning, Afternoon, Minutes
import network

# Disable the Access Point (AP) interface
ap = network.WLAN(network.AP_IF)
ap.active(False)  # Disable AP mode to stop broadcasting the SSID

# Disable the Station (STA) interface
wifi = network.WLAN(network.STA_IF)
wifi.active(False)  # Disable STA mode to disconnect from any Wi-Fi network

print("Wi-Fi and hotspot are turned off.")
# # Get the current RTC time
# ct = RTC()

# # Check if the alarm time matches the current time




# # Log the sleep time and then sleep for a while
# hours, minutes, seconds = milliseconds_to_time(alarmAt[1])
# print(f"Sleeping until {hours} hours, {minutes} minutes, and {seconds} seconds\n")

# hours, minutes, seconds = milliseconds_to_time(alarmAt[1]-600000)
# print(f"Sleeping until {hours} hours, {minutes} minutes, and {seconds} seconds")
# time.sleep(2)
# deepsleep(alarmAt[1]-600000)  # Uncomment to enable deep sleep
# tourch to manual
sqw_pin = Pin(clock_sqw, Pin.IN, Pin.PULL_UP) #D7
sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=alarm_handler)

sleep(900000000) # 15mins
# sleep(60000) #5mins and re run the system to log the battery
reset()



 

