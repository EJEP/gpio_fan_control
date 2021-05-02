import datetime
import time
from collections import deque
from statistics import mean
import sqlite3
from pyGPIO.gpio import gpio, port
from w1thermsensor import W1ThermSensor, W1ThermSensorError
import software_pwm
import config


class fan_control():

    def __init__(self, pwm_pin):
        self.pwm_pin = pwm_pin
        self.current_duty_cycle = 100
        self.prev_temps = {
            'cpu_1_min': deque(maxlen=6),
            'cpu_5_min': deque(maxlen=30),
            'cpu_10_min': deque(maxlen=60),
            'ds_1_min': deque(maxlen=6),
            'ds_5_min': deque(maxlen=30),
            'ds_10_min': deque(maxlen=60),
        }
        self.moving_avg_temp = {
            'cpu_1_min': None,
            'ds_1_min': None,
            'cpu_5_min': None,
            'ds_5_min': None,
            'cpu_10_min': None,
            'ds_10_min': None,
        }

    def get_temps(self):
        """Get temp from cpu. Logic with DS18B20 to follow"""

        with open(config.cpu_temp_file) as temp_file:
            cpu_temp = int(temp_file.read()) / 1000

        self.prev_temps['cpu_1_min'].append(cpu_temp)
        self.prev_temps['cpu_5_min'].append(cpu_temp)
        self.prev_temps['cpu_10_min'].append(cpu_temp)

        sensor = W1ThermSensor()
        try:
            ds_temp = sensor.get_temperature()
            self.prev_temps['ds_1_min'].append(ds_temp)
            self.prev_temps['ds_5_min'].append(ds_temp)
            self.prev_temps['ds_10_min'].append(ds_temp)
        except W1ThermSensorError:
            # Really want to log what happened somewhere...
            pass

    def log_status(self, duty_cycle_to_set):
        conn = sqlite3.connect(config.database_file)
        curs = conn.cursor()

        time_now = datetime.datetime.today()
        curs.execute('INSERT INTO temp_and_speed values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
                     (time_now,
                      self.prev_temps['cpu_1_min'][-1],
                      self.prev_temps['ds_1_min'][-1],
                      self.prev_temps['cpu_1_min'],
                      self.prev_temps['cpu_5_min'],
                      self.prev_temps['cpu_10_min'],
                      self.prev_temps['ds_1_min'],
                      self.prev_temps['ds_5_min'],
                      self.prev_temps['ds_10_min'],
                      100-self.current_duty_cycle,
                      100-duty_cycle_to_set
                      )
                     )

        conn.commit()
        conn.close()

    def calc_duty_cycle(self):
        """Calculate duty cycle as percentage of full speed. Remember that
        the duty cycle is inverted for the fan, so return 100 - calculated
        cycle.
        """

        levels = [20, 50, 100]
        threshold = 10

        for key, temps in self.prev_temps.items():
            self.moving_avg_temp[key] = \
                mean(temps)

        if (self.moving_avg_temp['cpu_1_min'] < 60 - threshold
            and self.moving_avg_temp['ds_1_min'] < 40 - threshold):
            duty_cycle = levels[0]
        elif (self.moving_avg_temp['cpu_1_min'] > 60
              or self.moving_avg_temp['ds_1_min'] > 40):
            duty_cycle = levels[1]
        elif (self.moving_avg_temp['cpu_1_min'] < 80 - threshold
              and self.moving_avg_temp['ds_1_min'] < 60 - threshold):
            duty_cycle = levels[1]
        elif (self.moving_avg_temp['cpu_1_min'] > 80
              or self.moving_avg_temp['ds_1_min']) > 60:
            duty_cycle = levels[2]

        duty_cycle_to_set = 100 - duty_cycle

        self.log_status(duty_cycle_to_set)

        return duty_cycle_to_set

    def run_fan_control(self):
        gpio.init()
        gpio.setcfg(self.pwm_pin, 1)
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
