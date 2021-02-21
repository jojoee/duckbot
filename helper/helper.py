import requests
import datetime
import os
import json
from dataclasses import dataclass
from types import SimpleNamespace
from typing import TypeVar, List, Union, Any
from helper.config import LINE_TOKEN

T = TypeVar('T')


def id_to_str(s: str) -> str:
    """
    :param s: string id e.g "20.12"
    :return: first of string split with "." e.g. "20"
    """
    return str(s).split(".")[0]


def send_line(txt: str) -> None:
    """
    send notification into LINE group
    :param txt: text that want to send into LINE
    """

    try:
        url = "https://notify-api.line.me/api/notify"
        header = {
            "content-type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer %s" % LINE_TOKEN,
        }
        data = {"message": txt}
        requests.post(url, headers=header, data=data)

    except Exception as e:
        now = datetime.datetime.now().replace(microsecond=0)
        msg = f"{now} Error send text line: {e}"
        print(msg)


def clear() -> None:
    """
    clear screen
    https://www.geeksforgeeks.org/clear-screen-python/
    """

    # for windows
    if os.name == "nt":
        os.system("cls")

    # for mac and linux(here, os.name is 'posix')
    else:
        os.system("clear")


def safe_cast(val, to_type: T, default=None) -> Union[T, None]:
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def parse_to_dataclass(data: object):
    """
    https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object
    """
    json_str = json.dumps(data)
    return json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))


@dataclass(frozen=True)
class TradingPosition:
    cost: float
    entryPrice: float
    future: str
    initialMarginRequirement: float
    longOrderSize: float
    maintenanceMarginRequirement: float
    netSize: float
    openSize: float
    realizedPnl: float
    shortOrderSize: float
    side: str
    size: float
    unrealizedPnl: float


@dataclass(frozen=True)
class TradingFeesResult:
    backstopProvider: bool
    collateral: float
    freeCollateral: float
    initialMarginRequirement: float
    liquidating: bool
    maintenanceMarginRequirement: float
    makerFee: float
    marginFraction: float
    openMarginFraction: float
    takerFee: float
    totalAccountValue: float
    totalPositionSize: float
    username: str
    positions: List[TradingPosition]


@dataclass(frozen=True)
class TradingFeesInfo:
    success: bool
    result: TradingFeesResult


@dataclass(frozen=True)
class TradingFeesResponse:
    info: TradingFeesInfo
    maker: float
    taker: float


@dataclass(frozen=False)
class Zone:
    zone_price: float
    zone_amount: float

    buy_id: Union[str, None] = None
    buy_price: Union[float, None] = None
    buy_unit: Union[float, None] = None
    buy_fee_unit: Union[float, None] = None
    buy_recive_unit: Union[float, None] = None
    buy_open_time: Union[str, None] = None
    buy_status: Union[str, None] = None
    buy_close_time: Union[str, None] = None

    sell_id: Union[str, None] = None
    sell_price: Union[float, None] = None
    sell_unit: Union[float, None] = None
    sell_fee_amount: Union[float, None] = None
    sell_recive_amount: Union[float, None] = None
    sell_open_time: Union[str, None] = None
    sell_status: Union[str, None] = None
    sell_close_time: Union[str, None] = None


@dataclass(frozen=False)
class Statement(Zone):
    symbol: Union[str, None] = None
    net_profit: Union[float, None] = None
    buy_fee_amount: Union[float, None] = None


@dataclass(frozen=True)
class TickerInfo:
    ask: float
    baseCurrency: None
    bid: float
    change1h: float
    change24h: float
    changeBod: float
    enabled: bool
    last: float
    name: str  # e.g. "ETH-PERP",
    price: float  # 171.29,
    priceIncrement: float  # e.g. 0.01,
    quoteCurrency: None  # quote currency for spot markets
    quoteVolume24h: float  # e.g. 8570651.12113,
    sizeIncrement: float  # e.g. 0.001,
    type: str  # e.g. "future"
    underlying: str  # e.g. "ETH"  # null for spot markets
    volumeUsd24h: float  # e.g. 8570651.12113


@dataclass(frozen=True)
class Ticker:
    symbol: str
    timestamp: int
    datetime: str
    high: float
    low: float
    bid: float
    bidVolume: float
    ask: float
    askVolume: float
    vwap: None
    open: None
    close: float
    last: float
    previousClose: None
    change: None
    percentage: float
    average: None
    baseVolume: None
    quoteVolume: float
    info: TickerInfo


@dataclass(frozen=True)
class LimitOrderInfo:
    createdAt: str  # e.g. "2019-03-05T09:56:55.728933+00:00",
    filledSize: float  # 0
    future: str  # XRP-PERP"
    id: int  # 9596912
    market: str  # "XRP-PERP"
    price: float  # 0.306525
    remainingSize: float  # 31431
    side: str  # "sell",
    size: float  # 31431,
    status: str  # "open"
    type: str  # "limit"
    reduceOnly: bool  # False
    ioc: bool  # False
    postOnly: bool  # False
    clientId: None


@dataclass(frozen=True)
class LimitOrder:
    info: LimitOrderInfo
    id: str
    clientOrderId: str
    timestamp: int
    datetime: str
    lastTradeTimestamp: int
    symbol: str
    type: str
    timeInForce: None
    postOnly: Any
    side: str
    price: float
    stopPrice: float
    amount: float
    cost: float
    average: float
    filled: float
    remaining: float
    status: str
    fee: None
    trades: None
