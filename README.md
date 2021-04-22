This repository contains code to control a Noctua PWM fan with GPIO pins, based on the CPU and ambient temperatures.

# GPIO Fan Control

## Hardware

Using Noctua 5V PWM fan. Note that the circuit diagram Noctua provides as an example for driving the PWM fan is incorrect. It should be a standard CMOS inverter circuit.

Pinout for Orange Pi Plus 2 is here: https://www.meccanismocomplesso.org/en/a-look-back-at-the-orange-pi-plus-2-board/

## Software

The code for Armbian uses [pyGPIO](https://forum.armbian.com/topic/5662-pygpio-a-more-general-python-gpio-library/), which is not available in `pip`. Install as follows:

```
sudo apt-get install python-dev
git clone https://github.com/chwe17/pyGPIO.git
cd pyGPIO
sudo python setup.py install
```

`fan_curve_control.py` controls the fan speed, and requires a config file setting:

+ Which pin to use for the PWM signal
+ The location of a database to log the temperatures and fan duty cycle
+ The file containing the cpu temperature

The controller sets the fan speed to run at one of three possible speeds.

# Monitoring

Also included is a dockerised flask web app to display a graph showing measured temperatures and the duty cycle of the fan. The `docker-compose.yml` file requires two variables to be set in a `.env` file:

+ The secret key for the web app
+ The location of the database with the temperature and duty cycle information

The secret key is passed to the flask app in the container as an environment variable.
