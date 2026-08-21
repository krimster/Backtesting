import logging
import backtester
import datetime
import optimizer

from exchanges.binance import BinanceClient
from data_collector import collect_all
from utils import TF_EQUIV

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


formatter = logging.Formatter("%(asctime)s %(levelname)s :: %(message)s")

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

file_handler = logging.FileHandler("logs/info.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.DEBUG)

logger.addHandler(stream_handler)
logger.addHandler(file_handler)

# logger.debug("This is an debug log")


## Program Mode selection

if __name__ == "__main__":  # only execute if main file executed

    mode = input("Specify the program mode (data / backtest / optimize): ").lower()

    while True:
        exchange = input("Choose an exchange: ").lower()
        if exchange in ["binance"]:
            break
        else:
            print("{} is not currently supported".format(exchange))

    if exchange == "binance":
        client = BinanceClient(True)
        # print(client.symbols)
        # print(client.get_historical_data("BTCUSDT"))

    while True:
        symbol = input("Choose a symbol: ").upper()
        if symbol in client.symbols:
            break
        else:
            print("{} is not currently supported".format(symbol))

    if mode == "data":
        collect_all(client, exchange, symbol)

    elif mode in ["backtest", "optimize"]:

        ## Strategy
        available_strategies = ["obv", "ichimoku", "sup_res", "sma", "psar"]

        while True:
            strategy = input(
                f"Choose a strategy ({', '.join(available_strategies)}): "
            ).lower()

            if strategy in available_strategies:
                break

        ## Timeframe
        while True:
            timeframe = input(
                f"Choose a timeframe ({', '.join(TF_EQUIV.keys())}): "
            ).lower()

            if timeframe in TF_EQUIV.keys():
                break

        ## From time
        while True:
            from_time = input(f"Backtest from (yyyy-mm-dd) or Press Enter: ").lower()
            if from_time == "":
                from_time = 0
                break

            try:
                # from datetime we get a datetime object we converted to a timestamp
                # then we get milliseconds
                from_time = int(
                    datetime.datetime.strptime(from_time, "%Y-%m-%d").timestamp() * 1000
                )
                break
            except ValueError:
                continue

        ## to time
        while True:
            to_time = input(f"Backtest to (yyyy-mm-dd) or Press Enter: ").lower()
            # use current time if empty
            if to_time == "":
                to_time = int(datetime.datetime.now().timestamp() * 1000)
                break

            try:
                to_time = int(
                    datetime.datetime.strptime(to_time, "%Y-%m-%d").timestamp() * 1000
                )
                break
            except ValueError:
                continue

        if mode == "backtest":
            print(
                backtester.run(
                    exchange, symbol, strategy, timeframe, from_time, to_time
                )
            )

        elif mode == "optimize":

            # Population size
            while True:
                try:
                    pop_size = int(input(f"Choose a population size: "))
                    break
                except ValueError:
                    continue

            # Iterations
            while True:
                try:
                    generations = int(input(f"Choose a number of generations: "))
                    break
                except ValueError:
                    continue

            nsga2 = optimizer.Nsga2(
                exchange=exchange,
                symbol=symbol,
                strategy=strategy,
                tf=timeframe,
                from_time=from_time,
                to_time=to_time,
                population_size=pop_size,
            )
