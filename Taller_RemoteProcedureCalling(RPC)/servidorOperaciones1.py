from concurrent import futures
import grpc
import calculo_servicio_pb2
import calculo_servicio_pb2_grpc

# Clase del servicio que implementa la funcionalidad de suma


class SumaService(calculo_servicio_pb2_grpc.CalculadoraServicer):
    def Suma(self, request, context):
        resultado = request.num1 + request.num2
        print(
            f'Recibida solicitud de suma: {request.num1} + {request.num2} = {resultado}')
        return calculo_servicio_pb2.OperacionResponse(resultado=resultado)

# Función para iniciar el servidor


def serve():
    print('Iniciando servidor de suma...')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    # Añadir la clase SumaService al servidor gRPC
    calculo_servicio_pb2_grpc.add_CalculadoraServicer_to_server(
        SumaService(), server)
    # Definir el puerto en el que escucha el servidor
    server.add_insecure_port('localhost:12346')
    server.start()
    print('Servidor de suma iniciado en el puerto 12346.')
    print('Esperando solicitudes de suma...')
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        print('Deteniendo servidor de suma...')
        server.stop(0)
        print('Servidor de suma detenido correctamente.')


if __name__ == '__main__':
    serve()
