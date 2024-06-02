
import grpc
import calculo_servicio_pb2
import calculo_servicio_pb2_grpc
import re


class CalculatorClient:
    def __init__(self, host='localhost', port=50051):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = calculo_servicio_pb2_grpc.CalculadoraStub(self.channel)

    def suma(self, num1, num2):
        return self.stub.Suma(calculo_servicio_pb2.SumaRequest(num1=num1, num2=num2)).resultado

    def resta(self, num1, num2):
        return self.stub.Resta(calculo_servicio_pb2.RestaRequest(num1=num1, num2=num2)).resultado

    def enviar_operacion(self, operacion):
        return self.stub.Operacion(calculo_servicio_pb2.OperacionRequest(operacion=operacion)).resultado


# Ejemplo de uso del cliente
if __name__ == '__main__':
    client = CalculatorClient()

    operacion = input("Ingrese la operación que desea realizar: ")

    resultado = re.findall(r'[^+-]+|[+-]', operacion)

    # print(resultado)

    print(f"Resultado de la operación: {client.enviar_operacion(operacion)}")

    # print(f"Resultado de la suma: {client.suma(num1, num2)}")
    # print(f"Resultado de la resta: {client.resta(num1, num2)}")
