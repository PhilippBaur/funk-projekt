import socket
import random
from threading import Thread
from colorama import Fore, init

# init colors
init()

# set the available colors
colors = [Fore.BLUE, Fore.CYAN, Fore.GREEN, Fore.LIGHTBLACK_EX,
    Fore.LIGHTBLUE_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTGREEN_EX,
    Fore.LIGHTMAGENTA_EX, Fore.LIGHTRED_EX, Fore.LIGHTWHITE_EX,
    Fore.LIGHTYELLOW_EX, Fore.MAGENTA, Fore.RED, Fore.WHITE, Fore.YELLOW
]

# choose a random color for the client
client_color = random.choice(colors)

# server's IP address
# if the server is not on this machine,
# put the private (network) IP address (e.g 192.168.1.2)
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 5002 # server's port
separator_token = "<SEP>" # we will use this to separate the client name & message

while True:
    # prompt the client for a name
    name = input("Enter your name: ")
    # initialize TCP socket
    s = socket.socket()
    print(f"[*] Connecting to {SERVER_HOST}:{SERVER_PORT}...")
    # connect to the server
    s.connect((SERVER_HOST, SERVER_PORT))
    s.send(name.encode())

    initial_msg = s.recv(1024).decode()
    if initial_msg == "Name schon vergeben, bitte neuen Namen auswählen!\nBitte melden Sie sich neu an.":
        pass
    else:
        print("[+] Connected.")
        print("\n" + initial_msg)
        break


def listen_for_messages():
    while True:
        message = s.recv(1024).decode()
        print("\n" + message)

# make a thread that listens for messages to this client & print them
t = Thread(target=listen_for_messages)
# make the thread daemon so it ends whenever the main thread ends
t.daemon = True
# start the thread
t.start()

while True:
    # input message we want to send to the server
    to_send = input()

    if to_send.lower() == 'users':
        to_send = f'{name}{separator_token}{to_send}'
        s.send(to_send.encode())

    # a way to exit the program
    elif to_send.lower() == 'q':
        break
    else:
        # add the datetime, name & the color of the sender
        # date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        to_send = f"{name}{separator_token}{to_send}"
        # finally, send the message
        s.send(to_send.encode())

# close the socket
s.close()
