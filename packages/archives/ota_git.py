from mpy.ota import OTAUpdater
# from WIFI_CONFIG import SSID, PASSWORD
import json
import time
from mpy.led_signal import *

start_blinking(50)
print("Do you want to update?")
for i in range(6):
    print('     Updating in ',i)
    time.sleep(1)
with open('configs/wifiSettings.json') as f:
    config = json.load(f)
    SSID = config['ssid']
    PASSWORD = config['ssid_password']


from configs.configs import files_to_update, giturl

led.value(0)

# for file in files_to_update:
ota_updater = OTAUpdater(SSID,PASSWORD,giturl,files_to_update)
ota_updater.download_and_install_update_if_available()    
    
stop_blinking()


led.value(1)
for i in range(20):
    led.value(0)
    time.sleep(0.1)
    led.value(1)
    time.sleep(0.1)
for i in range(5):
    led.value(0)
    time.sleep(1)
    led.value(1)
    time.sleep(1)
led.value(1)

# import machine
# machine.reset()

