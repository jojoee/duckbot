import configparser

# https://docs.python.org/3/library/configparser.html
config = configparser.ConfigParser()
config.read("./config.ini")

# LINE notification
LINE_TOKEN = config["Settings"]["LINE_TOKEN"] or ""

# FTX exchange
API_KEY = config["Settings"]["API_KEY"] or ""
API_SECRET = config["Settings"]["API_SECRET"] or ""
SUB_ACCOUNT = config["Settings"]["SUB_ACCOUNT"] or ""

# trade pair
SYMBOL = config["Settings"]["SYMBOL"] or ""
# trading algorithm
TAKE_PROFIT_PC = float(config["Settings"]["TAKE_PROFIT_PC"]) if config["Settings"]["TAKE_PROFIT_PC"] else ""
COMPOUND_PC = float(config["Settings"]["COMPOUND_PC"]) if config["Settings"]["COMPOUND_PC"] else ""
