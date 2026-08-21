import datetime
import pandas as pd

from ctypes import *


TF_EQUIV = {
    "1m": "1Min",
    "5m": "5Min",
    "15m": "15Min",
    "30m": "30Min",
    "1h": "1H",
    "4h": "4H",
    "12h": "12H",
    "1d": "D",
}

STRAT_PARAMS = {
    "obv": {
        "ma_period": {"name": "MA Period", "type": int},
    },
    "ichimoku": {
        "kijun": {"name": "Kijun Period", "type": int},
        "tenkan": {"name": "Tenkan Period", "type": int},
    },
    "sup_res": {
        "min_points": {"name": "Min. Points", "type": int},
        "min_diff_points": {"name": "Min. Difference between points", "type": int},
        "rounding_nb": {"name": "Rounding number", "type": float},
        "take_profit": {"name": "Take profit", "type": float},
        "stop_loss": {"name": "Stop loss", "type": float},
    },
    "sma": {
        "slow_ma": {"name": "Slow MA Period", "type": int},
        "fast_ma": {"name": "Fast MA Period", "type": int},
    },
    "psar": {
        "initial_acc": {"name": "Initial Acceleration", "type": float},
        "acc_increment": {"name": "Acceleration Increment", "type": float},
        "max_acc": {"name": "Maximum Acceleration", "type": float},
    },
}


def ms_to_dt(ms: int) -> datetime.datetime:
    return datetime.datetime.utcfromtimestamp(ms / 1000)


def resample_timeframe(data: pd.DataFrame, tf: str) -> pd.DataFrame:
    return data.resample(TF_EQUIV[tf]).agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
            "volume": "sum",
        }
    )


## load C++ library
def get_library():

    lib = CDLL("backtestingCpp/build/libbacktestingCpp.so", winmode=0)

    # SMA
    lib.sma_new.restype = c_void_p
    lib.sma_new.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_longlong]

    lib.sma_execute_backtest.restype = c_void_p
    lib.sma_execute_backtest.argtypes = [c_void_p, c_int, c_int]

    lib.sma_get_pnl.restype = c_double
    lib.sma_get_pnl.argtypes = [c_void_p]

    lib.sma_get_max_dd.restype = c_double
    lib.sma_get_max_dd.argtypes = [c_void_p]

    # PSAR
    lib.psar_new.restype = c_void_p
    lib.psar_new.argtypes = [c_char_p, c_char_p, c_char_p, c_longlong, c_longlong]

    lib.psar_execute_backtest.restype = c_void_p
    lib.psar_execute_backtest.argtypes = [c_void_p, c_double, c_double, c_double]

    lib.psar_get_pnl.restype = c_double
    lib.psar_get_pnl.argtypes = [c_void_p]

    lib.psar_get_max_dd.restype = c_double
    lib.psar_get_max_dd.argtypes = [c_void_p]

    return lib
