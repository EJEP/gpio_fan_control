import time
import threading
from pyGPIO.gpio import gpio


class PWM():

    def __init__(self, pin, frequency):
        """Assumes GPIO.setmode has been run already"""
        self.cycle_time = 1.0 / frequency
        self.frequency = frequency
        self.duty_cycle = 100.0
        self.pin = pin
        self.thread = None
        self.to_stop = False
        self.stopped_pwm = False

    def start_pwm(self):

        self.thread = threading.Thread(None, target=self.do_pwm)
        self.thread.start()

    def do_pwm(self):
        while self.to_stop is False:
            if self.duty_cycle > 0:
                # 1 is high
                gpio.output(self.pin, 1)
                time.sleep(self.cycle_time * self.duty_cycle / 100)

            if self.duty_cycle < 100:
                # 0 is low
                gpio.output(self.pin, 0)
                time.sleep(self.cycle_time * (100 - self.duty_cycle) / 100)

        self.stopped_pwm = True

    def set_duty_cycle(self, duty_cycle):
        self.duty_cycle = duty_cycle

    def stop_pwm(self):
        self.to_stop = True
        while not self.stopped_pwm:
            time.sleep(0.01)
        self.thread.join()
