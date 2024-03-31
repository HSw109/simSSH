# Creating an separate SSH server

import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))

HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event   # self.event initially = False

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == 'truong') and (password == 'sekret'):
            return paramiko.AUTH_SUCCESSFUL
        
if __name__ == '__main__':
    server = '192.155.34.104'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing local addresses
        sock.bind((server, ssh_port))     # Binds on server address
        sock.listen(100)
        print('[+] Listening for connection ...')
        client, addr = sock.accept()        
    except Exception as e:
        print('[-] Listen failed: ' + str(e))
        sys.exit(1)
        
    else:
        print(f'[+] Got a connection! from {addr[0]}:{addr[1]}')

    # Create a new SSH session over an existing socket, or socket-like object. This only creates the .Transport object; it doesn't begin the SSH session yet.
    bhSession = paramiko.Transport(client)  # bhSession => SSH object from received socket object 
    bhSession.add_server_key(HOSTKEY)       # add key to SSH object
    server = Server()

    # Negotiate a new SSH2 session as a server. This is the first step after creating a new .Transport and setting up your server host key(s). A separate thread is created for protocol negotiation.
    # If an event is passed in, this method returns immediately. When negotiation is done (successful or not), the given Event will be triggered. On failure, is_active will return False.
    bhSession.start_server(server=server)

    channel = bhSession.accept(20)        # Returning the channel opened by client, timeout = 20
    if channel is None:
        print('*** No channel.')
        sys.exit()

    print('[+] Authenticated!')
    print(channel.recv(1024))           # Print received data of channel, which is the first command (argument) we get from ssh_rcmd.py
    channel.send('Welcome to my SSH server')   # Send a message confirm that connect successfully to client
    try:
        while True:
            command = input('Enter command: ')    # Loops for entering commands
            if command != 'exit':
                channel.send(command)               # Sending command to client, which gonna be executed by the client (var: command in line 28 of ssh_rcmd.py)
                response = channel.recv(8192)         
                print(response.decode())            # Print the response after executed by client
            else:
                channel.send('exit')
                print('*** Exiting...')             # Exit 
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()

 
        
