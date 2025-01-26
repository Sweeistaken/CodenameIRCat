import requests, os
__ircat_type__ = "sql.provider" # The type of module
__ircat_requires__ = ["cf_accountid", "cf_apitoken", "cf_d1database"] # The required config.yml entries.
class broker:
    def __init__(self, cf_accountid:str, cf_apitoken:str, cf_d1database:str):
        self.account_id = cf_accountid
        self.api_token = cf_apitoken
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }
        requests.post(self.base_url, headers=self.headers, json={"sql": "CREATE table IF NOT EXISTS bans (ip varchar(255), reason varchar(255)); CREATE table IF NOT EXISTS nickserv (user varchar(255), modes varchar(255), hash varchar(255), email varchar(255)); CREATE table IF NOT EXISTS groups (name varchar(255), owner varchar(255)); CREATE table IF NOT EXISTS chanserv (name varchar(255), modes varchar(255), params varchar(255), owner varchar(255), usermodes varchar(255), optimodes varchar(255))"})
    def cf_insert(self, command:str, params:list):
        rq = requests.post(self.base_url, headers=self.headers, json={"sql": command, "params": params})