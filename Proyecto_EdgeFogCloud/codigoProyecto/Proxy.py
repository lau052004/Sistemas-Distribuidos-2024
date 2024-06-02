import datetime
import re
import statistics
import threading
from time import sleep
import time
from colorama import Fore, Style
import zmq
from Alerta import Alerta
from datetime import datetime
from ServidorLocal import ServidorLocal
from SistemaCalidad import SistemaCalidad

contador_mensajes_cloud = 0
contador_lock_cloud = threading.Lock()


class Proxy:
    promedio = {
        'tipo': '',
        'valor': ''
    }

    def _init_(self, servidor):
        print("Creando proxy")
        self.servidor: ServidorLocal = servidor
        self.temperaturas = []
        self.humedades = []
        # Límites establecidos para los sensores
        self.TEMP_MAX = 29.4
        self.tiempos_comunicacion = []
        self.tiempos_lock = threading.Lock()

    def recibirAlertasServidor(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://*:5559")

        while True:
            alert = socket.recv_pyobj()
            print("Alerta recibida en el Proxy:", alert)
            print(f"Se va a mandar al cloud: {alert}")
            self.enviarAlerta(alert)
            socket.send_string("Enviando alerta al cloud")

    def recibirMuestras(self):
        context = zmq.Context()
        socket = context.socket(zmq.PULL)
        socket.bind("tcp://10.43.101.86:5556")
        try:
            while True:
                datos = socket.recv_pyobj()
                print("Muestra recibida en el Proxy:", datos)
                if self.validarDatos(datos):
                    self.enviarMuestrasCloud(datos)
                    if datos['tipo'] == "temperatura":
                        self.temperaturas.append(datos['valor'])
                    elif datos['tipo'] == "humedad":
                        self.humedades.append(datos['valor'])
                    self.pedirPromedioServidor()
                    print("Datos válidos enviados al Cloud.")
                else:
                    self.enviarAlerta(datos)
                    print("Alerta enviada al sistema de calidad y al Cloud.")
        except zmq.ZMQError as e:
            print(f"Error al recibir la muestra: {e}")
        finally:
            socket.close()
            context.term()

    def validarDatos(self, datos):
        print("Validando datos")
        if re.search("humo", datos['tipo']):
            if datos['valor'] == True or datos['valor'] == False:
                print("Datos correctos")
                return True
            print("Datos Incorrectos: Valor no es True ni False")
            return False
        elif re.search("temperatura", datos['tipo']):
            if float(datos['valor']) < 0:
                print("Datos Incorrectos: Valor de temperatura negativo")
                return False
            elif float(datos['valor']) < 11 or float(datos['valor']) > 29.4:
                print("Datos fuera de rango: Generando alerta")
                return False
            print("Datos correctos")
            return True
        elif re.search("humedad", datos['tipo']):
            if float(datos['valor']) < 0:
                print("Datos Incorrectos: Valor de humedad negativo")
                return False
            print("Datos correctos")
            return True
        else:
            print("Tipo de datos desconocido")
            return False

    def enviarAlerta(self, datos):
        try:
            valor = float(datos['valor'])
            tipo_alerta = f"Alerta: {datos['tipo']} fuera de rango" if valor < 11 or valor > 29.4 else "Datos Correctos"
        except ValueError:
            tipo_alerta = "Datos Incorrectos"

        alerta = Alerta(
            origen_sensor=datos['tipo'], tipo_alerta=tipo_alerta, fecha=datetime.now())

        try:
            context = zmq.Context()
            socket = context.socket(zmq.REQ)
            socket.connect("tcp://10.43.103.83:5560")
            socket.send_pyobj(alerta)
            print("Alerta enviada al Cloud.")

            # Incrementar el contador de mensajes
            global contador_mensajes_cloud
            with contador_lock_cloud:
                contador_mensajes_cloud += 1
                print(
                    Fore.BLUE + f"Total de mensajes enviados al cloud: {contador_mensajes_cloud}" + Style.RESET_ALL)

        except zmq.ZMQError as e:
            print(f"Error al enviar la alerta: {e}")

    # self.enviarMensajesCloud(alerta)

    def pedirPromedioServidor(self):
        if len(self.temperaturas) >= 10:
            promedioTemp = self.servidor.enviarPromedio(self.temperaturas)
            print(
                f"Promedio de Temperatura: {promedioTemp} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # promedioTemp = 35
            if promedioTemp > self.TEMP_MAX:
                alerta = Alerta("Promedio temperatura elevado", promedioTemp,
                                datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                self.generarSistemaCalidad()
                self.enviarAlerta(alerta)
            print(
                f"Promedio de temperatura recibido en el Proxy: {promedioTemp}")
            self.enviarMensajesCloud(promedioTemp, "temperatura")
            self.temperaturas = []  # Resetear la lista para el próximo cálculo

        if len(self.humedades) == 10:
            promedioHumedad = self.servidor.enviarPromedio(self.humedades)
            print(
                f"Promedio de Humedad: {promedioHumedad} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            # enviar promedio al proxy
            print(
                f"Promedio de humedad recibido en el Proxy: {promedioHumedad}")
            self.enviarMensajesCloud(promedioHumedad, "humedad")
            self.humedades = []  # Resetear la lista para el próximo cálculo

    def enviarMensajesCloud(self, datos, tipo):
        sleep(5)
        print("Enviando promedio cloud")
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://10.43.103.83:5566")

        self.promedio['tipo'] = tipo
        self.promedio['valor'] = datos

        # Medir el tiempo de inicio
        start_time = time.time()
        socket.send_pyobj(self.promedio)
        response = socket.recv_string()
        print(f"Proxy: recibe '{response}' de la capa cloud")

        # Medir el tiempo de fin
        end_time = time.time()
        tiempo_comunicacion = end_time - start_time
        with self.tiempos_lock:
            self.tiempos_comunicacion.append(tiempo_comunicacion)

        socket.close()
        context.term()

        # Incrementar el contador de mensajes
        global contador_mensajes_cloud
        with contador_lock_cloud:
            contador_mensajes_cloud += 1
            print(
                Fore.YELLOW + f"Total de mensajes enviados al cloud: {contador_mensajes_cloud}" + Style.RESET_ALL)

    def enviarMuestrasCloud(self, datos):

        print("Enviando muestras cloud")
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://10.43.103.83:5557")

        # Medir el tiempo de inicio
        start_time = time.time()
        socket.send_pyobj(datos)
        response = socket.recv_string()
        print(f"Proxy: recibe '{response}' de la capa cloud")

        # Medir el tiempo de fin
        end_time = time.time()
        tiempo_comunicacion = end_time - start_time
        with self.tiempos_lock:
            self.tiempos_comunicacion.append(tiempo_comunicacion)

        socket.close()

        # Incrementar el contador de mensajes
        global contador_mensajes_cloud
        with contador_lock_cloud:
            contador_mensajes_cloud += 1
            print(
                Fore.YELLOW + f"Total de mensajes enviados al cloud: {contador_mensajes_cloud}" + Style.RESET_ALL)

    def generarSistemaCalidad(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5565")

        alerta = Alerta(origen_sensor=self._class.name_,
                        tipo_alerta="Alerta: Sistema de Calidad", fecha=datetime.now())
        socket.send_pyobj(alerta)

        response = socket.recv_string()
        print(f"Proxy: recibe '{response}' del sistema de calidad")

        socket.close()
        context.term()

    def health(self):
        context = zmq.Context()
        sender = context.socket(zmq.REQ)
        sender.connect(
            f"tcp://localhost:5568")
        sender.send_string("Hello :)")
        sender.recv_string()

        receiver = context.socket(zmq.REP)
        receiver.bind(
            f"tcp://localhost:5569")

        while True:
            receiver.recv_string()
            receiver.send_string("yes still alive")

    def calcular_estadisticas(self):
        while True:
            sleep(10)  # Calcular estadísticas cada 60 segundos
            with self.tiempos_lock:
                print("----------------------------------------------------------")
                print(self.tiempos_comunicacion)
                print("----------------------------------------------------------")
                if len(self.tiempos_comunicacion) > 2:
                    promedio = sum(self.tiempos_comunicacion) / \
                        len(self.tiempos_comunicacion)
                    desviacion_estandar = statistics.stdev(
                        self.tiempos_comunicacion)
                    print(
                        Fore.CYAN + f"Tiempo promedio de comunicación: {promedio:.2f} segundos" + Style.RESET_ALL)
                    print(
                        Fore.CYAN + f"Desviación estándar de comunicación: {desviacion_estandar:.2f} segundos" + Style.RESET_ALL)

                    self.escribirEnArchivo(promedio, desviacion_estandar)
                else:
                    print(
                        Fore.CYAN + "No hay datos suficientes para calcular estadísticas." + Style.RESET_ALL)

    def escribirEnArchivo(self, promedio, desviacion_estandar):
        with open("Comunicacion.txt", "a") as file:
            file.write(
                f"Promedio: {promedio}, Desviación estándar: {desviacion_estandar}\n")


def crearServidor():
    print("Creando servidor")
    return ServidorLocal()


def crearSistemaCalidad():
    print("Creando sistema de calidad")
    return SistemaCalidad("5565")


if __name__ == "__main__":
    servidor = crearServidor()
    proxy = Proxy(servidor)
    sistemaCalidad = crearSistemaCalidad()

    hiloProxy = threading.Thread(target=proxy.recibirMuestras)
    hiloHealth = threading.Thread(target=proxy.health)
    hiloSistemaCalidad = threading.Thread(target=sistemaCalidad.EsperarAlerta)
    hiloEstadisticas = threading.Thread(target=proxy.calcular_estadisticas)

    hiloProxy.start()
    hiloHealth.start()
    hiloSistemaCalidad.start()
    hiloEstadisticas.start()

    hiloProxy.join()
    hiloHealth.join()
    hiloSistemaCalidad.join()
    hiloEstadisticas.join()
