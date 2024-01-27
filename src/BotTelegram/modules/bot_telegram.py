import threading
import requests
import json
import modules.graphics as graphics
from firebase_admin import db
from time import sleep

class BotTelegram:

    STATUS_SAPCS_ON = "ON"
    STATUS_SAPCS_OFF = "OFF"


    def __init__(self, token):
        self.__base_url = f"https://api.telegram.org/bot{token}/"
        self.__last_update = 0
        self.__sapcs = self.STATUS_SAPCS_OFF  # Flag para menejar estado del sistema de alerta de proximidad
        self.__status_update = False

        self.__build_keyboard_buttons()
        self.__build_command_handlers()
        self.__build_message_handlers()


    def __build_keyboard_buttons(self):
        self.__turn_on = "Encender SAPCS"
        self.__turn_off = "Apagar SAPCS"
        self.__status = "Estado SAPCS"
        self.__graph_alert = "Ver gráficas de alerta"


    def __build_command_handlers(self):
        self.__command_handlers = {
            "/start": self.__new_chat
        }


    def __build_message_handlers(self):
        self.__message_handlers = {
            self.__turn_on: self.__on_sapcs,
            self.__turn_off: self.__off_sapcs,
            self.__status: self.__status_sapcs,
            self.__graph_alert: self.__build_alert_graphics
        }


    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = self.__base_url + f"sendMessage?chat_id={chat_id}&text={text}&parse_mode=Markdown"
            if reply_markup:
                url += f"&reply_markup={json.dumps(reply_markup)}"

            response = requests.get(url)
            response.close()
        except Exception as ex:
            print("Unsent message:", ex)


    def send_photos(self, chat_id, photo_list):
        try:
            url = self.__base_url + "sendPhoto"

            for photo_path in photo_list:
                with open(photo_path, "rb") as photo:
                    files = {"photo": photo}
                    data = {"chat_id": chat_id}
                    response = requests.post(url, files=files, data=data)
                    response.raise_for_status()

            print("Photos sent correctly")
        except Exception as ex:
            print("Photos could not be sent:", ex)


    def get_sapcs_status(self):
        return self.__sapcs


    def is_status_update(self):
        return self.__status_update


    def set_status_update(self, status_update):
        self.__status_update = status_update


    def turn_on(self):
        def __loop():
            while True:
                updates = self.__get_updates()

                for update in updates:
                    self.__handle_update(update)

        thread = threading.Thread(target=__loop, args=())
        thread.start()


    def __get_updates(self):
        request_body = {
            "offset": self.__last_update + 1,
            "timeout": 5,
            "allowed_updates": ["message"]
        }

        try:
            url = self.__base_url + "getUpdates"
            response = requests.post(url, json=request_body)

            data = response.json()
            response.close()

            return data["result"] if data["ok"] else []
        except Exception as ex:
            print("Error getting bot update:", ex)
            return []


    def __handle_update(self, update):
        self.__last_update = update["update_id"]
        text = update["message"]["text"]
        chat_id = update["message"]["chat"]["id"]

        if text in self.__command_handlers:
            self.__command_handlers[text](chat_id)

        elif text in self.__message_handlers:
            self.__message_handlers[text](chat_id)

        else:
            self.__handler_not_foud(chat_id)


    def __new_chat(self, chat_id):
        print("Init new chat")

        text = "¡Hola!👋👋👋"
        text += "%0ASoy 🤖ProxSafe🤖, "
        text += "tú sistema de 🚨alerta📢 "
        text += "para conducción🚗 segura🛡️"
        text += "%0A%0A🤔¿En qué te puedo ayudar?🤔"

        reply_markup = {
            "keyboard": [
                [self.__turn_on, self.__status, self.__turn_off],
                [self.__graph_alert]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        self.send_message(chat_id, text, reply_markup)


    def __on_sapcs(self, chat_id):
        if self.__sapcs == self.STATUS_SAPCS_OFF:
            print("Turning on the SAPCS")
            self.__sapcs = self.STATUS_SAPCS_ON
            self.__status_update = True
            text = "SAPCS Encendido🟢 con exito😀👌"
        else:
            print("SAPCS is already on")
            text = "SAPCS ya se encuentra encendido✅"

        reply_markup = {
            "keyboard": [
                [self.__status, self.__graph_alert],
                [self.__turn_off, self.__turn_on]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        sleep(1)
        self.send_message(chat_id, text, reply_markup)


    def __off_sapcs(self, chat_id):
        if self.__sapcs == self.STATUS_SAPCS_ON:
            print("Turning off the SAPCS")
            self.__sapcs = self.STATUS_SAPCS_OFF
            self.__status_update = True
            text = "SAPCS Apagado🔴 con exito☹️"
        else:
            print("SAPCS is already turned off")
            text = "SAPCS ya se encuentra apagado❌"

        reply_markup = {
            "keyboard": [
                [self.__status, self.__graph_alert],
                [self.__turn_on, self.__turn_off]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        sleep(1)
        self.send_message(chat_id, text, reply_markup)


    def __status_sapcs(self, chat_id):
        print("Check SAPCS status")

        if self.__sapcs == self.STATUS_SAPCS_ON:
            text = "SAPCS se encuentra encendido✅ y funcionando correctamente😎"
        else:
            text = "SAPCS se encuentra apagado‼️"
            text += "%0ANo podré enviar alertas🚨 en caso de una emergencia😰😰"

        reply_markup = {
            "keyboard": [
                [self.__turn_on, self.__turn_off],
                [self.__graph_alert, self.__status]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        print("SAPCS status is:", self.__sapcs)
        self.send_message(chat_id, text, reply_markup)

    def __build_alert_graphics(self, chat_id):
        print("Building alert graphics...")

        text = "Preparando datos📝, un momento por favor✋"
        self.send_message(chat_id, text)

        firebase = db.reference("proximity_data")
        data = firebase.get()

        photo_list = [
            graphics.plot_alerts_per_day(data),
            graphics.plot_alerts_by_day_week(data),
            graphics.plot_vehicle_side(data),
            graphics.plot_patterns_incidents(data)
        ]

        self.send_photos(chat_id, photo_list)


    def __handler_not_foud(self, chat_id):
        print("Unknown message")

        text = "Lo siento😖, no puedo interpretar tu mensaje✉️"
        text += "%0APor favor, selecciona una de las 🔘opciones del teclado⌨️ personalizado"

        reply_markup = {
            "keyboard": [
                [self.__turn_on, self.__turn_off],
                [self.__graph_alert, self.__status]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        self.send_message(chat_id, text, reply_markup)

