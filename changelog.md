# 0.0.9 (Pre-Release)
* [ ] Multi-server support (Progress: PLANNED)
* [ ] Full Chanserv support in `pawserv` plugin (Progress: PLANNED)
* [x] Dockerfile
* [ ] Add `rebellious` config, where channel and nicknames don't have to follow RFC1459 guidelines (Except for ones that will break clients if not followed)
* [ ] Prometheus metrics (Progress: PLANNED)
* Show connection information in COMM ([Explanation](https://lounge.swee.codes/uploads/fb071794558484f7/pasted%20file.png))
* Implement IRC features
  * ERR_NOTREGISTERED
* Implement IRCv3 features:
  * [ ] Notify on AWAY (`away-notify`)
  * [ ] Notify on IDENTIFY (`account-notify`)
  * [ ] More JOIN info (`extended-join`)
* Security
  * Argon2 instead of Fernet for passwords
* Bug fixes
  * SSL port times out
  * Decode with `latin-1` if `UTF-8` fails
  * Bind ident fetcher to make sure correct IP is being used when fetching ident for a client that is local
  * Reduce CPU usage in main process

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