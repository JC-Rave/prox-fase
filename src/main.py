import network, time
from proxsafe import ProxSafe

class Main:

    def __init__(self, ssid, password):
        self.__connect_to_network(ssid, password)
        self.__prox_safe = ProxSafe()
        self.__prox_safe.run()

    def __connect_to_network(self, ssid, password):
        self.__network = network.WLAN(network.STA_IF)

        if not self.__network.isconnected():         #Si no está conectado…
            self.__network.active(True)              #activa la interface
            self.__network.connect(ssid, password)   #Intenta conectar con la red
            print(f"Connecting to the '{ssid}' network...")

            timeout = time.time()
            while not self.__network.isconnected():  #Mientras no se conecte..
                if (time.ticks_diff(time.time(), timeout) > 10):
                    self.__network.active(False)
                    raise Exception(f"Could not connect to '{ssid}' network")
            else:
                print(f"Connected to the '{ssid}' network")
                print("Network data (IP/netmask/gw/DNS):", self.__network.ifconfig())


Main("my_red", "my_password")