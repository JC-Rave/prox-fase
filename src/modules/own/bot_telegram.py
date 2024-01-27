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
        self.__alert_history = "Ver hitorico de alertas"


    def __build_command_handlers(self):
        self.__command_handlers = {
            "/start": self.__new_chat
        }


    def __build_message_handlers(self):
        self.__message_handlers = {
            self.__turn_on: self.__on_sapcs,
            self.__turn_off: self.__off_sapcs,
            self.__status: self.__status_sapcs,
            self.__alert_history: self.__get_history_alert_stadistics
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
                [self.__alert_history]
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
                [self.__status, self.__alert_history],
                [self.__turn_off, self.__turn_on]
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
                [self.__status, self.__alert_history],
                [self.__turn_on, self.__turn_off]
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
                [self.__turn_on, self.__turn_off],
                [self.__alert_history, self.__status]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        print("SAPCS status is:", self.__sapcs)
        self.send_message(chat_id, text, reply_markup)

    def __get_history_alert_stadistics(self, chat_id):
        print("Get alert data")

        text = "Preparando datos📝, un momento por favor✋"
        self.send_message(chat_id, text)

        firebase.get("proximity_data", "data", bg=False, limit=False)
        self.__process_data(chat_id, firebase.data)



    def __process_data(self, chat_id, data):
        print("procesando datos\n")

        day_of_week = self.__get_day_of_week(data)
        estadisticas = self.calcular_estadisticas(data)

        reply_markup = {
            "keyboard": [
                [self.__alert_history, self.__status],
                [self.__turn_on, self.__turn_off]
            ],
            "resize_keyboard": False,
            "one_time_keyboard": True
        }

        text = f"Total de alertas generadas: {estadisticas["total_alerts"]}"
        text += f"%0ADía de la semana con mayor frecuencia de alertas: {day_of_week}"
        # text += f"%0ADía con mas alertas: {estadisticas["dia_con_mas_alertas"]}, con un total de: {estadisticas["total_alertas_dia_mas_alertas"]}"
        print(text)        
        self.send_message(chat_id, text, reply_markup)


    def __get_day_of_week(self, data):
        alert_count = {}
        weeks = ["Domingo", "Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado"]

        for alert in data.values():
            date_parts = alert['date'].split('-')
            year, month, day = map(int, date_parts)
            
            # 0 es domigo, 6 es sabado
            day_of_week = (year + year // 4 - year // 100 + year // 400 + (month * 306 + 5) // 10 + (day + 1)) % 7

            # Contar el numero de alertas por dia de la semana
            if day_of_week in alert_count:
                alert_count[day_of_week] += 1
            else:
                alert_count[day_of_week] = 1

        # Encontrar el dia de la semana con el mayor numero de alertas
        max_alerts = max(alert_count.values())
        most_frequent_day = [day for day, count in alert_count.items() if count == max_alerts]

        week = weeks[most_frequent_day[0]]
        print("Dia:", week)
        return week


    def calcular_estadisticas(self, alertas):
        # Inicializar diccionario para almacenar estadísticas
        estadisticas = {
            "total_alerts": 0,
            'alertas_por_dia': {},
            'dia_con_mas_alertas': None,
            'total_alertas_dia_mas_alertas': 0
        }

        # Calcular estadísticas por día
        for alerta in alertas.values():
            fecha = alerta['date']
            dia = fecha.split('-')[2]

            # Incrementar el conteo total de alertas
            estadisticas['total_alerts'] += 1

            # Incrementar el conteo de alertas para el día correspondiente
            if dia in estadisticas['alertas_por_dia']:
                estadisticas['alertas_por_dia'][dia] += 1
            else:
                estadisticas['alertas_por_dia'][dia] = 1

        # Encontrar el día con más alertas
        for dia, conteo in estadisticas['alertas_por_dia'].items():
            if conteo > estadisticas['total_alertas_dia_mas_alertas']:
                estadisticas['dia_con_mas_alertas'] = dia
                estadisticas['total_alertas_dia_mas_alertas'] = conteo

        return estadisticas


    def __handler_not_foud(self, chat_id):
        pass

