from main_sub import Power
import socket
import time
import network
import gc
from configs.configs import wifipassword, wifiSSID
from SimModule import Sim

def connect_or_create_wifi(sim=None):
    gnd = Power()
    ic = None
    def test_internet_connection():
        print('Testing Internet')
        try:
            # Try to connect to Google's DNS server (8.8.8.8)
            addr = socket.getaddrinfo('8.8.8.8', 80)
            s = socket.socket()
            s.connect(addr[0][-1])
            print('Internet connected') 
            s.close()
            return True
        except Exception as e:
            print('No internet connection:', e)

    def wait_for_change(check_func, timeout_ms, *args, **kwargs):
        start_time = time.ticks_ms()
        last_value = check_func(*args, **kwargs)  # Get the initial value
        print("waiting")
        while True:
            time.sleep(1)
            print('.',end="")
            current_value = check_func(*args, **kwargs)  # Check the value again
            if current_value != last_value:  # Check if the value has changed
                print("Value changed!")
                return current_value  # Return the new value
            if time.ticks_ms() - start_time > timeout_ms:
                print("Timeout reached, no change in value.")
                return False  # Timeout, return None

    try:
        wifi = network.WLAN(network.STA_IF)
        wifi.active(True)
        # networklists = wifi.scan()    
        # for n in networklists:
        #     nn = n[0]  # SSID (network name)
        #     rssi = n[3]  # RSSI (signal strength)
        #     print(f"SSID: {nn.decode()}, Signal Strength (RSSI): {rssi} dBm")
        wifi.connect(wifiSSID, wifipassword)
        # wifi.connect('Infinix HOT 10S', '123456789')
        # ic.config(essid=str('mywifi'),password='1234')
        print("Connecting to: ",wifiSSID)
        wifiConnection =  wait_for_change(wifi.isconnected, 7000)
        if wifiConnection == False:
            wifi.active(False)
            # blueLED.start(100)
            time.sleep(2)
            ic = network.WLAN(network.AP_IF)
            ic.active(True)        
            ic.config(essid=str('HGW-5DF528'),password='dayosfamily')
            # ic.config(essid=str('mywifi'),password='1234')
            print("     Created Hotspot")
        else:
            ic = network.WLAN(network.AP_IF)
            ic.active(False)
            ic = wifi
            print("     Connected to Wifi")
        print('Web REPL on :            ',ic.ifconfig())
        # return ic
    except Exception as e:
        print('Error in Network connection: ',e)
        # return
    # return
    if test_internet_connection():
        print("Connected to the internet")
    else:
        try:
            if sim==None:
                print('No Sim Given')
            gc.collect()
            # ic.active(False)
            gnd.off
            time.sleep(4)
            gnd.on
            print('Connecting to internet via sim')
            sim = Sim()
            ic = sim.connectInternet()
            if test_internet_connection():
                print("\n       SIM     Connected to the internet")
            else:
                print("No internet connection")
        except Exception as e:
            print('Cant Connect to Internet: ',e)
    return ic

