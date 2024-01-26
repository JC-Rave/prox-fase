import network
import urequests
import utime
import _thread
import ufirebase as firebase
from machine import RTC
from bot_telegram import BotTelegram
from proxsafe import ProxSafe

class Main:

    __URL_DATETIME = "http://worldtimeapi.org/api/timezone/America/Bogota"
    __URL_FIREBASE = "My_firebase"
    __TOKEN = "my_token"


    def __init__(self, ssid, password):
        self.__connect_to_network(ssid, password)
        self.__config_firebase()
        _thread.start_new_thread(self.__synchronize_rtc, ())

        self.__bot_telegram = BotTelegram(self.__TOKEN)
        self.__bot_telegram.turn_on()

        self.__prox_safe = ProxSafe(self.__bot_telegram)
        self.__prox_safe.run()


    def __connect_to_network(self, ssid, password):
        self.__network = network.WLAN(network.STA_IF)

        if not self.__network.isconnected():         #Si no está conectado…
            self.__network.active(True)              #activa la interface
            self.__network.connect(ssid, password)   #Intenta conectar con la red
            print(f"Connecting to the '{ssid}' network...")

            timeout = utime.time()
            while not self.__network.isconnected():  #Mientras no se conecte..
                if (utime.ticks_diff(utime.time(), timeout) > 10):
                    self.__network.active(False)
                    raise Exception(f"Could not connect to '{ssid}' network")
            else:
                print(f"Connected to the '{ssid}' network")
                print("Network data (IP/netmask/gw/DNS):", self.__network.ifconfig())


    def __synchronize_rtc(self):
        rtc = RTC()

        while True:
            print("Synchronizing RTC")
            response = urequests.get(self.__URL_DATETIME)

            if response.status_code == 200:
                print("Response:", response.text)
                json_data = response.json()

                datetime = str(json_data["datetime"])
                year = int(datetime[0:4])
                month = int(datetime[5:7])
                day = int(datetime[8:10])
                hour = int(datetime[11:13])
                minutes = int(datetime[14:16])
                seconds = int(datetime[17:19])
                microseconds = int(round(int(datetime[20:26]) / 10000))
                day_of_week = int(json_data["day_of_week"])

                rtc.datetime((year, month, day, day_of_week, hour, minutes, seconds, microseconds))
                print("Synchronized RTC")
                print("Current date and time: {0:02d}-{1:02d}-{2:02d} {4:02d}:{5:02d}:{6:02d}".format(*rtc.datetime()))

            utime.sleep(600)


    def __config_firebase(self):
        firebase.setURL(self.__URL_FIREBASE)


Main("my_red", "my_password")
