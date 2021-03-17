import socket
from threading import Thread

# Set initial parameters
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5002
separator_token = "<SEP>"

# users = {username: socket}
users = {}

# Saves the last message for every user
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
    This function keeps listening to the 'cs' socket.

    :param cs: The socket to listen for messages from
    :return: None
    """

    global users

    while True:
        try:
            # keep listening for a message from `cs` socket
            msg = cs.recv(1024).decode()

            # Try if message is not empty
            # After closing from clientside there comes another empty string
            if not msg:
                continue

        # Catch Exception from when the socket quit
        except Exception as e:
            # Client is not connected anymore, remove it from set (client_sockets) and dictionary (users)
            print(f"[!] Error: {e}")
            client_sockets.remove(cs)
            username = [key for key,value in users.items() if value == cs]
            users = {key:value for key,value in users.items() if value != cs}

            # Send message to everyone that the user has left
            for key, value in users.items():
                value.send(f">>{username[0]}<< has left.".encode())
            break
        else:
            # Split received message by the separator token
            # The message is split into two parts info[0]=sender, info[1]=message
            info = msg.split(separator_token)

            # If the message is 'users', send a list of all active users back
            if info[1].lower() == 'users':
                user_socket = users[info[0]]
                usernames = ', '.join(list(users.keys()))
                user_socket.send(usernames.encode())

            # If the message is 'all', send the next message to all active users
            elif info[1].lower() == 'all':
                alle_user = [name for name in users.keys()]
                user_dict[info[0]] = alle_user
                user_socket = users[info[0]]
                user_socket.send(f"Please write a message:".encode())

            # If the message is 'q', send a 'q' back to the user so his client quits
            elif info[1].lower() == 'q':
                user_socket = users[info[0]]
                user_socket.send("q".encode())

            # If the user sends a name of another user, send the next message to the given user
            elif info[1] in users.keys():
                user_dict[info[0]] = [info[1]]
                user_socket = users[info[0]]
                user_socket.send(f"Enter your message to >>{user_dict[info[0]][0]}<<".encode())

            # If its a normal message try if there is a user to send it to, otherwise request a username
            else:
                try:
                    for name in user_dict[info[0]]:
                        user_socket = users[name]
                        user_socket.send(': '.join(info).encode())
                except KeyError:
                    user_socket = users[info[0]]
                    user_socket.send("Please set recipient of message first!".encode())


while True:
    # Keep listening for new connections all the time
    client_socket, client_address = s.accept()
    print(f"[+] {client_address} connected.")   

    # Receive username
    user = client_socket.recv(1024).decode()

    # If the username is already taken send a message back saying to enter a new username
    if user in users.keys():
        client_socket.send("Username already used, please enter new username!\n"
                           "You will be logged in again.".encode())

    # The user is new
    else:
        # Send a message to every active user that someone has joined
        for usersocket in users.values():
            usersocket.send(f">>{user}<< has entered. UwU".encode())

        # Check if the user is the first, if so tell him. Otherwise tell him who is active
        usernames = ', '.join(list(users.keys()))
        if not usernames:
            client_socket.send("You are the first :)".encode())
        else:
            client_socket.send(f"Aktive users:\n{usernames}".encode())

        # Add the user with his socket to the users dictionary
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
