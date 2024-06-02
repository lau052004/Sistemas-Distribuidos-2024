from concurrent import futures
import grpc
import calculo_servicio_pb2
import calculo_servicio_pb2_grpc
import re

# Definir los clientes gRPC para los servidores de operaciones


class OperationClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.channel = None
        self.stub = None
        self.conectar_servidor()

    def conectar_servidor(self):
        print(
            f'Intentando conectar al servidor de operaciones en {self.host}:{self.port}')
        try:
            self.channel = grpc.insecure_channel(f'{self.host}:{self.port}')
            self.stub = calculo_servicio_pb2_grpc.CalculadoraStub(self.channel)
            print(
                f'Conectado al servidor de operaciones en {self.host}:{self.port}')
        except grpc.RpcError as e:
            print(
                f'No se pudo conectar al servidor de operaciones en {self.host}:{self.port}: {e}')

    def suma(self, num1, num2):
        try:
            return self.stub.Suma(calculo_servicio_pb2.SumaRequest(num1=num1, num2=num2))
        except grpc.RpcError:
            print(
                f'No se pudo realizar la suma a través del servidor en {self.host}:{self.port}, realizando operación localmente.')
            return None

    def resta(self, num1, num2):
        try:
            return self.stub.Resta(calculo_servicio_pb2.RestaRequest(num1=num1, num2=num2))
        except grpc.RpcError:
            print(
                f'No se pudo realizar la resta a través del servidor en {self.host}:{self.port}, realizando operación localmente.')
            return None

# Servicio que reenvía las peticiones a los servidores de operaciones


class CalculadoraService(calculo_servicio_pb2_grpc.CalculadoraServicer):
    def __init__(self):
        self.suma_client = OperationClient('localhost', 12346)
        self.resta_client = OperationClient('localhost', 12347)

    def realizar_suma_local(self, num1, num2):
        print(f'Realizando suma localmente: {num1} + {num2}')
        return num1 + num2

    def realizar_resta_local(self, num1, num2):
        print(f'Realizando resta localmente: {num1} - {num2}')
        return num1 - num2

    def Suma(self, request, context):
        response = self.suma_client.suma(request.num1, request.num2)
        if response is None:
            resultado = self.realizar_suma_local(request.num1, request.num2)
        else:
            resultado = response.resultado
        return calculo_servicio_pb2.OperacionResponse(resultado=resultado)

    def Resta(self, request, context):
        response = self.resta_client.resta(request.num1, request.num2)
        if response is None:
            resultado = self.realizar_resta_local(request.num1, request.num2)
        else:
            resultado = response.resultado
        return calculo_servicio_pb2.OperacionResponse(resultado=resultado)

    def Operacion(self, request, context):
        operacion = request.operacion
        elementos = re.findall(r'(\d+\.?\d*)|([+-])', operacion)

        resultado = float(elementos[0][0])  # Inicializa con el primer número

        i = 1
        while i < len(elementos):
            operador = elementos[i][1]
            siguiente_numero = float(elementos[i + 1][0])

            if operador == '+':
                response = self.suma_client.suma(resultado, siguiente_numero)
                if response:
                    resultado = response.resultado
                else:
                    resultado = self.realizar_suma_local(
                        resultado, siguiente_numero)
            elif operador == '-':
                response = self.resta_client.resta(resultado, siguiente_numero)
                if response:
                    resultado = response.resultado
                else:
                    resultado = self.realizar_resta_local(
                        resultado, siguiente_numero)

            i += 2

        return calculo_servicio_pb2.OperacionResponse(resultado=resultado)


def serve():
    print('Iniciando servidor...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    calculo_servicio_pb2_grpc.add_CalculadoraServicer_to_server(
        CalculadoraService(), server)
    server.add_insecure_port('[::]:50051')
    print('Servidor iniciado en el puerto 50051.')
    server.start()
    print('Servidor corriendo... Esperando solicitudes.')
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('Deteniendo servidor...')
        server.stop(0)
        print('Servidor detenido correctamente.')


if __name__ == '__main__':
    serve()
