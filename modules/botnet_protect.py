import threading
__ircat_type__ = "allsocket"
__ircat_requires__ = []
__ircat_giveme__ = ["banprovider", "threadid"] # Only command and allsocket have these.
class IRCatModule:
    sus_strings = [
        "                                 .''."
    ]
    memory = {} # {nick: {channel: trustlevel}} one can also be {nick: True} if it is whitelisted for the session.
    def __init__(self, banprovider):
        self.ban_provider = banprovider
    def onSocket(self, ip, socket, value, cachedNick=None, validated=False):
        if validated:
            if self.memory[cachedNick + "|" + ip] != True:
                if "JOIN" in value:
                    target = value.split(" ")[1]
                    memory[cachedNick + "|" + ip][target] = 1 # 1: Just joined the channel, continue observing.
                elif "PRIVMSG" in value:
                    target = value.split(" ")[1]
                    content = " ".join(value.split(" ")[2:])[1:]
                    if content in sus_strings and self.memory[cachedNick + "|" + ip][target] == 1:
                        self.ban_provider.ban(target_mask=ip, reason="Botnet detected!")
                    else:
                        self.memory[cachedNick + "|" + ip] = True # Trust the connection :3