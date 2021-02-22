import requests
import datetime
from helper.config import LINE_TOKEN


def line(txt: str) -> None:
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
