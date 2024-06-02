import threading
import time
import zmq

PrincipalActivo = False
lock = threading.Lock()

def main():
    threading.Thread(target=manejarPrincipal).start()
    threading.Thread(target=manejarSecundario).start()

def manejarPrincipal():
    context = zmq.Context()
    receiver = context.socket(zmq.REP)
    receiver.bind("tcp://localhost:5568")
    result = receiver.recv()
    print(f"PING RECIBIDO: {result}")
    receiver.send(b"Mensaje recibido por el SC")

    sender = context.socket(zmq.REQ)
    sender.connect("tcp://localhost:5569")
    sender.setsockopt(zmq.RCVTIMEO, 5000)  # 5000 ms = 5 s
    push_socket = context.socket(zmq.PUSH)
    push_socket.connect("tcp://10.43.101.24:5590")

    global PrincipalActivo
    while True:
        try:
            sender.send_string("EXISTES?")
            message = sender.recv_string()
            print(f"Respuesta recibida: {message}")
            with lock:
                PrincipalActivo = True
            push_socket.send_string("10.43.103.83")
            print("Enviando IP del proxy principal: 10.43.103.83")
            time.sleep(5)
        except zmq.error.Again:
            print("No se recibió respuesta en 5 segundos, reintentando...")
            enviar_ip_fallback(push_socket)
        except zmq.error.ZMQError as e:
            if e.errno == zmq.EFSM:  # Estado incorrecto del socket
                sender.close()
                sender = context.socket(zmq.REQ)
                sender.connect("tcp://localhost:5569")
                sender.setsockopt(zmq.RCVTIMEO, 5000)  # Timeout de 5 segundos para recibir
                with lock:
                    PrincipalActivo = False
                result = receiver.recv()
                print(f"PING RECIBIDO: {result}")
                receiver.send(b"Mensaje recibido por el SC")
                enviar_ip_fallback(push_socket)

def enviar_ip_fallback(push_socket):
    try:
        push_socket.send_string("10.43.100.174")
        print("Enviando IP de fallback: 10.43.100.174")
    except zmq.ZMQError as e:
        print(f"Error al enviar la IP de fallback: {e}")

def manejarSecundario():
    context = zmq.Context()
    receiver = context.socket(zmq.REP)
    receiver.bind("tcp://10.43.101.86:5570")
    while True:
        result = receiver.recv()
        print(f"PROXY2: {result}")
        with lock:
            receiver.send_string(f"{PrincipalActivo}")

if __name__ == "__main__":
    main()
