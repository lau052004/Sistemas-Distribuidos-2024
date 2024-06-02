import zmq
import time
import threading
def proxy_thread(frontend, backend):
    try:
        zmq.proxy(frontend, backend)
    except Exception as e:
        print(f"Error in proxy thread: {e}")
    finally:
        frontend.close()
        backend.close()


def main():
    print("Broker ejecutandose y esperando conexiones...")
    
    context = zmq.Context()

    # Socket facing publishers (publicadores)
    frontend = context.socket(zmq.SUB)
    frontend.bind("tcp://*:5555")
    frontend.setsockopt_string(zmq.SUBSCRIBE, 'ClientRequest')
    frontend.setsockopt_string(zmq.SUBSCRIBE, 'ClientReply')

    # Socket facing subscribers (subscriptores)s
    backend = context.socket(zmq.PUB)
    backend.bind("tcp://*:5556")

    sts = context.socket(zmq.SUB)
    sts.bind("tcp://*:5557")
    sts.setsockopt_string(zmq.SUBSCRIBE, 'ServerRequestSuma')
    sts.setsockopt_string(zmq.SUBSCRIBE, 'ServerRequestResta')
    sts.setsockopt_string(zmq.SUBSCRIBE, 'ServerReply')

    stsbackend = context.socket(zmq.PUB)
    stsbackend.bind("tcp://*:5558")
    # Initialize a proxy instance 
   
    thread1 = threading.Thread(target=proxy_thread, args=(frontend, backend))
    thread2 = threading.Thread(target=proxy_thread, args=(sts, stsbackend))

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()

    context.term()

if __name__ == "__main__":
    main()
