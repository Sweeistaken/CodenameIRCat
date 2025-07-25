#!/usr/bin/python3
import socket, time, ssl, threading, traceback, sys, subprocess, yaml, sqlite3, os, importlib, datetime
import prctl
from cryptography.fernet import Fernet
from requests import get
__version__ = "0.0.9-pre"
print(f"Codename IRCat v{__version__}")
print("Welcome! /ᐠ ˵> ⩊ <˵マ")
prctl.set_name("Codename IRCat")
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
def isalphanumeric(text:str, channel=False):
    alphanumericity = list(
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890+-_[]^\\|<>?`" +
        ("$%*,./~'\"{};#=" if channel else "")
    )
    for i in text:
        if not i in alphanumericity:
            return False
    return True
def parseOutContent(text:str):
    if text[0] == ":":
        return text[1:]
    else:
        return text.split(" ")[0]
def getident(hostt:str, clientport:int, ssll:bool, ip:str):
    try:
        identsender = socket.socket((socket.AF_INET6 if ":" in hostt else socket.AF_INET), socket.SOCK_STREAM)
        identsender.bind((ip, 0)) # If the server has multiple IPs
        identsender.settimeout(2)
        responsee = ""
        try:
            identsender.connect((hostt, 113))
        except Exception as ex:
            return {"success": False, "response": f"Could not connect to your ident server: {ex}"}
        serverport = "6697" if ssll else "6667"
        try:
            identsender.sendall(bytes(f"{clientport}, {serverport}\r\n", "UTF-8"))
            responsee = identsender.recv(2048).decode().replace(" ", "").replace("\r", "").replace("\n", "")
        except Exception as ex:
            return {"success": False, "response": f"Could not send packets to your server: {ex}"}
        if "ERROR:NO-USER" in responsee:
            return {"success": False, "response": "No user was found by the server."}
        elif "ERROR:" in responsee:
            return {"success": False, "response": "The ident server had an error."}
        elif responsee == "":
            return {"success": False, "response": "The connection was closed."}
        else:
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
    global data2
    data = yaml.safe_load(file)
    data2 = data
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
    try: multi_server = data["multiserver"]
    except: multi_server = False
    if multi_server:
        if multi_server.__class__.__name__ != "list" and multi_server != "loner":
            print("The multiserver option must be a list.")
            sys.exit(1)
        try: fnet = Fernet(data["fernet-key"])
        except:
            print("Multi-Server IRCat needs a Fernet key.")
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
        topic_list = {**topic_list, **i.__ircat_fakechannels__}
        for j, v in i.__ircat_fakechannels__.items():
            channels_list[j] = ["CatServ"]
    except Exception as ex:
        print(str(ex))
    socketListeners.append(i.IRCatModule(**requires))
commandProviders = []
nickname_list = {} # Stores nicknames and the respective sockets
lower_nicks =   {"catserv": "CatServ"} # Nicknames in lowercase
channel_modestore = {} # Channel: {nick: mode}
channel_modestore_identify = {} # Channel: {account: mode}
property_list = {"CatServ": {"host": server, "username": "system", "realname": "Updates bot (Internal)", "modes": "o", "away": False, "external": False}} # Stores properties for active users and channels
users_externalservers = {} # Nicknames that come from different servers, useful in netsplit situations
cache_properties = {} # Cached property lists from other servers, used to send out changes
for i in mods['command']:
    requires = {}
    for j in i.__ircat_requires__:
        requires[j.replace("-", "_")] = data[j]
    if "sql" in i.__ircat_giveme__:
        requires["sql"] = config
    try:
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
    if ":" in i:
        sockets[i] = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
    else:
        sockets[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sockets[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sockets[i].settimeout(None)
    sockets[i].bind((i,6667))
    sockets[i].listen(1)
if ssl_option:
    for i in restrict_ip.split(" "):
        if ":" in i:
            sockets_ssl[i] = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        else:
            sockets_ssl[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockets_ssl[i].setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sockets_ssl[i].settimeout(None)
        sockets_ssl[i].bind((i,6697))
        sockets_ssl[i].listen(1)
opened=True
lower_chans = {} # Channel names in lowercase
sessions = {}
def multiserverpinger(sock):
    while True:
        time.sleep(30)
        sock.sendall(fnet.encrypt(bytes("PING", "UTF-8")))
def multiserverhost(sock, client):
    try:
        threading.Thread(target=multiserverpinger, args=[sock]).start()
        global sessions
        global cache_properties
        sessions[client[0]] = sock
        cache_properties[client[0]] = {}
        global channels_list
        global property_list
        global nickname_list
        global topic_list
        if sock.recv(2048).decode() == "meow":
            sock.sendall(bytes("woem", "UTF-8"))
        else:
            raise Exception("This isn't an IRCat server!!")
        while True:
            txt = fnet.decrypt(sock.recv(2048)).decode()
            if txt.split(" ")[0] == "VERIFYUSER": # When a user from a different server logs in
                nck = txt.split(" ")[1] # Nickname
                usr = json.loads(" ".join(txt.split(" ")[2:])) # New JSON properties
                property_list[nck] = usr # Add the properties
                nickname_list[nck] = {"external": client[0]} # Add the nickname indicating it's external
                lower_nicks[nck.lower()] = usr # Add the lowercase nickname
                users_externalservers[nck] = client[0] # Add to the list of external users
            elif txt.split(" ")[0] == "SND": # When a token was sent by another server
                nck = txt.split(" ")[1] # Nickname
                cmd = txt.split(" ")[2] # Command
                arg = txt.split(" ")[3:] # Arguments
            elif txt.split(" ")[0] == "CNGPROP": # When properties changed on another server
                nck = txt.split(" ")[1] # Nickname
                usr = json.loads(" ".join(txt.split(" ")[2:])) # JSON
                property_list[nck] = usr # Change the JSON...
                cache_properties[client[0]][nck] = usr # ...And cache it
            elif txt.split(" ")[0] == "CNGNICK": # When nick changed on another server
                nck = txt.split(" ")[1] # Old nickname
                nnck = txt.split(" ")[2] # New nickname
                nickname_list[nnck] = nickname_list.pop(nck) # Move old nickname from list
                property_list[nnck] = property_list.pop(nck) # Move properties...
                cache_properties[client[0]][nnck] = cache_properties[client[0]].pop(nck) # ...And cache it
                del lower_nicks[nck.lower()] # Remove the old lowercase nickname...
                lower_nicks[nnck.lower()] = nnck # ...And replace it
            elif txt == "PING":
                sock.sendall(fnet.encrypt(bytes("PONG", "UTF-8")))
    finally:
        netsplit(client[0])
        sock.close()
def session(connection, client, ip, isssl=False):
    prctl.set_name("*")
    if isssl: # Then prepare SSL handshaking
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(ssl_cert, keyfile=ssl_pkey)
        connection = ctx.wrap_socket(connection, server_side=True)
    global channels_list
    global property_list
    global nickname_list
    global channel_modestore
    global channel_modestore_identify
    global topic_list
    pending = "*" # The nickname of the client
    already_set = False # If the client gave the server a NICK packet
    ready = False # If the client gave the server a USER packet
    finished = False # If the server gave the client its information, indicating it's ready.
    username = "oreo" # Username/ident specified by client
    rident = "~oreo" # Real ident - shown to other users
    hostname = "" # Hostname, can be IP or domain
    realname = "realname" # Realname specified by client
    safe_quit = False # If the client safely exited, or if the server should manually drop the connection
    cause = "Unknown" # The cause of the unexpected exit
    usesIRCv3 = False # If the client used CAP LS 302
    CAPEND = False # If the client used CAP END
    clident = None # Client's ident
    pendingCommands = "" # list of commands that were executed before verification
    textt = "" # Pending text (if the client sent incomplete packets before [CR]LF)
    pendingSend = "" # Text that should be sent to the client
    ping_pending = False # Did the server already ping the client?
    last_ping = time.time() # Last time the server pinged the client
    IRCv3Features = [] # List of Acknowledged IRCv3 features.
    stillRunning = True
    alreadyNotified = False
    def tags(): # Get IRCv3 tags
        tags = ""
        if "server-time" in IRCv3Features:
            tags += "@time=" + datetime.datetime.now(datetime.timezone.utc).isoformat()[:-9] + "Z"
            # >>> datetime.datetime.now(datetime.timezone.utc).isoformat()
            # '2025-02-05T00:15:50.370474+00:00'
            #                         ^^^^^^^^^
            #      Cutting these off the string
        return tags + (" " if tags != "" else "")
    def dosend(content):
        if content.__class__.__name__ != "bytes":
            content = bytes(content, "UTF-8")
        try:
            connection.sendall(content)
        except Exception as ex:
            raise ex
    def tags_diffclient(nick:str): # Get tags of another client
        othercap = property_list[nick]["v3cap"]
        tags = []
        if "server-time" in othercap:
            tags.append("time=" + datetime.datetime.now(datetime.timezone.utc).isoformat()[:-9] + "Z")
        if "account-tag" in othercap and property_list[pending]["identified"]:
            tags.append("account=" + property_list[pending]["identusername"])
        return ("@" if args != [] else "") + ";".join(tags) + (" " if args != [] else "")
    try:
        print("Connected to client IP: {}".format(client))
        connection.settimeout(None)
        dosend(bytes(f":{server} NOTICE * :*** Looking for your hostname...\r\n","UTF-8"))
        dosend(bytes(f":{server} NOTICE * :*** Checking your ident...\r\n","UTF-8"))
        try:
            hostname = socket.gethostbyaddr(client[0])[0]
            dosend(bytes(f":{server} NOTICE * :*** Got hostname! {hostname}\r\n","UTF-8"))
        except:
            hostname = client[0]
            dosend(bytes(f":{server} NOTICE * :*** Oof! Can't find your hostname, using IP...\r\n","UTF-8"))
        try:
            identQuery = getident(client[0], client[1], isssl, ip)
            responseee = identQuery["response"]
            if not identQuery["success"]:
                dosend(bytes(f":{server} NOTICE * :*** Uhm, Couldn't find your ident: {responseee}\r\n","UTF-8"))
            else:
                dosend(bytes(f":{server} NOTICE * :*** Got ident! {responseee}\r\n","UTF-8"))
                clident = responseee
                rident = responseee
        except:
            dosend(bytes(f":{server} NOTICE * :*** Uhm, Couldn't find your ident: Unknown error.\r\n","UTF-8"))
        while stillRunning:
            try:
                connection.settimeout(0.1)
                data = connection.recv(2048)
                if not data:
                    cause = "Remote host closed the connection"
                    break
            except socket.timeout:
                data = bytes("", "UTF-8")
            except Exception as ex:
                print(traceback.format_exc())
                cause = "Read error: " + str(ex)
                break
            if data != bytes("", "UTF-8"):
                print(f"Received data from {pending}: {data}")
            try:
                try:
                    textt += data.decode()
                except UnicodeDecodeError:
                    textt += data.decode("latin-1")
                if finished:
                    if (time.time() - last_ping) > 30 and not ping_pending:
                        print(f"Sending ping msg to {pending}")
                        ping_pending = True
                        time.sleep(0.1)
                        dosend(bytes(f"PING {server}\r\n","UTF-8"))
                    elif ping_pending and (time.time() - last_ping) > ping_timeout:
                        cause = f"Ping timeout: {ping_timeout} seconds"
                        break
                    if "kill" in property_list[pending] and property_list[pending]["kill"]:
                        raise Exception("Killed by " + property_list[pending]["kill_user"] + ": " + property_list[pending]["kill_comment"])
                if textt != "" and textt[-1] == "\n":
                    for text in textt.replace("\r", "").split("\n"):
                        for i in socketListeners:
                            if "onSocket" in dir(i):
                                i.onSocket(socket=connection, ip=client[0], value=text, cachedNick=pending if pending != "*" else None, validated=finished, v3tag=tags())
                        command = text.split(" ")[0].upper()
                        try:
                            args = text.split(" ")[1:]
                        except:
                            pass
                        if command == "NICK" and not finished:
                            pending = text.split(" ")[1]
                            if pending[0] == ":": pending = pending[1:]
                            if not isalphanumeric(pending):
                                dosend(bytes(f"{tags()}:{server} 432 * {pending} :Erroneus nickname\r\n","UTF-8"))
                                pending = "*"
                            elif pending.lower() in lower_nicks:
                                dosend(bytes(f"{tags()}:{server} 433 * {pending} :Nickname is already in use.\r\n","UTF-8"))
                                pending = "*"
                            else:
                                prctl.set_name(pending)
                                already_set = True
                        elif command == "USER":
                            if not ready:
                                username = text.split(" ")[1]
                                realname = " ".join(text.split(" ")[4:])[1:]
                                ready = True
                        elif command == "CAP":
                            if args[0].upper() == "LS":
                                dosend(bytes(f"{tags()}:{server} CAP * LS :server-time account-tag\r\n", "UTF-8"))
                            elif args[0].upper() == "REQ":
                                usesIRCv3 = True # Halt the registration process until CAP END
                                capabilities = " ".join(args[1:])[1:].split(" ")
                                capsuccess = True
                                for cap in capabilities:
                                    if cap == "server-time":
                                        IRCv3Features.append("server-time")
                                    elif cap == "account-tag":
                                        IRCv3Features.append("account-tag")
                                    else:
                                        capsuccess = False
                                        break
                                capper = " ".join(capabilities)
                                if capsuccess:
                                    dosend(bytes(f":{server} CAP * ACK :{capper}\r\n", "UTF-8"))
                                else:
                                    dosend(bytes(f":{server} CAP * NAK :{capper}\r\n", "UTF-8"))
                            elif args[0].upper() == "END":
                                CAPEND = True
                        elif command == "WEBIRC" and not finished:
                            try:
                                if args[0] == data2["webirc_pass"]:
                                    hostname = args[2]
                                    client = (args[3], client[1])
                                    dosend(bytes(f"{tags()}:{server} NOTICE * :*** WebIRC detected, welcome to IRC!\r\n", "UTF-8"))
                                    if hostname != client[0]:
                                        dosend(bytes(f"{tags()}:{server} NOTICE * :*** Got WebIRC hostname! {hostname}\r\n", "UTF-8"))
                            except:
                                print(traceback.format_exc())
                                break
                        elif (ready and already_set) and (CAPEND if usesIRCv3 else True) and not finished:
                            print(f"User {pending} successfully logged in.")
                            prctl.set_name(pending)
                            del alreadyNotified
                            nickname_list[pending] = connection
                            property_list[pending] = {"host": hostname, "username": clident if clident != None else f"~{username }", "realname": realname, "modes": "iw", "away": False, "identified": False, "ssl": isssl, "v3cap": IRCv3Features, "last_ping": time.time(), "ping_pending": False, "pendingSend": "", "external": False}
                            last_ping = time.time()
                            ping_pending = False
                            lower_nicks[pending.lower()] = pending
                            for i in socketListeners:
                                if "onValidate" in dir(i):
                                    i.onValidate(socket=connection, ip=client[0], v3cap=IRCv3Features)
                            if clident == None:
                                rident = f"~{username}"
                            dosend(bytes(f"{tags()}:{server} 001 {pending} :Welcome to the {displayname} Internet Relay Chat Network {pending}\r\n", "UTF-8"))
                            actport = "6697" if isssl else "6667"
                            dosend(bytes(f"{tags()}:{server} 002 {pending} :Your host is {server}[{ip}/{actport}], running version IRCat-v{__version__}\r\n", "UTF-8"))
                            dosend(bytes(f"{tags()}:{server} 004 {pending} {server} IRCat-{__version__} iow msitnR lfovkqb\r\n", "UTF-8"))
                            dosend(bytes(f"{tags()}:{server} 005 {pending} CHANMODES=bq,k,fl,irmnpst CHANTYPES=# NETWORK={displayname} :are supported by this server\r\n", "UTF-8"))
                            # dosend(bytes(f":{server} 251 {pending} :There are {allusers} users and {allinvis} invisible in {servers} servers\r\n", "UTF-8"))
                            ops = 0
                            for k, v in property_list.items():
                                if "o" in v["modes"]:
                                    ops+=1
                            dosend(bytes(f"{tags()}:{server} 252 {pending} {ops} :IRC Operators online\r\n", "UTF-8"))
                            # dosend(bytes(f"{tags()}:{server} 253 {pending} 0 :unknown connection(s)\r\n", "UTF-8")) # Replace 0 with a variable of not setup clients.
                            chans = len(channels_list)
                            dosend(bytes(f"{tags()}:{server} 254 {pending} {chans} :channels formed\r\n", "UTF-8"))
                            cleints = len(nickname_list)
                            servers = 1
                            dosend(bytes(f"{tags()}:{server} 255 {pending} :I have {cleints} clients and {servers} servers\r\n", "UTF-8"))
                            # Start the MOTD
                            if motd_file != None:
                                motd = open(motd_file).read()
                            dosend(bytes(f"{tags()}:{server} 375 {pending} :- {server} Message of the Day -\r\n", "UTF-8"))
                            for i in motd.rstrip().split("\n"):
                                dosend(bytes(f"{tags()}:{server} 372 {pending} :- {i}\r\n", "UTF-8"))
                            dosend(bytes(f"{tags()}:{server} 376 {pending} :End of /MOTD command\r\n", "UTF-8"))
                            # End the MOTD
                            dosend(bytes(f"{tags()}:{pending} MODE {pending} +iw\r\n","UTF-8"))
                            finished = True
                        elif command == "PING":
                            try:
                                e = text.split(" ")[1]
                                e = f":{e}" if e[0] != ":" else e
                                pendingSend += f"{tags()}:{server} PONG {server} {e}\r\n"
                            except:
                                pendingSend += f"{tags()}:{server} PONG {server}\r\n"
                        elif finished:
                            pendingCommands += text
                            for comd in pendingCommands.replace("\r", "").split("\n"):
                                command = comd.split(" ")[0].upper()
                                args = comd.split(" ")[1:]
                                text = comd
                                processedExternally = False
                                for i in commandProviders:
                                    cmdrun = i.command(command=command, args=args, nick=pending, ip=client[0], user=property_list[pending], connection=connection, v3tag=tags())
                                    if "identify" in cmdrun:
                                        if cmdrun["identify"] == "logout":
                                            if "o" in property_list[pending]["modes"]:
                                                dosend(bytes(f"{tags()}:{pending} MODE {pending} -o\r\n","UTF-8"))
                                            if not "i" in property_list[pending]["modes"]:
                                                dosend(bytes(f"{tags()}:{pending} MODE {pending} +i\r\n","UTF-8"))
                                            if not "w" in property_list[pending]["modes"]:
                                                dosend(bytes(f"{tags()}:{pending} MODE {pending} +w\r\n","UTF-8"))
                                            property_list[pending]["modes"] = "iw"
                                            property_list[pending]["identified"] = False
                                        else:
                                            property_list[pending]["identified"] = True
                                            property_list[pending]["identusername"] = cmdrun["identify"][0]
                                            temp_mode = cmdrun["identify"][1]
                                            property_list[pending]["modes"] = temp_mode
                                            dosend(bytes(f"{tags()}:{pending} MODE {pending} +{temp_mode}\r\n","UTF-8"))
                                    if "initchan" in cmdrun:
                                        for chran in cmdrun["initchan"]:
                                            if chran["name"] not in channels_list:
                                                channels_list[chran["name"]] = []
                                                topic_list[chran["name"]] = chran["topic"]
                                                lower_chans[chran["name"].lower()] = chran["name"]
                                                channel_modestore_identify[chran["name"]] = chran["automodes"]
                                                channel_modestore[chran["name"]] = {}
                                    if cmdrun["success"] == "skip":
                                        pass
                                    elif cmdrun["success"]:
                                        processedExternally = True
                                        break
                                if processedExternally:
                                    continue
                                elif command == "JOIN":
                                    channels = text.split(" ")[1]
                                    if channels[0] == ":":
                                        channels = channels[1:]
                                    for channelt in channels.split(","):
                                        channel = channelt.strip()
                                        if isalphanumeric(channel, True):
                                            if channel[0] == "#":
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
                                                            topic_list[channel] = ""
                                                            channel_modestore[channel] = {pending: "o"}
                                                            dosend(bytes(f":{server} MODE {channel} +o {pending}\r\n", "UTF-8"))
                                                    except:
                                                        dosend(bytes(f"{tags()}:{server} NOTICE * :*** Could not join {channel}\r\n","UTF-8"))
                                                    if property_list[pending]["identified"] and channel in channel_modestore_identify:
                                                        if property_list[pending]["identusername"] in channel_modestore_identify[channel]:
                                                            channel_modestore[channel][pending] = channel_modestore_identify[channel][property_list[pending]["identusername"]]
                                                            mo = channel_modestore[channel][pending]
                                                            pendingSend += f":{server} MODE {channel} +{mo} {pending}\r\n"
                                                    print(channel_modestore)
                                                    for i in channels_list[channel]:
                                                        try:
                                                            if i != pending:
                                                                property_list[i]["pendingSend"] += f":{pending}!{rident}@{hostname} JOIN {channel}\r\n"
                                                                if pending in channel_modestore[channel] and channel_modestore[channel][pending] != "":
                                                                    mo = channel_modestore[channel][pending]
                                                                    property_list[i]["pendingSend"] += f":{server} MODE {channel} +{mo} {pending}\r\n"
                                                        except:
                                                            pass
                                                dosend(bytes(f":{pending}!{rident}@{hostname} JOIN {channel}\r\n", "UTF-8"))
                                                users = ""
                                                for i in channels_list[channel]:
                                                    who_mode = "" if not i in channel_modestore[channel] else ("@" if channel_modestore[channel][i] == "o" else ("+" if channel_modestore[channel][i] == "v" else ""))
                                                    users += f"{who_mode}{i} "
                                                dosend(bytes(f"{tags()}:{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                                                dosend(bytes(f"{tags()}:{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                                                if topic_list[channel] != "":
                                                    tpc = topic_list[channel]
                                                    dosend(bytes(f"{tags()}:{server} 332 {pending} {channel} :{tpc}\r\n","UTF-8"))
                                                else:
                                                    dosend(bytes(f"{tags()}:{server} 331 {pending} {channel} :No topic is set\r\n","UTF-8"))
                                            else:
                                                dosend(bytes(f"{tags()}:{server} 479 {pending} {channel} :Channel name needs to start with #\r\n","UTF-8"))
                                        else:
                                            dosend(bytes(f"{tags()}:{server} 479 {pending} {channel} :Channel has erroneus characters\r\n","UTF-8"))
                                elif command == "LIST":
                                    dosend(bytes(f"{tags()}:{server} 321 {pending} Channel :Users  Name\r\n","UTF-8"))
                                    for key, value in topic_list.items():
                                        usersin = len(channels_list[key])
                                        dosend(bytes(f"{tags()}:{server} 322 {pending} {key} {usersin} :{value}\r\n","UTF-8"))
                                    dosend(bytes(f"{tags()}:{server} 323 {pending} :End of /LIST\r\n","UTF-8"))
                                elif command == "TOPIC":
                                    channel = args[0]
                                    if channel in channels_list:
                                        if pending in channels_list[channel]:
                                            if len(args) > 1:
                                                if "o" in channel_modestore[channel][pending]:
                                                    content = parseOutContent(" ".join(text.split(" ")[2:]))
                                                    for i in channels_list[channel]:
                                                        try:
                                                            property_list[i]["pendingSend"] += f":{pending}!{rident}@{hostname} TOPIC {channel} :{content}\r\n"
                                                        except:
                                                            pass
                                                else:
                                                    dosend(bytes(f"{tags()}:{server} 482 {pending} {channel} :You're not channel operator\r\n","UTF-8"))
                                            else:
                                                if topic_list[channel] != "":
                                                    tpc = topic_list[channel]
                                                    dosend(bytes(f"{tags()}:{server} 332 {pending} {channel} :{tpc}\r\n","UTF-8"))
                                                else:
                                                    dosend(bytes(f"{tags()}:{server} 331 {pending} {channel} :No topic is set\r\n","UTF-8"))
                                        else:
                                            dosend(bytes(f"{tags()}:{server} 441 {pending} {channel} :You're not on that channel\r\n","UTF-8"))
                                    else:
                                        dosend(bytes(f"{tags()}:{server} 441 {pending} {channel} :You're not on that channel\r\n","UTF-8"))
                                elif command == "PONG":
                                    e = text.split(" ")[1]
                                    if e == server or e == f":{server}":
                                        print(pending + " replied to PING.")
                                        #property_list[pending]["last_ping"] = time.time()
                                        #property_list[pending]["ping_pending"] = False
                                        last_ping = time.time()
                                        ping_pending = False
                                elif command == "NICK":
                                    if len(args) == 0:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                    elif text.split(" ")[1] == pending:
                                        pass
                                    else:
                                        pending2 = text.split(" ")[1]
                                        if pending2[0] == ":": pending2 = pending2[1:]
                                        if not isalphanumeric(pending2):
                                            dosend(bytes(f"{tags()}:{server} 432 {pending} {pending2} :Erroneus nickname\r\n","UTF-8"))
                                        elif pending2.lower() in lower_nicks:
                                            dosend(bytes(f"{tags()}:{server} 433 {pending} {pending2} :Nickname is already in use.\r\n","UTF-8"))
                                        else:
                                            dosend(bytes(f"{tags()}:{pending}!{rident}@{hostname} NICK {pending2}\r\n","UTF-8"))
                                            # Broadcast the nickname change
                                            done = []
                                            for i, users in channels_list.items():
                                                if pending in users:
                                                    for j in users:
                                                        if j != pending and j != pending2 and not j in done:
                                                            property_list[j]["pendingSend"] += f"{tags_diffclient(j)}:{pending}!{rident}@{hostname} {text}\r\n"
                                                            done.append(j)
                                                    # Replace the nickname
                                                    try:
                                                        channels_list[i].remove(pending)
                                                        channels_list[i].append(pending2)
                                                    except:
                                                        print(traceback.format_exc())
                                            property_list[pending2] = property_list.pop(pending)
                                            nickname_list[pending2] = nickname_list.pop(pending)
                                            del lower_nicks[pending.lower()]
                                            lower_nicks[pending2.lower()] = pending2
                                            #print("starting pinger...")
                                            pending = pending2
                                            #property_list[pending2]["ping_pending"] = False
                                            #property_list[pending2]["last_ping"] = time.time()
                                            #threading.Thread(target=pinger, args=[pending, connection]).start()
                                            prctl.set_name(pending)
                                elif command == "ISON":
                                    if args[0][0] == ":":
                                        args[0] = args[0][1:]
                                    onlines = []
                                    for someuser in args:
                                        if someuser.lower() in lower_nicks:
                                            someuser = lower_nicks[someuser.lower()]
                                        if someuser in nickname_list:
                                            onlines.append(someuser)
                                    onlines = " ".join(onlines)
                                    dosend(bytes(f"{tags()}:{server} 303 {pending} :{onlines}\r\n","UTF-8"))
                                elif command == "PART":
                                    if len(args) == 0:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                    else:
                                        channel = text.split(" ")[1]
                                        for i in channels_list[channel]:
                                            try:
                                                property_list[i]["pendingSend"] += f"{tags_diffclient(i)}:{pending}!{rident}@{hostname} {text}\r\n"
                                            except:
                                                pass
                                        try:
                                            channels_list[channel].remove(pending)
                                        except:
                                            print(traceback.format_exc())
                                elif command == "AWAY":
                                    if len(args) == 0:
                                        property_list[pending]["away"] = False
                                        dosend(bytes(f"{tags()}:{server} 305 {pending} :You are no longer marked as being away\r\n","UTF-8"))
                                    else:
                                        reasons = " ".join(args)
                                        if reasons[0] == ":": reasons = reasons[1:]
                                        property_list[pending]["away"] = True
                                        property_list[pending]["reason"] = reasons
                                        dosend(bytes(f"{tags()}:{server} 306 {pending} :You have been marked as being away\r\n","UTF-8"))
                                elif command == "WHO":
                                    if len(args) == 0:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                    else:
                                        channel = text.split(" ")[1]
                                        if channel in channels_list:
                                            for i in channels_list[channel]:
                                                who_host = property_list[i]["host"]
                                                who_user = property_list[i]["username"]
                                                who_realname = property_list[i]["realname"]
                                                who_away = "G" if property_list[i]["away"] else "H"
                                                who_mode = "" if not i in channel_modestore[channel] else ("@" if channel_modestore[channel][i] == "o" else ("+" if channel_modestore[channel][i] == "v" else ""))
                                                dosend(bytes(f"{tags()}:{server} 352 {pending} {channel} {who_user} {who_host} {server} {i} {who_away}{who_mode} :0 {who_realname}\r\n","UTF-8"))
                                        elif channel in nickname_list:
                                            who_host = property_list[channel]["host"]
                                            who_user = property_list[channel]["username"]
                                            who_realname = property_list[channel]["realname"]
                                            who_away = "G" if property_list[channel]["away"] else "H"
                                            dosend(bytes(f"{tags()}:{server} 352 {pending} * {who_user} {who_host} {server} {channel} {who_away} :0 {who_realname}\r\n","UTF-8"))

                                        dosend(bytes(f"{tags()}:{server} 315 {pending} {channel} :End of /WHO list.\r\n","UTF-8"))
                                elif command == "WHOIS":
                                    if len(args) == 0:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
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
                                            dosend(bytes(f"{tags()}:{server} 311 {pending} {target} {who_user} {who_host} * :{who_realname}\r\n","UTF-8"))
                                            dosend(bytes(f"{tags()}:{server} 312 {pending} {target} {server} :{identifier}\r\n","UTF-8"))
                                            if "o" in who_flags: dosend(bytes(f":{server} 313 {pending} {target} :is an IRC operator\r\n","UTF-8"))
                                            who_away = property_list[target]["away"]
                                            if who_away: 
                                                who_reason = who_away = property_list[target]["reason"]
                                                dosend(bytes(f"{tags()}:{server} 301 {pending} {target} :{who_reason}\r\n","UTF-8"))
                                            if who_identified:
                                                dosend(bytes(f"{tags()}:{server} 330 {pending} {target} {who_identifying} :is logged in as\r\n","UTF-8"))
                                            if who_ssl:
                                                dosend(bytes(f"{tags()}:{server} 671 {pending} {target} :is using a secure connection\r\n","UTF-8"))
                                            #dosend(bytes(f":{server} 317 {pending} {target} {time} :seconds idle\r\n","UTF-8")) # I haven't implemented idle time yet.
                                            if who_flags != None and who_flags != "iw":
                                                dosend(bytes(f"{tags()}:{server} 379 {pending} {target} :Is using modes +{who_flags}\r\n","UTF-8"))
                                            dosend(bytes(f"{tags()}:{server} 318 {pending} {target} :End of /WHOIS list\r\n","UTF-8"))
                                        else:
                                            dosend(bytes(f"{tags()}:{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                                elif command == "NAMES":
                                    if len(args) == 0:
                                        dosend(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                    else:
                                        channel = text.split(" ")[1]
                                        if channel in channels_list:
                                                if pending in channels_list[channel]:
                                                    users = ""
                                                    for i in channels_list[channel]:
                                                        who_mode = "" if not i in channel_modestore[channel] else ("@" if channel_modestore[channel][i] == "o" else ("+" if channel_modestore[channel][i] == "v" else ""))
                                                        users += f"{who_mode}{i} "
                                                    dosend(bytes(f"{tags()}:{server} 353 {pending} = {channel} :{users}\r\n","UTF-8"))
                                        dosend(bytes(f"{tags()}:{server} 366 {pending} {channel} :End of /NAMES list.\r\n","UTF-8"))
                                elif command == "NOTICE":
                                    if len(args) >= 2:
                                        content = parseOutContent(" ".join(text.split(" ")[2:]))
                                        target = text.split(" ")[1]
                                        if target.lower() in lower_nicks:
                                            target = lower_nicks[target.lower()]
                                        if target in channels_list:
                                            if pending in channels_list[target]:
                                                for i in channels_list[channel]:
                                                    try:
                                                        if i != pending:
                                                            property_list[i]["pendingSend"] += f"{tags_diffclient(i)}:{pending}!{rident}@{hostname} NOTICE {target} :{content}\r\n"
                                                    except:
                                                        pass
                                        elif target in nickname_list:
                                            property_list[target]["pendingSend"] += f"{tags_diffclient(target)}:{pending}!{rident}@{hostname} NOTICE {target} :{content}\r\n"
                                        else:
                                            dosend(bytes(f"{tags()}:{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                                    else:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
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
                                                    property_list[j]["pendingSend"] += f"{tags_diffclient(j)}:{pending}!{rident}@{hostname} {text}\r\n"
                                                    done.append(j)
                                            # Remove the quitting user from the channel.
                                            try:
                                                channels_list[i].remove(pending)
                                            except:
                                                print(traceback.format_exc())
                                    # Confirm QUIT and close the socket.
                                    stillRunning = False
                                    try:
                                        dosend(bytes(f"{tags()}:{pending}!{rident}@{hostname} {text}\r\n","UTF-8"))
                                        dosend(bytes(f"ERROR :Closing Link: {hostname} ({msg})\r\n","UTF-8"))
                                    except:
                                        connection.close()
                                        safe_quit = True
                                        break
                                elif command == "MODE":
                                    target = args[0]
                                    if len(args) == 0:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                    elif len(args) == 1:
                                        if args[0] == pending:
                                            yourmodes = property_list[pending]["modes"]
                                            dosend(bytes(f"{tags()}:{server} 221 {pending} +{yourmodes}\r\n","UTF-8"))
                                        elif args[0] in channels_list:
                                            if args[0] in property_list:
                                                if "modes" in property_list[args[0]]:
                                                    # Get the modes + parameters, then print them out.
                                                    modes = property_list[args[0]]["modes"]
                                                    params = property_list[args[0]]["params"]
                                                    dosend(bytes(f"{tags()}:{server} 221 {pending} {target} +{modes} {params}\r\n","UTF-8"))
                                                else:
                                                    # Default channel mode
                                                    dosend(bytes(f"{tags()}:{server} 324 {pending} {target} +n\r\n","UTF-8"))
                                            else:
                                                # Default channel mode
                                                dosend(bytes(f"{tags()}:{server} 324 {pending} {target} +n\r\n","UTF-8"))
                                        else:
                                            if args[0][0] == "#":
                                                dosend(bytes(f"{tags()}:{server} 403 {pending} {target} :No such channel\r\n","UTF-8"))
                                            else:
                                                dosend(bytes(f"{tags()}:{server} 505 {pending} :Cant change mode for other users\r\n","UTF-8"))

                                elif command == "CATSERV" or (command == "PRIVMSG" and args[0].lower() == "catserv"):
                                    if command == "PRIVMSG":
                                        args = args[1:]
                                        if args[0][0] == ":":
                                            args[0] = args[0][1:]
                                    if len(args) == 0:
                                        dosend(bytes(f":{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                    elif args[0].upper() == "PULL":
                                        updater = subprocess.run(["git", "pull"], stdout=subprocess.PIPE)
                                        if updater.stdout.decode().strip() == "Already up to date.":
                                            dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :Codename IRCat is already up-to-date.\r\n","UTF-8"))
                                        else:
                                            dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :Done, it is recommended to use /RESTART if you're an IRC op\r\n","UTF-8"))
                                    elif args[0].upper() == "VERSION":
                                        dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :Codename IRCat version {__version__}\r\n","UTF-8"))
                                        dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :This is Codename IRCat's integrated services.\r\n","UTF-8"))
                                    else:
                                        dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :CatServ Usage:\r\n","UTF-8"))
                                        dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :PULL     - Pulls the latest version of Codename IRCat\r\n","UTF-8"))
                                        dosend(bytes(f"{tags()}:CatServ!Meow@IRCatCore NOTICE {pending} :VERSION  - Gets the version number of this service.\r\n","UTF-8"))
                                elif command == "RESTART":
                                    if "o" in property_list[pending]["modes"]:
                                        global opened
                                        opened = False
                                    else:
                                        dosend(bytes(f"{tags()}:{server} 481 {pending} :Permission Denied- You're not an IRC operator\r\n","UTF-8"))
                                elif command == "KILL":
                                    if "o" in property_list[pending]["modes"]:
                                        target = args[0]
                                        try:
                                            reason = parseOutContent(" ".join(args[1:])) if len(args) > 1 else "No reason given"
                                            property_list[target]["kill_user"] = pending
                                            property_list[target]["kill_comment"] = reason
                                            property_list[target]["kill"] = True
                                        except:
                                            dosend(bytes(f"{tags()}:{server} 403 {pending} {target} :No such channel\r\n","UTF-8"))
                                    else:
                                        dosend(bytes(f"{tags()}:{server} 481 {pending} :Permission Denied- You're not an IRC operator\r\n","UTF-8"))
                                elif command == "PRIVMSG":
                                    if len(args) >= 2:
                                        content = parseOutContent(" ".join(text.split(" ")[2:]))
                                        target = text.split(" ")[1]
                                        if target.lower() in lower_nicks:
                                            target = lower_nicks[target.lower()]
                                        if target in channels_list:
                                            if pending in channels_list[target]:
                                                for i in channels_list[target]:
                                                    try:
                                                        if i != pending:
                                                            property_list[i]["pendingSend"] += f"{tags_diffclient(i)}:{pending}!{rident}@{hostname} PRIVMSG {target} :{content}\r\n"
                                                    except:
                                                        print(traceback.format_exc())
                                        elif target in nickname_list:
                                            property_list[target]["pendingSend"] += f"{tags_diffclient(target)}:{pending}!{rident}@{hostname} PRIVMSG {target} :{content}\r\n"
                                        else:
                                            dosend(bytes(f"{tags()}:{server} 401 {pending} {target} :No such nick/channel\r\n","UTF-8"))
                                    else:
                                        dosend(bytes(f"{tags()}:{server} 461 {pending} {command} :Not enough parameters\r\n","UTF-8"))
                                elif command == "MOTD":
                                    if motd_file != None:
                                        motd = open(motd_file).read()
                                    dosend(bytes(f":{server} 375 {pending} :- {server} Message of the Day -\r\n", "UTF-8"))
                                    for i in motd.rstrip().split("\n"):
                                        dosend(bytes(f":{server} 372 {pending} :- {i}\r\n", "UTF-8"))
                                    dosend(bytes(f":{server} 376 {pending} :End of /MOTD command\r\n", "UTF-8"))
                                # Ignore empty text
                                elif text.split(" ")[0] == "":
                                    pass
                                else:
                                    # Unknown command
                                    cmd = text.split(" ")[0]
                                    dosend(bytes(f":{server} 421 {pending} {cmd} :Unknown command\r\n","UTF-8"))
                            pendingCommands = ""
                        else:
                            if not alreadyNotified:
                                dosend(f":{server} 451 {pending} :You have not registered\r\n")
                                alreadyNotified = True
                            pendingCommands += text
                    textt = ""
                if finished and property_list[pending]["pendingSend"] != "":
                    dosend(bytes(str(property_list[pending]["pendingSend"]), "UTF-8"))
                    property_list[pending]["pendingSend"] = ""
                if pendingSend != "":
                    dosend(bytes(pendingSend, "UTF-8"))
                    pendingSend = ""
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
        for chan, users in channel_modestore.items():
            if pending in users:
                del channel_modestore[chan][pending]
        if not safe_quit:
            done = []
            for i, users in channels_list.items():
                if pending in users:
                    for j in users:
                        if j != pending and not j in done:
                            try:
                                property_list[j]["pendingSend"] += f":{pending}!{rident}@{hostname} QUIT :{cause}\r\n"
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
def tcp_session(sock, ip_to):
    prctl.set_name(f"Listener")
    while opened:
        try:
            print("Waiting for connection...")
            connection, client = sock.accept()
            threading.Thread(target=session, daemon=True, args=[connection, client, ip_to]).start()
        except:
            print("Something went wrong...")
            print(traceback.format_exc())
def ssl_session(sock, ip_to):
    prctl.set_name(f"SSL Listener")
    while opened:
        try:
            print("Waiting for SSL connection...")
            connection, client = sock.accept()
            threading.Thread(target=session, daemon=True, args=[connection, client, ip_to, True]).start()
        except:
            print("Something went wrong...")
            print(traceback.format_exc())
for ip, i in sockets.items():
    print("Now listening on port 6667 with IP " + ip)
    threading.Thread(target=tcp_session, args=[i, ip], daemon=True).start()
if ssl_option:
    for ip, i in sockets_ssl.items():
        print("Now listening on SSL port 6697 with IP " + ip)
        threading.Thread(target=ssl_session, args=[i, ip], daemon=True).start()
while opened:
    time.sleep(5)
print("Shutting down...")
