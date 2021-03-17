import socket
from threading import Thread

# Ask if the user wants to specify a IP or if the user wants to connect to localhost
decision = input("Enter 'l' to connect to localhost (default) or use 'o' to enter own IP address: ")
if decision.strip() == 'o':
    SERVER_HOST = input("Enter a Server IP in the given format xxx.xxx.xxx.xxx: ")
else:
    SERVER_HOST = "127.0.0.1"

# Specify server port an separator token
SERVER_PORT = 5002
separator_token = "<SEP>"

# Try to connect to the server with the given IP
try:
    while True:
        # Prompt the client for a name
        name = input("Enter your name: ")

        # Initialize TCP socket
        s = socket.socket()

        # Try to connect to the server and send the username
        print(f"[*] Trying to connect to {SERVER_HOST}:{SERVER_PORT}...")
        s.connect((SERVER_HOST, SERVER_PORT))
        s.send(name.encode())

        # Get the response message from the server
        initial_msg = s.recv(1024).decode()

        # If username is taken request new name
        if initial_msg == "Username already used, please enter new username!\nYou will be logged in again.":
            continue

        # If the connection is successful show the user the keywords of the server
        else:
            print("[+] Connected.")
            print("-" * 25)
            print(initial_msg)
            print("-" * 25)
            print("Keywords for this server:\n"
                  "'users': Lists all active users.\n"
                  "'all: Sends a message to all users.\n"
                  "'q': Leaves the server and quits the program.")
            print("-" * 25)
            break


    def listen_for_messages():
        """
        Function to listen for messages from the server and print them to the user
        """
        while True:
            message = s.recv(1024).decode()

            # If server returns the quit message, break the loop to quit the thread
            if message == 'q':
                break
            print(message)


    # Make a thread that listens for messages to this client & print them
    t = Thread(target=listen_for_messages)
    t.start()

    while True:
        # Input message we want to send to the server
        to_send = input()

        # Exit the program by typing 'q' and give the server the info that the user is leaving
        if to_send.lower() == 'q':
            to_send = f"{name}{separator_token}{to_send}"
            s.send(to_send.encode())
            break

        # Send the message to the server in the format 'name<SEP>message'
        else:
            to_send = f"{name}{separator_token}{to_send}"
            s.send(to_send.encode())

    # Join the thread back to the main thread and close the socket
    t.join()
    s.close()

# Very broad exception to catch every problem with the connection
except:
    print(f"Connection to server with IP {SERVER_HOST} failed.")
