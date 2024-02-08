import os
import MetaTrader5 as mt5
from src.project_helper_functions.check_env import check_env
from src.project_helper_functions.helpers import load_config
from logging_functions.class_logging import Logger


check_env()

class MetaTraderConnection:
    logger = Logger(__qualname__).logger
    def __init__(self, account: str = 'demo_meta_100k'):
        self.config = load_config()
        self.get_creds(account)
        self.connect_and_auth()

    def get_creds(self, account: str = 'demo_meta_100k'):
        self.creds = self.config['accounts'][account]
        for key, value in self.creds.items():
            self.creds.update({
                key: os.environ.get(value)
            })
    def connect_and_auth(self):
        authorized = mt5.login(self.creds['login'])
        self.logger.info(f"Authorizing with creds {self.creds['login']}, {self.creds['server']}, {self.creds['password']}")
        if authorized:
            authorized = mt5.login(self.creds['login'], password=self.creds['password'])

        init = mt5.initialize(login=int(self.creds['login']), password=self.creds['password'],
                              server=self.creds['server'], timeout=3600000)

if __name__ == '__main__':
    MetaTraderConnection()