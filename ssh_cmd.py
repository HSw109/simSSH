import paramiko
import getpass

def ssh_command(ip, port, user, passwd):
    client = paramiko.SSHClient()

    # Because we’re controlling both ends of this connection
    # we set the policy to accept the SSH key for the SSH server we’re connecting to and make the connection
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=int(port), username=user,
                   password=passwd, timeout=1)
    while True:
        cmd = input('Enter command or <CR>: ') 
        if not cmd.strip():
            return

        _, stdout, stderr = client.exec_command(cmd)
        output = stdout.readlines() + stderr.readlines()
        if output:
            print('--- Output ---')
            for line in output:
                print(line.strip())


if __name__ =='__main__':
    # user = getpass.getuser()
    user = input('Username: ')
    password = getpass.getpass()
    ip = input('Enter server IP: ') 
    port = input('Enter port or <CR>: ')
    
    while True: 
        ssh_command(ip, port, user, password)
