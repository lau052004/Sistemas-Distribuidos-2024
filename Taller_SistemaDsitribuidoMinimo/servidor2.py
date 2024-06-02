import socket

# Definimos la dirección IP y el puerto en el que escuchará el servidor secundario
# Esto significa que escuchará en todas las interfaces de red disponibles
HOST = 'localhost'
PORT = 12346       # Puerto de escucha

# Creamos un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlazamos el socket a la dirección y puerto especificados
server_socket.bind((HOST, PORT))

# Ponemos el servidor en modo de escucha
server_socket.listen(1)

print('El servidor secundario está escuchando en {}:{}'.format(HOST, PORT))

while True:
    # Esperamos a que llegue una conexión
    client_socket, client_address = server_socket.accept()

    print('Conexión establecida desde:', client_address)

    # Recibimos los datos del cliente
    data = client_socket.recv(1024)
    if not data:
        break

    # Decodificamos los datos recibidos
    operacion, num1, num2 = data.decode().split(',')
    num1 = float(num1)
    num2 = float(num2)

    # Realizamos la operación de suma
    resultado = num1 + num2

    # Imprimimos la respuesta antes de enviarla
    print(f'Respuesta al servidor principal: {resultado}')

    # Enviamos la respuesta al servidor principal
    client_socket.sendall(str(resultado).encode())

    # Cerramos la conexión con el cliente
    client_socket.close()
