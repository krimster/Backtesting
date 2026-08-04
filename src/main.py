import logging

from exchanges.binance import BinanceClient
from data_collector import collect_all

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
