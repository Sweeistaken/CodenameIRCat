import os, traceback
from cryptography.fernet import Fernet
from cloudflare import Cloudflare # Please make sure you install this module from pip, not package manager.
__ircat_type__ = "sql.provider" # The type of module
__ircat_requires__ = ["cf_accountid", "cf_apitoken", "cf_d1database", "fernet-key"] # The required config.yml entries.
class broker:
    def __init__(self, cf_accountid:str, cf_apitoken:str, cf_d1database:str, fernet_key:str):
        self.account_id = cf_accountid
        self.api_token = cf_apitoken
        self.database = cf_d1database
        self.client = Cloudflare(api_token=cf_apitoken)
        self.fnet = Fernet(fernet_key)
        self.client.d1.database.query(
            database_id=self.database,
            account_id=self.account_id,
            sql="CREATE table IF NOT EXISTS bans (ip varchar(255), reason varchar(255)); CREATE table IF NOT EXISTS nickserv (user varchar(255), modes varchar(255), hash varchar(255), email varchar(255)); CREATE table IF NOT EXISTS groups (name varchar(255), owner varchar(255)); CREATE table IF NOT EXISTS chanserv (name varchar(255), modes varchar(255), params varchar(255), owner varchar(255), usermodes varchar(255), optimodes varchar(255))",
        )
    def cfexec(self, command:str, params:list):
        query = self.client.d1.database.query(
            database_id=self.database,
            account_id=self.account_id,
            sql=command,
            params=params
        )
        return query[0].results
    def parse2sqlite(self, results):
        temp = []
        for k, v in results.items():
            temp.append(v)
        return temp
    def nickserv_identify(self, nick, password:str):
        f = self.cfexec("SELECT * FROM groups WHERE name=?;", [nick])
        if len(f) != 0:
            nick = f[0]["owner"]
        e = self.cfexec("SELECT * FROM nickserv WHERE user=?;", [nick])
        if len(e) == 0:
            return False
        else:
            try:
                return self.parse2sqlite(e[0]) if self.fnet.decrypt(bytes(e[0]["hash"], "UTF-8")).decode() == password else False
            except:
                print(traceback.format_exc())
                return False
    def nickserv_register(self, nick, password, email):
        hashed = self.fnet.encrypt(bytes(password, "UTF-8")).decode()
        e = self.cfexec("INSERT INTO nickserv values(?, 'iw', ?, ?);", [nick, hashed, email])
    def chanserv_details(self, channel):
        e = self.cfexec("SELECT * FROM chanserv WHERE name=?;", [channel])
        print(e)
        if len(e) == 0:
            return False
        else:
            try:
                return e[0]
            except:
                print(traceback.format_exc())
                return False
    def nickserv_isexist(self, nick):
        e = self.cfexec("SELECT * FROM nickserv WHERE user=?;", [nick])
        f = self.cfexec("SELECT * FROM groups WHERE name=?;", [nick])
        return len(e) != 0 or len(f) != 0
    def nickserv_group(self, nick, account):
        self.cfexec("INSERT INTO groups VALUES (?, ?);", [nick.lower(), account.lower()])
    def nickserv_drop(self, account):
        self.cfexec("DELETE FROM nickserv WHERE user=?;", [account.lower()])
        self.cfexec("DELETE FROM groups WHERE owner=?;", [account.lower()])