import threading  
import socket

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 

server.bind(('127.0.0.1', 55545))

server.listen()  

clients = []
nicknames = []

def broadcast(message): 
    for client in clients:
        client.send(message)

def handle(client):
    while True:
        try: 
            msg = message = client.recv(1024)  #recieve message from client  #msg also taken to check for kick or ban msgs

            # if message.decode('ascii')[len(nickname)+2:] =='#active':
            #     nickname.send(f'total active users are {len(nicknames)}'.encode('ascii'))
           
            if msg.decode('ascii').startswith('KICK'):  #Client can return after a kick
                if nicknames[clients.index(client)] == 'admin':   #check index of that nname admin
                    name_to_kick = msg.decode('ascii')[5:]  # as /KICK then the nickname of client to be kicked
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused'.encode('ascii'))

            elif msg.decode('ascii').startswith('BAN'):  #Client cannot return after a ban
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            else: 
                broadcast(message)  #broadcast that mssg to other clients
        except:
            if client in clients:  #this condn reqd otherwise banned and kicked clients will throw error
                index = clients.index(client)  
                clients.remove(client) 
                client.close() 
                nickname = nicknames[index]  
                broadcast(f'{nickname} left the chat!'.encode('ascii')) 
                print(f'{nickname} left the chat!')
                nicknames.remove(nickname)
                break

def recieve():
    while True: 
        client, address = server.accept()  
        print(f"connected with {str(address)}")

        client.send('NICK'.encode('ascii')) 
        
        nickname = client.recv(1024).decode('ascii')  #client sends data for nickname
        
        with open('bans.txt', 'r') as f:
            bans = f.readlines()  #as line-wise
        
        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue
        
        if nickname == 'admin':
            client.send('Password?: '.encode('ascii'))
            password = client.recv(1024).decode('ascii')
            if password != '$ahaj':
                client.send('REFUSE'.encode('ascii'))
                client.close() #connection to client is closed
                continue  #do not break, as we in while loop

        nicknames.append(nickname)  #append nickname of client to the list 
        clients.append(client)   #append nickname of client to the list 

        print(f'Nickname of client is {nickname}!!')   #informing other clients
        broadcast(f'{nickname} joined the chat'.encode('ascii'))   #broadcasting to all clients
        client.send('Connected to the Server!'.encode('ascii'))  #server infroms new client that he is connectecd

        thread = threading.Thread(target=handle, args=(client,))  
        #as we have to handle multiple clients, and so multiple threads.
        thread.start()  # we can't send and recv data serially, and for parallel exec, we use threads

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked by an admin!'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was kicked by an admin!'.encode('ascii'))


print("server is listening..")

recieve()  # as the recieve fn is itself calling the handle fn whcih thereby calls the broadcast
#RECIEVE() & HANDLE() are in parallel so that mssg handling and client joining & all can take parallely