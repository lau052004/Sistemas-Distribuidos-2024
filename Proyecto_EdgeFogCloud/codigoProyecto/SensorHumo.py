import datetime
import random
from Sensor import Sensor
from time import sleep
from Aspersor import Aspersor
import zmq
from threading import Thread
from Alerta import Alerta


class SensorHumo(Sensor, Thread):
    def __init__(self, parametro1, parametro2, aspersor):
        Sensor.__init__(self, parametro1, parametro2)
        Thread.__init__(self)
        self.valores_booleanos = (True, False, "Error")
        self.aspersor: Aspersor = aspersor

    def run(self):
        while True:
            self.tomarMuestra()
            # sleep(3)

    def tomarMuestra(self):
        while True:
            probabilidades = {
                "correcto": self.pCorrecto,
                "error": self.pError,
            }
            eleccion = random.choices(
                list(probabilidades.keys()), probabilidades.values())[0]

            if eleccion == "correcto":
                self.muestra['valor'] = random.choice([True, False])
            else:
                self.muestra['valor'] = "error"

            if self.muestra['valor'] == True:
                self.muestra['tipo'] = "alerta humo"  # cambiar a alerta humo
                self.muestra['hora'] = str(datetime.datetime.now())
                self.enviarMensajeAspersor()
                self.generarSistemaCalidad()

            else:
                self.muestra['tipo'] = "humo"
                self.muestra['hora'] = str(datetime.datetime.now())

            self.enviarMuestraProxy()
            sleep(3)

    def generarSistemaCalidad(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        alerta = Alerta(origen_sensor=self.__class__.__name__,
                        tipo_alerta="Alerta: Sistema de Calidad", fecha=datetime.datetime.now())
        socket.send_pyobj(alerta)

        response = socket.recv_string()
        print(f"Sensor humo: recibe '{response}' del sistema de calidad")

        socket.close()
        context.term()

    def enviarMensajeAspersor(self):
        self.aspersor.activarAspersor()
        # Código para el método enviarMensajeAspersor

    # def enviarMuestraProxy(self):
    #     context = zmq.Context()
    #     socket = context.socket(zmq.PUSH)
    #     # socket.bind("tcp://localhost:5555")
    #     socket.connect("tcp://localhost:5556")
    #     try:
    #         socket.send_pyobj(self.muestra)
    #         print("Muestra enviada al Proxy.")
    #     except zmq.ZMQError as e:
    #         print(f"Error al enviar la muestra: {e}")
    #     finally:
    #         socket.close()
    #         context.term()
