import argparse
import socket
from loguru import logger
import sys
import encryption
import time

# the default values for the IP address and the port of the server
IP = '127.0.0.1'
PORT = 7777
# the command to send to the server
TIME = 'TIME'.encode('utf-8')
TEMP = 'TEMP'.encode('utf-8')
DATE = 'DATE'.encode('utf-8')

if __name__ == '__main__':
    # argument parser for using the command line to provide arguments
    parser = argparse.ArgumentParser(prog="Date, Time, Temp client",
        description="Create a connection to a server and request from it time, date and temperature")
    parser.add_argument('-ip', '--ipaddress', help='The IP address of the server, if not provided will be 127.0.0.1', type=str)
    parser.add_argument('-p', '--port', help='The port where the server is open, if not provided will be 7777', type=int)
    args = parser.parse_args()

    # for a beautiful output
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

    # connect to the server using a TCP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    client_socket.connect((IP, PORT))
    logger.success(f'User {socket.gethostname()} with {client_socket.getsockname()[0]} address on port {client_socket.getsockname()[1]} connected to the server with {IP} address on port {PORT}. Sum: {PORT+client_socket.getsockname()[1]}')

    # client generate his pair of keys and send the public key to the server
    client_private, client_public = encryption.get_pair_key()
    client_socket.sendall(str(client_public).encode('utf-8'))

    # client receive the public key of the server and generates the shared key
    server_key = int(client_socket.recv(1024).decode('utf-8'))
    shared_key = encryption.get_shared_key(client_private, server_key)

    try: 
        while True: 
            print('Select one of the option below:')
            print('1. Request time from the server.')
            print('2. Request date from the server.')
            print('3. Request temperature from the server.')
            print('4. Exit')
            try:
                # read the option selected by the user
                option = int(input())
                start_time = time.time() # start the timer for the RTT 
                match option:
                    case 1:
                        client_socket.sendall(encryption.encrypt(TIME, shared_key))
                    case 2:
                        client_socket.sendall(encryption.encrypt(DATE, shared_key))
                    case 3:
                        client_socket.sendall(encryption.encrypt(TEMP, shared_key))
                    case 4:
                        break
                    case _:
                        logger.error('The option is not a valid one, please try again.')
                        continue
            except:
                # handle the exception create by the int() function if the input is not a number
                logger.error('The option is not a valid one, please try again.')
                continue

            # receive the response from the server
            response = client_socket.recv(1024)

            # get the end time for RTT
            end_time = time.time()

            message = encryption.decrypt(response, shared_key).decode('utf-8') # decrypt the message
            rtt = (end_time - start_time) * 1000 # compute the RRT

            logger.info(f'Response: {message} with RTT {rtt:.4f} ms') # print the response and the RTT
    finally:
        # close the socket 
        logger.warning('Connection closed')
        client_socket.close()