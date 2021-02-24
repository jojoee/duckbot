import configparser
from pprint import pprint
import os
import sys

# https://docs.python.org/3/library/configparser.html
config = configparser.ConfigParser()
config.read("./config.ini")

# LINE notification
LINE_TOKEN = config.get('Settings', 'LINE_TOKEN', fallback="")

# FTX exchange
API_KEY = config.get('Settings', 'API_KEY', fallback="")
API_SECRET = config.get('Settings', 'API_SECRET', fallback="")
SUB_ACCOUNT = config.get('Settings', 'SUB_ACCOUNT', fallback="")

# trade pair
SYMBOL = config.get('Settings', 'SYMBOL', fallback="")

# trading algorithm
TAKE_PROFIT_PC = config.getfloat("Settings", "TAKE_PROFIT_PC", fallback=0)
COMPOUND_PC = config.getfloat("Settings", "COMPOUND_PC", fallback=0)

# other settings
TIMEZONE = 'Asia/Bangkok'  # "Europe/Berlin", "Asia/Bangkok"
os.environ['TZ'] = TIMEZONE


def blackout(s: str, n_left: int = 4) -> str:
    if len(s) <= n_left: return ""
    return "*" * len(s[:-n_left]) + s[-n_left:]


def ensure_config():
    global LINE_TOKEN
    global API_KEY
    global API_SECRET
    global SUB_ACCOUNT
    global SYMBOL
    global TAKE_PROFIT_PC
    global COMPOUND_PC

    # debug
    obj = {
        "LINE_TOKEN": blackout(LINE_TOKEN),
        "API_KEY": blackout(API_KEY),
        "API_SECRET": blackout(API_SECRET),
        "SUB_ACCOUNT": SUB_ACCOUNT,
        "SYMBOL": SYMBOL,
        "TAKE_PROFIT_PC": TAKE_PROFIT_PC,
        "COMPOUND_PC": COMPOUND_PC,
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
