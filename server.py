import argparse
from loguru import logger
import socket
import sys
import server_extras
from datetime import datetime
import random
import encryption
import time

# default values for the ip address where listen, the port and for the number of threads used
IP = '0.0.0.0'
PORT = 7777
THREADS = 32

def handleClient(connection, address):
    """
    Handle the client connection.

    Args:
        connetion (socket): The client connection.
    """

    # receive the public key of the client
    client_key = int(connection.recv(1024).decode('utf-8'))

    # generate the server keys and send the public one to the server
    server_private, server_public = encryption.get_pair_key()
    connection.sendall(str(server_public).encode('utf-8'))

    # generate the shared key
    shared_key = encryption.get_shared_key(server_private, client_key)
    

    try:
        while True:
            # receive the data
            data = connection.recv(1024)

            # if not data receive the client close the connection
            if not data:
                break
            
            # decrypt data and convert it to the uppercase
            input_data = encryption.decrypt(data, shared_key).decode('utf-8').strip().upper()

            response = ''
            match input_data:
                case 'TIME':
                    response = str(datetime.now().time()) # get the time using datetime module
                case 'DATE':
                    response = str(datetime.now().date()) # get the date using datetime module
                case 'TEMP':
                    response = str(random.randint(-50, 50)) + '°C' # generate a random value for temperature
            # encrypt the response and send it back to the client
            response = encryption.encrypt(response.encode('utf-8'), shared_key)
            connection.sendall(response)
    finally:
        # close the connection and display a message
        connection.close()
        logger.warning(f'Connection closed with the client with {address[0]} on port {address[1]}')

if __name__ == '__main__':
    # set the seed for random selection
    random.seed(time.time())

    # parse the argument from command line
    parser = argparse.ArgumentParser(prog="Date, Time, Temp server",
                description="Accept multiple connection from client and provide them information like time, date and temperature")
    parser.add_argument('-ip', '--ipaddress', help='The IP address of the server, if not provided will be 0.0.0.0', type=str)
    parser.add_argument('-p', '--port', help='The port where the server will be open, if not provided will be 7777', type=int)
    parser.add_argument('-t', '--threads', help='Number of threads to use, if not provided will be 32', type=int)
    args = parser.parse_args()

    # to display the logs in a better way
    logger.remove()
    logger.add(sys.stdout, colorize=True, format="<level>{level.icon}</level> <level>{message}</level>", level="DEBUG")

    logger.level(name='INFO', icon='💡', color='<magenta><bold>')
    logger.level(name='WARNING', icon='⚠️ ', color='<yellow><bold>')
    logger.level(name='DEBUG', icon='🔧', color='<blue><bold>')
    logger.level(name='ERROR', icon='🛑', color='<red><bold>')
    logger.level(name='SUCCESS', icon='✅', color='<green><bold>')

    # save in the program the informations provided by the user
    if args.ipaddress is not None:
        IP = args.ipaddress
    if args.port is not None:
        PORT = args.port
    if args.threads is not None:
        THREADS = args.threads

    # create the socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # to can reuse the port is the connection remain open 
                                                                        # when we close the program using ^C 

    # bind and open the connection
    server_socket.bind((IP, PORT))
    server_socket.listen()
    logger.success(f'Listening on {IP} port {PORT}...')
    logger.warning('To close the server press CTRL+C')

    # create the ThreadPool
    thread_pool = server_extras.ThreadPool(THREADS)

    try:
        while True:
            # accept any connection made by clients
            client_socket, client_address = server_socket.accept()
            logger.info(f'Connection open from client with ip address {client_address[0]} on port {client_address[1]}')
            # add the client in the thread pool
            thread_pool.submit(handleClient, client_socket, client_address)
    except KeyboardInterrupt:
        # close the program when the CTRL+C is pressed
        logger.warning('Server closing...')
        thread_pool.shutdown()
        server_socket.close()
