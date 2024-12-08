# IRCat

Lightweight IRCd in Python

TODO:
- [ ] Implement the base of an IRCd, using Libera.Chat as a reference
  -  [ ] Add the connection process
  -  [x] Add join/part, and it's requirements (WHO, etc)
  -  [x] Implement proper PRIVMSG
  -  [ ] Broadcast QUIT
  -  [ ] DNS lookup
  -  [ ] Identity management
- [ ] Implement services.
  -  [ ] Nickserv
  -  [ ] ChanServ
  -  [ ] Link `PRIVMSG *serv` and `*s` to `*serv`
- [ ] Add IRCv3 features.
  -  Will research later.