# duckbot
Duck learns trading bot. With his 1-3-inch-flying-algorithm makes, he rules them all.

![continuous integration](https://github.com/jojoee/cyclical/workflows/continuous%20integration/badge.svg?branch=master)

## Getting Started

1. Install [Python](https://www.python.org/) and [Conda](https://docs.conda.io/en/latest/)
2. Install dependencies `pip install -r requirements.txt`
3. 3rd party setup
- FTX: Register [FTX exchange](https://ftx.com/#a=13144711)
- FTX: do the KYC
- FTX: Create [API key](https://ftx.com/profile)
- LINE: create LINE group
- LINE: create [LINE bot token](https://notify-bot.line.me/my/)
- LINE: invite "LINE Notify" bot into that group
4. Setup project and run
```bash
# config
cp example/config.ini.example config.ini 

# statement.csv log
cp example/statement.example.ini statement.ini

# generate zone.csv for the algorithm
x

# compile (optional)
pyinstaller ./duckbot.py --distpath=./dist --onefile --name=duckbot

# run
python duckbot.py
python dist/duckbot
```

## Note
- Interesting training pair `BTC/USD`, `ETH/USD`, `BNB/USD`, `FTT/USD`, `OMG/USD`, `DOGE/USD`
- [ ] Backtesting
- [ ] Gracefully shutdown then close all opened positions ?
- [ ] Trading algorithm that not depends on historical data
- [ ] Check https://www.cryptohopper.com/marketplace
- [ ] Fix floating point error e.g. 3.7572000000000005
- `ALL_UPPER_CASE` is for global variable and constant
- [ ] `generate_zone.py`
- [ ] Setup https://github.com/pyinstaller/pyinstaller
- Logger
    - Daily rotation
    - Specify timezone 

## CMD

```
conda info
conda env list
conda create --name duckbot python=3.8.3
conda activate duckbot
```

## Reference
- Originally created by Pisut Oncharoen
- [วิธีสมัคร FTX และการยืนยันตัว + เปิด sub account และ เปิด API บอทเทรด ปี 2021](https://www.youtube.com/watch?v=o1tEz7H_ITM)
- [วิธีรับ Token Line แจ้งเตือน Line notify](https://www.youtube.com/watch?v=pNQq-alDYTM)
- https://docs.ftx.com/#rest-api
- https://github.com/ftexchange/ftx
- https://github.com/ccxt/ccxt
- https://github.com/ccxt/ccxt/tree/master/examples
