import machine
from time import sleep
class LEDSignal:
    def __init__(self, pin=2):
        self.led = machine.Pin(pin, machine.Pin.OUT)
        self.timer = None

    def blink_led(self, timer):
        self.led.value(not self.led.value())

    def start_blinking(self, speed=500):
        if self.timer is None:
            self.timer = machine.Timer(0)
            self.timer.init(period=speed, mode=machine.Timer.PERIODIC, callback=self.blink_led)

    def stop_blinking(self):
        if self.timer is not None:
            self.timer.deinit()
            self.timer = None
            self.led.value(1)

# Example usage
if __name__ == "__main__":
    led_signal = LEDSignal(pin=2)
    print('Led working')
    led_signal.start_blinking(speed=100) 
    sleep(2)
    led_signal.stop_blinking()