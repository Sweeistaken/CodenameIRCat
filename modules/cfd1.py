import requests, os
__ircat_type__ = "sql.provider" # The type of module
__ircat_requires__ = ["cf_accountid", "cf_apitoken", "cf_d1database"] # The required config.yml entries.
class broker:
    def __init__(self, cf_accountid, cf_apitoken, cf_d1database):
        self.account_id = cf_accountid
        self.api_token = cf_apitoken
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/d1/database"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_token}"
        }