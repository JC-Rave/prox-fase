from machine import Pin, PWM
from hcsr04 import HCSR04

class ProxSafe:

    __MINIMAL_DISTANCE = 100
    __WORK_CYCLE = 1023
    __FREQUENCY = 261


    def __init__(self):
        self.__north_sensor = HCSR04(trigger_pin=27, echo_pin=26)
        self.__south_sensor = HCSR04(trigger_pin=33, echo_pin=32)
        self.__east_sensor = HCSR04(trigger_pin=5, echo_pin=17)
        self.__west_sensor = HCSR04(trigger_pin=23, echo_pin=22)
        self.__buzzer_sensor = PWM(Pin(4))
        self.__buzzer_sensor.duty(0)


    def run(self):
        while True:
            north_distance = self.__north_sensor.distance_cm()
            south_distance = self.__south_sensor.distance_cm()
            east_distance = self.__east_sensor.distance_cm()
            west_distance = self.__west_sensor.distance_cm()

            if north_distance <= self.__MINIMAL_DISTANCE or south_distance <= self.__MINIMAL_DISTANCE or \
            east_distance <= self.__MINIMAL_DISTANCE or west_distance <= self.__MINIMAL_DISTANCE:
                self.__buzzer_sensor.freq(self.__FREQUENCY)
                self.__buzzer_sensor.duty(self.__WORK_CYCLE)
            else:
                self.__buzzer_sensor.duty(0)

