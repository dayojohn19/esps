## Firmware
### Esp 12 F [check this link](https://forum.micropython.org/viewtopic.php?t=3217)
```
esptool.py --port /dev/tty.usbserial-110 erase_flash

esptool.py --port /dev/cu.usbserial-10 --baud 115200 write_flash --flash_mode=dout --flash_size=detect 0 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin
 
```
### Esp 8266
```
esptool.py --port /dev/tty.usbserial-10 erase_flash

 esptool.py --chip esp8266 --port  /dev/cu.usbserial-10 erase_flash


 esptool.py --chip esp8266 --port /dev/cu.usbserial-10 --baud 460800 write_flash -z 0x1000 
            /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin


esptool.py --port /dev/tty.usbserial-10 --baud 115200 write_flash --flash_mode=dout --flash_size=detect 0 /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP8266_GENERIC-20241129-v1.24.1.bin


```

### ESP 32
```
esptool.py --chip esp32 --port /dev/tty.usbserial-58EA0095511 erase_flash

esptool.py --chip esp32 --port /dev/tty.usbserial-58EA0095511 --baud 115200 write_flash -z 0x1000 

                                /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP32_GENERIC-20241129-v1.24.1.bin

                                /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP32_GENERIC-20220618-v1.19.1.bin

                                /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP32_GENERIC-OTA-20241129-v1.24.1.bin

```

## ESP C3
esptool.py --port /dev/tty.usbmodem101 erase_flash

esptool.py --baud 115200 write_flash 0 
                                        /Users/nhoj/Desktop/garden/ESP_/firmwares/ESP32_GENERIC_C3-07e52c65-.bin
                                        Note* This Firmware the GPIO wakeUp is Working




ser = serial.Serial(
    port='/dev/tty.usbserial-110',
    baudrate=115200,
    #parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS
)

ser = serial.Serial('/dev/tty.usbserial-110',115200)