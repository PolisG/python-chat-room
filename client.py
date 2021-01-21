import threading
import socket

#define host address, port number
localhost = '127.0.0.1'
port = 49800 

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((localhost, port))

nickname = input("Choose your nickname: ")
if nickname == 'admin':
    password = input("Enter password for admin: ")

stop_thread_flag = False

#receive function
def receive():
    while True:
        global stop_thread_flag
        if stop_thread_flag:
            break
        try: #receive message from the server if there is a nickname
            msg = client.recv(1024).decode('ascii')
            if msg == 'nick':
                client.send(nickname.encode('ascii'))
                next_msg = client.recv(1024).decode('ascii')
                if next_msg == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') == 'REFUSE':
                        print("Connection refused! Wrong password.")
                        stop_thread_flag = True
                elif next_msg == 'BAN':
                    print("Connection refused! You are banned from the server.")
                    client.close()
                    stop_thread_flag = True
            else:
                print(msg)
        except: #close connection - error
            print("An error has occured!")
            client.close()
            break

#write function - receive and print messages
def write():
    while True:
        if stop_thread_flag:
            break       #if server refuses connection stop/break the loop
        msg = '{}: {}'.format(nickname, input(''))
        
        #check if message starts with /command (e.g. /kick)
        if msg[len(nickname)+2:].startswith('/'):   #skip the length of the nickname + colon + space
            #username: /command
            if nickname == 'admin':
                if msg[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {msg[len(nickname)+8:]}'.encode('ascii'))  #nickname: /kick  -> the user to kick
                elif msg[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {msg[len(nickname)+7:]}'.encode('ascii'))   #nickname: /ban  -> the user to ban
            else:
                print("Command can't be excecuted by the user!")
        else:
            client.send(msg.encode('ascii'))


#starting threads for listening 
receive_thread = threading.Thread(target=receive)
receive_thread.start()
#starting threads for writing
write_thread = threading.Thread(target=write)
write_thread.start()
