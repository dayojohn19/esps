import network
import time
try:
    import re
    import requests
except:
    import urequests as requests
from machine import UART

from configs.configs import myPhoneNumber, whatsapp_key ,rootpath, sim_rx, sim_tx, sim_uart

class WhatsApp():
    def __init__(self):
        self.mynumber = myPhoneNumber
        self.whatsapp_key = whatsapp_key

    def urlencode(self, text):
        return text.replace(' ', '%20').replace('\n', '%0A').replace('\r', '%0D')

    def send_message(self, message='Default SMS'):
        try:
            pattern = r" "
            message = re.sub(pattern, "%20", message)
            message = self.urlencode(message)
            url = f'https://api.callmebot.com/whatsapp.php?phone=+{myPhoneNumber}&text={message}&apikey={whatsapp_key}'
            response = requests.get(url)
            if response.status_code == 200:
                return '\nSuccess! Whatsapp message sent'
            else:
                print('Error')
                print(response.text)
        except Exception as e:
            return f'\nError Whatsapp message {e} '

class Sim():
    def __init__(self, uart_num = sim_uart,tx=sim_tx,rx=sim_rx,  baudrate=115200):
        self.uart = UART(uart_num, tx=tx, rx=rx)
        self.tx=tx
        self.rx=rx
        self.receivedSMS = None
        self.uart_num = uart_num
        self.commands = {
            'text':self.text, # text 639568543802 message
            'whatsapp':self.sendWhatsapp, # whatsapp 639568543802 [MESSAGE]
        }
    def checkInternet(self):
        def useWifi(self):
            import json
            # Function to read the Wi-Fi credentials from the JSON file
            def read_wifi_credentials():
                try:
                    # Open the wifiSettings.json file
                    with open('/config/wifiSettings.json', 'r') as f:
                        # Load the JSON content
                        config = json.load(f)
                        ssid = config['ssid']
                        password = config['password']
                        print(f"Loaded SSID: {ssid}")
                        return ssid, password
                except Exception as e:
                    print(f"Error reading wifiSettings.json: {e}")
                    return None, None

            # Initialize the Wi-Fi station (client) interface
            wifi = network.WLAN(network.STA_IF)
            wifi.active(True)  # Enable the Wi-Fi interface

            # Read the SSID and password from the config file
            ssid, password = read_wifi_credentials()

            if ssid and password:
                # Connect to the Wi-Fi network
                wifi.connect(ssid, password)

                # Wait for the connection
                print("Connecting to Wi-Fi...")
                start_time = time.time()

                # Wait until connected or timeout after 15 seconds
                while not wifi.isconnected():
                    if time.time() - start_time > 15:
                        print("Connection failed!")
                        break
                    time.sleep(0.5)

                # If connected, print the network details
                if wifi.isconnected():
                    print("Connected to Wi-Fi!")
                    print("IP address:", wifi.ifconfig()[0])  # Print the device's IP address
                    return True
                else:
                    print('Failed to connect to Wi-Fi!')
                    return False
            else:
                print("Failed to load Wi-Fi settings from config.")        
                return False
        def useLTE(self):

            # Initialize UART for communication with Air780E (adjust pins as needed)
            uart = self.uart

            # Helper function to send AT commands to the Air780E
            def send_at_command(command, timeout=2000):
                uart.write(command + "\r\n")
                time.sleep_ms(timeout)
                response = uart.read()  # Read the response from the module
                if response:
                    print("Response: ", response.decode())  # Print the response as a string

            # Connect to the internet
            def connect(apn="internet"):
                send_at_command("AT")  # Check if the module is responsive
                send_at_command("AT+CREG?")  # Network registration status
                send_at_command(f"AT+CGDCONT=1,\"IP\",\"{apn}\"")  # Set APN
                send_at_command("AT+CGACT=1,1")  # Start GPRS
                send_at_command("AT+CGPADDR")  # Get IP address
                print("Connected to the internet!")
                return True

            # Disconnect from the internet
            def disconnect():
                send_at_command("AT+CGACT=0,1")  # Deactivate GPRS
                print("Disconnected from the internet.")
            connect()
            # Example usage:
            # connect_to_internet("internet")  # Replace 'internet' with your carrier's APN
            # time.sleep(10)  # Keep the connection for 10 seconds
            # disconnect_from_internet()
        print('Checking Internet Connection')
        if useWifi(self):
            print('can connect to wifi')
            return True
        elif useLTE(self):
            print('can connect to LTE')
            return True
        else:
            print('No Connection')
            return False


    def checkSimcard(self):
        print(' Sim Module Starting ....')
        self.write("AT\r")
        # self.write('AT+COPS=?\r', cmdPurpose='Checking Simcard') # 
        isConnected = self.write('AT+CREG?\r',cmdPurpose='Check connection')
        if 'CREG: 0,1' in isConnected or 'CREG: 1,1' in isConnected:
            CCSignal = self.write('AT+CSQ\r',cmdPurpose='Signal Strength')
            print(f"CONNECTED Signal: {CCSignal}" )
            return True
        else:
            CCSignal = self.write('AT+CSQ\r')
            print(f'Cant Connect Signal: {CCSignal}')
            # self.write("AT+IPR=115200\r") 
            print('Changing Baud Rate with ES BAUD RATE')
            self.uart = UART(self.uart_num,9600,tx=self.tx,rx=self.rx)
                
            self.write('AT+CREG=1\r', cmdPurpose='Forcing to Connect')
            self.checkSimcard()
    def sendWhatsapp(self, number=myPhoneNumber, message=None):
        try:
            if message != None:
                if self.checkInternet():
                    if self.checkInternet.useWifi():
                        WhatsApp.send_message(number=myPhoneNumber, message=self.receivedSMS)
                        time.sleep(3)
                        network.WLAN().active(False)
                    elif self.checkInternet.useLTE():
                        WhatsApp.send_message(number=myPhoneNumber, message=self.receivedSMS)
                        time.sleep(3)
                        self.checkInternet.disconnect()
            return 'Whatsapp Sent'
        except Exception as e:
            print(f'Error in sending Whatsapp {e}')
            return f'Error in sending Whatsapp {e}'
    def text(self,number=myPhoneNumber,message=None):
        self.write("AT\r",cmdPurpose='refresh')
        self.write("AT+CMGF=1\r", cmdPurpose='Text Mode')
        self.write(f'AT+CMGS=\"+{number}\"\r')
        self.uart.write(message)
        self.uart.read()
        time.sleep(1)
        self.uart.write(bytes([26]))
        self.uart.read()
    
    def lowPowerMode(self):
        from machine import freq
        freq(80000000)

        self.write("AT+IPR=9600\r")
        time.sleep(2)
        self.write("AT+IPR?\r")
        self.uart = UART(self.uart_num,9600,tx=self.tx,rx=self.rx)
        try:
            import esp32
            esp32.ULP()
            esp32.raw_temperature()
        except:
            print('Error in low power mode not ESP32')

    def checkMessageType(self, messageReceived):
        message = str(messageReceived).find('CMT')
        if message >=0:
            m = m[message:]
            m=m.decode()
            x,y = self.find_1st_2nd(m,'\r\n')
            n = m[x+1:y]
            print('Text Message Extracted',n)
            n = n.split(" ", 1)
            try:
                if n[0] in self.commands:
                    self.commands[n[0]](n[1])
                    cm = f'Command found {self.commands[n[0]](n[1])}'
                    print(cm)
                else:
                    cm = 'No command found'
                    print(cm)
            except:
                print('Command Err')
            self.commands[n[0]](n[1]) #Execute

            self.log(m)
            self.receivedSMS = m
            return m
        
        else:
            cm= 'No message found'
            print(cm)
            pass
        self.log(cm)

    def find_1st_2nd(self,string, substring):
        firstSubstring = string.find(substring)
        secondSubstring = string.find(substring, firstSubstring + 1)
        return [firstSubstring+1,secondSubstring]

    def datetime(self):
        timetoday   =   self.write("AT+CCLK?\r\n")
        x,y = self.find_1st_2nd(timetoday,'"')
        timetoday=timetoday[x:y]
        date_time_str, offset_str = timetoday.split('+')
        date_time_str = date_time_str.strip()  # Remove any extra spaces
        year, month, day, time_str = date_time_str.split('/')[0], date_time_str.split('/')[1], date_time_str.split('/')[2][:2], date_time_str.split(',')[1]
        hour, minute, second = map(int, time_str.split(':'))  # Convert the time into integers
        if hour >= 24:
            hour -= 24
        elif hour < 0:
            hour += 24
        period = "AM"
        if hour >= 12:
            period = "PM"
            if hour > 12:
                hour -= 12
        elif hour == 0:
            hour = 12  # Midnight case
        months = [
            "January", "February", "March", "April", "May", "June", 
            "July", "August", "September", "October", "November", "December"
        ]
        month_name = months[int(month) - 1]
        formatted_time = "{}, {} 20{}, {:02}:{:02}:{:02} {}".format(month_name, day, year, hour, minute, second, period)
        return formatted_time

    def battery(self):
        raw=self.write("AT+CBC\r")
        rawBat = ''.join(filter(lambda i: i.isdigit(), raw))
        batLvl = int(int(rawBat)/3778*100)
        timestamp = self.datetime()
        return f' {timestamp} - {rawBat} - {batLvl}% Battery \n'

    def receive(self):
        sms = self.uart.read()
        if sms != None:
            self.checkMessageType(sms)
            return sms

    def log(self,message=None, path=rootpath+'sim_device.txt'):
        with open(path, 'a') as file:
            try:
                print('Read')
                file.write(self.battery())
            except:
                print('cant read battery')
                file.write(" Cant read Battery")
            file.write('  -  ')
            if message != None:
                file.write(message)
                file.write('\n')
            file.close()


    def write(self, cmd, cmdPurpose=None):
        self.uart.write("AT\r") # Hand Shake
        # print(f"            {cmdPurpose}  :  {cmd}")
        wcm=None
        wtt=0
        while wcm == None and wtt!=4:
            self.uart.write(cmd)
            time.sleep(0.5)
            wcm = self.uart.read()
            # print(',',end='')
            wtt+=1
            while wtt%2 != 0 and wcm==None:
                time.sleep(0.5)
                # print(".",end="")
                wtt+=1
                wcm = self.uart.read()
        if wcm == None:
            wcm = 'Commanding Sim TimeOUT'
        else:
            wcm = wcm.decode('utf-8').rstrip()
        print(wcm)
        if cmdPurpose != None:
            self.log(wcm)
        return wcm