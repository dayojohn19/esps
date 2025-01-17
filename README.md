# ESP libraryies


``` source env/bin/activate```
<small>Python3.9</small>

## Firmware
### Esp 12 F [check this link](https://forum.micropython.org/viewtopic.php?t=3217)
```
esptool.py --port /dev/tty.usbserial-10 erase_flash

esptool.py --port /dev/cu.usbserial-10 --baud 115200 write_flash --flash_mode=dout --flash_size=detect 0 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin
 
```
### Esp 8266
```
 esptool.py --port /dev/tty.usbserial-10 erase_flash

 esptool.py --chip esp8266 --port  /dev/cu.usbserial-10 erase_flash
 esptool.py --chip esp8266 --port /dev/cu.usbserial-10 --baud 460800 write_flash -z 0x1000 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin
```

### ESP 32
```
esptool/esptool.py --chip esp32 --port /dev/tty.usbserial-58EA0095511 erase_flash

esptool.py --chip esp32 --port /dev/tty.usbserial-58EA0095511 --baud 115200 write_flash -z 0x1000 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP32_GENERIC-20241129-v1.24.1.bin
```
integrated workspace esp libs
