from datetime import datetime

class Alerta:
    def __init__(self, origen_sensor, tipo_alerta, fecha=None):
        self.fecha = fecha if fecha else datetime.now()
        self.origen_sensor = origen_sensor
        self.tipo_alerta = tipo_alerta
