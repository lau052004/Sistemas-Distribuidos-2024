import zmq
import re

def main():
    context = zmq.Context()
    
    # Socket to receive messages on
    receiver = context.socket(zmq.SUB)
    receiver.connect("tcp://10.43.103.83:5558")
    receiver.setsockopt_string(zmq.SUBSCRIBE, "ServerRequestResta")
    
    # Socket to send messages on
    sender = context.socket(zmq.PUB)
    sender.connect("tcp://10.43.103.83:5557")

    print("Server 3 is running and waiting for subtraction operations...")
    
    while True:
        # Receive a message
        message = receiver.recv_string()
        print(f"Received operation: {message}")
        topic, num1, num2 = message.split(',')
        
        num1 = float(num1)
        num2 = float(num2)
        
        resultado = num1-num2
        

        print(f"Substraction operation received: {num1} - {num2} = {resultado}")
        response = f"ServerReply,{resultado}"
        sender.send_string(response)
        print("Sent substraction result to broker")
        

if __name__ == "__main__":
    main()
