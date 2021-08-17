# duckbot

:duck: -is swimming in the pond.

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
# TODO: complete it
```

## Note
- [ ] Backtesting
- [ ] Gracefully shutdown by closing all opened positions
- [ ] Trading algorithm that not depends on historical data
- [ ] Fix floating point error e.g. 3.7572000000000005
- [x] `ALL_UPPER_CASE` is for global variable and constant
- [ ] `generate_zone.py`
- [ ] Setup https://github.com/pyinstaller/pyinstaller
- [x] Logger
    - Daily rotation
    - Specify timezone 

## Reference
- Originally created by Pisut Oncharoen
- https://docs.ftx.com/#rest-api
