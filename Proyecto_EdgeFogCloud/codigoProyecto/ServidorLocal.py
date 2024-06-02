from time import sleep
import zmq
import json
from datetime import datetime

from Alerta import Alerta


class ServidorLocal:
    
    def __init__(self):
        print("Creando servidor local")

    def enviarPromedio(self, datos):
        # context = zmq.Context()
        # socket = context.socket(zmq.REP)
        # socket.bind("tcp://localhost:5561")
        # datos = socket.recv_pyobj()
        promedio = sum(datos) / len(datos)
        print(f"promedio servidor: {promedio}")
        return promedio
        
        

