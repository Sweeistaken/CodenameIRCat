# Codename IRCat

Lightweight IRCd in Python

* [Mastodon tag (for updates)](https://mastodon.swee.codes/tags/CodenameIRCat)
* [Issue tracker](https://discuss.swee.codes/c/12)

TODO:
- [ ] Implement the base of an IRCd, using Libera.Chat as a reference
   -  [x] Add the (full) connection process
   -  [x] Add join/part, and it's requirements (WHO, etc)
   -  [x] Implement proper PRIVMSG
   -  [x] Broadcast QUIT
   -  [x] DNS lookup
   -  [x] Identity management
   -  [ ] WallOps
   -  [ ] Channel invite system
   -  [ ] Wildcard logic (for +b and +q)
   -  [x] Send PING and wait for PONG
   -  [x] Reply PONG if received PING
   -  [ ] Change of nicknames
   -  [ ] Change of hostnames
-  [ ] User Flags
   -  [ ] i (invisible)
   -  [ ] o (IRCOP)
   -  [ ] w (gets wallops)
-  [ ] Channel Flags
   -  [ ] o \<user\> (CHANOP)
   -  [ ] v \<user\> (voice)
   -  [ ] m (moderated, only let voice or op talk)
   -  [ ] s (don't show in LIST)
   -  [ ] i (invite-only)
   -  [ ] t (topic lock)
   -  [ ] n (no outside msgs, people have to join first)
   -  [ ] l \<num\> (user limit)
   -  [ ] b \<usermask\> (ban a user)
   -  [ ] k \<key\> (password lock)
   -  [ ] EXTRAS q (Quiet)
- [ ] Destructive features for CHANOPS
   -  [ ] `KICK`
   -  [ ] `MODE <channel>`
- [ ] Destructive features for IRCOPS
   -  [ ] `KILL <user> <comment>`
   -  [ ] `MODE <external user>`
   -  [ ] `RESTART`
- [ ] Extra commands
   -  [ ] `USERS`
   -  [x] `WHOIS`
   -  [ ] `WHOWAS`
- [ ] Implement services.
   -  [ ] Nickserv
   -  [ ] ChanServ
   -  [x] GitServ (Custom user for pull)
   -  [ ] Link `PRIVMSG *serv` to `*serv`
- [ ] Extra (not planned) features
   -  [ ] ident support
- [ ] Add IRCv3 features.
   -  [x] List capabilities (`CAP LS 302`)
   -  [ ] `away-notify`
   -  Will research later.

I am going to fully read [RFC 1459](https://datatracker.ietf.org/doc/html/rfc1459) soon and add each part to the TODO.