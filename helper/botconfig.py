import configparser
from pprint import pprint
import os
import sys


def blackout(s: str, n_left: int = 4) -> str:
    if len(s) <= n_left:
        return ""
    return "*" * len(s[:-n_left]) + s[-n_left:]


class BotConfig:
    bot_dir: str = ''

    # LINE notification
    line_token: str = ""

    # FTX exchange
    api_key: str = ""
    api_secret: str = ""
    sub_account: str = ""

    # trade pair
    symbol: str = ""

    # trading algorithm
    take_profit_pc: float = ""
    compound_pc: float = ""

    def __init__(self, bot_dir: str):
        self.bot_dir = bot_dir

        # https://docs.python.org/3/library/configparser.html
        config = configparser.ConfigParser()
        config_path = os.path.join(self.bot_dir, 'config.ini')
        config.read(config_path)

        self.line_token = config.get('Settings', 'LINE_TOKEN', fallback="")
        self.api_key = config.get('Settings', 'API_KEY', fallback="")
        self.api_secret = config.get('Settings', 'API_SECRET', fallback="")
        self.sub_account = config.get('Settings', 'SUB_ACCOUNT', fallback="")
        self.symbol = config.get('Settings', 'SYMBOL', fallback="")
        self.take_profit_pc = config.getfloat("Settings", "TAKE_PROFIT_PC", fallback=0)
        self.compound_pc = config.getfloat("Settings", "COMPOUND_PC", fallback=0)

    def ensure_config(self):
        # debug
        # TODO: optimize it
        obj = {
            "LINE_TOKEN": blackout(self.line_token),
            "API_KEY": blackout(self.api_key),
            "API_SECRET": blackout(self.api_secret),
            "SUB_ACCOUNT": self.sub_account,
            "SYMBOL": self.symbol,
            "TAKE_PROFIT_PC": self.take_profit_pc,
            "COMPOUND_PC": self.compound_pc,
        }
        pprint(obj)

        # validate
        is_valid = True
        for o in obj:
            if obj[o] == "" or obj[o] == 0:
                is_valid = False
                print(f"{o} must be provided")
        if not is_valid:
            sys.exit()
