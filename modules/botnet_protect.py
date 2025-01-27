import threading
__ircat_type__ = "allsocket"
__ircat_requires__ = ["ban-provider"]
__ircat_giveme__ = ["sql"] # Only command and allsocket have these.
__ircat_fakechannels__ = {"#IRCATSUCKS": "B0tn3t pr0t3ct10n, do not join."} # Fake channels that plugins control.
class IRCatModule:
    sus_strings = [
        # Known SupernetS botnet texts
        # Contribute here: https://discuss.swee.codes/t/61
        "                                 .''.", # 2025 new year
        "⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣤⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀" # "The United States of America" LATEST
    ]
    memory = {} # {nick: {channel: trustlevel}} one can also be {nick: True} if it is whitelisted for the session.
    useSQLengine = False
    def __init__(self, ban_provider, sql):
        self.ban_provider = ban_provider
        if ban_provider == "sql":
            self.useSQLengine = True
            self.SQLengine = sql
    def ban(self, ip):
        del self.memory[ip] # Forget this all happened
        # Add the ban
        if self.useSQLengine:
            self.SQLengine.addban(ip, "Botnet detected!") # Use the SQL provider if {'ban-provider': 'sql'}
        else:
            open(self.ban_provider, "a").write(f"\n{ip} Botnet detected!") # Else, write on the banfile.
        raise Exception("Botnet detected!") # Kill the connection
    def onSocket(self, ip, socket, value, cachedNick=None, validated=False):
        if cachedNick != None:
            print(value)
            if "JOIN" in value:
                target = value.split(" ")[1]
                self.memory[ip] = 1 # 1: Just joined the channel, continue observing.
                if target.lower() == "#ircatsucks":
                    self.ban(ip) # Ruh roh
            elif "PRIVMSG" in value
                if not (ip in self.memory and self.memory[ip] == 0): # Continue observing
                    target = value.split(" ")[1]
                    content = " ".join(value.split(" ")[2:])[1:]
                    if content in self.sus_strings:
                        if ip in self.memory: # Hey stinky! YOU'RE BANNED
                            if self.memory[ip] == 1:
                                self.ban(ip)
                    else:
                        self.memory[ip] = 0 # 0: Trust the connection :3