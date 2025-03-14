
from machine import UART, Pin # type: ignore
from time import *
# from configs.configs import sim_rx,sim_tx, sim_uart, sim_baud,sim_pin
 


class Sim():
    def __init__(self,uart_num=None, tx=None,rx=None,baudrate=115200):
        self.uart_num = uart_num
        self.tx =tx
        self.rx =rx
        self.log_run_times=0   
        self.uart = UART(self.uart_num,baudrate,tx=self.tx,rx=self.rx)
        self.commands = {
            'text':self.sendSMS, # text 639568543802 message
            'whatsapp':self.sendwhatsapp, # whatsapp 639568543802 [MESSAGE]
            # 'wifi':sendWifiConfig # wifi [NAME] [PASSWORD]
        }
        # self.write("AT+CMGF=1\r", cmdPurpose='Text Mode') # Put to Text Mode
        print(f"\n----SIM Checking   -----\n")
        self.checkConnection()
        self.lowPowerMode()
 
    def sendwhatsapp(self,message='default Message', whatsappnumber=639765514253):
        try:
            self.connectInternet()
            def urlencode(text):
                return text.replace(' ', '%20').replace('\n', '%0A').replace('\r', '%0D')
            import re
            whatsappnumber = 639765514253
            message = urlencode(message)
            self.write('AT+SAPBR=1,1\r') ##
            sleep(2)
            self.write('AT+HTTPINIT\r')
            sleep(2)
            self.write(f'AT+HTTPPARA="URL","https://api.callmebot.com/whatsapp.php?phone=+{whatsappnumber}&text={message}&apikey=2890524"\r')
            sleep(2)
            self.write('AT+HTTPACTION=0\r')
        except Exception as e:
            print('Error Sending to Whats app',e)
            pass

    def connectInternet(self):
        self.write('AT+CSQ\r\n')
        sleep(1)
        self.write('AT+CGDCONT=1,"IP","internet"\r\n')
        sleep(1)
        self.write('AT+CGACT=1,1\r\n')
        self.write('AT+CGPADDR=1\r\n')

    def checkConnection(self):
        print(' Sim Module Starting ....')
        self.write("AT\r")
        # self.write('AT+COPS=?\r', cmdPurpose='CHECK NETWORK') # 
        isConnected = self.write('AT+CREG?\r',cmdPurpose='Check connection')
        if 'CREG: 0,1' in isConnected or 'CREG: 1,1' in isConnected:
            CCSignal = self.write('AT+CSQ\r',cmdPurpose='Signal Strength')
            print(f"CONNECTED Signal: {CCSignal}" )
        else:
            CCSignal = self.write('AT+CSQ\r')
            print(f'Cant Connect Signal: {CCSignal}')
            # self.write("AT+IPR=115200\r") 
            print('Trying Again.. CHECK BAUD RATE OF SIM AND ESP')
            self.uart = UART(self.uart_num,9600,tx=self.tx,rx=self.rx)
            self.write('AT+CREG=1\r', cmdPurpose='Forcing to Connect')
            self.checkConnection()

    def sendSMS(self,number=639568543802,message="messageTemplate"): #working now
        try:
            self.write("AT\r",cmdPurpose='refresh') # Hand Shake
            self.write("AT+CMGF=1\r", cmdPurpose='Text Mode') # Put to Text Mode
            # atd.write(f'AT+CMGS=\"+639765514253\"\r')
            # self.write("ATE0\r")
            self.write(f'AT+CMGS=\"+{number}\"\r')
            # self.write("ATE1\r")
            self.uart.write(message)
            self.uart.read()
            sleep(1)
            self.uart.write(bytes([26])) # stop the SIM Module for SMS
            self.uart.read()
            print('message Sent')
            return True
        except Exception as e:
            print('Cant Send Message')
            return False
    

    def lowPowerMode(self):
        print('         Low Power Mode      ')
        from time import sleep
        from machine import deepsleep, freq # type: ignore
        # freq(80000000)
        import esp32 # type: ignore
        self.write("AT+IPR=9600\r") # put the SIM MODULE BAUD Rate to 9600
        sleep(2) # wait to set the SIM module before changing to UART
        self.write("AT+IPR?\r")
        self.uart = UART(self.uart_num,9600,tx=self.tx,rx=self.rx)
        self.write("AT+CSCLK=2\r") # put the SIM MODULE To Sleep mode, change to 0 to wake
        try:
            esp32.ULP()
            esp32.raw_temperature() # READ TEMPERATUIRE IN FARENHEIGT
        except:
            print('Not esp32 ULP')
            pass

    def checkTypeOfMessage(self,messageReceived):
        # def sendtextSMS(commandValue):
        #     print("Sending Sms")
        #     n = commandValue.split(" ", 1)
        #     self.sendSMS(self,phone_number=n[0],message=n[1])
        # def sendWhatsApp(commandValue):
        #     import whatsappControl
        #     n = commandValue.split(" ", 1)
        #     whatsappControl.send_message(phone_number=n[0],message=n[1])
        # def sendWifiConfig(commandValue):
        #     n= commandValue.split(" ")
        #     import wifiControl
        #     wifiControl.connectWifi(n[0],n[1])


        textmsg = str(messageReceived).find('CMT: ')
        if textmsg >=0: # Receiving Text MEssage and write here
            # print("   NEW text Message: ")            
            # m = self.checkTypeOfMessage(rx_value)
            m = messageReceived[textmsg:]
            m = m.decode()
            x,y = self.find_1st_2nd(m,'\r\n')
            n = m[x+1:y]
            print('Text Message Extracted',n)
            n = n.split(" ", 1)
            # self.commands[n[0]](n[1]) #Execute
            self.commands[n[0]](*n[1]) # Execute
            
            return messageReceived[textmsg:]
        
    def find_1st_2nd(self,string, substring):
        firstSubstring = string.find(substring)
        secondSubstring = string.find(substring, firstSubstring + 1)
        return [firstSubstring+1,secondSubstring]

    def datetime(self):
        timetoday=self.write("AT+CCLK?\r\n")
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


    def battery(self, logSheet='simbattery.txt'):
        batterylevel=self.write("AT+CBC\r")
        batterylevel = ''.join(filter(lambda i: i.isdigit(), batterylevel))
        batterylevel = int(int(batterylevel)/3778*100)
        timetoday = self.datetime()
        self.record(logSheet,f"{timetoday} - {batterylevel }% Battery \n") 
        print(f' {self.log_run_times}  {timetoday}  - {int(batterylevel)}%')
        self.log_run_times+=1
        return f' {self.log_run_times}  {timetoday}  - {int(batterylevel)}%'

        

    def receive_message(self):
        # self.write("AT\r") # Hand Shake
        rx_value = self.uart.read()
        print(rx_value)
        if rx_value !=None:
            self.record('smsreceived.txt',toWriteData=str(rx_value)+'\n')
            self.checkTypeOfMessage(rx_value)

  
            return  # the text message extracted
        sleep(1)
        


    def record(self , fileName='record.txt',toWriteData=''):
        # TODO INSERT A COMMAND TODO FOR THE CONTROLLER AFTER MESSAGE IS RECEIVED
        print(f'            Writing:   ',toWriteData)
        with open(fileName , "a") as myfile:
            myfile.write(toWriteData)
            myfile.flush()
            myfile.close()

    def write(self,cmd,cmdPurpose='Command'):
        self.uart.write("AT\r") # Hand Shake
        sleep(0.5)
        # print(f"            {cmdPurpose}  :  {cmd}")
        message=None
        timeout=0
        while message == None and timeout!=4:
            self.uart.write(cmd)
            sleep(0.5)
            message = self.uart.read()
            # print(',',end='')
            timeout+=1
            while timeout%2 != 0 and message==None:
                sleep(0.5)
                # print(".",end="")
                timeout+=1
                message = self.uart.read()
        if message == None:
            message = 'TimeOUT'
        else:
            message = message.decode('utf-8').rstrip()
        return message
        # return Status.OK


# import time
# from machine import UART

# # Initialize UART for communication with Air780E (adjust pins as needed)
# uart = UART(1, baudrate=115200, tx=17, rx=16)  # Adjust TX/RX pins for your ESP

# # Helper function to send AT commands to the Air780E
# def send_at_command(command, timeout=2000):
#     uart.write(command + "\r\n")
#     time.sleep_ms(timeout)
#     response = uart.read()  # Read the response from the module
#     if response:
#         print("Response: ", response.decode())  # Print the response as a string

# # Connect to the internet
# def connect_to_internet(apn="internet"):
#     send_at_command("AT")  # Check if the module is responsive
#     send_at_command("AT+CREG?")  # Network registration status
#     send_at_command(f"AT+CGDCONT=1,\"IP\",\"{apn}\"")  # Set APN
#     send_at_command("AT+CGACT=1,1")  # Start GPRS
#     send_at_command("AT+CGPADDR")  # Get IP address
#     print("Connected to the internet!")

# # Disconnect from the internet
# def disconnect_from_internet():
#     send_at_command("AT+CGACT=0,1")  # Deactivate GPRS
#     print("Disconnected from the internet.")

# # Example usage:
# connect_to_internet("internet")  # Replace 'internet' with your carrier's APN
# time.sleep(10)  # Keep the connection for 10 seconds
# disconnect_from_internet()
