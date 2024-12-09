#!/usr/bin/python3
__version__ = "0.0.1-pre-alpha"
print(f"INTERNET RELAY CAT v{__version__}")
print("Welcome! /ᐠ ˵> ⩊ <˵マ")
import socket, time, threading, traceback, sys, os, yaml
from requests import get
if not len(sys.argv) == 2:
    print("IRCat requires the following arguments: config.yml")
    sys.exit(1)
server = "127.0.0.1"
displayname = "foo"
with open(sys.argv[1], 'r') as file:
    data = yaml.safe_load(file)
    try: server = data["host"]
    except: print("using fallback server address")
    try: displayname = data["name"]
    except: print("using fallback display name")
    file.close()
    print("Successfully loaded config!")
ip = get('https://api.ipify.org').content.decode('utf8')
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('0.0.0.0', 6667)
tcp_socket.bind(server_address)
tcp_socket.listen(1)
nickname_list = {}
channels_list = {}
flags_list =    {}
print("Now listening on port 6667")
def session(connection, client):
    pending = "*" # The nickname of the client
    already_set = False # If the client gave the server a NICK packet
    ready = False # If the client gave the server a USER packet
    finished = False # If the server gave the client its information, indicating it's ready.
    username = "oreo"
    hostname = client[0]
    try:
        print("Connected to client IP: {}".format(client))
        connection.sendall(bytes(f":{server} NOTICE * :*** Looking for your hostname...\r\n","UTF-8"))
        connection.sendall(bytes(f":{server} NOTICE * :*** Oof! Can't find your hostname, using IP...\r\n","UTF-8"))
        
        while True:
            try:
                data = connection.recv(2048)
            except:
                print("Disconnected.")
            print("Received data: {}".format(data))
            try:
                textt = data.decode()
                for text in textt.split("\r\n"):
                    command = text.split(" ")[0].upper()
                    try:
                        args = text.split(" ")[1:]
                    except:
                        pass
                    if command == "NICK":
                        pending = text.split(" ")[1]
                        if pending in nickname_list:
                            connection.sendall(bytes(f":{server} 433 * {pending} :Nickname is already in use.\r\n","UTF-8"))
                            pending = "*"
                        else:
                            if not already_set:
                                nickname_list[pending] = connection
                                already_set = True
                    elif command == "USER":
                        if not ready:
                            username = text.split(" ")[1]
                            ready = True
                    elif "CAP LS 302" in text:
                        connection.sendall(bytes(f":{server}  CAP * LS :", "UTF-8"))
                    elif (ready and already_set) and not finished:
                        connection.sendall(bytes(f":{server} 001 {pending} :Welcome to the {displayname} Internet Relay Chat Network {pending}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 002 {pending} :Your host is {server}[{ip}/6667], running version IRCat-v{__version__}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 004 {pending} {server} IRCat-{__version__} iow ovmsitnlbkq\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 005 {pending} CHANMODES=bq NETWORK={displayname} CHANTYPES=# :are supported by this server\r\n", "UTF-8"))
                        
                        connection.sendall(bytes(f":{pending} MODE {pending} +iw\r\n","UTF-8"))
                        finished = True
                    elif command == "PING":
                        e = text.split(" ")[1]
                        print("Replied to PING.")
                        connection.sendall(bytes(f"PONG {e}\r\n","UTF-8"))
                    elif (ready and already_set) and finished:
                        if command == "JOIN":
                            channel = text.split(" ")[1]
                            success = True
                            if channel in channels_list:
                                if pending in channels_list[channel]:
                                    success=False
                                    print(f"{pending} is already in {channel} , ignoring JOIN request.")
                            if success:
                                try:
                                    if channel in channels_list:
                                        channels_list[channel].append(pending)
                                    else:
                                        channels_list[channel] = [pending]
                                except:
                                    connection.sendall(bytes(f":{server} NOTICE * :*** Could not join {channel}\r\n","UTF-8"))
                                print(channels_list)
                                for i in channels_list[channel]:
                                    try:
                                        nickname_list[i].sendall(bytes(f":{pending}!~{username}@{client[0]} JOIN {channel}\r\n","UTF-8"))
                                    except:
                                        pass
                            # Code re-used in the WHO command
                            if channel in channels_list:
                                    if pending in channels_list[channel]:
                                        users = " ".join(channels_list[channel])
                                        connection.sendall(bytes(f":{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                            connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                        elif command == "PART":
                            channel = text.split(" ")[1]
                            for i in channels_list[channel]:
                                try:
                                    nickname_list[i].sendall(bytes(f":{pending}!~{username}@{client[0]} {text}\r\n","UTF-8"))
                                except:
                                    pass
                            try:
                                channels_list[channel].remove(pending)
                            except:
                                print(traceback.format_exc())
                        elif command == "WHO":
                            channel = text.split(" ")[1]
                            if channel in channels_list:
                                if pending in channels_list[channel]:
                                    users = " ".join(channels_list[channel])
                                    connection.sendall(bytes(f":{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                            connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                        elif command == "PRIVMSG":
                            target = text.split(" ")[1]
                            if target in channels_list:
                                if pending in channels_list[target]:
                                    for i in channels_list[channel]:
                                        try:
                                            if i != pending:
                                                nickname_list[i].sendall(bytes(f":{pending}!~{username}@{hostname} {text}\r\n","UTF-8"))
                                        except:
                                            pass
                            elif target in nickname_list:
                                nickname_list[target].sendall(bytes(f":{pending}!~{username}@{hostname} {text}\r\n","UTF-8"))
                            else:
                                connection.sendall(bytes(f":{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                            nickname_list[i].sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                        elif command == "QUIT":
                            # Parse the quit message.
                            done = []
                            msg = text.split(" ")[1:]
                            if len(msg) > 0:
                                mse = " ".join(msg)
                                msg = f"Quit: {mse}"
                            else:
                                msg = "Client Quit"
                            text = f"QUIT :{msg}"
                            # Broadcast all users in the joined channels that the person quit.
                            for i, users in channels_list.items():
                                if pending in users:
                                    for j in users:
                                        if j != pending and not j in done:
                                            nickname_list[j].sendall(bytes(f":{pending}!~{username}@{client[0]} {text}\r\n","UTF-8"))
                                            done.append(j)
                                    # Remove the quitting user from the channel.
                                    try:
                                        channels_list[i].remove(pending)
                                    except:
                                        print(traceback.format_exc())
                            # Confirm QUIT and close the socket.
                            connection.sendall(bytes(f":{pending}!~{username}@{client[0]} {text}\r\n","UTF-8"))
                            connection.sendall(bytes(f"ERROR :Closing Link: {client[0]} ({msg})\r\n","UTF-8"))
                            connection.close()
                            break
                        elif command == "GITSERV":
                            connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :Hello!\r\n","UTF-8"))



                        # Ignore empty text
                        elif text.split(" ")[0] == "":
                            pass
                        else:
                            # Unknown command
                            cmd = text.split(" ")[0]
                            connection.sendall(bytes(f":{server} 421 {pending} {cmd} :Unknown command\r\n","UTF-8"))
                    
                    
                        
            except:
                print(traceback.format_exc())
            
            if not data:
                break
    finally:
        connection.close()
    if pending != "*":
        del nickname_list[pending]
try:
    while True:
        connection, client = tcp_socket.accept()
        threading.Thread(target=session, daemon=True, args=[connection, client]).start()
except:
    print("Shutting down...")
    time.sleep(2)
    tcp_socket.shutdown(1)
    tcp_socket.close()