import os, sys, sqlite3
from __main__ import config
__ircat_type__ = "allsocket"
__ircat_requires__ = ["ban-provider", "host"]
class IRCatModule:
    memory = {} # {ip: [content]}
    useSQLengine = False
    def __init__(self, ban_provider, host):
        self.ban_provider = ban_provider
        if ban_provider == "sql":
            self.host = host
            self.useSQLengine = True
            self.SQLengine = config
    def onValidate(self, socket, ip):
        print("IP is banned, killing connection now...")
        reason = " ".join(i.split(" ")[1:])
        host = self.host
        socket.sendall(bytes(f":{host} 465 * :You are banned from this server\r\n","UTF-8"))
        socket.sendall(bytes(f"ERROR :Closing Link: {ip} (K-Lined: {reason})\r\n","UTF-8"))
        raise Exception("K-Lined: " + " ".join(i.split(" ")[1:]))
    def onSocket(self, socket, value, ip, cachedNick=None):
        if self.useSQLengine:
            pass
        else:
            bans = open(self.ban_provider).read.split("\n")
            for i in bans:
                if ip in i.split(" ")[0]:
                    print("IP is banned, killing connection now...")
                    reason = " ".join(i.split(" ")[1:])
                    host = self.host
                    socket.sendall(bytes(f":{host} 465 * :You are banned from this server\r\n","UTF-8"))
                    socket.sendall(bytes(f"ERROR :Closing Link: {ip} (K-Lined: {reason})\r\n","UTF-8"))
                    raise Exception("Banned: " + " ".join(i.split(" ")[1:]))
        pass
    def ban(self, target_mask, reason="The ban() hammer has spoken!"):
        if self.useSQLengine:
            cur = self.SQLengine.conn.cursor()
        else:
            open(self.ban_provider, "a").write(f"\n{target_mask} {reason}")