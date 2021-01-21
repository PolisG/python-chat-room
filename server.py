import threading
import socket

#define host address, port number
host = '127.0.0.1'  #localhost (can also be the ip of the server if it's running on web server)
port = 49800        #random port - not from well-known ports (0-1023) or registered ports (1024-49151)

#starting the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))   #bind server to host and ip address
server.listen()             #listen for incoming connections


#client and nickname lists
clients = []
nicknames = []


#broadcast function - sends message to all connected clients
def broadcast(msg):
    for client in clients:
        client.send(msg)


#handle function - handles messages from clients
def handle(client):
    while True:
        try:
            special_msg = msg = client.recv(1024)                   #special_msg for kick or ban
            if special_msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    user_to_kick = special_msg.decode('ascii')[5:]  #after the first 5 characters (kick+space)
                    kick_user(user_to_kick)
                else:
                    client.send('Command was refused!'.encode('ascii'))
            elif special_msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    user_to_ban = special_msg.decode('ascii')[4:]   #after the first 4 characters (ban+space)
                    ban_user(user_to_ban)
                    
                    with open('banned_users.txt','a') as bu:
                        bu.write(f'{user_to_ban}\n')
                    print(f'{user_to_ban} was banned from the server!')
                else:
                    client.send('Command was refused!'.encode('ascii'))
            else:
                broadcast(msg)          #broadcast the message to all other clients
        except:
            if client in clients:
                index = clients.index(client)   #remove client from the list
                clients.remove(client)
                client.close()
                
                nickname = nicknames[index]
                nicknames.remove(nickname)
                broadcast(f'{nickname} has left the chat.'.encode('ascii'))
                break


#receive function
def receive():
    while True:
        client, address = server.accept()   #accept method returns a client and his address
        print("Connected with {}".format(str(address)))

        client.send('nick'.encode('ascii')) #message visible only to the client to give his nickname
        nickname = client.recv(1024).decode('ascii')

        with open('banned_users.txt','r') as bu:
            bans = bu.readlines()

        if nickname+'\n' in bans:           #refuse connection to banned client
            client.send('BAN'.encode('ascii'))
            client.close()                  #close connection to the client
            continue

        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'adminpwd':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue
        
        nicknames.append(nickname)          #add nickname to nicknames list
        clients.append(client)              #add client to clients list

        print(f'Nickname of the client is {nickname}.')
        broadcast(f'{nickname} has joined the chat!'.encode('ascii'))
        client.send("Connected to the server!".encode('ascii'))     #let the client know that he has connected successfully to the server

        thread = threading.Thread(target=handle, args=(client,))   #one thread per client connected to handle them at the same time
        thread.start()


def kick_user(user):
    if user in nicknames:
        user_index = nicknames.index(user)  #find the position of user in nicknames which is the same position as the client
        client_to_kick = clients[user_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were kicked from the server by the admin.'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(user)
        broadcast(f'{user} was kicked from the server by the admin!'.encode('ascii'))


def ban_user(user): 
    if user in nicknames:
        user_index = nicknames.index(user)  #find the position of user in nicknames which is the same position as the client
        client_to_ban = clients[user_index]
        clients.remove(client_to_ban)
        client_to_ban.send('You were banned from the server by the admin.'.encode('ascii'))
        client_to_ban.close()
        nicknames.remove(user)
        broadcast(f'{user} was banned from the server by the admin!'.encode('ascii'))


print("Server is listening...")
receive()
