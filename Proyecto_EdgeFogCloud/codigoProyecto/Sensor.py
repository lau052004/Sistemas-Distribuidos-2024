from colorama import Fore, Style
import zmq
import threading

# Contador global y bloqueo
contador_mensajes = 0
contador_lock = threading.Lock()
# ip_proxy = "10.43.101.86"  # IP inicial del proxy
ip_proxy = "10.43.101.86"


class Sensor:

    muestra = {
        'tipo': '',
        'valor': '',
        'tiempo': ''
    }

    def __init__(self, parametro1, parametro2):
        self.tipo: str = parametro1
        self.configFile: str = parametro2
        self.pCorrecto: float = -1
        self.pFueraRango: float = -1
        self.pError: float = -1
        self.PUERTO_PROXY = 5556
        self.leerArchivo()
            
        

    def tomarMuestra(self):
        print("Muestra de humo tomada")

    def leerArchivo(self):
        # Abrir el archivo para lectura ('r')
        with open(self.configFile, 'r') as archivo:
            # Leer todas las líneas del archivo
            lineas = archivo.readlines()

            # Procesar cada línea
            for linea in lineas:
                # Dividir la línea por el delimitador ';'
                partes = linea.strip().split(';')

                # Convertir cada parte a entero (o flotante si fuera necesario)
                numeros = [float(parte) for parte in partes]

                # Hacer algo con los números (aquí simplemente los imprimo)
                print(numeros)
                self.pCorrecto = numeros[0]
                self.pFueraRango = numeros[1]
                self.pError = numeros[2]

    def enviarMuestraProxy(self):
        # threading.Thread(target=self.actualizar_ip_proxy, daemon=True).start()
        if(self.tipo=="humo_0"):
            self.actualizar_ip_proxy()
            
        global ip_proxy
        context = zmq.Context()
        socket = context.socket(zmq.PUSH)
        # socket.bind("tcp://localhost:5555")
        socket.connect(f"tcp://{ip_proxy}:5556")

        try:
            socket.send_pyobj(self.muestra)
            print("Muestra enviada al Proxy.")
            # Incrementar el contador de mensajes
            global contador_mensajes
            with contador_lock:
                contador_mensajes += 1
                # Imprimir el contador de mensajes en amarillo
                if (contador_mensajes % 30 == 0):
                    print(
                        Fore.YELLOW + f"Mensajes enviados hasta ahora: {contador_mensajes}" + Style.RESET_ALL)
        except zmq.ZMQError as e:
            print(f"Error al enviar la muestra: {e}")
        finally:
            socket.close()
            context.term()
            
    @classmethod
    def actualizar_ip_proxy(cls):
        global ip_proxy
        print("ENTRANDO A CAMBIAR IP")
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://10.43.101.24:5590")  # IP y puerto del proxy que envía la nueva IP
        try:
            print("ENTRA AL TRY")
            while True:
                print("ENTR AL WHILE")
                ip_proxy = socket.recv_string()
                print(Fore.GREEN + f"IP actualizada: {ip_proxy}" + Style.RESET_ALL)
        except zmq.ZMQError as e:
            print(f"Error al recibir la IP del proxy: {e}")
        finally:
            socket.close()
            context.term()
