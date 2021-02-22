from typing import List, Tuple
from helper.dataclass import TradingPosition
from helper.helper import id_to_str, safe_cast, parse_to_dataclass


# test helper
# https://stackoverflow.com/questions/36420022/how-can-i-compare-two-ordered-lists-in-python/36420107
def is_list_equals(actual: List[any], expected: List[any]) -> bool:
    actual = sorted(actual)
    expected = sorted(expected)

    return actual == expected


# test helper
# https://stackoverflow.com/questions/8560131/pytest-assert-almost-equal
def almost_equal(x: Tuple[float, float], threshold=0.00001) -> bool:
    return abs(x[0] - x[1]) < threshold


class TestIdToStr:
    def test_normal(self):
        assert id_to_str("before.after") == "before"
        assert id_to_str("20.13") == "20"


class TestSafeCast:
    def test_cast_to_int(self):
        assert safe_cast("30", int) == 30
        assert safe_cast(40, int) == 40
        assert safe_cast(20.25, int) == 20

    def test_cast_to_float(self):
        # to float
        assert safe_cast("30", float) == 30.00
        assert safe_cast(40, float) == 40.00
        assert safe_cast(20.25, float) == 20.25

    def test_cast_to_string(self):
        # to float
        assert safe_cast("30", str) == "30"
        assert safe_cast(40, str) == "40"
        assert safe_cast(20.25, str) == "20.25"

    def test_cast_then_error(self):
        assert safe_cast("something invalid", int, -2) == -2
        assert safe_cast("", float, -4) == -4
        assert safe_cast(None, int, 50) == 50


class TestParseToDataclass:
    def test_able_to_call_with_dot_notation(self):
        obj = {
            "cost": 2.03,
            "entryPrice": 2.03,
            "future": "some-future",
            "initialMarginRequirement": 2.03,
            "longOrderSize": 2.03,
            "maintenanceMarginRequirement": 2.03,
            "netSize": 2.03,
            "openSize": 2.03,
            "realizedPnl": 2.03,
            "shortOrderSize": 2.03,
            "side": "buy",
            "size": 2.03,
            "unrealizedPnl": 2.03,
        }
        tp: TradingPosition = parse_to_dataclass(obj)

        assert tp.cost == 2.03
        assert tp.entryPrice == 2.03
        assert tp.future == "some-future"
        assert tp.initialMarginRequirement == 2.03
        assert tp.longOrderSize == 2.03
        assert tp.maintenanceMarginRequirement == 2.03
        assert tp.netSize == 2.03
        assert tp.openSize == 2.03
        assert tp.realizedPnl == 2.03
        assert tp.shortOrderSize == 2.03
        assert tp.side == "buy"
        assert tp.size == 2.03
        assert tp.unrealizedPnl == 2.03
