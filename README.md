![IRCat Logo](https://git.swee.codes/swee/IRCat/raw/branch/main/ircat-invert.svg)

Lightweight and modular IRCd in Python

* <a rel="me" href="https://mastodon.swee.codes/@ircat">Mastodon</a>
* [To-do list](todo.md)

# Looking for SweeNet?

You may check out the server details on https://ircat.xyz/try

Alternatively, you can access the webchat on https://web.ircat.xyz

# Disclaimer

This project is very experimental and is currently not recommended for production usage.

Although this IRCd software is pretty stable when it comes to security, there's still a lot of IRC features that need to be implemented.

# How to install

## Requirements

* A Linux machine
* Python 3 (Tested in 3.12)
   * Don't forget to use `pip install -r requirements.txt`

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