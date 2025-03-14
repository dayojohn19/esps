# from time import sleep_ms, ticks_ms 
from machine import I2C, Pin ,PWM
from lcd_i2c import I2cLcd 

# Here to make icons, settings: hex, i2c
# https://maxpromer.github.io/LCD-Character-Creator/

class lcd1602:
  def __init__ (self, lcd_scl, lcd_sda ,lcd_contrast):
    import time

    lcd_i2c = I2C(scl=Pin(lcd_scl), sda=Pin(lcd_sda) ) 
    self.contrast = Pin(lcd_contrast, Pin.OUT)  
    self.pwm = PWM(lcd_contrast)
    self.pwm.freq()
    self.pwm.duty()

    DEFAULT_I2C_ADDR = 0x27
    self.lcd = I2cLcd(lcd_i2c, DEFAULT_I2C_ADDR, 2, 16)
    self.lcd.clear()
    self.lcd.backlight_on()
    time.sleep(1.5)
    self.lcd.blink_cursor_off()
    self.iconlist = {
      'degree' : [0,[0x07,0x05,0x07,0x00,0x00,0x00,0x00,0x00]],
      'heart' : [1,[0x00,0x00,0x0A,0x15,0x11,0x0A,0x04,0x00]],
      'water': [2,[0x04,0x0E,0x1D,0x1F,0x1F,0x0E,0x00,0x00]],
      'heading':[3,[0x04,0x0E,0x1F,0x1F,0x04,0x04,0x04,0x04]],
      'distance':[4,[0x07,0x03,0x05,0x04,0x04,0x14,0x18,0x1C]],
      'light':[5,[0x04,0x11,0x04,0x0E,0x04,0x11,0x04,0x00]]
    }

  def greeting(self):
    import utime
    self.lcd.clear()
    self.lcd.move_to(5,0)
    self.lcd.putstr("Welcome")
    self.lcd.move_to(1,1)
    self.lcd.putstr("To HAHA DAYOMEN")
    utime.sleep(2)
    self.lcd.clear()
    self.lcd.custom_char(2, bytearray([0x00,0x00,0x0A,0x00,0x15,0x11,0x0E,0x00]))

  def icon(self,icon_name):
    icon = self.iconlist[icon_name]
    self.lcd.custom_char(icon[0], icon[1])
    self.lcd.putchar(chr(icon[0]))
    
  def scroll_text(self, text,line=0, max_length=16, speed=0.5):
    import time
    self.lcd.clear()
    words = text.split()  
    full_text = ' '.join(words)
    if len(text)>16:
      while True:
          for i in range(len(full_text) - max_length + 1):
              scroll_window = full_text[i:i + max_length]
              self.lcd.clear()
              self.lcd.move_to(0, line)
              self.lcd.putstr(scroll_window)
              time.sleep(speed)
          time.sleep(1)  
    else:
      self.lcd.putstr(text)
      

