from machine import Pin, PWM
from hcsr04 import HCSR04

MINIMAL_DISTANCE = 100
WORK_CYCLE = 1023
FREQUENCY = 261

north_sensor = HCSR04(trigger_pin=27, echo_pin=26)
south_sensor = HCSR04(trigger_pin=33, echo_pin=32)
east_sensor = HCSR04(trigger_pin=5, echo_pin=17)
west_sensor = HCSR04(trigger_pin=23, echo_pin=22)
buzzer_sensor = PWM(Pin(4))
buzzer_sensor.duty(0)

while True:
    north = north_sensor.distance_cm()
    south = south_sensor.distance_cm()
    east = east_sensor.distance_cm()
    west = west_sensor.distance_cm()

    if north <= MINIMAL_DISTANCE or south <= MINIMAL_DISTANCE or \
       east <= MINIMAL_DISTANCE or west <= MINIMAL_DISTANCE:
        buzzer_sensor.freq(FREQUENCY)
        buzzer_sensor.duty(WORK_CYCLE)
    else:
        buzzer_sensor.duty(0)
