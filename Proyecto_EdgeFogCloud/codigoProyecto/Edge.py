import threading
from SensorHumo import SensorHumo
from SensorHumedad import SensorHumedad
from SensorTemperatura import SensorTemperatura
from Aspersor import Aspersor
from SistemaCalidad import SistemaCalidad

class Edge:
    def __init__(self):
        self.aspersor = None  # Inicializar aspersor como None

    def CrearSensores(self):
        print("Creando sistema de calidad")
        sistemaCalidad = SistemaCalidad("5555")

        print("Creando sensores")
        sensoresHumo = [SensorHumo(f"humo_{i}", f"config/configFile1.txt", self.aspersor) for i in range(10)]
        sensoresTemperatura = [SensorTemperatura(f"temperatura_{i}", f"config/configFile2.txt") for i in range(10)]
        sensoresHumedad = [SensorHumedad(f"humedad_{i}", f"config/configFile3.txt") for i in range(10)]

        # Crear hilos para cada sensor y sistema de calidad
        hiloSC = threading.Thread(target=sistemaCalidad.EsperarAlerta)

        hilosHumo = [threading.Thread(target=lambda sensor=sensor: sensor.tomarMuestra()) for sensor in sensoresHumo]
        hilosTemperatura = [threading.Thread(target=sensor.tomarMuestra) for sensor in sensoresTemperatura]
        hilosHumedad = [threading.Thread(target=sensor.tomarMuestra) for sensor in sensoresHumedad]

        # Iniciar hilos
        hiloSC.start()
        for hilo in hilosHumo + hilosTemperatura + hilosHumedad:
            hilo.start()

        # Opcional: Esperar a que los hilos terminen
        hiloSC.join()
        for hilo in hilosHumo + hilosTemperatura + hilosHumedad:
            hilo.join()

    def CrearAspersor(self):
        print("Creando aspersor")
        self.aspersor = Aspersor()

if __name__ == "__main__":
    edge = Edge()
    edge.CrearAspersor()
    edge.CrearSensores()
