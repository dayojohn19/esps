from lcd_writer import lcd1602

lcd_scl,lcd_sda,lcd_contrast
lcd = lcd1602(lcd_scl=lcd_scl,lcd_sda=lcd_sda,lcd_contrast=lcd_contrast)

lcd.pwm.freq(int(lv/3))
lcd.pwm.duty(int(lv/5))


lcd.lcd.move_to(0,0)
lcd.lcd.putstr(str(tof_d))
lcd.icon("distance")
lcd.lcd.putstr(" ")
lcd.icon("light")


lcd.lcd.move_to(0,1)

lcd.icon('water')
lcd.lcd.putstr(" ")
lcd.icon('degree')
lcd.lcd.putstr(" ")
lcd.icon('heading')
lcd.lcd.putstr(" ")