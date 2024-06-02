import socket

# Definimos la dirección IP y el puerto en el que escuchará el servidor principal
# Esto significa que escuchará en todas las interfaces de red disponibles
HOST = 'localhost'
PORT = 12345       # Puerto de escucha

# Creamos un socket TCP/IP
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Enlazamos el socket a la dirección y puerto especificados
server_socket.bind((HOST, PORT))

# Ponemos el servidor en modo de escucha
server_socket.listen(1)

print('El servidor principal está escuchando en {}:{}'.format(HOST, PORT))

# Esperamos a que llegue una conexión
client_socket, client_address = server_socket.accept()

print('Conexión establecida desde:', client_address)

while True:
    # Recibimos los datos del cliente
    data = client_socket.recv(1024)
    if not data:
        break

    # Decodificamos los datos recibidos
    operacion, num1, num2 = data.decode().split(',')
    num1 = float(num1)
    num2 = float(num2)

    # Imprimimos la operación y los números recibidos
    print(f'Operación: {operacion}, Número 1: {num1}, Número 2: {num2}')

    try:
        if operacion == 'suma':
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as secondary_server_socket:
                # Cambia con la dirección IP del servidor secundario
                secondary_server_socket.connect(
                    ('localhost', 12346))
                secondary_server_socket.sendall(data)
                resultado_bytes = secondary_server_socket.recv(1024)
                # Decodificamos la respuesta del servidor secundario
                resultado = resultado_bytes.decode()
        elif operacion == 'resta':
            # Delegamos la operación de resta a un servidor secundario
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as secondary_server_socket:
                # Cambia con la dirección IP del servidor secundario
                secondary_server_socket.connect(
                    ('localhost', 12347))
                mensaje = f"{operacion},{num1},{num2}"
                secondary_server_socket.sendall(mensaje.encode())
                resultado_bytes = secondary_server_socket.recv(1024)
                # Decodificamos la respuesta del servidor secundario
                resultado = resultado_bytes.decode()
        else:
            resultado = 'Operación no válida'

    except Exception as e:
        # Manejo de excepciones: si la conexión con el servidor secundario falla, realiza la operación en el servidor principal
        print("Error en la conexión con el servidor secundario:", e)
        if operacion == 'suma':
            resultado = num1 + num2
        elif operacion == 'resta':
            resultado = num1 - num2
        else:
            resultado = 'Operación no válida'

    # Enviamos la respuesta al cliente
    client_socket.sendall(str(resultado).encode())

# Cerramos la conexión con el cliente
client_socket.close()
