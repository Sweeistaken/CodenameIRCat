#!/usr/bin/python3
__version__ = "0.0.1-pre-alpha"
print(f"INTERNET RELAY CAT v{__version__}")
print("Welcome! /ᐠ ˵> ⩊ <˵マ")
import socket, time, threading, traceback, sys, subprocess, yaml, sqlite3, os
from requests import get
if not len(sys.argv) == 2:
    print("IRCat requires the following arguments: config.yml")
    sys.exit(1)
server = "127.0.0.1"
displayname = "foo"
identifier = "somewhere in the universe"
admin_nick = "admin"
data_path  = ""
with open(sys.argv[1], 'r') as file:
    data = yaml.safe_load(file)
    try: server = data["host"]
    except: print("using fallback server address")
    try: displayname = data["name"]
    except: print("using fallback display name")
    try: identifier = data["identifier"]
    except: print("using fallback identifier")
    try: admin_nick = data["admin-nick"]
    except: print("using fallback admin nick")
    try: data_path = data["data-path"]
    except:
        print("IRCat requires \"data-path\" in config.yml")
        sys.exit(1)
    file.close()
    print("Successfully loaded config!")
class IRCat_DATA_BROKER:
    def __init__(self):
        if not os.path.isfile(data_path):
            print("Creating database file...")
            open(data_path, "w").write("")
        self.conn = sqlite3.connect(data_path)
        self.db = self.conn.cursor()
        self.db.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='nickserv' ''')
        if self.db.fetchall()[0]!=1:
            print("Creating NickServ table...")
            self.db.execute("""CREATE table nickserv (
user varchar(255),
modes varchar(255),
hash varchar(255),
group varchar(255));""")
        self.db.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='chanserv' ''')
        if self.db.fetchall()[0]!=1:
            print("Creating ChanServ table...")
            self.db.execute("""CREATE table chanserv (
name varchar(255),
modes varchar(255),
params varchar(255),
owner varchar(255),
usermodes varchar(255),
optimodes varchar(255),
);""")
        
ip = get('https://api.ipify.org').content.decode('utf8')
tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_address = ('', 6667)
tcp_socket.bind(server_address)
tcp_socket.listen(1)
opened=True
reserved = ["nickserv", "chanserv", "gitserv"] # Reserved nicknames
nickname_list = {} # Stores nicknames and the respective sockets
lower_nicks =   {"gitserv": "GitServ"} # Nicknames in lowercase
channels_list = {} # Store channels and their user lists
property_list = {"GitServ": {"host": "IRCatCore", "username": "IRCat", "realname": "Codename IRCat Integrated services - Updates bot"}} # Stores properties for active users and channels
print("Now listening on port 6667")
def pinger(nick, connection):
    global property_list
    while nick in property_list:
        if (time.time() - property_list[nick]["last_ping"]) > 60 and not property_list[nick]["ping_pending"]:
            print("Sent ping message to " + nick)
            property_list[nick]["ping_pending"] = True
            time.sleep(0.5)
            connection.sendall(bytes(f"PING {server}\r\n","UTF-8"))
        elif property_list[nick]["ping_pending"] and ((time.time() - property_list[nick]["last_ping"]) > 120):
            property_list[nick]["cause"] = "Ping timeout: 120 seconds"
            connection.shutdown(socket.SHUT_WR)
            connection.close()
            break
def session(connection, client):
    pending = "*" # The nickname of the client
    already_set = False # If the client gave the server a NICK packet
    ready = False # If the client gave the server a USER packet
    finished = False # If the server gave the client its information, indicating it's ready.
    username = "oreo" # Username/ident specified by client
    hostname = "" # Hostname, can be IP or domain
    realname = "realname" # Realname specified by client
    safe_quit = False # If the client safely exited, or if the server should manually drop the connection
    cause = "Unknown" # The cause of the unexpected exit
    try:
        print("Connected to client IP: {}".format(client))
        connection.sendall(bytes(f":{server} NOTICE * :*** Looking for your hostname...\r\n","UTF-8"))
        try:
            hostname = socket.gethostbyaddr(client[0])[0]
            connection.sendall(bytes(f":{server} NOTICE * :*** Got it! {hostname}\r\n","UTF-8"))
        except:
            hostname = client[0]
            connection.sendall(bytes(f":{server} NOTICE * :*** Oof! Can't find your hostname, using IP...\r\n","UTF-8"))
        while True:
            try:
                data = connection.recv(2048)
            except Exception as ex:
                cause = "Read error: " + str(ex)
                break
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
                        if pending[0] == ":": pending[1:]
                        if "!" in pending or ":" in pending or "#" in pending or "*" in pending:
                            connection.sendall(bytes(f":{server} 432 * {pending} :Erroneus nickname\r\n","UTF-8"))
                            pending = "*"
                        elif pending.lower() in lower_nicks or pending in reserved:
                            connection.sendall(bytes(f":{server} 433 * {pending} :Nickname is already in use.\r\n","UTF-8"))
                            pending = "*"
                        else:
                            if not already_set:
                                already_set = True
                    elif command == "USER":
                        if not ready:
                            username = text.split(" ")[1]
                            realname = " ".join(text.split(" ")[4:])[1:]
                            ready = True
                    elif command == "CAP":
                        if args[0] == "LS":
                            connection.sendall(bytes(f":{server}  CAP * LS :\r\n", "UTF-8"))
                    elif (ready and already_set) and not finished:
                        nickname_list[pending] = connection
                        property_list[pending] = {"host": hostname, "username": username, "realname": realname, "modes": "iw", "last_ping": time.time(), "ping_pending": False}
                        lower_nicks[pending.lower()] = pending
                        threading.Thread(target=pinger, args=[pending, connection]).start()
                        connection.sendall(bytes(f":{server} 001 {pending} :Welcome to the {displayname} Internet Relay Chat Network {pending}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 002 {pending} :Your host is {server}[{ip}/6667], running version IRCat-v{__version__}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 004 {pending} {server} IRCat-{__version__} iow ovmsitnlbkq\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 005 {pending} CHANMODES=bq NETWORK={displayname} CHANTYPES=# :are supported by this server\r\n", "UTF-8"))
                        
                        connection.sendall(bytes(f":{pending} MODE {pending} +iw\r\n","UTF-8"))
                        finished = True
                    elif command == "PING":
                        e = text.split(" ")[1]
                        print("Replying with \"" + str([f":{server} PONG {server} :{e}\r\n"]) + "\"")
                        connection.sendall(bytes(f":{server} PONG {server} :{e}\r\n","UTF-8"))
                    elif (ready and already_set) and finished:
                        if command == "JOIN":
                            channels = text.split(" ")[1]
                            for channelt in channels.split(","):
                                channel = channelt.strip()
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
                                            nickname_list[i].sendall(bytes(f":{pending}!~{username}@{hostname} JOIN {channel}\r\n","UTF-8"))
                                        except:
                                            pass
                                # Code re-used in the NAMES command
                                if channel in channels_list:
                                        if pending in channels_list[channel]:
                                            users = " ".join(channels_list[channel])
                                            connection.sendall(bytes(f":{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                                connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                                print("Successfully pre-loaded /NAMES list")
                        elif command == "PONG":
                            e = text.split(" ")[1]
                            if e == server:
                                print(pending + " replied to PING.")
                                property_list[pending]["last_ping"] = time.time()
                                property_list[pending]["ping_pending"] = False
                        elif command == "PART":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            else:
                                channel = text.split(" ")[1]
                                for i in channels_list[channel]:
                                    try:
                                        nickname_list[i].sendall(bytes(f":{pending}!~{username}@{hostname} {text}\r\n","UTF-8"))
                                    except:
                                        pass
                                try:
                                    channels_list[channel].remove(pending)
                                except:
                                    print(traceback.format_exc())
                        elif command == "WHO":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            else:
                                channel = text.split(" ")[1]
                                if channel in channels_list:
                                    for i in channels_list[channel]:
                                        who_host = property_list[i]["host"]
                                        who_user = property_list[i]["username"]
                                        who_realname = property_list[i]["realname"]
                                        connection.sendall(bytes(f":{server} 352 {pending} {who_user} ~{who_host} {server} {i} H :0 {who_realname}\r\n","UTF-8"))
                                elif channel in nickname_list:
                                    who_host = property_list[channel]["host"]
                                    who_user = property_list[channel]["username"]
                                    who_realname = property_list[channel]["realname"]
                                    connection.sendall(bytes(f":{server} 352 {pending} * {who_user} ~{who_host} {server} {channel} H :0 {who_realname}\r\n","UTF-8"))

                                connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /WHO list.\r\n","UTF-8"))
                        elif command == "WHOIS":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            else:
                                target = text.split(" ")[1]
                                if target.lower() in lower_nicks:
                                    target = lower_nicks[target.lower()]
                                if target in property_list:
                                    who_user = property_list[target]["username"]
                                    who_realname = property_list[target]["realname"]
                                    who_host = property_list[target]["host"]
                                    try:
                                        who_flags = property_list[target]["modes"]
                                    except:
                                        who_flags = None
                                    connection.sendall(bytes(f":{server} 311 {pending} {target} ~{who_user} {who_host} * :{who_realname}\r\n","UTF-8"))
                                    connection.sendall(bytes(f":{server} 312 {pending} {target} {server} :{identifier}\r\n","UTF-8"))
                                    #connection.sendall(bytes(f":{server} 313 {target} :is an IRC operator\r\n","UTF-8")) # I haven't implemented modes yet.
                                    #connection.sendall(bytes(f":{server} 317 {target} {time} :seconds idle\r\n","UTF-8")) # I haven't implemented idle time yet.
                                    if who_flags != None and who_flags != "iw":
                                        connection.sendall(bytes(f":{server} 379 {pending} {target} :Is using modes +{who_flags}\r\n","UTF-8"))
                                    connection.sendall(bytes(f":{server} 318 {pending} {target} :End of /WHOIS list\r\n","UTF-8"))
                                else:
                                    connection.sendall(bytes(f":{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                        elif command == "NAMES":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            else:
                                channel = text.split(" ")[1]
                                if channel in channels_list:
                                        if pending in channels_list[channel]:
                                            users = " ".join(channels_list[channel])
                                            connection.sendall(bytes(f":{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                                connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                        elif command == "NOTICE":
                            if len(args) >= 2:
                                target = text.split(" ")[1]
                                if target.lower() in lower_nicks:
                                    target = lower_nicks[target.lower()]
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
                            else:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                        elif command == "QUIT":
                            # Parse the quit message.
                            done = []
                            msg = text.split(" ")[1:]
                            if len(msg) > 0:
                                mse = " ".join(msg)
                                msg = f"Quit: {mse}"
                            else:
                                msg = "Quit: " + pending
                            text = f"QUIT :{msg}"
                            # Broadcast all users in the joined channels that the person quit.
                            for i, users in channels_list.items():
                                if pending in users:
                                    for j in users:
                                        if j != pending and not j in done:
                                            nickname_list[j].sendall(bytes(f":{pending}!~{username}@{hostname} {text}\r\n","UTF-8"))
                                            done.append(j)
                                    # Remove the quitting user from the channel.
                                    try:
                                        channels_list[i].remove(pending)
                                    except:
                                        print(traceback.format_exc())
                            # Confirm QUIT and close the socket.
                            try:
                                connection.sendall(bytes(f":{pending}!~{username}@{hostname} {text}\r\n","UTF-8"))
                                connection.sendall(bytes(f"ERROR :Closing Link: {hostname} ({msg})\r\n","UTF-8"))
                            finally:
                                connection.close()
                                safe_quit = True
                                break
                        elif command == "MODE":
                            target = args[0]
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            elif len(args) == 1:
                                if args[0] == pending:
                                    yourmodes = property_list[pending]["modes"]
                                    connection.sendall(bytes(f":{server} 221 {pending} +{yourmodes}\r\n","UTF-8"))
                                elif args[0] in channels_list:
                                    if args[0] in property_list:
                                        if "modes" in property_list[args[0]]:
                                            # Get the modes + parameters, then print them out.
                                            modes = property_list[args[0]]["modes"]
                                            params = property_list[args[0]]["params"]
                                            connection.sendall(bytes(f":{server} 221 {pending} {target} +{modes} {params}\r\n","UTF-8"))
                                        else:
                                            # Default channel mode
                                            connection.sendall(bytes(f":{server} 324 {pending} {target} +n\r\n","UTF-8"))
                                    else:
                                        # Default channel mode
                                        connection.sendall(bytes(f":{server} 324 {pending} {target} +n\r\n","UTF-8"))
                                else:
                                    if args[0][0] == "#":
                                        connection.sendall(bytes(f":{server} 403 {pending} {target} :No such channel\r\n","UTF-8"))
                                    else:
                                        connection.sendall(bytes(f":{server} 505 {pending} :Cant change mode for other users\r\n","UTF-8"))

                        elif command == "GITSERV":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            elif args[0].upper() == "PULL":
                                updater = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
                                if updater.stdout.decode().strip() == "Already up to date.":
                                    connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :Codename IRCat is already up-to-date.\r\n","UTF-8"))
                                else:
                                    connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :Done, it is recommended to use /RESTART if you're an IRC op\r\n","UTF-8"))
                            elif args[0].upper() == "VERSION":
                                connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :Codename IRCat version {__version__}\r\n","UTF-8"))
                                connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :This is Codename IRCat's integrated services.\r\n","UTF-8"))
                            else:
                                connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :GitServ Usage:\r\n","UTF-8"))
                                connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :PULL     - Pulls the latest version of Codename IRCat\r\n","UTF-8"))
                                connection.sendall(bytes(f":GitServ!~IRCat@IRCatCore NOTICE {pending} :VERSION  - Gets the version number of this service.\r\n","UTF-8"))
                        
                        elif command == "RESTART":
                            if "o" in property_list[pending]["modes"]:
                                tcp_socket.shutdown(socket.SHUT_RDWR)
                                tcp_socket.close()
                                opened = False
                            else:
                                connection.sendall(bytes(f":{server} 481 {pending} :Permission Denied- You're not an IRC operator\r\n","UTF-8"))

                        elif command == "PRIVMSG":
                            if len(args) >= 2:
                                target = text.split(" ")[1]
                                if target.lower() in lower_nicks:
                                    target = lower_nicks[target.lower()]
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
                            else:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))



                        # Ignore empty text
                        elif text.split(" ")[0] == "":
                            pass
                        else:
                            # Unknown command
                            cmd = text.split(" ")[0]
                            connection.sendall(bytes(f":{server} 421 {pending} {cmd} :Unknown command\r\n","UTF-8"))
                        
            except Exception as ex:
                print(traceback.format_exc())
                cause = "Read error: " + str(ex)
                break
            
            if not data:
                cause = "Remote host closed the connection"
                break
    finally:
        connection.close()
    if "cause" in property_list[pending]:
        cause = property_list[pending]["cause"]
    if pending != "*":
        del nickname_list[pending]
        del property_list[pending]
        del lower_nicks[pending.lower()]
    if not safe_quit:
        done = []
        for i, users in channels_list.items():
            if pending in users:
                for j in users:
                    if j != pending and not j in done:
                        nickname_list[j].sendall(bytes(f":{pending}!~{username}@{hostname} QUIT :{cause}\r\n","UTF-8"))
                        done.append(j)
                # Remove the quitting user from the channel.
                try:
                    channels_list[i].remove(pending)
                except:
                    print(traceback.format_exc())
try:
    while opened:
        connection, client = tcp_socket.accept()
        threading.Thread(target=session, daemon=True, args=[connection, client]).start()
except:
    print("Shutting down...")
    time.sleep(2)
    tcp_socket.shutdown(1)
    tcp_socket.close()