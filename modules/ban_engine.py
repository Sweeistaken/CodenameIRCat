import os, sys, sqlite3
__ircat_type__ = "allsocket"
__ircat_requires__ = ["ban-provider", "host"]
__ircat_giveme__ = ["sql"] # Only command and allsocket have these.
class IRCatModule:
    memory = {} # {ip: [content]}
    useSQLengine = False
    def __init__(self, ban_provider, host, sql):
        self.ban_provider = ban_provider
        self.host = host
        if ban_provider == "sql":
            self.useSQLengine = True
            self.SQLengine = sql
    def onValidate(self, socket, ip, *args, **kwargs):
        bans = open(self.ban_provider).read().split("\n")
        for i in bans:
            if ip in i.split(" ")[0]:
                print("IP is banned, killing connection now...")
                reason = " ".join(i.split(" ")[1:])
                host = self.host
                socket.sendall(bytes(f":{host} 465 * :You are banned from this server\r\n","UTF-8"))
                socket.sendall(bytes(f"ERROR :Closing Link: {ip} (K-Lined: {reason})\r\n","UTF-8"))
                raise Exception("K-Lined: " + " ".join(i.split(" ")[1:]))
    def onSocket(self, socket, value, ip, cachedNick=None, validated=False, *args, **kwargs):
        if validated:
            if self.useSQLengine:
                pass
            else:
                bans = open(self.ban_provider).read().split("\n")
                for i in bans:
                    if ip in i.split(" ")[0]:
                        print("IP is banned, killing connection now...")
                        reason = " ".join(i.split(" ")[1:])
                        host = self.host
                        socket.sendall(bytes(f":{host} 465 * :You are banned from this server\r\n","UTF-8"))
                        socket.sendall(bytes(f"ERROR :Closing Link: {ip} (K-Lined: {reason})\r\n","UTF-8"))
                        raise Exception("Banned: " + " ".join(i.split(" ")[1:]))
    def ban(self, target_mask, reason="The ban() hammer has spoken!"):
        if self.useSQLengine:
            self.SQLengine.ban(target_mask, reason)
        else:
            open(self.ban_provider, "a").write(f"\n{target_mask} {reason}")