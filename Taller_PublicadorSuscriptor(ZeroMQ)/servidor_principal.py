import zmq
import re

def main():
    context = zmq.Context()

    # Socket to receive messages on
    receiver = context.socket(zmq.SUB)
    receiver.connect("tcp://10.43.101.24:5556")
    receiver.setsockopt_string(zmq.SUBSCRIBE, "ClientRequest")
    receiver2 = context.socket(zmq.SUB)
    receiver2.connect("tcp://10.43.103.83:5558")
    receiver2.setsockopt_string(zmq.SUBSCRIBE, "ServerReply")

    # Socket to send messages on
    sender = context.socket(zmq.PUB)
    sender.connect("tcp://10.43.101.24:5555")

    sender2 = context.socket(zmq.PUB)
    sender2.connect("tcp://10.43.103.83:5557")

    print("Server Principal is running and waiting for messages...")

    while True:
        # Recibir mensaje del cliente
        message = receiver.recv_string()
        topic, operacion = message.split(',', 1)
        
        # Procesar la cadena de operación
        numeros = re.findall(r'\d+\.?\d*', operacion)
        operadores = re.findall(r'[+-]', operacion)
        
        num1 = float(numeros[0])  # Inicializa con el primer número
        resultado = num1
        
        
        i = 1
        j = 0
        while i < (len(numeros)):
            operador = operadores[j]
            num2 = numeros[i]
            # Enviar la suboperación al servidor correspondiente
            
            if operador == '+':
                sender2.send_string(f"ServerRequestSuma,{resultado},{num2}")
                
                # Esperar hasta 5 segundos por una respuesta
                if receiver2.poll(5000): 
                    response = receiver2.recv_string()
                    _, result = response.split(',', 1)
                    resultado = float(result)
                else:
                    print("Timeout: No response from operation servers")
                    print("No hubo operación recibida por los servidores, operación realizada en servidor principal")
                    resultado = resultado + num2   
            elif operador == '-':
                sender2.send_string(f"ServerRequestResta,{resultado},{num2}")
                # Esperar hasta 5 segundos por una respuesta
                if receiver2.poll(5000): 
                    response = receiver2.recv_string()
                    _, result = response.split(',', 1)
                    resultado = float(result)
                else:
                    print("Timeout: No response from operation servers")
                    print("No hubo operación recibida por los servidores, operación realizada en servidor principal")
                    resultado = resultado - num2
            i=i+1
            j=j+1
        

        # Enviar el resultado final al cliente
        sender.send_string(f"ClientReply,{resultado}")
        print(f"Sent final result to client: {resultado}")
             

if __name__ == "__main__":
    main()