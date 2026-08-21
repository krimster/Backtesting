from ctypes import *
from database import Hdf5Client
from utils import resample_timeframe, STRAT_PARAMS, get_library

import strategies.obv
import strategies.ichimoku
import strategies.support_resistance


def run(
    exchange: str, symbol: str, strategy: str, tf: str, from_time: int, to_time: int
):

    params_desc = STRAT_PARAMS[strategy]

    params = dict()

    for p_code, p in params_desc.items():
        while True:
            try:
                params[p_code] = p["type"](input(p["name"] + ": "))
                break
            except ValueError:
                continue

    if strategy == "obv":

        # init database client
        h5_db = Hdf5Client(exchange)

        # get the data and resample it according
        # to the timeframe argument
        data = h5_db.get_data(symbol, from_time, to_time)
        data = resample_timeframe(data, tf)

        # for moving average we use 9 as default for now
        pnl, max_drawdown = strategies.obv.backtest(data, ma_period=params["ma_period"])
        return pnl, max_drawdown

    elif strategy == "ichimoku":
        h5_db = Hdf5Client(exchange)
        data = h5_db.get_data(symbol, from_time, to_time)
        data = resample_timeframe(data, tf)

        pnl, max_drawdown = strategies.ichimoku.backtest(
            data, tenkan_period=params["tenkan"], kijun_period=params["kijun"]
        )
        return pnl, max_drawdown

    elif strategy == "sup_res":
        h5_db = Hdf5Client(exchange)
        data = h5_db.get_data(symbol, from_time, to_time)
        data = resample_timeframe(data, tf)

        pnl, max_drawdown = strategies.support_resistance.backtest(
            data,
            min_points=params["min_points"],
            min_diff_points=params["min_diff_points"],
            rounding_nb=params["rounding_nb"],
            take_profit=params["take_profit"],
            stop_loss=params["stop_loss"],
        )

        return pnl, max_drawdown

    elif strategy == "sma":

        ## load C++ library
        lib = get_library()

        obj = lib.sma_new(
            exchange.encode(),
            symbol.encode(),
            tf.encode(),
            from_time,
            to_time,
        )

        lib.sma_execute_backtest(obj, params["slow_ma"], params["fast_ma"])
        pnl = sma_get_pnl(obj)
        max_dd = sma_get_max_dd(obj)

        return pnl, max_dd

    elif strategy == "psar":

        ## load C++ library
        lib = get_library()

        obj = lib.psar_new(
            exchange.encode(),
            symbol.encode(),
            tf.encode(),
            from_time,
            to_time,
        )

        lib.psar_execute_backtest(
            obj, params["initial_acc"], params["acc_increment"], params["max_acc"]
        )

        pnl = psar_get_pnl(obj)
        max_dd = psar_get_max_dd(obj)

        return pnl, max_dd
