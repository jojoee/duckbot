import time
import os
import sys
from typing import List
import gc
import pandas as pd
import numpy as np
import ccxt
import schedule
from helper.config import API_KEY, API_SECRET, SUB_ACCOUNT, SYMBOL, TAKE_PROFIT_PC, COMPOUND_PC, ensure_config
from helper.dataclass import TradingFeesResponse, Zone, Ticker, LimitOrder, Statement
from helper.helper import parse_to_dataclass
from helper.botlogger import BotLogger

# const
OPEN_BUY_STATUS = "open"
CLOSED_BUY_STATUS = "closed"
CANCELED_BUY_STATUS = "canceled"
OPEN_SELL_STATUS = "open"
CLOSED_SELL_STATUS = "closed"
CANCELED_SELL_STATUS = "canceled"

# debug and setup
ensure_config()
LOGGER = BotLogger(SUB_ACCOUNT)
FTX = ccxt.ftx({"apiKey": API_KEY, "secret": API_SECRET, "enableRateLimit": True})
FTX.headers = {"FTX-SUBACCOUNT": SUB_ACCOUNT} if len(SUB_ACCOUNT) > 0 else {}
fee: TradingFeesResponse = parse_to_dataclass(FTX.fetch_trading_fees())
FEE_TAKER = fee.taker  # limit order

# algorithm setup
ZONE_FILE_PATH = './zone.csv'
ZONES: List[Zone] = []
STATEMENT_FILE_PATH = './statement.csv'


def save_zones() -> None:
    global ZONES
    global ZONE_FILE_PATH

    # revert into simple dict
    zones = [row.__dict__ for row in ZONES]

    # save
    pd.DataFrame(zones).to_csv(ZONE_FILE_PATH, index=False)


def save_new_statement(statement: Statement) -> None:
    global STATEMENT_FILE_PATH

    # revert into simple dict
    statements = [statement.__dict__]

    pd.DataFrame(statements).to_csv(STATEMENT_FILE_PATH, mode='a', header=False, index=False)


def get_zones() -> List[Zone]:
    global ZONE_FILE_PATH

    # TODO: fix duplication
    zone_df = pd.read_csv(
        ZONE_FILE_PATH,
        dtype={
            "zone_price": "float",
            "zone_amount": "float",
            "buy_id": "str",
            "buy_price": "float",
            "buy_unit": "float",
            "buy_fee_unit": "float",
            "buy_recive_unit": "float",
            "buy_open_time": "str",
            "buy_status": "str",
            "buy_close_time": "str",
            "sell_id": "str",
            "sell_price": "float",
            "sell_unit": "float",
            "sell_fee_amount": "float",
            "sell_recive_amount": "float",
            "sell_open_time": "str",
            "sell_close_time": "str",
            "sell_status": "str",
        },
    )

    zone_df = zone_df.fillna(np.nan).replace([np.nan], [None])
    zones = [parse_to_dataclass(row) for row in zone_df.to_dict('records')]

    return zones


def main():
    global ZONES
    global FTX
    global FEE_TAKER
    global OPEN_BUY_STATUS
    global CLOSED_BUY_STATUS
    global CANCELED_BUY_STATUS
    global OPEN_SELL_STATUS
    global CLOSED_SELL_STATUS
    global CANCELED_SELL_STATUS

    # load zone info
    ZONES = get_zones()

    # loop for each zone
    for i in range(len(ZONES)):
        zone: Zone = ZONES[i]

        # get latest price and time
        ticker: Ticker = parse_to_dataclass(FTX.fetch_ticker(SYMBOL))
        last_price = ticker.last
        last_time = ticker.datetime

        # no buying then force buy
        if zone.buy_status is None:
            # Create a new order if there is no opening order
            try:
                # force
                if last_price < zone.zone_price:
                    # perform market-order
                    # assumption: right liquidity (no big gap of buy-sell order)
                    # so we buy at "ask" price
                    current_ticket: Ticker = parse_to_dataclass(FTX.fetch_ticker(SYMBOL))
                    buy_price = current_ticket.ask
                    txt_action = "Buy collective order"
                else:
                    buy_price = zone.zone_price
                    txt_action = "Open limit buy order"

                # open limit buy order
                buy_unit = zone.zone_amount / buy_price
                order_result: LimitOrder = parse_to_dataclass(FTX.create_order(
                    SYMBOL, "limit", "buy", buy_unit, buy_price
                ))

                # Update & save zone.csv
                # update and save
                buy_unit = order_result.amount
                buy_fee = buy_unit * FEE_TAKER

                ZONES[i].zone_price = zone.zone_price
                ZONES[i].zone_amount = zone.zone_amount
                ZONES[i].buy_id = order_result.id
                ZONES[i].buy_price = order_result.price
                ZONES[i].buy_unit = buy_unit
                ZONES[i].buy_fee_unit = buy_fee
                ZONES[i].buy_recive_unit = buy_unit - buy_fee
                ZONES[i].buy_open_time = order_result.info.createdAt
                ZONES[i].buy_status = order_result.status

                save_zones()

                # log
                amt = buy_unit * order_result.price
                msg = f"{SYMBOL} Zone {zone.zone_price}: {txt_action} amount($) : {amt}"
                LOGGER.info(msg)

            except Exception as e:
                msg = f"{SYMBOL} Error : {e}"
                LOGGER.error(msg)

                # TODO: implement parent-try-catch instead
                time.sleep(10)

        # still open (no match or partial match)
        elif zone.buy_status == OPEN_BUY_STATUS:
            try:
                # Update Order Status
                current_order: LimitOrder = parse_to_dataclass(FTX.fetch_order(zone.buy_id))
                updated_buy_status = current_order.status
                txt_action = f"Buy status: {OPEN_BUY_STATUS} => {updated_buy_status}"

                # may be the order has been updated
                if zone.buy_status != updated_buy_status:
                    # TODO other values might also be updated
                    # update
                    ZONES[i].buy_status = updated_buy_status
                    save_zones()

                msg = f"{SYMBOL} Zone {zone.zone_price} : {txt_action} "
                LOGGER.debug(msg)

            except Exception as e:
                # TODO: implement parent-try-catch instead
                msg = f"{SYMBOL} Error : {e}"
                LOGGER.error(msg)

                time.sleep(10)

        # buy-order is fulfilled
        elif zone.buy_status == CLOSED_BUY_STATUS:

            # this should not be check but just incase
            # TODO: recheck it
            if zone.buy_close_time is None:
                # TODO: if you need more accurate then use time from FTX response instead
                ZONES[i].buy_close_time = last_time
                save_zones()

            # open TP
            if zone.sell_status is None:
                # Open a new limit sell order
                try:
                    # Open Limit Sell Order

                    # TAKE_PROFIT_PC = 1.5, create TP at 1.5% from the buy-order
                    # need "max(zone.zone_price, zone.buy_price)"
                    # cause sometime the "ask" (buy_price) already over the zone_price
                    sell_price = (1 + TAKE_PROFIT_PC / 100) * max(zone.zone_price, zone.buy_price)

                    # to avoid incremental size problem, actually it should be buy_recive_unit
                    # TODO: why not buy_recive_unit
                    sell_unit = zone.buy_unit
                    # sell_unit = zone.buy_recive_unit

                    order_result: LimitOrder = parse_to_dataclass(FTX.create_order(
                        SYMBOL, "limit", "sell", sell_unit, sell_price
                    ))

                    # Update & save zone.csv
                    sell_amount = order_result.price * order_result.amount
                    sell_fee = sell_amount * FEE_TAKER
                    ZONES[i].sell_id = order_result.id
                    ZONES[i].sell_price = order_result.price
                    ZONES[i].sell_unit = order_result.amount
                    ZONES[i].sell_fee_amount = sell_fee
                    ZONES[i].sell_recive_amount = sell_amount - sell_fee
                    ZONES[i].sell_open_time = order_result.info.createdAt
                    ZONES[i].sell_status = order_result.status

                    save_zones()

                    txt_action = "Open limit sell order"
                    msg = f"{SYMBOL} Zone {zone.zone_price} : {txt_action}  amount($) : {sell_amount}"
                    LOGGER.info(msg)

                except Exception as e:
                    msg = f"{SYMBOL} Error : {e}"
                    LOGGER.error(msg)
                    time.sleep(10)

            elif zone.sell_status == OPEN_SELL_STATUS:
                try:
                    # Update Order Status
                    current_order: LimitOrder = parse_to_dataclass(FTX.fetch_order(zone.sell_id))
                    updated_sell_status = current_order.status
                    txt_action = "Buy status : Closed   Sell status : Open"

                    if zone.sell_status != updated_sell_status:
                        # Save if status has changed
                        ZONES[i].sell_status = updated_sell_status
                        save_zones()
                        txt_action = f"Save updated sell status ({updated_sell_status})"

                    msg = f"{SYMBOL} Zone {zone.zone_price} : {txt_action} "
                    LOGGER.debug(msg)

                except Exception as e:
                    msg = f"{SYMBOL} Error : {e}"
                    LOGGER.error(msg)
                    time.sleep(10)

            elif zone.sell_status == CLOSED_SELL_STATUS:
                # calculate net profit
                buy_fee_amount = zone.buy_price * zone.buy_fee_unit

                # TODO: zone.sell_recive_amount ??
                sell_fee_amount = (zone.sell_price * zone.sell_unit) - zone.sell_recive_amount
                total_fee = buy_fee_amount + sell_fee_amount

                # profit
                net_profit = ((zone.sell_unit * zone.sell_price) - (zone.buy_unit * zone.buy_price) - total_fee)

                # COMPOUND_PC=50
                # we take the 50% from profit then re-invest into this zone
                ZONES[i].zone_amount = zone.zone_amount + round(net_profit * COMPOUND_PC / 100, 2)
                ZONES[i].sell_close_time = last_time

                # Update statement
                statement = Statement(
                    symbol=SYMBOL,
                    net_profit=net_profit,

                    buy_fee_amount=buy_fee_amount,  # new

                    zone_price=zone.zone_price,
                    zone_amount=zone.zone_amount,

                    buy_id=zone.buy_id,
                    buy_price=zone.buy_price,
                    buy_unit=zone.buy_unit,
                    buy_fee_unit=zone.buy_fee_unit,
                    buy_recive_unit=zone.buy_recive_unit,
                    buy_open_time=zone.buy_open_time,
                    buy_status=CLOSED_BUY_STATUS,
                    buy_close_time=zone.buy_close_time,

                    sell_id=zone.sell_id,
                    sell_price=zone.sell_price,
                    sell_unit=zone.sell_unit,
                    sell_fee_amount=zone.sell_fee_amount,
                    sell_recive_amount=zone.sell_recive_amount,
                    sell_open_time=zone.sell_open_time,
                    sell_status=zone.sell_status,
                    sell_close_time=zone.sell_close_time
                )
                save_new_statement(statement)

                # reset zone
                new_zone = Zone(
                    zone_price=zone.zone_price,
                    zone_amount=zone.zone_amount,
                )
                ZONES[i] = new_zone
                save_zones()

                # log
                msg = f"{SYMBOL} Zone {zone.zone_price} : Profit($) : {net_profit}"
                LOGGER.info(msg)

            # TODO: manual cancel sell order
            elif zone.sell_status == CANCELED_SELL_STATUS:

                # Remove canceled sell order
                ZONES[i].sell_id = None
                ZONES[i].sell_price = None
                ZONES[i].sell_unit = None
                ZONES[i].sell_fee_amount = None
                ZONES[i].sell_recive_amount = None
                ZONES[i].sell_open_time = None
                ZONES[i].sell_status = None
                ZONES[i].sell_close_time = None

                # save
                save_zones()

                # log
                msg = f"{SYMBOL} Zone {zone.zone_price} : Remove canceled sell order"
                LOGGER.debug(msg)

            else:
                msg = f"something wrong zone.sell_status: {zone.sell_status}"
                LOGGER.error(msg)

        # it will happened when user manually cancelling all orders in FTX
        elif zone.buy_status == CANCELED_BUY_STATUS:
            # Remove canceled buy order
            # reset buy order
            ZONES[i].buy_id = None
            ZONES[i].buy_price = None
            ZONES[i].buy_unit = None
            ZONES[i].buy_fee_unit = None
            ZONES[i].buy_recive_unit = None
            ZONES[i].buy_open_time = None
            ZONES[i].buy_status = None
            ZONES[i].buy_close_time = None
            save_zones()
            msg = f"{SYMBOL} Zone {zone.zone_price}: Remove canceled buy order"
            LOGGER.debug(msg)

        else:
            msg = f"something wrong zone.buy_status: {zone.buy_status}"
            LOGGER.error(msg)

        time.sleep(0.15)  # To avoid reaching maximum API call per sec (30 times)


def healthcheck():
    LOGGER.info("I'm ok healthcheck: ok")


def wakeup_bot():
    try:
        """
        TODO: optimize
        use 4 loops to clear/check current position
        4 is came from worst case which is:
        1. sell-closed then clear
        2. buy-none then buy
        3. buy-open then update
        4. buy-closed then sell
        """
        for i in range(4):
            main()
            gc.collect()  # forcing garbage collection

    except Exception as e:
        LOGGER.error(f"{SYMBOL} error: {e}")

    LOGGER.debug(f'waiting 60 seconds for the new process')


# init
if os.environ.get('ENVIRONMENT') == 'debug': sys.exit()
wakeup_bot()

# schedule
# it will behave like, waiting for 60 seconds after the job is completed
schedule.every(1).minutes.do(wakeup_bot)
schedule.every(1).hour.do(healthcheck)

while True:
    schedule.run_pending()
    time.sleep(1)
