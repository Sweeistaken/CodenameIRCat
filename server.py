#!/usr/bin/python3
__version__ = 0
print(f"INTERNET RELAY CAT v{__version__}")
print("Welcome! /ᐠ ˵> ⩊ <˵マ")
import socket, time, threading, traceback
from requests import get
ip = get('https://api.ipify.org').content.decode('utf8')
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server = "127.0.0.1"
displayname = "SWEE.codes"
server_address = ('0.0.0.0', 6667)
tcp_socket.bind(server_address)
tcp_socket.listen(1)
nickname_list = {}
channels_list = {}
flags_list =    {}
print("Now listening on port 6667")
def session(connection, client):
    pending = None
    already_set = False
    ready = False
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
                    if text.split(" ")[0] == "NICK":
                        pending = text.split(" ")[1]
                        if pending in nickname_list:
                            connection.sendall(bytes(f":{server} 433 * {pending} :Nickname is already in use.\r\n","UTF-8"))
                            pending = None
                        else:
                            if not already_set:
                                connection.sendall(bytes(f":{server} 001 {pending} :Welcome to the {displayname} Internet Relay Chat Network {pending}\r\n", "UTF-8"))
                                connection.sendall(bytes(f":{server} 002 {pending} :Your host is {server}[{ip}/6667], running version IRCat-v{__version__}\r\n", "UTF-8"))
                                connection.sendall(bytes(f":{pending} MODE {pending} +iw\r\n","UTF-8"))
                                nickname_list[pending] = connection
                                already_set = True
                    if text.split(" ")[0] == "USER":
                        if not ready:
                            username = text.split(" ")[1]
                    if text.split(" ")[0] == "JOIN":
                        channel = text.split(" ")[1]
                        success = True
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
                                nickname_list[i].sendall(bytes(f":{pending}!~oreo@{client[0]} JOIN {channel}\r\n","UTF-8"))
                            except:
                                pass
                    if text.split(" ")[0] == "PART":
                        channel = text.split(" ")[1]
                        for i in channels_list[channel]:
                            try:
                                nickname_list[i].sendall(bytes(f":{pending}!~oreo@{client[0]} {text}\r\n","UTF-8"))
                            except:
                                pass
                        try:
                            channels_list[channel].remove(pending)
                        except:
                            print(traceback.format_exc())
                    if text.split(" ")[0] == "WHO":
                        channel = text.split(" ")[1]
                        if channel in channels_list:
                            if pending in channels_list[channel]:
                                users = " ".join(channels_list[channel])
                                connection.sendall(bytes(f":{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                        connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                    if text.split(" ")[0] == "PRIVMSG":
                        target = text.split(" ")[1]
                        if target in channels_list:
                            if pending in channels_list[target]:
                                for i in channels_list[channel]:
                                    try:
                                        if i != pending:
                                            nickname_list[i].sendall(bytes(f":{pending}!~oreo@{client[0]} {text}\r\n","UTF-8"))
                                    except:
                                        pass
                        elif target in nickname_list:
                            nickname_list[target].sendall(bytes(f":{pending}!~oreo@{client[0]} {text}\r\n","UTF-8"))
                        else:
                            nickname_list[target].sendall(bytes(f":{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                        nickname_list[i].sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                    if text.split(" ")[0] == "QUIT":
                        # Parse the quit message.
                        done = []
                        msg = text.split(" ")[1:]
                        if len(msg) > 0:
                            mse = " ".join(msg)
                            msg = f"Quit: {mse}"
                        else:
                            msg = "Client Quit"
                        text = f"QUIT :{msg}"
                        # Broadcast all users in the joined channels that the person left.
                        for i in channels_list:
                            if pending in i:
                                for j in channels_list[i]:
                                    if j != pending and not j in done:
                                        nickname_list[j].sendall(bytes(f":{pending}!~oreo@{client[0]} {text}\r\n","UTF-8"))
                                        done.append(j)
                                # Remove the quitting user from the channel.
                                channels_list[i].remove(pending)
                        # Finally, confirm that the client quitted by mirroring the QUIT message.
                        connection.sendall(bytes(f":{pending}!~oreo@{client[0]} {text}\r\nERROR :Closing Link: {client[0]} ({msg})\r\n","UTF-8"))
                        break
            except:
                print(traceback.format_exc())
            
            if not data:
                break
    finally:
        connection.close()
    if pending != None:
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