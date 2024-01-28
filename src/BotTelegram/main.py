import firebase_admin
from firebase_admin import credentials
from modules.bot_telegram import BotTelegram
from modules.api import API

class Main:

    __URL_FIREBASE = ""
    __PATH_CERTIFICATE = ""
    __TOKEN = ""


    def __init__(self):
        self.__config_firebase()
        self.__bot = BotTelegram(self.__TOKEN)
        self.__bot.turn_on()

        self.__api = API(self.__bot)
        self.__api.run()


    def __config_firebase(self):
        credential = credentials.Certificate(self.__PATH_CERTIFICATE)
        firebase_admin.initialize_app(credential, {
            "databaseURL": self.__URL_FIREBASE
        })


Main()
