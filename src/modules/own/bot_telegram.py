from utelegram import Bot, ReplyKeyboardMarkup, KeyboardButton

class BotTelegram:

    __TOKEN = 'my_token'


    def __init__(self):
        self.__bot = Bot(self.__TOKEN)
        self.__sapcs = False  # Flag para menejar estado de encendido o apagado del
        self.__build_keyboard_buttons()
        self.__generate_comands_handlers()
        self.__bot.start_loop()


    def __build_keyboard_buttons(self):
        self.__turn_on = KeyboardButton('Encender SAPCS')
        self.__turn_off = KeyboardButton('Apagar SAPCS')
        self.__status = KeyboardButton('Estado SAPCS')
        self.__alert_frequency = KeyboardButton('Ver día de la semana con mayor frecuencia de alerta')
        self.__emergency_contact = KeyboardButton("Contacto de emergencia")
        self.__add_contact = KeyboardButton("Agregar contacto")
        self.__contact_list = KeyboardButton("Ver contactos")
        self.__delete_contact = KeyboardButton("Eliminar contacto")


    def __generate_comands_handlers(self):

        @self.__bot.add_command_handler("start")
        def start(update):
            keyboard = [
                [self.__turn_on, self.__status, self.__turn_off],
                [self.__alert_frequency],
                [self.__emergency_contact]
            ]

            reply_keyboard = ReplyKeyboardMarkup(keyboard)
            update.reply("Hola", reply_markup=reply_keyboard)


        @self.__bot.add_command_handler("^(?!start$).*$")
        def default_command(update):
            update.reply("Lo siento, mensaje no reconocido")
            update.reply("Por, mensaje no reconocido")