from time import sleep
from datetime import datetime, time
import zmq
from Alerta import Alerta
import threading
from SistemaCalidad import SistemaCalidad


class Cloud:

    def __init__(self):
        self.sumatoriahumedad = 0
        self.minimo_humedad = 70
        self.humedadesArray = []
        self.alertas_totales = 0
        self.alertas_por_tipo = {}
        self.lock = threading.Lock()

    def recibirAlertasProxy(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://10.43.103.83:5560")
        # self.socket.setsockopt_string(zmq.SUBSCRIBE, "")
        while True:
            alerta = socket.recv_pyobj()  # Recibimos directamente la instancia de Alerta
            if isinstance(alerta, Alerta):
                self.escribirEnArchivo(alerta)
                self.contarAlerta(alerta)
            else:
                print("Recibido objeto no esperado:", alerta)

            socket.send_string("Datos recibidos impresos")

    def escribirEnArchivo(self, alerta):
        with open("Alertas.txt", "a") as file:
            file.write(
                f"Fecha: {alerta.fecha}, Origen del sensor: {alerta.origen_sensor}, Tipo de alerta: {alerta.tipo_alerta}\n")

    def contarAlerta(self, alerta):
        with self.lock:
            self.alertas_totales += 1
            if alerta.tipo_alerta not in self.alertas_por_tipo:
                self.alertas_por_tipo[alerta.tipo_alerta] = 1
            else:
                self.alertas_por_tipo[alerta.tipo_alerta] += 1

        print("////////////////////////////////////////////////////////////")
        print(f"Alertas totales: {self.alertas_totales}")
        print(f"Alertas por tipo: {self.alertas_por_tipo}")
        print("////////////////////////////////////////////////////////////")

    def recibirInfoProxy(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://10.43.103.83:5557")
        while True:
            message = socket.recv_pyobj()
            print(f"{message}")
            socket.send_string("Datos recibidos impresos")

    def recibirPromedios(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind("tcp://10.43.103.83:5566")
        while True:
            message = socket.recv_pyobj()
            print(f"{message}")
            if message['tipo'] == "humedad":
                self.humedadesArray.append(float(message['valor']))
                print("---------------------PROMEDIO LLEGA ----------------------")
                print(self.humedadesArray)
                print("----------------------------------------------------------")

                if self.humedadesArray.__len__() >= 4:
                    print(
                        "------------------- CONDICION = 4 --------------------------")
                    print(self.humedadesArray)
                    print("----------------------------------------------------------")
                    self.sumatoriahumedad = sum(
                        self.humedadesArray) / self.humedadesArray.__len__()
                    print("Sumatoria de humedad: ", self.sumatoriahumedad)
                    if self.sumatoriahumedad < self.minimo_humedad:
                        alerta = Alerta(
                            "Humedad", "Alta", "El valor de humedad es inferior al minimo permitido")
                        self.escribirEnArchivo(alerta)
                        self.generarSistemaCalidad(alerta)

                    self.humedadesArray.clear()

            socket.send_string("Promedios recibidos impresos")

    def generarSistemaCalidad(self, alerta):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5567")
        socket.send_pyobj(alerta)

        response = socket.recv_string()
        print("//////////////////////////////////////////////////////")
        print(f"Cloud: recibe '{response}' del sistema de calidad")
        print("//////////////////////////////////////////////////////")

        socket.close()
        context.term()


def crearSistemaCalidad():
    print("Creando sistema de calidad")
    sistemaCalidad = SistemaCalidad("5567")
    return sistemaCalidad


if __name__ == "__main__":
    cloud = Cloud()
    sistemaCalidad = crearSistemaCalidad()

    hiloCloud = threading.Thread(target=cloud.recibirInfoProxy)
    hiloCloudAlert = threading.Thread(target=cloud.recibirAlertasProxy)
    hiloPromedios = threading.Thread(target=cloud.recibirPromedios)
    hiloSistemaCalidad = threading.Thread(target=sistemaCalidad.EsperarAlerta)

    hiloCloud.start()
    hiloCloudAlert.start()
    hiloPromedios.start()
    hiloSistemaCalidad.start()

    hiloCloud.join()
    hiloCloudAlert.join()
    hiloPromedios.join()
    hiloSistemaCalidad.join()
