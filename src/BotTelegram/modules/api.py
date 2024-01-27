import time
from flask import Flask, request, jsonify

class API:

    def __init__(self, bot):
        self.__bot = bot

        self.__app = Flask(__name__)
        self.__app.add_url_rule('/sapcs_status', 'sapcs_status', self.__sapcs_status)

    def __sapcs_status(self):
        print("Get SAPCS status")
        timeout = int(request.args.get('timeout', 20))
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


    def run(self):
        self.__app.run(debug=False)

