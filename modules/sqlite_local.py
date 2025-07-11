# IRCat module for local SQLite database (default)
import sqlite3, os, traceback
from cryptography.fernet import Fernet
from argon2 import PasswordHasher
ph = PasswordHasher()
__ircat_type__ = "sql.provider" # The type of module
__ircat_requires__ = ["data-path", "fernet-key"] # The required config.yml entries.
class broker:
    def __init__(self, data_path, fernet_key):
        if not os.path.isfile(data_path):
            print("Creating database file...")
            open(data_path, "w").write("")
        self.conn = sqlite3.connect(data_path, check_same_thread=False)
        self.fnet = Fernet(fernet_key)
        db = self.conn.cursor()
        db.execute("""CREATE table IF NOT EXISTS bans (ip varchar(255), reason varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS nickserv (user varchar(255), modes varchar(255), hash varchar(255), email varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS groups (name varchar(255), owner varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS chanserv (name varchar(255), modes varchar(255), params varchar(255), owner varchar(255), usermodes varchar(255), optimodes varchar(255))""")
    def nickserv_identify(self, nick, password:str):
        db = self.conn.cursor()
        db.execute("SELECT * FROM groups WHERE name=?", [nick])
        f = db.fetchall()
        if f != []:
            nick = f[0][1]
        db.execute("SELECT * FROM nickserv WHERE user=?;", [nick])
        e = db.fetchall()
        if e == []:
            return False
        else:
            try:
                if "$argon2id" not in e[0][2]:
                    print("[XXX] User was registered before 0.0.9, automatically porting hash to Argon2...")
                    hash = self.fnet.decrypt(bytes(e[0][2], "UTF-8")).decode() == password
                    temphash = self.fnet.decrypt(bytes(e[0][2], "UTF-8")).decode()
                    temphash = ph.hash(temphash)
                    db = self.conn.cursor()
                    db.execute("UPDATE nickserv SET hash=? WHERE user=?;", [temphash, nick])
                    self.conn.commit()
                else:
                    try:
                        hash = ph.verify(e[0][2], password)
                    except:
                        hash = False
                return e[0] if hash else False
            except:
                print(traceback.format_exc())
                return False
    def nickserv_register(self, nick, password, email):
        hashed = ph.hash(password)
        db = self.conn.cursor()
        db.execute("INSERT INTO nickserv values(?, 'iw', ?, ?);", [nick, hashed, email])
        self.conn.commit()
    def nickserv_isexist(self, nick):
        db = self.conn.cursor()
        db.execute("SELECT * FROM nickserv WHERE user=?;", [nick.lower()])
        e = db.fetchall()
        db.execute("SELECT * FROM groups WHERE name=?;", [nick.lower()])
        f = db.fetchall()
        return e != [] or f != []
    def nickserv_group(self, nick, account):
        db = self.conn.cursor()
        db.execute("INSERT INTO groups VALUES (?, ?);", [nick.lower(), account.lower()])
        self.conn.commit()
    def nickserv_drop(self, account):
        db = self.conn.cursor()
        db.execute("DELETE FROM nickserv WHERE user=?;", [account.lower()])
        db.execute("DELETE FROM groups WHERE owner=?;", [account.lower()])