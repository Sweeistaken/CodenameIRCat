# IRCat module for local SQLite database (default)
import sqlite3, os, traceback
from cryptography.fernet import Fernet
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
        db.execute("""CREATE table IF NOT EXISTS nickserv (user varchar(255), modes varchar(255), hash varchar(255), cloak varchar(255), email varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS groups (name varchar(255), owner varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS chanserv (name varchar(255), modes varchar(255), params varchar(255), owner varchar(255), usermodes varchar(255), optimodes varchar(255))""")
    def nickserv_identify(self, nick, password:str):
        db = self.conn.cursor()
        db.execute("SELECT * FROM nickserv WHERE user=?;", [nick])
        e = db.fetchall()
        if e == []:
            return False
        else:
            try:
                print(e)
                print(nick)
                print(password)
                print(e[0][2])
                print(self.fnet.decrypt(bytes(e[0][2], "UTF-8")))
                return e[0] if self.fnet.decrypt(bytes(e[0][2], "UTF-8")).decode() == password else False
            except:
                print(traceback.format_exc())
                return False
    def nickserv_register(self, nick, password, email):
        hashed = self.fnet.encrypt(bytes(password, "UTF-8")).decode()
        db = self.conn.cursor()
        db.execute("INSERT INTO nickserv values(?, 'iw', ?, ?, ?);", [nick, hashed, f"user/{nick}", email])