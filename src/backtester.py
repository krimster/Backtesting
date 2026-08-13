from database import Hdf5Client
from utils import resample_timeframe

import strategies.obv
import strategies.ichimoku


def run(
    exchange: str, symbol: str, strategy: str, tf: str, from_time: int, to_time: int
):

    if strategy == "obv":

        # init database client
        h5_db = Hdf5Client(exchange)

        # get the data and resample it according
        # to the timeframe argument
        data = h5_db.get_data(symbol, from_time, to_time)
        data = resample_timeframe(data, tf)

        # for moving average we use 9 as default for now
        print(strategies.obv.backtest(data, 9))

    elif strategy == "ichimoku":
        h5_db = Hdf5Client(exchange)
        data = h5_db.get_data(symbol, from_time, to_time)
        data = resample_timeframe(data, tf)

        print(strategies.ichimoku.backtest(data, tenkan_period=9, kijun_period=26))
