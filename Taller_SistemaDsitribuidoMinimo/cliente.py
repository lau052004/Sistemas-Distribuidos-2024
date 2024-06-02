import socket

# Definimos la dirección IP y el puerto del servidor al que nos conectaremos
HOST = 'localhost'  # Cambia 'dirección_IP_del_servidor' por la dirección IP del servidor
PORT = 12345       # Puerto del servidor

# Creamos un socket TCP/IP
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Nos conectamos al servidor
client_socket.connect((HOST, PORT))

# Enviamos la operación y los números al servidor
operacion = input("Ingrese la operación (suma/resta): ")
num1 = float(input("Ingrese el primer número: "))
num2 = float(input("Ingrese el segundo número: "))

# Construimos el mensaje a enviar
mensaje = f"{operacion},{num1},{num2}"

# Enviamos el mensaje al servidor
client_socket.sendall(mensaje.encode())

# Recibimos la respuesta del servidor y la decodificamos
data = client_socket.recv(1024).decode()

# Convertimos la respuesta a un entero
# Convertimos primero a float y luego a entero
resultado_entero = int(float(data))

print('Respuesta del servidor (entero):', resultado_entero)

# Cerramos la conexión con el servidor
client_socket.close()
