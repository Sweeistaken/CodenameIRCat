# IRCat module for local SQLite database (default)
import sqlite3
__ircat_type__ = "sql.provider" # The type of module
__ircat_requires__ = ["data_path"] # The required config.yml entries.
class SQLiteDataBroker:
    def __init__(self):
        if not os.path.isfile(data_path):
            print("Creating database file...")
            open(data_path, "w").write("")
        self.conn = sqlite3.connect(data_path)
        db = self.conn.cursor()
        db.execute("""CREATE table IF NOT EXISTS nickserv (user varchar(255), modes varchar(255), hash varchar(255), cloak varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS groups (name varchar(255), owner varchar(255))""")
        db.execute("""CREATE table IF NOT EXISTS chanserv (name varchar(255), modes varchar(255), params varchar(255), owner varchar(255), usermodes varchar(255), optimodes varchar(255))""")
    def nickserv_gethash(self, nick, password:str):
        db = self.conn.cursor()
        password = password.encode("UTF-8")
        db.execute("SELECT * FROM nickserv WHERE user=?;", [nick])
        e = db.fetchall()
        if e == []:
            return ["Nickname doesn't exist."]
        else:
            return e