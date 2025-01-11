import threading
__ircat_type__ = "allsocket"
__ircat_requires__ = ["ban-provider"]
__ircat_giveme__ = ["sql"] # Only command and allsocket have these.
__ircat_fakechannels__ = {"#IRCATSUCKS": "WHATEVER YOU DO, DO NOT JOIN IF YOU ARE HUMAN"}
class IRCatModule:
    sus_strings = [
        "                                 .''." # Latest Supernets spambot!
    ]
    memory = {} # {nick: {channel: trustlevel}} one can also be {nick: True} if it is whitelisted for the session.
    def __init__(self, ban_provider, sql):
        self.ban_provider = ban_provider
        if ban_provider == "sql":
            self.useSQLengine = True
            self.SQLengine = sql
    def ban(self, ip):
        if self.useSQLengine:
            cur = self.SQLengine.conn.cursor()
        else:
            open(self.ban_provider, "a").write(f"\n{ip} Botnet detected!")
        raise Exception("Botnet detected!")
    def onSocket(self, ip, socket, value, cachedNick=None, validated=False):
        if validated:
            if self.memory[cachedNick + "|" + ip] != True:
                if "JOIN" in value:
                    target = value.split(" ")[1]
                    self.memory[cachedNick + "|" + ip][target] = 1 # 1: Just joined the channel, continue observing.
                    if target == "#IRCATSUCKS":
                        self.ban(ip)
                elif "PRIVMSG" in value:
                    target = value.split(" ")[1]
                    content = " ".join(value.split(" ")[2:])[1:]
                    if content in sus_strings and self.memory[cachedNick + "|" + ip][target] == 1:
                        self.ban(ip)
                    else:
                        self.memory[cachedNick + "|" + ip] = True # Trust the connection  :3