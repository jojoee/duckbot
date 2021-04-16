import time
import datetime
import gc
import pandas as pd
import ccxt
import sys
import os
from typing import List
from helper.dataclass import Ticker, LimitOrder, Balance, LimitOrderInfo
from helper.helper import parse_to_dataclass
from helper.botlogger import BotLogger
import configparser
import schedule

# config
BOT_DIR = sys.argv[1]
config = configparser.ConfigParser()
config_path = os.path.join(BOT_DIR, 'config.ini')
config.read(config_path)
LINE_TOKEN = config['Settings']['LINE_TOKEN']
API_KEY = config['Settings']['API_KEY']
API_SECRET = config['Settings']['API_SECRET']
SUB_ACCOUNT = config['Settings']['SUB_ACCOUNT']
COIN = config['Settings']['COIN']
COIN_TARGET_PC = float(config['Settings']['COIN_TARGET_PC'])
THRESHOLD_PC = float(config['Settings']['THRESHOLD_PC'])
RB_TIME_SECS = int(config['Settings']['RB_TIME_SECS'])
UPPER_LIMIT = (COIN_TARGET_PC + THRESHOLD_PC) / 100
LOWER_LIMIT = (COIN_TARGET_PC - THRESHOLD_PC) / 100
STATEMENT_FILE_PATH = os.path.join(BOT_DIR, 'statement.csv')

# Set limit variables
LOGGER = BotLogger(SUB_ACCOUNT, LINE_TOKEN)
FTX = ccxt.ftx({"apiKey": API_KEY, "secret": API_SECRET, "enableRateLimit": True})
FTX.headers = {"FTX-SUBACCOUNT": SUB_ACCOUNT} if len(SUB_ACCOUNT) > 0 else {}

# TODO optimize
"""
bot create order by "ask" price
so if we fast/lucky enough then it will be fine

but if the order did not completed then
the order will stay forever
which makes the bot stuck
"""


def get_balance_coin_value(coin: str) -> float:
    global FTX

    try:
        balance: Balance = parse_to_dataclass(FTX.fetch_balance())
        coins = [coin.__dict__ for coin in balance.info.result]
        balance_df = pd.DataFrame(coins, columns=['coin', 'usdValue'])
        balance_df = balance_df.set_index('coin')
        usd_value = balance_df.loc[coin, 'usdValue']

        return usd_value
    except:
        return 0


def reblance():
    now = datetime.datetime.now().replace(microsecond=0)

    try:
        symbol = f'{COIN}/USD'
        ticker: Ticker = parse_to_dataclass(FTX.fetch_ticker(symbol))

        sell_price = ticker.bid
        buy_price = ticker.ask

        coin_value = get_balance_coin_value(COIN)
        usd_value = get_balance_coin_value('USD')
        port_value = coin_value + usd_value
        coin_ratio = coin_value / port_value

        cols = ['symbol', 'id', 'price', 'side', 'amount', 'datetime']

        # close all open orders
        open_orders: List[LimitOrderInfo] = parse_to_dataclass(FTX.fetch_open_orders(symbol))
        if len(open_orders) >= 1:
            message: parse_to_dataclass(FTX.cancel_all_orders(symbol))
            LOGGER.info(message)

        if coin_ratio > UPPER_LIMIT:
            sell_unit = (coin_ratio - COIN_TARGET_PC / 100) * port_value / sell_price
            order_result: LimitOrder = parse_to_dataclass(FTX.create_order(
                symbol, "limit", "sell", sell_unit, sell_price
            ))
            res = pd.DataFrame(order_result.__dict__, columns=cols, index=[0])
            res.to_csv(STATEMENT_FILE_PATH, mode='a', header=False, index=False)

            txt = f'SELL {symbol}   Price : {sell_price}   Unit : {sell_unit}'
            LOGGER.info(txt)

        elif coin_ratio < LOWER_LIMIT:
            buy_unit = (COIN_TARGET_PC / 100 - coin_ratio) * port_value / buy_price
            order_result: LimitOrder = parse_to_dataclass(FTX.create_order(
                symbol, "limit", "buy", buy_unit, buy_price
            ))

            res = pd.DataFrame(order_result.__dict__, columns=cols, index=[0])
            res.to_csv(STATEMENT_FILE_PATH, mode='a', header=False, index=False)

            txt = f'BUY {symbol}   Price : {buy_price}   Unit : {buy_unit}'
            LOGGER.info(txt)

        else:
            ratio = round(coin_ratio * 100, 1)
            value = round(port_value, 2)

            txt = f'{now}  Port Value($): {value} {COIN} Ratio: {ratio}%'
            LOGGER.debug(txt)

    except Exception as e:

        txt = f'Rebalance {COIN} Error : {e}'
        LOGGER.error(txt)


def healthcheck():
    LOGGER.info("I'm ok healthcheck: ok")


def wakeup_bot():
    try:
        reblance()
        gc.collect()

    except Exception as e:
        txt = f'Rebalance {COIN} Error : {e}'
        LOGGER.error(txt)

    LOGGER.debug('waiting 20 seconds for the new process')


# init
wakeup_bot()

# schedule
# it will behave like, waiting for 60 seconds after the job is completed
schedule.every(RB_TIME_SECS).seconds.do(wakeup_bot)
schedule.every(1).hour.do(healthcheck)

while True:
    schedule.run_pending()
    time.sleep(1)
