![IRCat Logo](https://git.swee.codes/swee/IRCat/raw/branch/main/ircat-invert.svg)

Lightweight IRCd in Python

* <a rel="me" href="https://mastodon.swee.codes/@ircat">Mastodon</a>
* [Issue tracker](https://discuss.swee.codes/c/12)

[To-do list](todo.md)

# Looking for SweeNet?

You may check out the server details on https://ircat.xyz/try

Alternatively, you can access the webchat on https://web.ircat.xyz

# Our mission

We want to make IRC good again, we're talking about botnet protection,

ease to host, easily build your own IRC network, etc etc.

With our updating plugins, you can make your network use IRCat and protect

your network from the nasty botnets, spambots, and exploits.

# Disclaimer

This project is very experimental and is currently not recommended for production usage.

Although this IRCd software is pretty stable, there's still a lot of IRC features that need to be implemented.

# How to install

## Requirements

* Python 3 (Doesn't matter which platform, but IRCat is only tested on Linux)
   * `requests` module
   * `argon2-cffi` module
   * `yaml` module (`pyyaml` on PyPi/pip)
   * `cloudflare` module (MUST be version 4.0.0 or higher, Optional: only needed for `cfd1` plugin.)

## Configuration

You can get configuration by editing the `config.yml` example in this repo.

## Command syntax

```bash
python3 /path/to/ircat/server.py /path/to/config.yml
```

# Docker

Use this compose file

```yaml
services:
    ircat:
        image: git.swee.codes/swee/ircat:latest
        restart: unless-stopped
        ports:
            - 6667:6667
            # - 6697:6697
        volumes:
            - ./data:/app/data
```

Create a `config.yml` inside the `data` directory of your compose file, using the example in this repository, or else IRCat will fail to start.