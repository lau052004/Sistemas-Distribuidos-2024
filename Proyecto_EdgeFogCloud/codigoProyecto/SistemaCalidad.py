import zmq
from Alerta import Alerta

class SistemaCalidad:
    
    def __init__(self, puerto):
        self.PUERTO: str = puerto
        print("Creando sistema de calidad")
    
    def EsperarAlerta(self):
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{self.PUERTO}") #PUERTO = 5555 socket.bind("tcp://*:5555")

        while True:
            alerta = socket.recv_pyobj()
            self.ImprimirAlerta(alerta)
            socket.send_string("Alerta impresa en pantalla")

    def ImprimirAlerta(self, alerta):
        print(f"Sistema de Calidad: recibe '{alerta.tipo_alerta}' de {alerta.origen_sensor} con fecha {alerta.fecha}")

if __name__ == "__main__":
    sistema_calidad = SistemaCalidad()
    sistema_calidad.EsperarAlerta()
