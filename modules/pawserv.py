# Replacement for services bots.
import traceback, smtplib, uuid, ssl
__ircat_type__ = "command"
__ircat_requires__ = ["name", "smtp_host", "smtp_port", "smtp_starttls", "smtp_username", "smtp_password"]
__ircat_giveme__ = ["sql"] # Only command and allsocket have these.
__ircat_fakeusers__ = {
    "NickServ": {
        "host": "PawServ",
        "username": "Meow", 
        "realname": "PawServ plugin - Identification bot", 
        "modes": "iw", "away": False
        }, 
    "ChanServ": {
        "host": "PawServ", 
        "username": "Meow", 
        "realname": "PawServ plugin - Channel management bot", 
        "modes": "iw", 
        "away": False
        }
    }
class IRCatModule:
    def __init__(self, sql, smtp_host, smtp_port, smtp_starttls, smtp_username, smtp_password, name):
        self.sql = sql
        self.smtp_server = smtp_host
        self.smtp_port = smtp_port
        self.smtp_starttls = smtp_starttls
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.net_name = name
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
                        if args[1] in self.memory:
                            if args[2] == self.memory[args[1]][0]:
                                self.sql.nickserv_register(nick=args[1], password=self.memory[args[1]][1], email=self.memory[args[1]][2])
                        else:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Nickname doesn't exist, try registering again?\r\n", "UTF-8"))
                    else:
                        connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Invalid verification.\r\n", "UTF-8"))
                elif len(args) > 0 and args[0].lower() == "register":
                    if len(args) == 3:
                        if not nick in self.memory:
                            context = ssl.create_default_context()
                            token = str(uuid.uuid4())
                            message = f"\\nSubject: {self.net_name} Account Verification\n\nHi,\nIt appears you have tried to register an account ({nick}) with this email on {self.net_name},\nIf you did not register an account, feel free to delete this email.\nIf you did, use this command:\n/nickserv verify {nick} {token}"
                            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                                server.ehlo()
                                server.starttls(context=context)
                                server.ehlo()
                                server.login(self.smtp_username, self.smtp_password)
                                server.sendmail(self.smtp_username, args[2], message)
                            self.memory[nick] = [token, args[1], args[2]]
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Email sent, please verify.\r\n", "UTF-8"))
                        else:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :A verification is already pending.\r\n", "UTF-8"))
                    else:
                        connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Needs 3 arguments, nickname, password, and email.\r\n", "UTF-8"))
                elif len(args) > 0 and args[0].lower() == "identify":
                    temp = self.sql.nickserv_identify(nick=nick if len(args) == 2 else args[2], password=args[1])
                    if temp:
                        connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Now, it would've been a successful identification, but this is work in progress.\r\n", "UTF-8"))
                    else:
                        if nick in self.memory:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Your account isn't verified, please verify now.\r\n", "UTF-8"))
                        else:
                            connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Invalid username/password.\r\n", "UTF-8"))
                else:
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :NickServ Usage:\r\n","UTF-8"))
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :IDENTIFY pass <nick> - Identifies your nickname\r\n","UTF-8"))
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :REGISTER pass email - Register your nickname\r\n","UTF-8"))
                return True
            else:
                return False
        except:
            print(traceback.format_exc())
            return False