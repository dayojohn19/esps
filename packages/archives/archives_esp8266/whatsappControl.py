try:
    import requests
except:
    import urequests as requests
phoneNumber = '639765514253'
api_key = '2890524'

def send_message(phone_number=phoneNumber, api_key=api_key, message='Default SMS'):
    try:
        import re
        pattern = r" "
        message = re.sub(pattern, "%20", message)
  #set your host URL
        url = f'https://api.callmebot.com/whatsapp.php?phone=+{phoneNumber}&text={message}&apikey={api_key}'
        response = requests.get(url)
        # response = requests.get(url, timeout=3)
        if response.status_code == 200:
            print('Success! Send message')
        else:
            print('Error')
            print(response.text)
    except Exception as e:
        print("Sending Error : ",e)

