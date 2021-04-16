from dataclasses import dataclass
from typing import List, Union, Any


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
    zone_amount: float  # amount that take for the zone e.g. zone_amount = 20 in "BTC/USD so it will buy BTC with 20 USD

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


@dataclass(frozen=True)
class OpenOrderResponse:
    success: bool
    result: List[LimitOrderInfo]


@dataclass(frozen=True)
class CancelAllOrdersResponse:
    success: bool
    result: str  # e.g."Orders queued for cancelation"


@dataclass(frozen=True)
class BalanceInfoResult:
    coin: str  # e.g. "BNB", "USD"
    total: float  # e.g. 0.6389626
    free: float  # e.g. 0.2389626,
    availableWithoutBorrow: float  # e.g. 0.2389626
    usdValue: float  # e.g. 168.7672754552929
    spotBorrow: float  # e.g. 0.0


@dataclass(frozen=True)
class BalanceInfo:
    success: bool
    result: List[BalanceInfoResult]


@dataclass(frozen=True)
class Balance:
    info: BalanceInfo
    # there are more keys in here but can be ignored for now

    free: Any
    used: Any
    total: Any

    """
    e.g.
    'info': ...,
    'BNB': {
        'free': 0.08994015,
        'used': 0.0,
        'total': 0.08994015
    },
    'USD': {
        'free': 500.02723,
        'used': 0.0,
        'total': 500.02723
    },
    'free': {
        'BNB': 0.08994015,
        'USD': 500.02723
    },
    'used': {
        'BNB': 0.0,
        'USD': 0.0
    },
    'total': {
        'BNB': 0.08994015,
        'USD': 500.02723
    }
    """
