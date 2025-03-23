from machine import RTC
import time
def textWriter(fileName=None, toWrite=None):
    try:
        with open(fileName, "a") as myfile:
            myfile.write(f"\n[ {RTC().datetime()} ]     {toWrite}")
            myfile.flush()
        print(f"Log written successfully:\n      {fileName}  ---  {toWrite}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error while writing to log: {e}")      
