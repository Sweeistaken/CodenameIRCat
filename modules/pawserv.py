# Replacement for services bots.
import traceback, smtplib, uuid, ssl
__ircat_type__ = "command"
__ircat_requires__ = ["name", "smtp_host", "smtp_port", "smtp_starttls", "smtp_username", "smtp_password", "host"]
__ircat_giveme__ = ["sql"] # Only command and allsocket have these.
__ircat_fakeusers__ = {
    "NickServ": {
        "host": "PawServ",
        "username": "Meow", 
        "realname": "PawServ plugin - Identification bot", 
        "modes": "iw", 
        "away": False,
        "identified": False,
        "ssl": False
        }, 
    "ChanServ": {
        "host": "PawServ", 
        "username": "Meow", 
        "realname": "PawServ plugin - Channel management bot", 
        "modes": "iw", 
        "away": False,
        "identified": False,
        "ssl": False
        }
    }
class IRCatModule:
    def __init__(self, sql, smtp_host, smtp_port, smtp_starttls, smtp_username, smtp_password, name, host):
        self.sql = sql
        self.smtp_server = smtp_host
        self.smtp_port = smtp_port
        self.smtp_starttls = smtp_starttls
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.net_name = name
        self.hostname = host
        self.memory = {} # {nick: [authtoken, password, email]}
        print("PawServ loaded!")
    def command(self, command, args, ip, nick, connection, user):
        try:
            if command == "NICKSERV" or (command == "PRIVMSG" and args[0].lower() == "nickserv"):
                if command == "PRIVMSG":
                    args = args[1:]
                    args[0] = args[0][1:] if args[0][0] == ":" else args[0]
                if len(args) > 0 and args[0].lower() == "verify":
                    if len(args) == 3:
                        if args[1].lower() in self.memory:
                            if args[2] == self.memory[args[1].lower()][0]:
                                self.sql.nickserv_register(nick=args[1].lower(), password=self.memory[args[1].lower()][1], email=self.memory[args[1].lower()][2])
                                nck = args[1].lower()
                                connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Done, you may now identify as {nck}.\r\n", "UTF-8"))
                                del self.memory[args[1].lower()]
                            else:
                                connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Invalid verification.\r\n", "UTF-8"))
                        else:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Nickname doesn't exist, try registering again?\r\n", "UTF-8"))
                    else:
                        connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Invalid verification.\r\n", "UTF-8"))
                elif len(args) > 0 and args[0].lower() == "register":
                    if len(args) == 3:
                        if not self.sql.nickserv_isexist(nick.lower()):
                            if not nick in self.memory:
                                context = ssl.create_default_context()
                                token = str(uuid.uuid4())
                                message = f"Subject: {self.net_name} Account Verification\n\nHi,\nIt appears you have tried to register an account ({nick}) with this email on {self.net_name},\nIf you did not register an account, feel free to delete this email.\nIf you did, use this command:\n/nickserv verify {nick} {token}"
                                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                                    server.ehlo()
                                    if self.smtp_starttls:
                                        server.starttls(context=context)
                                        server.ehlo()
                                    server.login(self.smtp_username, self.smtp_password)
                                    server.sendmail(self.smtp_username, args[2], message)
                                self.memory[nick.lower()] = [token, args[1], args[2]]
                                connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Email sent, please verify.\r\n", "UTF-8"))
                            else:
                                connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :A verification is already pending.\r\n", "UTF-8"))
                        else:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :The user {nick} already exists.\r\n", "UTF-8"))
                    else:
                        connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Needs 3 arguments, nickname, password, and email.\r\n", "UTF-8"))
                elif len(args) > 0 and args[0].lower() == "identify":
                    nck = nick if len(args) == 2 else args[2]
                    temp = self.sql.nickserv_identify(nick=nck.lower(), password=args[1])
                    if temp != False:
                        hostmask = user["host"]
                        connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :You are now identified as {nck}.\r\n", "UTF-8"))
                        connection.sendall(bytes(f":{self.hostname} 900 {nick} {hostmask} {nck} :You are now logged in as {nck}.\r\n", "UTF-8"))
                        return {"success": True, "identify": temp}
                    else:
                        if nick.lower() in self.memory:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Your account isn't verified, please verify now.\r\n", "UTF-8"))
                        else:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Invalid username/password.\r\n", "UTF-8"))
                else:
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :NickServ Usage:\r\n","UTF-8"))
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :IDENTIFY pass <nick> - Identifies your nickname\r\n","UTF-8"))
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :REGISTER pass email - Register your nickname\r\n","UTF-8"))
                return {"success": True}
            else:
                return {"success": False}
        except:
            print(traceback.format_exc())
            return {"success": False}