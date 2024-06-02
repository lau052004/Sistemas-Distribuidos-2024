import random
import threading
import zmq
from Sensor import Sensor
from time import sleep
import datetime
from threading import Thread


class SensorTemperatura(Sensor):
    def __init__(self, parametro1, parametro2):
        self.inicializado = threading.Event()
        super().__init__(parametro1, parametro2)
        self.rango_normal = (11, 29.4)

        self.inicializado.set()

    def run(self):
        while True:
            self.tomarMuestra()
            # sleep(6)

    def tomarMuestra(self):
        self.inicializado.wait()
        while True:
            probabilidades = {
                "correctos": self.pCorrecto,
                "fuera_rango": self.pFueraRango,
                "error": self.pError,
            }
            eleccion = random.choices(
                list(probabilidades.keys()), probabilidades.values())[0]

            if eleccion == "correctos":
                self.muestra['valor'] = random.uniform(*self.rango_normal)
            elif eleccion == "fuera_rango":
                self.muestra['valor'] = random.uniform(
                    self.rango_normal[1], self.rango_normal[1] + 10)
            else:
                self.muestra['valor'] = random.uniform(-10, 0)

            self.muestra['tipo'] = "temperatura"
            self.muestra['hora'] = str(datetime.datetime.now())
            self.enviarMuestraProxy()
            # sleep(6)
            sleep(20)

    # def simular_medicion(self):
    #     valor = self.generar_valor()
    #     return {"tipo": self.tipo, "valor": valor}

    # def enviarMuestraProxy(self):
    #     context = zmq.Context()
    #     socket = context.socket(zmq.PUSH)
    #     #socket.bind("tcp://localhost:5555")
    #     socket.connect("tcp://localhost:5556")

    #     try:
    #         socket.send_pyobj(self.muestra)
    #         print("Muestra enviada al Proxy.")
    #     except zmq.ZMQError as e:
    #         print(f"Error al enviar la muestra: {e}")
    #     finally:
    #         socket.close()
    #         context.term()#
