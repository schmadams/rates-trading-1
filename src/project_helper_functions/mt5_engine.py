import os
import MetaTrader5 as mt5
from src.project_helper_functions.check_env import check_env
from src.project_helper_functions.helpers import load_config

check_env()

def mt5_connect_and_auth(strategy: str):
    config = load_config()
    account = config['strategies'][strategy]['account']
    creds = config['accounts'][account]
    for key, value in creds.items():
        creds.update({
            key: os.environ.get(value)
        })

    # Initialize MetaTrader 5 connection
    mt5.initialize()

    # Connect to MetaTrader 5 account and authenticate
    authorized = mt5.login(login=int(creds['login']), password=creds['password'], server=creds['server'])

    print(f"Authorizing with creds {creds['login']}, {creds['server']}, {creds['password']}")
    if authorized:
        print('Authentication successful')
    else:
        print('Authentication failed')
        print(mt5.last_error())

if __name__ == '__main__':
    mt5_connect_and_auth(strategy='demo_triarb_v1')
