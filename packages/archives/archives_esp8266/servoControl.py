
from machine import Pin, PWM
import machine
from time import sleep
from configs.configs import servoPin
# Set up PWM Pin for servo control
servo_pin = machine.Pin(servoPin)
servo = PWM(servo_pin)
# Set Duty Cycle for Different Angles
max_duty = 7864
min_duty = 1802
half_duty = int(max_duty/2)
#Set PWM frequency
frequency = 50
servo.freq (frequency)

def runServo(times=1):
    for i in range(int(times)):
        x = 500
        while x <=4000:
            x+=30
            servo.duty_u16(x)
            print(x)
            sleep(0.01)
        sleep(5)
    servo.deinit()
    led = Pin(2, Pin.OUT)
    led.value(1)
    return 'Motor Run Successfully'


