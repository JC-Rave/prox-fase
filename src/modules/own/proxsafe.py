import utime
import _thread
import ufirebase as firebase
from machine import Pin, PWM
from hcsr04 import HCSR04

class ProxSafe:

    __MINIMAL_DISTANCE = 100
    __WORK_CYCLE = 1023
    __FREQUENCY = 261


    def __init__(self, bot_telegram):
        self.__bot_telegram = bot_telegram
        self.__front_sensor = HCSR04(trigger_pin=27, echo_pin=26)
        self.__right_sensor = HCSR04(trigger_pin=33, echo_pin=32)
        self.__rear_sensor = HCSR04(trigger_pin=5, echo_pin=17)
        self.__left_sensor = HCSR04(trigger_pin=23, echo_pin=22)
        self.__buzzer_sensor = PWM(Pin(21))
        self.__buzzer_sensor.duty(0)


    def run(self):
        self.__proximity_data_list = []
        _thread.start_new_thread(self.__insert_proximity_data, ())

        while True:
            front_distance = self.__front_sensor.distance_cm()
            right_distance = self.__right_sensor.distance_cm()
            rear_distance = self.__rear_sensor.distance_cm()
            left_distance = self.__left_sensor.distance_cm()

            if front_distance <= self.__MINIMAL_DISTANCE or right_distance <= self.__MINIMAL_DISTANCE or \
            rear_distance <= self.__MINIMAL_DISTANCE or left_distance <= self.__MINIMAL_DISTANCE:
                print("Object detected, activating alarm...")
                self.__buzzer_sensor.freq(self.__FREQUENCY)
                self.__buzzer_sensor.duty(self.__WORK_CYCLE)

                print("Procesing data...")
                datetime = self.__get_date_time()
                data = {
                    "date": datetime["date"],
                    "time": datetime["time"],
                    "crash_occurred": self.__is_crash_occurred(front_distance, right_distance, rear_distance, left_distance),
                    "side": self.__get_occurrence_side(front_distance, right_distance, rear_distance, left_distance)
                }

                self.__proximity_data_list.append(data)
                print(f"Processed data: {data}\n")
            else:
                self.__buzzer_sensor.duty(0)

            utime.sleep(1)


    def __insert_proximity_data(self):
        while True:
            utime.sleep(5)

            if len(self.__proximity_data_list):
                proximity_data_list = self.__proximity_data_list.copy()
                self.__proximity_data_list.clear()

                for data in proximity_data_list:
                    print("Recording data...")
                    firebase.put(f"proximity_data/{data["date"]} {data["time"]}", data, bg=0)
                    print(f"Recorded data: {data}\n")


    def __get_date_time(self):
        now = utime.localtime()
        return {
            "date": f"{now[0]}-{now[1]:02d}-{now[2]:02d}",
            "time": f"{now[3]:02d}:{now[4]:02d}:{now[5]:02d}"
        }


    def __is_crash_occurred(self, front_distance, right_distance, rear_distance, left_distance):
        return front_distance <= 5 or right_distance <= 5 or rear_distance <= 5 or left_distance <= 5


    def __get_occurrence_side(self, front_distance, right_distance, rear_distance, left_distance):
        if front_distance <= self.__MINIMAL_DISTANCE:
            return "Delantero"
        elif right_distance <= self.__MINIMAL_DISTANCE:
            return "Derecha"
        elif rear_distance <= self.__MINIMAL_DISTANCE:
            return "Trasero"
        elif left_distance <= self.__MINIMAL_DISTANCE:
            return "Izquierda"
        else:
            return "Desconocido"

