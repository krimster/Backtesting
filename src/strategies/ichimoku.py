import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", 100)
pd.set_option("display.width", 1000)


def backtest(df: pd.DataFrame, tenkan_period: int, kijun_period: int):

    # Tenkan Sen :  Short-term signal line

    df["rolling_min_tenkan"] = df["low"].rolling(window=tenkan_period).min()
    df["rolling_max_tenkan"] = df["high"].rolling(window=tenkan_period).max()

    # the Tenken Sen is based on the average of the above 2 columns
    df["tenkan_sen"] = (df["rolling_max_tenkan"] + df["rolling_min_tenkan"]) / 2

    # drop columns we don't need anymore
    df.drop(["rolling_min_tenkan", "rolling_max_tenkan"], axis=1, inplace=True)

    # Kijun Sen :  Long-term signal line

    df["rolling_min_kijun"] = df["low"].rolling(window=kijun_period).min()
    df["rolling_max_kijun"] = df["high"].rolling(window=kijun_period).max()

    # the Kijun Sen is based on the average of the above 2 columns
    df["kijun_sen"] = (df["rolling_max_kijun"] + df["rolling_min_kijun"]) / 2

    # drop columns we don't need anymore
    df.drop(["rolling_min_kijun", "rolling_max_kijun"], axis=1, inplace=True)

    # Senkou Span A : Average of the Tenkan and Kijun, projected Y candles ahead

    df["senkou_span_a"] = ((df["tenkan_sen"] + df["kijun_sen"]) / 2).shift(kijun_period)

    # Senkou Span B : Average between the highest high and lowest low over the last Y*2 candles, projected Y candles ahead

    df["rolling_min_senkou"] = df["low"].rolling(window=kijun_period * 2).min()
    df["rolling_max_senkou"] = df["high"].rolling(window=kijun_period * 2).max()

    df["senkou_span_b"] = (
        (df["rolling_max_senkou"] + df["rolling_min_senkou"]) / 2
    ).shift(kijun_period)

    df.drop(["rolling_min_senkou", "rolling_max_senkou"], axis=1, inplace=True)

    # Chikou Span : COnfirmation line. Close price compared with the price Y candles back

    df["chikou_span"] = df["close"].shift(kijun_period)

    df.dropna(inplace=True)

    # Signal

    df["tenkan_minus_kijun"] = df["tenkan_sen"] - df["kijun_sen"]
    df["previous_tenkan_minus_kijun"] = df["tenkan_minus_kijun"].shift(1)

    df["signal"] = np.where(
        (df["tenkan_minus_kijun"] > 0)
        & (df["previous_tenkan_minus_kijun"] < 0)  # crossover occured
        & (df["close"] > df["senkou_span_a"])  # check it is above the ichimoku cloud
        & (df["close"] > df["senkou_span_b"])  # the ichimoku cloud
        & (df["close"] > df["chikou_span"]),
        1,  # if all the above conditions are satisfied we have a long signal
        np.where(
            (df["tenkan_minus_kijun"] < 0)
            & (df["previous_tenkan_minus_kijun"] > 0)
            & (df["close"] < df["senkou_span_a"])
            & (df["close"] < df["senkou_span_b"])
            & (df["close"] < df["chikou_span"]),
            -1,  # short signal
            0,  # no conditions satsified for long or short signal
        ),
    )

    # create a new dataframe with only signals of 1 or -1, ie remove the 0
    # from the above signal condition outcome

    signal_data = df[df["signal"] != 0].copy()

    signal_data["pnl"] = signal_data["close"].pct_change() * signal_data[
        "signal"
    ].shift(1)

    return signal_data["pnl"].sum()
