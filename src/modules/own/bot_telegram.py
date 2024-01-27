import _thread
import urequests
import ujson
import ufirebase as firebase
import pandas as pd
from datetime import datetime, timedelta

class BotTelegram:

    STATUS_SAPCS_ON = "ON"
    STATUS_SAPCS_OFF = "OFF"


    def __init__(self, token):
        self.__base_url = f"https://api.telegram.org/bot{token}/"
        self.__last_update = 0
        self.__sapcs = self.STATUS_SAPCS_OFF  # Flag para menejar estado del sistema de alerta de proximidad

        self.__build_keyboard_buttons()
        self.__build_command_handlers()
        self.__build_message_handlers()


    def __build_keyboard_buttons(self):
        self.__turn_on = "Encender SAPCS"
        self.__turn_off = "Apagar SAPCS"
        self.__status = "Estado SAPCS"
        self.__alert_frequency = "Ver día de la semana con mayor frecuencia de alerta"
        self.__alert_day = "Ver alertas del día"
        self.__alert_history = "Ver hitorico de alertas"
        self.__alert_seven_days = "Ver alertas de los ultimos 7 días"


    def __build_command_handlers(self):
        self.__command_handlers = {
            "/start": self.__new_chat
        }


    def __build_message_handlers(self):
        self.__message_handlers = {
            self.__turn_on: self.__on_sapcs,
            self.__turn_off: self.__off_sapcs,
            self.__status: self.__status_sapcs,
            self.__alert_frequency: self.__get_alert_frequency,
            self.__alert_day: self.__get_day_alert_stadistics,
            self.__alert_seven_days: self.__get_seven_days_alert_stadisctics,
            self.__alert_history: self.__get_history_alert_stadistics,
        }


    def send_message(self, chat_id, text, reply_markup=None):
        try:
            url = self.__base_url + f"sendMessage?chat_id={chat_id}&text={text}&parse_mode=Markdown"
            if reply_markup:
                url += f"&reply_markup={ujson.dumps(reply_markup)}"

            response = urequests.get(url)
            response.close()
        except Exception as ex:
            print("Unsent message:", ex)


    def get_status_sapcs(self):
        return self.__sapcs


    def turn_on(self):
        def __loop():
            while True:
                updates = self.__get_updates()

                for update in updates:
                    self.__handle_update(update)

        _thread.start_new_thread(__loop, ())


    def __get_updates(self):
        request_body = {
            "offset": self.__last_update + 1,
            "timeout": 5,
            "allowed_updates": ["message"]
        }

        try:
            url = self.__base_url + "getUpdates"
            response = urequests.post(url, json=request_body)

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
                [self.__alert_frequency],
                [self.__alert_day, self.__alert_history, self.__alert_seven_days]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        self.send_message(chat_id, text, reply_markup)


    def __on_sapcs(self, chat_id):
        if self.__sapcs == self.STATUS_SAPCS_OFF:
            print("Turning on the SAPCS")
            self.__sapcs = self.STATUS_SAPCS_ON
            text = "SAPCS Encendido🟢 con exito😀👌"
        else:
            print("SAPCS is already on")
            text = "SAPCS ya se encuentra encendido✅"

        reply_markup = {
            "keyboard": [
                [self.__alert_frequency],
                [self.__alert_day, self.__alert_history, self.__alert_seven_days],
                [self.__status, self.__turn_off, self.__turn_on]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        self.send_message(chat_id, text, reply_markup)


    def __off_sapcs(self, chat_id):
        if self.__sapcs == self.STATUS_SAPCS_ON:
            print("Turning off the SAPCS")
            self.__sapcs = self.STATUS_SAPCS_OFF
            text = "SAPCS Apagado🔴 con exito☹️"
        else:
            print("SAPCS is already turned off")
            text = "SAPCS ya se encuentra apagado❌"

        reply_markup = {
            "keyboard": [
                [self.__turn_on, self.__alert_day],
                [self.__alert_history, self.__alert_seven_days],
                [self.__alert_frequency],
                [self.__status, self.__turn_off]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

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
                [self.__turn_on, self.__status, self.__turn_off],
                [self.__alert_frequency],
                [self.__alert_day, self.__alert_history, self.__alert_seven_days]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        print("SAPCS status is:", self.__sapcs)
        self.send_message(chat_id, text, reply_markup)

    def __get_alert_frequency(self, chat_id):
        print("Get day of the week with the highest number of alerts")

        firebase.getfile("proximity_data", "data.json", bg=True, id=2, cb=(self.__process_data, (chat_id, "data.json")))

        text = "Estoy consultando los registros🗃️, un momento por favor✋"

        self.send_message(chat_id, text)


    def __process_data(self, chat_id, data):
        
        reply_markup = {
            "keyboard": [
                [self.__alert_frequency],
                [self.__emergency_contact, self.__status],
                [self.__turn_on, self.__turn_off]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }


    def __get_day_alert_stadistics(self, chat_id):
        pass

    def __get_seven_days_alert_stadisctics(self, chat_id):

        data = firebase.getfile("proximity_data", "data.json", bg=True, id=2)
        df = pd.DataFrame(data)

        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')

        seven_days_ago = datetime.now() - timedelta(days=7)
        df_last_seven_days = df[df['timestamp'] >= seven_days_ago]

        day_with_most_events = df_last_seven_days['timestamp'].dt.day_name().mode().values[0]
        hour_with_most_events = df_last_seven_days['timestamp'].dt.hour.mode().values[0]

        text = f"En los últimos 7 días:\n"
        text += f"Día con más eventos: {day_with_most_events}\n"
        text += f"Hora con más eventos: {hour_with_most_events}:00"

        self.send_message(chat_id, text)
        pass


    def __get_history_alert_stadistics(self, chat_id):
        pass


    def __handler_not_foud(self, chat_id):
        pass

