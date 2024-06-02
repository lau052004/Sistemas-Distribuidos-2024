import zmq
import sys

def main():
    context = zmq.Context()

    try:
        # Socket to talk to the server via broker
        print("Connecting to the server via broker...")
        socket = context.socket(zmq.PUB)
        socket.connect("tcp://10.43.101.24:5555")

        # Subscribe to the reply topic
        subscriber = context.socket(zmq.SUB)
        subscriber.connect("tcp://10.43.101.24:5556")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, 'ClientReply')
        
        while(True):
            operacion = input("Ingrese la operación: ")

            # Build the message with the topic
            message = f"ClientRequest,{operacion}"

            print("Sending request...")
            socket.send_string(message)

            # Receive the reply from the server
            reply_message = subscriber.recv_string()
            topic, response = reply_message.split(',', 1)

            print("Received reply:", response)

    except KeyboardInterrupt:
        print("Interrupted...")
    finally:
        print("Closing sockets and context...")
        socket.close()
        subscriber.close()
        context.term()
        sys.exit(0)

if __name__ == "__main__":
    main()
