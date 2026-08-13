import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 1000)


def backtest(df: pd.DataFrame, ma_period: int):

    # we first get the obv indicator
    df["obv"] = (np.sign(df["close"].diff()) * df["volume"]).fillna(0).cumsum()

    # now we get the moving average
    df["obv_ma"] = round(df["obv"].rolling(window=ma_period).mean(), 2)

    df["signal"] = np.where(df["obv"] > df["obv_ma"], 1, -1)

    ## debug columns
    df["close_change"] = df["close"].pct_change()
    df["signal_shift"] = df["signal"].shift(1)

    # lastly we calculate the PNL, there are several ways
    # to calculate the PNL, here we will use the percentage
    # change in the close prices
    df["pnl"] = df["close"].pct_change() * df["signal"].shift(1)

    df["cum_pnl"] = df["pnl"].cumsum()
    df["max_cum_pnl"] = df["cum_pnl"].cummax()
    df["drawndown"] = df["max_cum_pnl"] - df["cum_pnl"]

    # print(df)
    return df["pnl"].sum(), df["drawdown"].max()
