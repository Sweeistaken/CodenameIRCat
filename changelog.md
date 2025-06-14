# 0.0.9 (Pre-Release)
* Multi-server support (Progress: STARTING)
* Full Chanserv support in `pawserv` plugin (Progress: PLANNED)
* Dockerfile (Progress: PLANNED)
* Argon2 instead of Fernet (Progress: Working on....)

# 0.0.7
* The first stable release of IRCat (SweeNet stability is OK)
* Implement IRC features:
    * ISON
    * TOPIC
    * LIST (After new topic feature)
    * KILL
    * WEBIRC (For SweeNet webchat)
    * RESTART
* Implement IRCv3 features:
    * Timestamps (`server-time`)
    * Account indicator (`account-tag`)
* Bare chanserv support on `pawserv` plugin
* IRC operator support
* Channel mode support
* Fixed bugs:
    * Mostly SSL issues
    * Erroneus nicknames/channels
    * Problems with NICK not being synced


# 0.0.5
* Ident support
* Create plugins:
    * Cloudflare D1 (`cfd1`)
* Implement IRC features:
    * LIST (bare support)
* Rename GitServ to CatServ
* Full nickserv support on `pawserv`
* Fixed bugs:
    * MOTD printed incorrectly
    * Revolution IRC crashes on RPL_ISUPPORT

# 0.0.4

* Implement IRC features:
    * NOTICE
    * MOTD
* Create plugins:
    * Botnet filtering (`botnet_protect`)
    * K-Lines (`ban_engine`)
    * PawServ service bots (`pawserv`)
* Create GitServ (External from `pawserv` plugin)
* SSL support
* And overall, a lot of bug fixes with the existing code.

# 0.0.1
* Create stable (Non-SSL) TCP sockets
* Add YAML config
* Create plugins:
    * SQLite file (`sqlite_local`)
* Implement IRC features:
    * RPL_ISUPPORT
    * PING
    * CAP LS (IRCv3)
    * PRIVMSG
    * WHO
    * NAMES
    * JOIN/PART
    * Bare MODE support (read-only user modes `+iw` and read-only channel modes `+nt`)
    * NICK
    * USER
    * WHOIS
    * AWAY
    * QUIT
* The very first version