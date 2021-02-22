import os
import json
from types import SimpleNamespace
from typing import TypeVar, Union

T = TypeVar('T')


def id_to_str(s: str) -> str:
    """
    :param s: string id e.g "20.12"
    :return: first of string split with "." e.g. "20"
    """
    return str(s).split(".")[0]


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
    """

    :param val:
    :param to_type:
    :param default:
    :return:
    """
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def parse_to_dataclass(data: object):
    """
    https://stackoverflow.com/questions/6578986/how-to-convert-json-data-into-a-python-object

    :param data:
    :return:
    """
    json_str = json.dumps(data)
    return json.loads(json_str, object_hook=lambda d: SimpleNamespace(**d))
