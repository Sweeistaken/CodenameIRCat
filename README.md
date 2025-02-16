![IRCat Logo](https://git.swee.codes/swee/IRCat/raw/branch/main/ircat-invert.svg)

Lightweight IRCd in Python

* [Mastodon tag (for updates)](https://mastodon.swee.codes/tags/CodenameIRCat)
* [Issue tracker](https://discuss.swee.codes/c/12)

[To-do list](todo.md)

# Looking for SweeNet?

You may check out the server details on https://ircat.xyz/try

Alternatively, you can access the webchat on https://web.ircat.xyz

# How to install

## Requirements

* Python 3 (Doesn't matter which platform, but IRCat is only tested on Linux)
   * `requests` module
   * `yaml` module (`pyyaml` on PyPi/pip)
   * `cloudflare` module (MUST be version 4.0.0 or higher, Optional: only needed for `cfd1` plugin.)

You can get configuration by editing the `config.yml` example in this repo.

Command syntax:

```bash
python3 /path/to/ircat/server.py /path/to/config.yml
```