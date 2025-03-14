# ESP libraryies

## Everyday Use
        source env/bin/activate
<small>Python3.9</small>

after editing files always update the files with 

        mpy-cross path/file 
        
<small>can just drag and drop the file on the terminal</small>


## View all reusable ESP packages
-   [packages](/packages/)
# OTA REPL or Terminal
- [repl OTA link](https://learn.adafruit.com/micropython-basics-esp8266-webrepl/access-webrepl)
- install a firmware with OTA compatible
                `import webrepl`
```
import network
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wap = network.WLAN(network.AP_IF)
wap.active()
wlan.connect('ssid', 'password')
wlan.ifconfig()
wlan.ifconfig()
('192.168.101.2', '255.255.255.0', '192.168.101.1', '192.168.101.1')

import webrepl

```
then open the [webrepl-master](/webrepl-master%20/webrepl.html)
then connect on `ws://192.168.101.2:8266`
## Firmware
### Esp 12 F [check this link](https://forum.micropython.org/viewtopic.php?t=3217)
```
esptool.py --port /dev/tty.usbserial-110 erase_flash

esptool.py --port /dev/cu.usbserial-10 --baud 115200 write_flash --flash_mode=dout --flash_size=detect 0 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin
 
```
### Esp 8266
```
 esptool.py --port /dev/tty.usbserial-110 erase_flash


 esptool.py --chip esp8266 --port  /dev/cu.usbserial-10 erase_flash


 esptool.py --chip esp8266 --port /dev/cu.usbserial-10 --baud 460800 write_flash -z 0x1000 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin


 esptool.py --port /dev/tty.usbserial-110 --baud 115200 write_flash --flash_mode=dout --flash_size=detect 0 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin
```

### ESP 32
```
esptool.py --chip esp32 --port /dev/tty.usbserial-58EA0095511 erase_flash

esptool.py --chip esp32 --port /dev/tty.usbserial-58EA0095511 --baud 115200 write_flash -z 0x1000 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP32_GENERIC-20241129-v1.24.1.bin
```
