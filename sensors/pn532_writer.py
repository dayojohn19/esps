import pn532 as nfc
from machine import Pin, SPI
sclk=14 # 
miso=12
mosi=13
ss=16
# SPI
cs = Pin(16, Pin.OUT)

cs.on()

spi_dev = SPI(1, baudrate=1000000)
# SENSOR INIT
pn532 = nfc.PN532(spi_dev,cs)
ic, ver, rev, support = pn532.get_firmware_version()
print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

# Configure PN532 to communicate with MiFare cards
pn532.SAM_configuration()

# FUNCTION TO READ 
def read_nfc(dev, tmot):
    print('Reading...')
    uid = dev.read_passive_target(timeout=tmot)
    if uid is None:
        print('CARD NOT FOUND')
    else:
        numbers = [i for i in uid]
        string_ID = '{}-{}-{}-{}'.format(*numbers)
        print('Found card with UID:', [hex(i) for i in uid])
        print('Number_id: {}'.format(string_ID))

z=1
read_nfc(pn532, 500)
import time
while True:
    time.sleep(0.1)
    read_nfc(pn532,500)

