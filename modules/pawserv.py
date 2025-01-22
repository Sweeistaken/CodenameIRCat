# Replacement for services bots.
import traceback
__ircat_type__ = "command"
__ircat_requires__ = []
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
class command:
    def __init__(self, sql):
        self.sql = sql
        print("PawServ loaded!")
    def command(self, command, args, ip, nick, connection, user):
        try:
            if command == "NICKSERV" or (command == "PRIVMSG" and args[0].lower() == "nickserv"):
                if command == "PRIVMSG":
                    args = args[1:]
                    args[0] = args[0][1:] if args[0][0] == ":"
                if args[0].lower() == "identify":
                    connection.sendall(Bytes(f":NickServ!Meow@PawServ NOTICE {nick} :Feature not implemented in PawServ plugin yet.", "UTF-8"))
                elif:
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :NickServ Usage:\r\n","UTF-8"))
                    connection.sendall(bytes(f":NickServ!Meow@PawServ NOTICE {nick} :IDENTIFY <nick> pass - Identifies your nickname\r\n","UTF-8"))
                return True
            else:
                return False
        except:
            print(traceback.format_exc())
            return False