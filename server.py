#!/usr/bin/python3
__version__ = "0.0.5"
print(f"Codename IRCat v{__version__}")
print("Welcome! /ᐠ ˵> ⩊ <˵マ")
import socket, time, ssl, threading, traceback, sys, subprocess, yaml, sqlite3, os, importlib
from OpenSSL import SSL
from requests import get
if not len(sys.argv) == 2:
    print("IRCat requires the following arguments: config.yml")
    sys.exit(1)
server = "127.0.0.1"
displayname = "foo"
identifier = "somewhere in the universe"
admin_nick = "admin"
data_path  = ""
motd = """
  ____          _                                   ___ ____   ____      _  
 / ___|___   __| | ___ _ __   __ _ _ __ ___   ___  |_ _|  _ \ / ___|__ _| |_ 
| |   / _ \ / _` |/ _ \ '_ \ / _` | '_ ` _ \ / _ \  | || |_) | |   / _` | __|
| |__| (_) | (_| |  __/ | | | (_| | | | | | |  __/  | ||  _ <| |__| (_| | |_ 
 \____\___/ \__,_|\___|_| |_|\__,_|_| |_| |_|\___| |___|_| \_\\\\____\__,_|\__|
https://ircat.xyz
This server doesn't have a MOTD in its configuration, or is invalid."""
motd_file = None
ping_timeout = 255
restrict_ip = ''
def isalphanumeric(text:str):
    return False
def getident(hostt:str, clientport:int, ssll:bool):
    try:
        identsender = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        identsender.settimeout(5)
        responsee = ""
        try:
            identsender.connect((hostt, 113))
        except Exception as ex:
            return {"success": False, "response": f"Could not connect to your ident server: {ex}"}
        serverport = "6697" if ssll else "6667"
        try:
            identsender.sendall(bytes(f"{clientport}, {serverport}\r\n", "UTF-8"))
            responsee = identsender.recv(2048).decode().replace(" ", "").replace("\r", "").replace("\n", "")
            print(responsee)
        except Exception as ex:
            return {"success": False, "response": f"Could not send packets to your server: {ex}"}
        if "ERROR:NO-USER" in responsee:
            return {"success": False, "response": "No user was found by the server."}
        elif "ERROR:" in responsee:
            return {"success": False, "response": "The ident server had an error."}
        elif responsee == "":
            return {"success": False, "response": "The connection was closed."}
        else:
            print(responsee.split(",")[0])
            print(responsee.split(",")[1].split(":")[0])

            if responsee.split(",")[0] != str(clientport):
                return {"success": False, "response": "The ident server sent an invalid client port."}
            elif responsee.split(",")[1].split(":")[0] != serverport:
                return {"success": False, "response": "The ident server doesn't know what the server port is."}
            else:
                return {"success": True, "response": responsee.split(",")[1].split(":")[3]}
        return {"success": False, "response": "Unknown error."}
    except:
        print(traceback.format_exc())
        return {"success": False, "response": "Unknown error."}
global mods
mods = {"sql_provider": None, "command": [], "allsocket": [], "identified": False, "ssl": False}
with open(sys.argv[1], 'r') as file:
    global data
    data = yaml.safe_load(file)
    try: server = data["host"]
    except: print("using fallback server address")
    try: displayname = data["name"]
    except: print("using fallback display name")
    try: identifier = data["identifier"]
    except: print("using fallback identifier")
    try: admin_nick = data["admin-nick"]
    except: print("using fallback admin nick")
    try: motd = data["motd"]
    except: print("using fallback MOTD")
    try: motd_file = data["motd-file"]
    except: print("Not reading MOTD from a file.")
    try: ping_timeout = int(data["ping-timeout"])
    except: print("Using 255 as a ping timeout.")
    try: restrict_ip = data["restrict-ip"]
    except: print("Listening on all hosts possible.")
    try: ssl_option = bool(data["ssl"])
    except: 
        print("SSL will be off.")
        ssl_option = False
    if ssl_option:
        try: ssl_cert = data["ssl_cert"]
        except:
            print("IRCat needs an SSL cert to use SSL!")
            sys.exit(1)
        try: ssl_pkey = data["ssl_pkey"]
        except:
            print("IRCat needs an SSL Private Key to use SSL!")
    try: modules = data["modules"]
    except:
        print("IRCat needs at least one module enabled.")
        sys.exit(1)
    file.close()
    print("Successfully loaded config!")
for mod in modules:
    i = mod
    if not os.path.isabs(i):
        i = os.path.dirname(__file__) + "/modules/" + i
    try:
        print(f"Importing module {mod}...")
        spc = importlib.util.spec_from_file_location(mod, f"{i}.py")
        temp_module = importlib.util.module_from_spec(spc)
        spc.loader.exec_module(temp_module)
        for j in temp_module.__ircat_requires__:
            if not j in data:
                raise Exception(f"Module {mod} requires {j} in configuration.")
        if temp_module.__ircat_type__ == "sql.provider":
            if mods["sql_provider"] == None:
                mods["sql_provider"] = temp_module
            else:
                raise Exception(f"Tried to import {mod} as an SQL provider, but something's already the SQL provider.")
        elif temp_module.__ircat_type__ == "command":
            mods["command"].append(temp_module)
        elif temp_module.__ircat_type__ == "allsocket":
            mods["allsocket"].append(temp_module)
    except:
        print(f"Module {i} failed to load.")
        print(traceback.format_exc())
        sys.exit(1)
global topic_list
topic_list = {}
channels_list = {} # Store channels and their user lists
if mods["sql_provider"] == None:
    print("IRCat needs an SQL provider.")
    sys.exit(1)
sqlproviderequires = {}
for i in mods["sql_provider"].__ircat_requires__:
    sqlproviderequires[i.replace("-", "_")] = data[i]
config = mods["sql_provider"].broker(**sqlproviderequires)
global socketListeners
socketListeners = []
for i in mods['allsocket']:
    requires = {}
    for j in i.__ircat_requires__:
        requires[j.replace("-", "_")] = data[j]
    if "sql" in i.__ircat_giveme__:
        requires["sql"] = config
    try:
        print(i.__ircat_fakechannels__)
        topic_list = {**topic_list, **i.__ircat_fakechannels__}
        for j, v in i.__ircat_fakechannels__.items():
            channels_list[j] = ["CatServ"]
    except Exception as ex:
        print(str(ex))
    socketListeners.append(i.IRCatModule(**requires))
commandProviders = []
nickname_list = {} # Stores nicknames and the respective sockets
lower_nicks =   {"catserv": "CatServ"} # Nicknames in lowercase
property_list = {"CatServ": {"host": "IRCatCore", "username": "Meow", "realname": "Updates bot", "modes": "iw", "away": False}} # Stores properties for active users and channels
for i in mods['command']:
    requires = {}
    for j in i.__ircat_requires__:
        requires[j.replace("-", "_")] = data[j]
    if "sql" in i.__ircat_giveme__:
        requires["sql"] = config
    try:
        print(i.__ircat_fakeusers__)
        property_list = {**property_list, **i.__ircat_fakeusers__}
        for j, v in i.__ircat_fakeusers__.items():
            lower_nicks[j.lower()] = j
    except Exception as ex:
        print(str(ex))
    commandProviders.append(i.IRCatModule(**requires))
sockets = {}
sockets_ssl = {}
# Open the specified non-SSL sockets.
for i in restrict_ip.split(" "):
    sockets[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockets[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockets[i].settimeout(None)
    sockets[i].bind((i,6667))
    sockets[i].listen(1)
if ssl_option:
    for i in restrict_ip.split(" "):
        sockets_ssl[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets_ssl[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockets_ssl[i].settimeout(None)
        sockets_ssl[i].bind((i,6697))
        sockets_ssl[i].listen(1)
opened=True
lower_chans = {} # Channel names in lowercase
def pinger(nick, connection):
    global property_list
    while nick in property_list:
        if (time.time() - property_list[nick]["last_ping"]) > 30 and not property_list[nick]["ping_pending"]:
            if nick in property_list:
                print("Sent ping message to " + nick)
                property_list[nick]["ping_pending"] = True
                time.sleep(0.5)
                try:
                    connection.sendall(bytes(f"PING {server}\r\n","UTF-8"))
                except Exception as ex:
                    print(traceback.format_exc())
                    property_list[nick]["cause"] = "Send error: " + str(ex)
                    print("SHUTTING DOWN FOR " + nick)
                    connection.shutdown(socket.SHUT_WR)
                    connection.close()
                    break
        elif property_list[nick]["ping_pending"] and ((time.time() - property_list[nick]["last_ping"]) > ping_timeout):
            if nick in property_list:
                property_list[nick]["cause"] = f"Ping timeout: {ping_timeout} seconds"
                print("SHUTTING DOWN FOR " + nick)
                connection.shutdown(socket.SHUT_WR)
                connection.close()
                break
def session(connection, client, ip, isssl=False):
    global property_list
    global channels_list
    global nickname_list
    pending = "*" # The nickname of the client
    already_set = False # If the client gave the server a NICK packet
    ready = False # If the client gave the server a USER packet
    finished = False # If the server gave the client its information, indicating it's ready.
    username = "oreo" # Username/ident specified by client
    rident = "~oreo"
    hostname = "" # Hostname, can be IP or domain
    realname = "realname" # Realname specified by client
    safe_quit = False # If the client safely exited, or if the server should manually drop the connection
    cause = "Unknown" # The cause of the unexpected exit
    usesIRCv3 = False
    CAPEND = False
    clident = None
    try:
        print("Connected to client IP: {}".format(client))
        connection.sendall(bytes(f":{server} NOTICE * :*** Looking for your hostname...\r\n","UTF-8"))
        connection.sendall(bytes(f":{server} NOTICE * :*** Checking your ident...\r\n","UTF-8"))
        try:
            hostname = socket.gethostbyaddr(client[0])[0]
            connection.sendall(bytes(f":{server} NOTICE * :*** Got hostname! {hostname}\r\n","UTF-8"))
        except:
            hostname = client[0]
            connection.sendall(bytes(f":{server} NOTICE * :*** Oof! Can't find your hostname, using IP...\r\n","UTF-8"))
        try:
            identQuery = getident(hostname, client[1], isssl)
            responseee = identQuery["response"]
            print(identQuery)
            if not identQuery["success"]:
                connection.sendall(bytes(f":{server} NOTICE * :*** Uhm, Couldn't find your ident: {responseee}\r\n","UTF-8"))
            else:
                connection.sendall(bytes(f":{server} NOTICE * :*** Got ident! {responseee}\r\n","UTF-8"))
                clident = responseee
                rident = responseee
        except:
            print(traceback.format_exc())
            connection.sendall(bytes(f":{server} NOTICE * :*** Uhm, Couldn't find your ident: Unknown error.\r\n","UTF-8"))
        while True:
            try:
                data = connection.recv(2048)
                if not data:
                    cause = "Remote host closed the connection"
                    break
            except ssl.SSLEOFError:
                pass
            except ssl.SSLZeroReturnError:
                cause = "Remote host closed the connection"
                break
            except Exception as ex:
                cause = "Read error: " + str(ex)
                break
            print("Received data: {}".format(data))
            try:
                textt = data.decode()
                for text in textt.replace("\r", "").split("\n"):
                    for i in socketListeners:
                        if "onSocket" in dir(i):
                            i.onSocket(socket=connection, ip=client[0], value=text, cachedNick=pending if pending != "*" else None, validated=finished)
                    command = text.split(" ")[0].upper()
                    try:
                        args = text.split(" ")[1:]
                    except:
                        pass
                    if command == "NICK" and not finished:
                        pending = text.split(" ")[1]
                        if pending[0] == ":": pending = pending[1:]
                        if "!" in pending or ":" in pending or "#" in pending or "*" in pending:
                            connection.sendall(bytes(f":{server} 432 * {pending} :Erroneus nickname\r\n","UTF-8"))
                            pending = "*"
                        elif pending.lower() in lower_nicks:
                            connection.sendall(bytes(f":{server} 433 * {pending} :Nickname is already in use.\r\n","UTF-8"))
                            pending = "*"
                        else:
                            already_set = True
                            print(f"User {pending} set nick")
                    elif command == "USER":
                        if not ready:
                            username = text.split(" ")[1]
                            realname = " ".join(text.split(" ")[4:])[1:]
                            ready = True
                    elif command == "CAP":
                        #usesIRCv3 = True
                        if args[0].upper() == "LS":
                            connection.sendall(bytes(f":{server} CAP * LS :ircat.xyz/foo\r\n", "UTF-8"))
                        elif args[0].upper() == "REQ":
                            if args[1].lower() == ":sasl":
                                pass
                                #connection.sendall(f":{server} CAP * ACK :sasl")
                        elif args[0].upper() == "END":
                            CAPEND = True
                    elif command == "WEBIRC" and not finished:
                        if args[0] == data["webirc_pass"]:
                            hostname = args[2]
                            connection.sendall(bytes(f":{server} NOTICE * :*** WebIRC detected, welcome to IRC!\r\n", "UTF-8"))
                    elif (ready and already_set) and (CAPEND if usesIRCv3 else True) and not finished:
                        cleanup_manual()
                        print(f"User {pending} successfully logged in.")
                        nickname_list[pending] = connection
                        property_list[pending] = {"host": hostname, "username": clident if clident != None else f"~{username }", "realname": realname, "modes": "iw", "last_ping": time.time(), "ping_pending": False, "away": False, "identified": False, "ssl": isssl}
                        lower_nicks[pending.lower()] = pending
                        for i in socketListeners:
                            if "onValidate" in dir(i):
                                i.onValidate(socket=connection, ip=client[0])
                        threading.Thread(target=pinger, args=[pending, connection]).start()
                        if clident == None:
                            rident = f"~{username}"
                        connection.sendall(bytes(f":{server} 001 {pending} :Welcome to the {displayname} Internet Relay Chat Network {pending}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 002 {pending} :Your host is {server}[{ip}/6667], running version IRCat-v{__version__}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 004 {pending} {server} IRCat-{__version__} iow ovmsitnlbkq\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 005 {pending} CHANMODES=bq,k,l,irmnpst CHANTYPES=# NETWORK={displayname} :are supported by this server\r\n", "UTF-8"))
                        # connection.sendall(bytes(f":{server} 251 {pending} :There are {allusers} users and {allinvis} invisible in {servers} servers\r\n", "UTF-8")) Not supported as there isn't multi-server capability (yet)
                        ops = 0 # Placeholder, will replace with caclulating how much people have +o
                        connection.sendall(bytes(f":{server} 252 {pending} {ops} :IRC Operators online\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 253 {pending} 0 :unknown connection(s)\r\n", "UTF-8")) # Replace 0 with a variable of not setup clients.
                        chans = len(channels_list)
                        connection.sendall(bytes(f":{server} 254 {pending} {chans} :channels formed\r\n", "UTF-8"))
                        cleints = len(nickname_list)
                        servers = 1
                        connection.sendall(bytes(f":{server} 255 {pending} :I have {cleints} clients and {servers} servers\r\n", "UTF-8"))
                        # Start the MOTD
                        if motd_file != None:
                            motd = open(motd_file).read()
                        connection.sendall(bytes(f":{server} 375 {pending} :- {server} Message of the Day -\r\n", "UTF-8"))
                        for i in motd.rstrip().split("\n"):
                            connection.sendall(bytes(f":{server} 372 {pending} :- {i}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 376 {pending} :End of /MOTD command\r\n", "UTF-8"))
                        # End the MOTD
                        connection.sendall(bytes(f":{pending} MODE {pending} +iw\r\n","UTF-8"))
                        finished = True
                    elif command == "PING":
                        try:
                            e = text.split(" ")[1]
                            e = f":{e}" if e[0] != ":" else e
                            connection.sendall(bytes(f":{server} PONG {server} {e}\r\n","UTF-8"))
                        except:
                            connection.sendall(bytes(f":{server} PONG {server}\r\n","UTF-8"))
                    elif command == "MOTD":
                        if motd_file != None:
                            motd = open(motd_file).read()
                        connection.sendall(bytes(f":{server} 375 {pending} :- {server} Message of the Day -\r\n", "UTF-8"))
                        for i in motd.rstrip().split("\n"):
                            connection.sendall(bytes(f":{server} 376 {pending} :- {i}\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{server} 372 {pending} :End of /MOTD command\r\n", "UTF-8"))
                    elif finished:
                        processedExternally = False
                        for i in commandProviders:
                            cmdrun = i.command(command=command, args=args, nick=pending, ip=client[0], user=property_list[pending], connection=connection)
                            if cmdrun["success"]:
                                if "identify" in cmdrun:
                                    if cmdrun["identify"] == "logout":
                                        if "o" in property_list[pending]["modes"]:
                                            connection.sendall(bytes(f":{pending} MODE {pending} -o\r\n","UTF-8"))
                                        if not "i" in property_list[pending]["modes"]:
                                            connection.sendall(bytes(f":{pending} MODE {pending} +i\r\n","UTF-8"))
                                        if not "w" in property_list[pending]["modes"]:
                                            connection.sendall(bytes(f":{pending} MODE {pending} +w\r\n","UTF-8"))
                                        property_list[pending]["modes"] = "iw"
                                        property_list[pending]["identified"] = False
                                    else:
                                        property_list[pending]["identified"] = True
                                        property_list[pending]["identusername"] = cmdrun["identify"][0]
                                        temp_mode = cmdrun["identify"][1]
                                        property_list[pending]["modes"] = temp_mode
                                        connection.sendall(bytes(f":{pending} MODE {pending} +{temp_mode}\r\n","UTF-8"))
                                processedExternally = True
                                break
                        if processedExternally:
                            pass
                        elif command == "JOIN":
                            channels = text.split(" ")[1]
                            if channels[0] == ":":
                                channels = channels[1:]
                            for channelt in channels.split(","):
                                channel = channelt.strip()
                                if channel.lower() in lower_chans:
                                    channel = lower_chans[channel.lower()]
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
                                            lower_chans[channel.lower()] = channel
                                            topic_list[channel] = "Topic is not implemented."
                                    except:
                                        connection.sendall(bytes(f":{server} NOTICE * :*** Could not join {channel}\r\n","UTF-8"))
                                    print(channels_list)
                                    for i in channels_list[channel]:
                                        try:
                                            nickname_list[i].sendall(bytes(f":{pending}!{rident}@{hostname} JOIN {channel}\r\n","UTF-8"))
                                        except:
                                            pass
                                # Code re-used in the NAMES command
                                if channel in channels_list:
                                        if pending in channels_list[channel]:
                                            users = " ".join(channels_list[channel])
                                            connection.sendall(bytes(f":{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                                connection.sendall(bytes(f":{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                                print("Successfully pre-loaded /NAMES list")
                        elif command == "LIST":
                            connection.sendall(bytes(f":{server} 321 {pending} Channel :Users  Name\r\n","UTF-8"))
                            for key, value in topic_list.items():
                                usersin = len(channels_list[key])
                                connection.sendall(bytes(f":{server} 322 {pending} {key} {usersin} :{value}\r\n","UTF-8"))
                            connection.sendall(bytes(f":{server} 323 {pending} :End of /LIST\r\n","UTF-8"))
                        elif command == "PONG":
                            e = text.split(" ")[1]
                            if e == server or e == f":{server}":
                                print(pending + " replied to PING.")
                                property_list[pending]["last_ping"] = time.time()
                                property_list[pending]["ping_pending"] = False
                        elif command == "NICK":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            elif text.split(" ")[1] == pending:
                                pass
                            else:
                                pending2 = text.split(" ")[1]
                                if pending2[0] == ":": pending2 = pending2[1:]
                                if "!" in pending2 or ":" in pending2 or "#" in pending2 or "*" in pending2:
                                    connection.sendall(bytes(f":{server} 432 {pending} {pending2} :Erroneus nickname\r\n","UTF-8"))
                                elif pending2.lower() in lower_nicks:
                                    connection.sendall(bytes(f":{server} 433 {pending} {pending2} :Nickname is already in use.\r\n","UTF-8"))
                                else:
                                    print("Sending nickname change...")
                                    connection.sendall(bytes(f":{pending}!{rident}@{hostname} NICK {pending2}\r\n","UTF-8"))
                                    # Broadcast the nickname change
                                    done = []
                                    for i, users in channels_list.items():
                                        if pending in users:
                                            for j in users:
                                                if j != pending and j != pending2 and not j in done:
                                                    print("Broadcasting on " + j)
                                                    nickname_list[j].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                                    done.append(j)
                                            # Replace the nickname
                                            try:
                                                print("Changing on " + i)
                                                channels_list[i].remove(pending)
                                                channels_list[i].append(pending2)
                                            except:
                                                print(traceback.format_exc())
                                    print("Moving config...")
                                    property_list[pending2] = property_list.pop(pending)
                                    nickname_list[pending2] = nickname_list.pop(pending)
                                    del lower_nicks[pending.lower()]
                                    lower_nicks[pending2.lower()] = pending2
                                    print("starting pinger...")
                                    pending = pending2
                                    property_list[pending2]["ping_pending"] = False
                                    property_list[pending2]["last_ping"] = time.time()
                                    threading.Thread(target=pinger, args=[pending, connection]).start()
                                    print(f"User {pending} set nick")
                                    print("Broadcasting nickname change...")
                        elif command == "PART":
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            else:
                                channel = text.split(" ")[1]
                                for i in channels_list[channel]:
                                    try:
                                        nickname_list[i].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                    except:
                                        pass
                                try:
                                    channels_list[channel].remove(pending)
                                except:
                                    print(traceback.format_exc())
                        elif command == "AWAY":
                            if len(args) == 0:
                                property_list[pending]["away"] = False
                                connection.sendall(bytes(f":{server} 305 {pending} :You are no longer marked as being away\r\n","UTF-8"))
                            else:
                                reasons = " ".join(args)
                                if reasons[0] == ":": reasons = reasons[1:]
                                property_list[pending]["away"] = True
                                property_list[pending]["reason"] = reasons
                                connection.sendall(bytes(f":{server} 306 {pending} :You have been marked as being away\r\n","UTF-8"))
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
                                        who_away = "G" if property_list[i]["away"] else "H"
                                        connection.sendall(bytes(f":{server} 352 {pending} {channel} {who_user} {who_host} {server} {i} {who_away} :0 {who_realname}\r\n","UTF-8"))
                                elif channel in nickname_list:
                                    who_host = property_list[channel]["host"]
                                    who_user = property_list[channel]["username"]
                                    who_realname = property_list[channel]["realname"]
                                    who_away = "G" if property_list[channel]["away"] else "H"
                                    connection.sendall(bytes(f":{server} 352 {pending} * {who_user} {who_host} {server} {channel} {who_away} :0 {who_realname}\r\n","UTF-8"))

                                connection.sendall(bytes(f":{server} 315 {pending} {channel} :End of /WHO list.\r\n","UTF-8"))
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
                                    who_identified = property_list[target]["identified"]
                                    who_ssl = property_list[target]["ssl"]
                                    if who_identified:
                                        who_identifying = property_list[target]["identusername"]
                                    else:
                                        who_identifying = None
                                    try:
                                        who_flags = property_list[target]["modes"]
                                    except:
                                        who_flags = None
                                    connection.sendall(bytes(f":{server} 311 {pending} {target} {who_user} {who_host} * :{who_realname}\r\n","UTF-8"))
                                    connection.sendall(bytes(f":{server} 312 {pending} {target} {server} :{identifier}\r\n","UTF-8"))
                                    if "o" in who_flags: connection.sendall(bytes(f":{server} 313 {pending} {target} :is an IRC operator\r\n","UTF-8"))
                                    who_away = property_list[target]["away"]
                                    if who_away: 
                                        who_reason = who_away = property_list[target]["reason"]
                                        connection.sendall(bytes(f":{server} 301 {pending} {target} :{who_reason}\r\n","UTF-8"))
                                    if who_identified:
                                        connection.sendall(bytes(f":{server} 330 {pending} {target} {who_identifying} :is logged in as\r\n","UTF-8"))
                                    if who_ssl:
                                        connection.sendall(bytes(f":{server} 671 {pending} {target} :is using a secure connection\r\n","UTF-8"))
                                    #connection.sendall(bytes(f":{server} 317 {pending} {target} {time} :seconds idle\r\n","UTF-8")) # I haven't implemented idle time yet.
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
                                                    nickname_list[i].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                            except:
                                                pass
                                elif target in nickname_list:
                                    nickname_list[target].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                else:
                                    connection.sendall(bytes(f":{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                            else:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                        elif command == "QUIT":
                            # Parse the quit message.
                            done = []
                            if len(text.split(" ")) == 1:
                                msg = "Client Quit"
                            else:
                                msg = text.split(" ")[1:]
                                if msg[0][0] == ":":
                                    msg[0]=msg[0][1:]
                                if len(msg) > 0:
                                    mse = " ".join(msg)
                                    msg = f"Quit: {mse}"
                            text = f"QUIT :{msg}"
                            # Broadcast all users in the joined channels that the person quit.
                            for i, users in channels_list.items():
                                if pending in users:
                                    for j in users:
                                        if j != pending and not j in done:
                                            nickname_list[j].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                            done.append(j)
                                    # Remove the quitting user from the channel.
                                    try:
                                        channels_list[i].remove(pending)
                                    except:
                                        print(traceback.format_exc())
                            # Confirm QUIT and close the socket.
                            try:
                                connection.sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
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

                        elif command == "CATSERV" or (command == "PRIVMSG" and args[0].lower() == "catserv"):
                            if command == "PRIVMSG":
                                args = args[1:]
                                if args[0][0] == ":":
                                    args[0] = args[0][1:]
                            if len(args) == 0:
                                connection.sendall(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                            elif args[0].upper() == "PULL":
                                updater = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
                                if updater.stdout.decode().strip() == "Already up to date.":
                                    connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :Codename IRCat is already up-to-date.\r\n","UTF-8"))
                                else:
                                    connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :Done, it is recommended to use /RESTART if you're an IRC op\r\n","UTF-8"))
                            elif args[0].upper() == "VERSION":
                                connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :Codename IRCat version {__version__}\r\n","UTF-8"))
                                connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :This is Codename IRCat's integrated services.\r\n","UTF-8"))
                            else:
                                connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :CatServ Usage:\r\n","UTF-8"))
                                connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :PULL     - Pulls the latest version of Codename IRCat\r\n","UTF-8"))
                                connection.sendall(bytes(f":CatServ!Meow@IRCatCore NOTICE {pending} :VERSION  - Gets the version number of this service.\r\n","UTF-8"))
                        elif command == "RESTART":
                            if "o" in property_list[pending]["modes"]:
                                global opened
                                opened = False
                            else:
                                connection.sendall(bytes(f":{server} 481 {pending} :Permission Denied- You're not an IRC operator\r\n","UTF-8"))
                        elif command == "PRIVMSG":
                            if len(args) >= 2:
                                target = text.split(" ")[1]
                                if target.lower() in lower_nicks:
                                    target = lower_nicks[target.lower()]
                                if target in channels_list:
                                    print("Sending to "+ target + " Channel")
                                    if pending in channels_list[target]:
                                        print(channels_list[target])
                                        for i in channels_list[target]:
                                            try:
                                                if i != pending:
                                                    print(i)
                                                    print(f":{pending}!{rident}@{hostname} {text}\r\n")
                                                    nickname_list[i].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                                else:
                                                    print(i + " Is the current user!")
                                            except:
                                                print(traceback.format_exc)
                                elif target in nickname_list:
                                    nickname_list[target].sendall(bytes(f":{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
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
            except ssl.SSLEOFError:
                print("EOF occured...")
            except Exception as ex:
                print(traceback.format_exc())
                cause = "" + str(ex)
                break
    finally:
        connection.close()
    try:
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
                            try:
                                nickname_list[j].sendall(bytes(f":{pending}!{rident}@{hostname} QUIT :{cause}\r\n","UTF-8"))
                                done.append(j)
                            except:
                                print(traceback.format_exc())
                    # Remove the quitting user from the channel.
                    try:
                        channels_list[i].remove(pending)
                    except:
                        print(traceback.format_exc())
    except:
        print(traceback.format_exc())
    cleanup_manual()
def cleanup():
    while True:
        time.sleep(15)
        cleanup_manual()
def cleanup_manual():
    global channels_list
    global property_list
    print("Cleaning up...")
    for j, i in channels_list.items():
        for h in i:
            if not h in property_list:
                print("Found a detached connection: " + h)
                i.remove(h)
                for k in channels_list[j]:
                    if k != h and k in nickname_list:
                        nickname_list[k].sendall(f":{h}!DISCONNECTED@DISCONNECTED PART {j} :IRCat Cleanup: Found missing connection!!\r\n")

def tcp_session(sock):
    while True:
        try:
            while opened:
                print("Waiting for connection...")
                connection, client = sock.accept()
                ip_to = restrict_ip
                threading.Thread(target=session, daemon=True, args=[connection, client, ip_to]).start()
        except:
            print("Something went wrong...")
            print(traceback.format_exc())
def ssl_session(sock):
    while True:
        try:
            while opened:
                context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
                context.minimum_version = ssl.TLSVersion.TLSv1
                context.set_ciphers('DEFAULT:@SECLEVEL=0')
                context.load_cert_chain(ssl_cert, keyfile=ssl_pkey)
                print("Waiting for connection...")
                connection, client = sock.accept()
                ip_to = restrict_ip
                threading.Thread(target=session, daemon=True, args=[context.wrap_socket(connection, server_side=True), client, ip_to, True]).start()
        except:
            print("Something went wrong...")
            print(traceback.format_exc())
for ip, i in sockets.items():
    print("Now listening on port 6667 with IP " + ip)
    threading.Thread(target=tcp_session, args=[i], daemon=True).start()
if ssl_option:
    for ip, i in sockets_ssl.items():
        print("Now listening on SSL port 6697 with IP " + ip)
        threading.Thread(target=ssl_session, args=[i], daemon=True).start()
while opened:
    pass
print("Shutting down...")