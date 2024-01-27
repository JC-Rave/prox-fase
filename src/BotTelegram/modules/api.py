from flask import Flask

class API:

    def __init__(self):
        self.app = Flask(__name__)
        self.app.add_url_rule('/', 'index', self.index)
        self.app.add_url_rule('/saludo/<string:nombre>', 'saludo', self.saludo)

    def index(self):
        return '¡Hola, Mundo! Este es mi API.'

    def saludo(self, nombre):
        return f'Hola, {nombre}!'

    def run(self):
        self.app.run(debug=True, host='0.0.0.0')

if __name__ == '__main__':
    api = API()
    api.run()
