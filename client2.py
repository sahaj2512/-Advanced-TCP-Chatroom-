import socket
import threading

nickname = input("choose a nickname: ")
if nickname == 'admin':
    password = input("Password?: ")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55545))  #after this request, server will trigger the accept & client is accepted

stop_thread = False

def recieve():
    while True:

        global stop_thread
        if stop_thread:
            break

        try:
            message = client.recv(1024).decode('ascii')  #client recvs mssg from server
            if message == 'NICK':
                client.send(nickname.encode('ascii'))  #client sends msssg to server
                
                #for ADMIN conrtols
                next_mssg = client.recv(1024).decode('ascii')
                if next_mssg == 'Password?: ': 
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == "REFUSE":
                        print("Connection Refused, Wrong Password")
                        stop_thread = True 
                elif next_mssg == 'BAN':
                    print("Connection refused because of BAN!")
                    client.close()
                    stop_thread = True  # used when Banned or Refused access

            else:
                print(message)

        except:
            print("An error Occurred!")
            client.close() #close connection with the client
            break

def write():  #client writes mssg
    while True:

        if stop_thread:
            break

        message = f'{nickname}: {input("")}'  
        if message[len(nickname)+2:].startswith('/'):
            #username: /whatever  ,  checking if '/' is first thing written, then it is admin command 
            if nickname == 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+2+6:]}'.encode('ascii')) # 6 is /kick and space 
                elif message[len(nickname)+2:].startswith('/ban'):                     
                    client.send(f'BAN {message[len(nickname)+2+5:]}'.encode('ascii'))
            else:
                print("Commands can only be executed by the admin")
        else:
            client.send(message.encode('ascii'))

recieve_thread = threading.Thread(target=recieve) #these threads recieve from and send mssg to the server
recieve_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

