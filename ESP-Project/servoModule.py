
from machine import Pin, PWM

import machine
from time import sleep
from configs.configs import feederpin
servo_pin = machine.Pin(feederpin)

# # servoPin = 5 
# # Set up PWM Pin for servo control
servo = PWM(servo_pin)
# # Set Duty Cycle for Different Angles
# max_duty = 7864
# min_duty = 1802
# half_duty = int(max_duty/2)
# #Set PWM frequency
# frequency = 50
# servo.freq (frequency)

def runServo(times=1):
    for i in range(int(times)):
        x = 500
        while x <=4000: 
            x+=30
            servo.duty_u16(x)
            print(x)
            sleep(0.01)
    servo.duty_u16(0)
    # servo.deinit()
    return 'Motor Run Successfully'


def feedRun():
    for i in range(1023):
        print(i)
        sleep(0.01)
        servo.duty(i)
    sleep(0.1)
    servo.duty_u16(0)


class feedRun2():
    def __init__(self):
        self.servo_pin = machine.Pin(feederpin)
        self.servo = PWM(servo_pin)
        self.servo.freq(50)
        self.backwward = 23
        self.stop = 0
        self.forward = 110
        self.slowforward = 90
    def back(self):
        sleep(0.01)
        for s in range(10):
            sleep(0.1)
            self.servo.duty(self.backwward)
            sleep(0.1)
            self.servo.duty(self.stop)
            sleep(0.1)
            print(s)
    def stop(self):
        self.servo.duty_u16(0)
    def go(self, initFeed= 30):
        print(' \n  Starting Feeding')
        print('First Feed for first comer')
        sleep(0.01)
        self.servo.duty(self.forward)
        sleep(2)
        self.servo.duty(self.slowforward)
        print('     End')
        sleep(2)
        for i in range(initFeed):
            print(f'Initial Feeding in {i+1}/{initFeed}')
            sleep(0.4)
            self.servo.duty(self.forward)
            sleep(0.05)
            self.servo.duty_u16(self.stop)
            sleep(0.4)
        sleep(0.1)
        self.servo.duty_u16(0)
feeder = feedRun2()





class Servo:
    __servo_pwm_freq = 50
    __min_u10_duty = 26 - 0 # offset for correction
    __max_u10_duty = 123- 0  # offset for correction
    min_angle = 50
    max_angle = 300
    current_angle = 0.001
    def __init__(self, pin):
        self.__initialise(pin)
    def update_settings(self, servo_pwm_freq, min_u10_duty, max_u10_duty, min_angle, max_angle, pin):
        self.__servo_pwm_freq = servo_pwm_freq
        self.__min_u10_duty = min_u10_duty
        self.__max_u10_duty = max_u10_duty
        self.min_angle = min_angle
        self.max_angle = max_angle
        self.__initialise(pin)
    def move(self, angle):
        # round to 2 decimal places, so we have a chance of reducing unwanted servo adjustments
        angle = round(angle, 2)
        # do we need to move?
        if angle == self.current_angle:
            return
        self.current_angle = angle
        # calculate the new duty cycle and move the motor
        duty_u10 = self.__angle_to_u10_duty(angle)
        self.__motor.duty(duty_u10)
    def __angle_to_u10_duty(self, angle):
        return int((angle - self.min_angle) * self.__angle_conversion_factor) + self.__min_u10_duty
    def __initialise(self, pin):
        self.current_angle = -0.001
        self.__angle_conversion_factor = (self.__max_u10_duty - self.__min_u10_duty) / (self.max_angle - self.min_angle)
        self.__motor = PWM(Pin(pin))
        self.__motor.freq(self.__servo_pwm_freq)




