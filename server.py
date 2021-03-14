import socket
from threading import Thread

# server's IP address
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002 # port we want to use
separator_token = "<SEP>" # we will use this to separate the client name & message
users = {}
user_dict = {}

# initialize list/set of all connected client's sockets
client_sockets = set()
# create a TCP socket
s = socket.socket()
# make the port as reusable port
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
# bind the socket to the address we specified
s.bind((SERVER_HOST, SERVER_PORT))
# listen for upcoming connections
s.listen(5)
print(f"[*] Listening as {SERVER_HOST}:{SERVER_PORT}")


def listen_for_client(cs):
    """
    This function keep listening for a message from `cs` socket
    Whenever a message is received, broadcast it to all other connected clients
    """
    global users
    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()
        except Exception as e:
            # client no longer connected
            # remove it from the set
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
            username = [key for key,value in users.items() if value == cs]
            users = {key:value for key,value in users.items() if value != cs}
            for key, value in users.items():
                value.send(f">>{username[0]}<< hat das Programm verlassen.".encode())
            break
        else:
            # if we received a message, replace the <SEP>
            # token with ": " for nice printing
            info = msg.split(separator_token)
            if info[1].lower() == 'users':
                #info[0] = von
                #info[1] = nachricht
                user_socket = users[info[0]]
                usernames = ', '.join(list(users.keys()))
                user_socket.send(usernames.encode())
            elif info[1].lower() == 'alle':
                alle_user = [name for name in users.keys()]
                user_dict[info[0]] = alle_user
                user_socket = users[info[0]]
                user_socket.send(f"Geben Sie Ihre Nachricht an alle ein".encode())
            elif info[1] in users.keys():
                user_dict[info[0]] = [info[1]]
                #users = {username: socket}
                #user_dict[0] = von
                #user_dict[1] = an
                user_socket = users[info[0]]
                user_socket.send(f"Geben Sie Ihre Nachricht an {user_dict[info[0]][0]} ein".encode())
            else:
                try:
                    for name in user_dict[info[0]]:
                        user_socket = users[name]
                        user_socket.send(': '.join(info).encode())
                except KeyError:
                    user_socket = users[info[0]]
                    user_socket.send("Bitte zuerst Empfänger der Nachricht eingeben!".encode())


while True:
    # we keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")   
    # recieve username and save to dictionary users
    user = client_socket.recv(1024).decode()
    if user in users.keys():
        # schick ne nachricht zurück und sag der soll nen neuen Namen eingeben
        client_socket.send("Name schon vergeben, bitte neuen Namen auswählen!\n"
                           "Bitte melden Sie sich neu an.".encode())
    else:
        for usersocket in users.values():
            usersocket.send(f"Nutzer >>{user}<< ist beigetreten UwU".encode())

        usernames = ', '.join(list(users.keys()))
        if not usernames:
            client_socket.send("Du bist der Erste :)".encode())
        else:
            client_socket.send(f"Diese Nutzer sind bereits da:\n{usernames}".encode())

        if client_socket not in users.values():
            users[user] = client_socket

        # add the new connected client to connected sockets
        client_sockets.add(client_socket)
        # start a new thread that listens for each client's messages
        t = Thread(target=listen_for_client, args=(client_socket,))
        # make the thread daemon so it ends whenever the main thread ends
        t.daemon = True
        # start the thread
        t.start()


# close client sockets
for cs in client_sockets:
    cs.close()
# close server socket
s.close()
