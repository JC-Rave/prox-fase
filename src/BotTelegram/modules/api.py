import time
from flask import Flask, request, jsonify

class API:

    def __init__(self, bot):
        self.__bot = bot

        self.__app = Flask(__name__)
        self.__app.add_url_rule("/sapcs_status", "sapcs_status", self.__sapcs_status)
        self.__app.add_url_rule("/send_message", "send_message", self.__send_message, methods=["POST"])

    def __sapcs_status(self):
        print("Get SAPCS status")
        timeout = int(request.args.get("timeout", 20))
        start_time = time.time()

        while True:
            if self.__bot.is_status_update():
                sapcs_status = self.__bot.get_sapcs_status()
                print("SAPCS status is:", sapcs_status)

                self.__bot.set_status_update(False)
                return jsonify({
                    "sapcs_status": sapcs_status
                })

            end_time = time.time()
            elapsed_time = end_time - start_time

            if elapsed_time >= timeout:
                sapcs_status = self.__bot.get_sapcs_status()
                print("SAPCS status is:", sapcs_status)

                return jsonify({
                    "sapcs_status": sapcs_status
                })


    def __send_message(self):
        data = request.json

        chat_id = data.get("chat_id")
        date = data.get("date")
        time = data.get("time")
        crash_occurred = data.get("crash_occurred")
        side = data.get("side")

        if crash_occurred:
            text = "Has chocado💥 con un objeto😱😱"
            text += f"%0AFecha y hora de lo ocurrido: {date} {time}"
            text += f"%0ALado que se impacto: {side}"
        else:
            text = "Estuviste demasiado cerca de un objeto😟"
            text += f"%0AFecha y hora de lo ocurrio: {date} {time}"
            text += f"%0ALado que estuvo por impactar: {side}"

        response = self.__bot.send_message(chat_id, text)
        if isinstance(response, Exception):
            response_data = {
                "status": "Failed",
                "message": response
            }
        else:
            response_data = {
                "status": "Success",
                "message": response
            }

        return jsonify(response_data)


    def run(self):
        self.__app.run(debug=False)

