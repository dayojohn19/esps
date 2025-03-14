import time
import clock
import machine
import network
from machine import Pin, sleep, reset, RTC
from configs.configs import *
from clockAlarm import set_alarm_everyday, set_alarm2_everyday, alarmclock
from servoControl import runServo

# Initialize global variables
adc = machine.ADC(analog_battery)
 
# Function to run the servo manually
def run_manual_servo(pin):
    runServo()
    time.sleep(1)

# Function to convert milliseconds to hours, minutes, and seconds
def milliseconds_to_time(milliseconds):
    seconds = milliseconds / 1000
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = int(seconds % 60)
    return hours, minutes, remaining_seconds

# Function to write logs to a file
def textWriter(fileName='text_logs/alarm_logs.txt', toWriteData=''):
    try:
        from clock import getTime
        timeStamp = ' '.join(clock.getTime())
        with open(fileName, "a") as myfile:
            myfile.write(f"\n[{timeStamp}] {toWriteData}")
            myfile.flush()
        print(f"Log written successfully: {timeStamp} {toWriteData}")
    except Exception as e:
        print(f"Error while writing to log: {e}")

# Function to handle alarms
def alarm_handler(pin):
    print('Alarming...')
    timeStamp = ' '.join(clock.getTime())
    logmessage = ''
    alarmclock.check_alarm(1)
    alarmclock.check_alarm(2)
    servorun = runServo(5)
    textWriter(toWriteData=f"\n [ {timeStamp} ] Alarm Servo Runs \n ")
    handle_sim_module(servorun)
    handle_wifi_module()
    network.WLAN().active(False)
    textWriter(toWriteData=f"Servo Runs {' '.join(clock.getTime())}")
    time.sleep(1)
    textWriter(toWriteData=f"{logmessage} Closing:")

# Function to handle SIM module operations
def handle_sim_module(servorun):
    try:
        import SimModule
        atd = SimModule.AT_Device(tx=sim_tx, rx=sim_rx)
        print('Opening Simcard')
        atd.write("AT+CMGF=1\r", cmdPurpose='Text Mode')
        battery_level = atd.log_run_device(logSheet='text_logs/esp8266_feeder_runtime.txt')
        atd.sendSMS(message=f"{servorun} {battery_level}%")
        print('Done')
    except Exception as e:
        print("\n Simcard Error")
        print(f"Error: {e} \n")
        logmessage += f"Error: {e} \n"

# Function to handle Wi-Fi module operations
def handle_wifi_module():
    try:
        from wifiControl import connectWifi
        for i in range(3):
            time.sleep(1)
            wifiSetup = connectWifi()
        logmessage += wifiSetup[1]
        if wifiSetup[0]:
            import whatsappControl
            ct = ' '.join(clock.getTime())
            whatsappControl.send_message(message=f"Device Run [ {ct} ]")
    except Exception as e:
        print(f"Error: {e}")
        logmessage += f"Error: {e}"

# Function to alert the user about battery level
def alertUser(battery_level):
    from wifiControl import connectWifi
    for i in range(3):
        time.sleep(1)
        wifiSetup = connectWifi()
    import whatsappControl
    ct = ' '.join(clock.getTime())
    whatsappControl.send_message(message=f"Battery Reading {battery_level} [ {ct} ]")

# Function to read the battery voltage
def read_battery_voltage():
    def scale_value(value, min_val=490, max_val=690, new_min=0, new_max=100):
        return ((value - min_val) / (max_val - min_val)) * (new_max - new_min) + new_min

    min_val = 460
    max_val = 690
    total = 0
    num_samples = 5
    for _ in range(num_samples):
        total += adc.read()
        time.sleep(0.01)
    average_value = total / num_samples
    battery_percent = scale_value(average_value)
    print('AVERAGE READING: ', average_value)
    V_min = 3
    V_max = 3.8
    battery_voltage = (average_value / 690) * (V_max - V_min) + V_min
    battery_percentage = ((battery_voltage - V_min) / (V_max - V_min)) * 100
    return [battery_voltage, battery_percentage, f" Reading: {average_value}  Battery {battery_percent} %", battery_percent, average_value]

# Main execution starts here
def main():
    button = Pin(0, Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=run_manual_servo)

    uptime_ms = time.ticks_ms()
    uptime_sec = uptime_ms / 1000
    hours = int(uptime_sec // 3600)
    minutes = int((uptime_sec % 3600) // 60)
    seconds = int(uptime_sec % 60)
    time.sleep(1)
    battery_reading = read_battery_voltage()
    welcome_text = f"  {battery_reading[2]}  Uptime: {hours} hours, {minutes} minutes, {seconds} seconds ------"
    textWriter(fileName='text_logs/battery_logs.txt', toWriteData=welcome_text)
    led = Pin(2, Pin.OUT)
    for i in range(10):
        print('sleepings in ', 10 - i)
        led.value(1)
        time.sleep(1)
        led.value(0)
        time.sleep(1)
    led.value(0)

    if int(battery_reading[4]) <= 550:
        alertUser(battery_reading[4])
    print("Setting up Alarm")
    set_alarm_everyday(alarm['am'], alarm['min'])
    set_alarm2_everyday(alarm['pm'], alarm['min'])
    print("DONE Setting up Alarm")

    ap = network.WLAN(network.AP_IF)
    ap.active(False)
    wifi = network.WLAN(network.STA_IF)
    wifi.active(False)
    print("Wi-Fi and hotspot are turned off.")

    sqw_pin = Pin(clock_sqw, Pin.IN, Pin.PULL_UP)
    sqw_pin.irq(trigger=Pin.IRQ_FALLING, handler=alarm_handler)

    sleep(900000000)
    reset()

if __name__ == "__main__":
    main()





