import network
import gc
import esp
import time

WifiConnected = False
WifiName = ''

def connectWifi(wifiSSID=None,wifiPassword=None): # option to put SSID AND PAssword
    import json
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    # wlan.PM_POWERSAVE
    time.sleep(1)
    gc.collect()
    time.sleep(1)
    esp.osdebug(None)
    # esp.debug(None)
    time.sleep(1)
    # networks = []
    # for nl in network_list:
    #     newData = {}
    #     nl = list(nl)
    #     newData['ssid'] = nl[0].decode("utf-8")
    #     networks.append(newData)
    #     # [ssid,randStr,randStr2,signal,randNum,randNum4,boolidk] = 
    #     print(f'            -  {nl}')
    # print(f" Connected: {wlan.isconnected()}     {wlan.ifconfig()}")
    time.sleep(1)
    if wifiSSID==None:
        print('         Importing from wifi settings json..')
        with open('configs/wifiSettings.json') as f:
            config = json.load(f)
            wifiSSID = config['ssid']
            wifiPassword = config['ssid_password']
    # wlan.connect(wifiSSID,wifiPassword)
    # time.sleep(1)
    # print("    WIFI Control initializing...    ")
    elif wifiSSID != None:
        print(f"\n\n     Creating New Config for {wifiSSID}")
        with open('configs/wifiSettings.json') as f:
            config = json.load(f)
        with open('configs/wifiSettings.json','w') as f:
            config["ssid"] = wifiSSID
            config["ssid_password"] = wifiPassword
            json.dump(config, f)
        print("Restarting Wifi")
        import machine
        machine.reset()
    time.sleep(1)
    # wifiSSID = "HGW-5DF528"
    # wifiPassword = "dayosfamily"
    print(f"     Connecting:  {wifiSSID}  {wifiSSID}")
    wlan.connect(wifiSSID,wifiPassword)
    time.sleep(1)
    WifiName = wifiSSID
    time.sleep(1)
    WifiConnected = wlan.isconnected()
    time.sleep(1)
    # print("web Server")
    # createWebserber()
    # print("server")
    if wlan.isconnected():
        print('Wifi Connected')
        return [True,' Wifi Connected']
    else:
        print('Cant Connect Restarting')
        time.sleep(1)
        return [False, ' Wifi not Connected ']
        # import machine
        # machine.reset()