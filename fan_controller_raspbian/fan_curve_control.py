import datetime
import RPi.GPIO as GPIO
import time
from w1thermsensor import W1ThermSensor, W1ThermSensorError
import sqlite3
import software_pwm
import config


class fan_control():

    def __init__(self, pwm_pin):
        self.pwm_pin = pwm_pin
        self.current_duty_cycle = 100
        self.cpu_temp = None
        self.ds_temp = None

    def get_temps(self):
        """Get temp from cpu. Logic with DS18B20 to follow"""

        with open(config.cpu_temp_file) as temp_file:
            cpu_temp = int(temp_file.read()) / 1000
            print('cpu temp is {}'.format(cpu_temp))

        self.cpu_temp = cpu_temp

        sensor = W1ThermSensor()
        try:
            self.ds_temp = sensor.get_temperature()
            print('sensor temp is {}'.format(self.ds_temp))
        except W1ThermSensorError:
            # Really want to log what happened somewhere...
            pass

    def log_status(self, duty_cycle_to_set):
        conn = sqlite3.connect(config.database_file)
        curs = conn.cursor()

        print('current duty cycle is {}'.format(self.current_duty_cycle))
        print('duty cycle to set is {}'.format(duty_cycle_to_set))
        time_now = datetime.datetime.today()
        curs.execute('INSERT INTO temp_and_speed values(?, ?, ?, ?, ?)',
                     (time_now, self.cpu_temp, self.ds_temp,
                      100-self.current_duty_cycle, 100-duty_cycle_to_set))

        conn.commit()
        conn.close()

    def calc_duty_cycle(self):
        """Calculcate duty cycle as percentage of full speed. Remember that the
        duty cycle is inverted for the fan, so return 100 - calculated
        cycle."""

        levels = [20, 50, 100]
        threshold = 10
        if self.cpu_temp < 60 - threshold and self.ds_temp < 40 - threshold:
            duty_cycle = levels[0]
        elif self.cpu_temp > 60 or self.ds_temp > 40:
            duty_cycle = levels[1]
        elif self.cpu_temp < 80 - threshold and self.ds_temp < 60 - threshold:
            duty_cycle = levels[1]
        elif self.cpu_temp > 80 or self.ds_temp > 60:
            duty_cycle = levels[2]

        duty_cycle_to_set = 100 - duty_cycle

        self.log_status(duty_cycle_to_set)

        return duty_cycle_to_set

    def run_fan_control(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pwm_pin, GPIO.OUT)
        # Get our PWM object
        pwm = software_pwm.PWM(self.pwm_pin, 25000)

        pwm.start_pwm()

        while True:
            # get temp
            self.get_temps()

            # decide duty cycle
            duty_cycle_to_set = self.calc_duty_cycle()

            # set duty cycle
            pwm.set_duty_cycle(duty_cycle_to_set)
            self.current_duty_cycle = duty_cycle_to_set

            # probably sleep rather than run as fast as possible forever
            time.sleep(10)


def main():
    control = fan_control(config.fan_control_pin)
    control.run_fan_control()


if __name__ == "__main__":
    main()
