

import network
import time
from main_sub import *

"""
New Way to receive rx signal
!important
import select
u = UART(1,baudrate=9600,rx=5)
poll = select.poll()
poll.register(u,select.POLLIN)
while True:
    time.sleep(0.01)                                                                                                              
    events=poll.poll()                                                                                                         
    for f, e in events:                                                                                                        
        if e & select.POLLIN:                                                                                                  
            d = u.read()                                                                                                       
            print('received: ',d)  

# Sample receiveSMS
return ['test command fiirst - +639765514253 [ 25/03/04 14:41:59 +32 ] - +639765514253 [ 25/03/04 14:41:59 +32 ]', '+639765514253']
"""
try:
    # print('trying to update')
    # try:
    gnd = Power()
    # ic = connect_or_create_wifi()
    # gnd.off
    # time.sleep(1)
    gnd.on
    from otaupdater import OTAUpdater
    from internetwifi import connect_or_create_wifi
    # o = OTAUpdater()
    #     ou = OTAUpdater()
    # except Exception as e:
    #     print('Cant connect to internet reason: ',e)
    # gnd.on
    # time.sleep(3)
    s= Sim()
    s.connectInternet()
    o = OTAUpdater()
    # x = RFIDReader()
    gnd.off
    time.sleep(3)
    # time.sleep(2) 4 5 6 7 8
    # x.scan()
    # test 2 permission
    # ic = connect_or_create_wifi()
    gnd.on 
    af = AutoFeeder()
    af.run()
except Exception as e: 
    print("Error Main", "   Reason: ",e)
    print('Resetting in 10')
    textWriter('error.txt',f'Error in Main: {e}')
    for i in range(10):
        time.sleep(1)
    reset()

# gnd.on
time.sleep(1)

# if gnd.power:
#     # try:
#     #     af = AutoFeeder()
#     # except Exception as e:
#     #     print('Error')
# else:
#     for i in range(3):
#         print('\n\n     Please type "gnd.on"  First to power up\n\n')
#         time.sleep(2)

time.sleep(1)
print('sleeping in 3')

# adc = ADC(0)
# adc.atten(ADC.ATTN_11DB)   
# adc.read() # MAx 4095
# door = DoorGate()
# checkBattery()

# Initialize 
#  on GPIO 3 (or choose another pin like GPIO 34)
# print("Turning off everything")
# time.sleep(1)
# import webrepl
# webrepl.start()
 # internetconnection
# print('Turning Off Again')
# time.sleep(60)
# time.sleep(3)
# ic.active(False)
# blueLED.stop()
# self.gnd_active.off()
# deepsleep()



# uart1 = UART(1, baudrate=115200, tx=Pin(20), rx=Pin(21)) 
# while True:
#     uart1.write('AT\r\n')  # Basic AT command to check if ESP32 B responds
#     time.sleep(1)  # Wait for a second
    
#     if uart1.any():  # Check if there is a response
#         response = uart1.read()
#         print("Response from ESP32 B:", response.decode('utf-8'))
#     time.sleep(1)  # Wait for a second




