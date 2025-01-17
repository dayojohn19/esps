import machine
timer = None
led = machine.Pin(2, machine.Pin.OUT)
def blink_led(timer):
    led.value(not led.value()) 

def start_blinking(speed=500):
    global timer
    if timer is None: 
        timer = machine.Timer(0)
        timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=blink_led)
def stop_blinking():
    global timer
    if timer is not None:
        timer.deinit() 
        timer = None 
        led.value(1)

