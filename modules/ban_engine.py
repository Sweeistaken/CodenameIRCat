import os, sys
from __main__ import config
__ircat_type__ = "allsocket"
__ircat_requires__ = "ban-provider"
class IRCatModule:
    memory = {} # {ip: [content]}
    useSQLengine = False
    def __init__(self, ban_provider):
        self.ban_provider = ban_provider
        if ban_provider = "sql":
            self.useSQLengine = True
    def onValidate(self, socket, ip):
        pass
    def onSocket(self, socket, value, ip, cachedNick=None):
        pass