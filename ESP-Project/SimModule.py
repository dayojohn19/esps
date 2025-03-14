
from machine import UART, Pin # type: ignore
from configs.configs import sim_rx,sim_tx, sim_uart, sim_baud
import time
# ,sim_pin
 

class Sim():
    def __init__(self,uart_num=sim_uart, tx=sim_tx,rx=sim_rx,baudrate=sim_baud):
        self.uart_num = uart_num
        self.tx =tx
        self.rx =rx        
        self.uart = UART(self.uart_num,baudrate,tx=self.tx,rx=self.rx)
        print('Starting Sim')
        try:
            print("     Checking if Sim is Connected: ",end=' ')
            isConnected = self.write("AT\r")
            i=0
            s = time.time()
            print('Checking: ',end='')
            while not 'OK' in isConnected:
                if time.time()-s >=10:
                    break
                time.sleep(1)
                print('.',end='')
                i+=1

            if 'OK' in isConnected :
                print('         True')   
                return
            print('         isConnected',isConnected)   
        except Exception as e:
            print('     checking Error',e)
        # try:
        print('     Creating Sim')
    # self.power = Pin(sim_pin,Pin.OUT)
        self.log_run_times=0   
        
        self.ic = None
        self.commands = {
            'text':self.sendSMS, # text 639568543802 message
            'whatsapp':self.sendwhatsapp, # whatsapp 639568543802 [MESSAGE]
            # 'wifi':sendWifiConfig # wifi [NAME] [PASSWORD]
        }
        # self.power.off()
        time.sleep(0.5)
        # self.power.on()
        # self.write("AT+CMGF=1\r", cmdPurpose='Text Mode') # Put to Text Mode
        if self.checkConnection() == False:
            return print('Cant Connect Signal')

        print('Sim Attributes: ') 
        for attr in dir(self):
            # Check if the attribute is callable (method) or a property
            if (callable(getattr(self, attr)) and not attr.startswith("__")) or isinstance(getattr(self.__class__, attr, None), property):
                print('         ',attr)     
            time.sleep(0.1)
        # except Exception as e:
        #     print('Cant Initialize Sim',e)
        #     return None


    # def sms(self):
    #     return self.receiveSMS()
        # self.lowPowerMode()
    def uart_callback(self):
        if self.uart.any():
            data = self.uart.read()
            print(f"    RX Received     {data}")

    def sendwhatsapp(self,message='default Message', whatsappnumber=639765514253):
        try:
            self.connectInternet()
            def urlencode(text):
                return text.replace(' ', '%20').replace('\n', '%0A').replace('\r', '%0D')
            import re
            whatsappnumber = 639765514253
            message = urlencode(message)
            self.write('AT+SAPBR=1,1\r') ##
            time.sleep(2)
            self.write('AT+HTTPINIT\r')
            time.sleep(2)
            self.write(f'AT+HTTPPARA="URL","https://api.callmebot.com/whatsapp.php?phone=+{whatsappnumber}&text={message}&apikey=2890524"\r')
            time.sleep(2)
            self.write('AT+HTTPACTION=0\r')
        except Exception as e:
            print('Error Sending to Whats app',e)
            pass

    def connectInternet(self):
        st = time.time()
        while True:
            print('     Trying Connecting to network')
            if time.time() - st > 120:
                print('Cant Check Connection')
                return False                
            try:
                self.write('AT+CSQ\r\n')
                time.sleep(1)
                print('Connected 1/6')
                self.write('AT+CGDCONT=1,"IP","internet"\r\n')
                time.sleep(1)
                print('Connected 2/6')
                self.write('AT+CGACT=1,1\r\n')
                self.write('AT+CGPADDR=1\r\n')
                print('Connected Address 3/6')
                time.sleep(1)
                # self.write('AT+CGDATA="PPP",1\r\n')
                self.write('ATD*99#\r\n')
                print('Connected 4/6')
                time.sleep(1)            
                import network
                # network.WLAN().active(False)
                ic = network.PPP(self.uart)
                ic.active(True)
                ic.connect()
                print('Connected 5/6')
                time.sleep(3)
                if ic.isconnected():
                    print('Connected 6/6')
                else:
                    print('waiting for connection')
                    time.sleep(10)
                    if ic.isconnected():
                        print('Connected 6/6')

                    else:
                        print('Cant Connect')

                print('Internet Connected variable  self.ic   ')
                self.ic = ic
                return ic

                    
            except Exception as e:
                print(f'Cant Connect Internet {e}')
                return False
    

    def checkConnection(self):
        print('         Sim checking connection')
        notConnected = True
        # self.write('AT+COPS=?\r', cmdPurpose='CHECK NETWORK') # 
        st = time.time()

        while notConnected:
            print('.', end='')
            if time.time() - st > 30:
                print('Cant Check Connection')
                return False
            time.sleep(1)
            self.write("AT\r")
            isConnected = self.write('AT+CREG?\r',cmdPurpose='Check connection')
            print('     Connection: ', isConnected)
            if 'CREG: 0,2' in isConnected:
                print('         No signal')
                time.sleep(1)
                self.uart = self.uart
                time.sleep(1)
                continue
            elif 'CREG: 0,1' in isConnected or 'CREG: 1,1' in isConnected or 'CREG: 13,0':
                CCSignal = self.write('AT+CSQ\r',cmdPurpose='Signal Strength')
                print(f"        Signal: {CCSignal}" )
                notConnected = False
                return

            CCSignal = self.write('AT+CSQ\r')
            print(f'            Cant Connect Signal: {CCSignal}')
            # self.write("AT+IPR=115200\r") 
            print('             Changing Baud Rate to        9600')
            self.uart = UART(self.uart_num,9600,tx=self.tx,rx=self.rx)
            time.sleep(1)
            self.write('AT+CREG=1\r', cmdPurpose='Forcing to Connect')
            print('     Trying Again')
        print('     Connected')
        if notConnected:
            return False
        return True


    def sendSMS(self,message="messageTemplate",number=639568543802): #working now
        sending = True
        st = time.time()
        while sending:
            if time.time() - st > 60:
                print('Cant Check Connection')
                return False        
            try:
                time.sleep(1)
                self.write("AT\r",cmdPurpose='refresh') # Hand Shake
                time.sleep(1)
                self.write("AT+CMGF=1\r", cmdPurpose='Text Mode') # Put to Text Mode
                self.record('sms.txt',f"{self.datetime()} - Sent - {message} \n") 
                time.sleep(1)
                # self.record('sms.txt',f"Sent - {message}") 
                # atd.write(f'AT+CMGS=\"+639765514253\"\r')
                # self.write("ATE0\r")
                time.sleep(1)
                self.write(f'AT+CMGS=\"+{number}\"\r')
                time.sleep(1)
                # self.write("ATE1\r")
                # self.uart.write(message)
                self.uart.write(message)
                time.sleep(1)
                response = self.uart.read()
                time.sleep(1)
                self.uart.write(bytes([26])) # stop the SIM Module for SMS
                time.sleep(1)
                response = self.uart.read()
                if 'ERROR' in response:
                    continue
                else: 
                    print('message Sent')
                    sending = False
                    break
                return True
            except Exception as e:
                print('Cant Send Message, Probably no Signal', e)
                print('     Trying again')
                self.checkConnection()
                # try:
                #     time.sleep(1)
                #     self.uart = UART(self.uart_num,baudrate= sim_baud,tx=self.tx,rx=self.rx)
                #     time.sleep(6)
                #     self.write(f'AT+CMGS=\"+{number}\"\r')
                #     time.sleep(1)
                #     self.uart.write(message)
                #     time.sleep(1)
                #     self.uart.read()
                #     time.sleep(1)
                #     self.uart.write(bytes([26])) # stop the SIM Module for SMS
                #     time.sleep(1)
                #     self.uart.read()
                #     time.sleep(1)
                #     print('Message Sent Second time')
                #     print('Trying again for second time:')
                # except Exception as e:
                #     print('really cant send message')
                # return False
    

    def lowPowerMode(self):
        print('         Low Power Mode      ')
        from time import sleep
        from machine import deepsleep, freq # type: ignore
        # freq(80000000)
        import esp32 # type: ignore
        self.write("AT+IPR=9600\r") # put the SIM MODULE BAUD Rate to 9600
        time.sleep(2) # wait to set the SIM module before changing to UART
        self.write("AT+IPR?\r")
        self.uart = UART(self.uart_num,9600,tx=self.tx,rx=self.rx)
        self.write("AT+CSCLK=2\r") # put the SIM MODULE To Sleep mode, change to 0 to wake
        try:
            esp32.ULP()
            esp32.raw_temperature() # READ TEMPERATUIRE IN FARENHEIGT
        except:
            print('Not esp32 ULP')
            pass

    def find_1st_2nd(self,string, substring):
        firstSubstring = string.find(substring)
        secondSubstring = string.find(substring, firstSubstring + 1)
        return [firstSubstring+1,secondSubstring]

    def datetime(self):
        datetime = True
        st = time.time()
        while datetime == True:
            if time.time() - st > 30:
                print('     Cant get sim.datetime')
                return False
            time.sleep(1)
            try:
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
            except:
                print('Fail Sim.datetime() maybe no power')
                print('     Trying again')
                self.checkConnection()



    def battery(self, logSheet='battery.txt'):
        batterylevel=self.write("AT+CBC\r")
        batterylevel = ''.join(filter(lambda i: i.isdigit(), batterylevel))
        batterylevel = int(int(batterylevel)/3778*100)
        timetoday = self.datetime()
        self.record(logSheet,f"{timetoday} - {batterylevel }% Battery Sim \n") 
        print(f' {self.log_run_times}  {timetoday}  - {int(batterylevel)}%')
        self.log_run_times+=1
        return f' {self.log_run_times}  {timetoday}  - {int(batterylevel)}%'

    
    def smsCommands(self):
        # self.write("AT+CNMI=2,2,0,0,0\r", cmdPurpose='Auto Show Message')
        self.write('AT+CMGL="ALL"\r\n', cmdPurpose="Check All all receive message")
        self.write('AT+CSMP=49,167,0,0\r\n', cmdPurpose="Ensure Auto Save Sent SMS")
        self.write('AT+CSMP=17,167,0,0\r\n', cmdPurpose="Ensure Auto Save Sent SMS")
        self.write('AT+CMGR=1\r\n', cmdPurpose="read 1 index sms")
        self.write("AT+CMGD=2,0\r\n", cmdPurpose="Delate index message 2, 0=only")
        self.write('AT+CMGL="STO SENT"\r\n', cmdPurpose="Check all Sent Mesasge")
        self.write('AT+CPMS?', cmdPurpose="Check How Many saved message 1/4 first digit number of sms and last digit upto ")
        self.wr('AT+CPMS?')        

    def receiveSMS(self, longer=False):
        try:
            self.write("AT+CMGF=1\r", cmdPurpose='Text Mode')
            self.write('AT+CPMS="SM","SM","SM"\r\n', cmdPurpose='Config Save  sms to sim')
            self.write('AT+CNMI=2,1,0,0,0\r\n', cmdPurpose='Ensure Auto SMS Storage to sim')
            response_str = None
            def checkSMS(timeout=5):
                global response_str
                response_str = None
                ncount = 0
                rcvsms = self.uart.read()
                while rcvsms == None and ncount < timeout:
                    ncount+=1
                    rcvsms = self.uart.read()
                    print('                     Checking SMS ',rcvsms ,ncount)
                    time.sleep(1)
                    if rcvsms != None:
                        break                    
                r = self.write('AT+CMGL="ALL"\r\n', cmdPurpose="Check All receive message")
                latest = None
                ls = r.split('\n')
                for l in ls:
                    if "REC UNREAD" in l:
                        print('Found New Message')
                        print('ID: ',l[7])
                        response_str = self.write(f'AT+CMGR={l[7]}\r')
                        break
                    elif l.startswith("+CMGL:"):
                        i = l.split(",")[0].split(':')[1].strip()
                        response_str = self.write(f'AT+CMGR={i}\r')
                        latest = i
                return response_str
            def deleteSMS():
                r = self.write('AT+CMGL="ALL"\r\n', cmdPurpose="Check All receive message")
                oldest = False
                latest = None
                ls = r.split('\n')
                for l in ls:
                    if l.startswith("+CMGL:"):
                        i = l.split(",")[0].split(':')[1].strip()
                        latest = i
                        if oldest == False:
                            oldest = i
                            self.write(f"AT+CMGD={oldest},0\r\n", cmdPurpose="del oldst sms")
                            print('Oldest Deleted')         
            
            response_str = checkSMS()
            if longer:
                if response_str == None:
                    print('Re Check the Sim with Longer Timeout')
                    response_str = checkSMS(10)
            time.sleep(0.5)
            if response_str == None:
                print('No New Message')
                return response_str
            parts = response_str.split(',')
            i = self.find_1st_2nd(parts[4],'\n')
            date_sms = parts[3].strip('"')
            time_sms = parts[4].split('"')[0]
            phone_number = parts[1].strip('"')
            message = parts[4][i[0]+1:i[1]-2]
            message = f'{message} - {phone_number} [ {date_sms} {time_sms} ]'

            self.record('sms.txt', toWriteData=f'[ {self.datetime()} ] - Receive -  {str(message)} ' )
            deleteSMS()

            self.checkTypeOfMessage(message)
            rcvsms = [f'{message} - {phone_number} [ {date_sms} {time_sms} ]',phone_number]
            print('Found SMS: ',rcvsms)
            self.processSMS(rcvsms)
            return rcvsms
        except Exception as e:
            print('Cant Receive SMS Error',e)
            return None
    def processSMS(self,sms=None):
        if sms == None:
            print('No New Command')
        else:
            print('New Command: ',sms)
            sms  = sms[0].lower().split()
            # if "feed" in sms[0]:
            #     # 'feed 3'  Sample message
            #     print('Requesting to feed', sms)
            #     self.feed = Feeder()
            #     for i in range(int(sms[1])):
            #         print(f'Feeding in {i+1}/{sms[1]}')
            #         self.feed.go
            #         time.sleep(0.5)
            # if "mode" in sms[0]:
                # 'mode session'
                # 'mode toss'
            print(f'checking mode {sms[1]}')
            try:
                from settings import Settings
                setting = Settings(sms[0],sms[1])
                setting.change()
            except Exception as e:
                print('Error Changing Mode: ',e)
            for i in range(5):
                print(f'sengind message in {i-5}')
                time.sleep(1)
            self.sim.sendSMS(message=f'Changed {sms[0]} to {self.mode.change(sms[1])}',  number=sms[1][1:])
            if "check" in sms[0]:
                # 'check battery'
                if 'battery' in sms[1]:
                    b= self.battery.record
                    print(b)
            print(f"Create a Func that will create a Command\n       {sms}")



    def checkTypeOfMessage(self,messageReceived):
        try:
            n = messageReceived.split(" ", 1) # Check if has commands
            self.record('command.txt',n)
            # self.commands[n[0]](n[1]) #Execute
            self.commands[n[0]](*n[1]) # Execute
        except Exception as e:
            print('No Command Found')
            return messageReceived
        print('Commanded: ',messageReceived)
        return messageReceived
  
  

    def record(self , fileName='record.txt',toWriteData=''):
        # TODO INSERT A COMMAND TODO FOR THE CONTROLLER AFTER MESSAGE IS RECEIVED
        print(f'record         {fileName}           {toWriteData}')
        with open(fileName , "a") as myfile:
            myfile.write(toWriteData+'\n')
            myfile.flush()
            myfile.close()

    def write(self,cmd,cmdPurpose='Command'):
        self.uart.write("AT\r") # Hand Shake
        time.sleep(0.5)
        # print(f"            {cmdPurpose}  :  {cmd}")
        message=None
        timeout=0
        while message == None and timeout!=8:
            self.uart.write(cmd)
            time.sleep(0.5)
            message = self.uart.read()
            # print(',',end='')
            timeout+=1
            while timeout%2 != 0 and message==None:
                time.sleep(0.5)
                # print(".",end="")
                timeout+=1
                message = self.uart.read()
        if message == None:
            message = 'TimeOUT'
        else:
            message = message.decode('utf-8').rstrip()
        return message
    def wr(self,cmd,cmdPurpose='Command'):
        self.uart.write("AT\r") # Hand Shake
        time.sleep(0.5)
        # print(f"            {cmdPurpose}  :  {cmd}")
        message=None
        timeout=0
        while message == None and timeout!=8:
            self.uart.write(cmd+'\r\n')
            time.sleep(0.5)
            message = self.uart.read()
            # print(',',end='')
            timeout+=1
            while timeout%2 != 0 and message==None:
                time.sleep(0.5)
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
