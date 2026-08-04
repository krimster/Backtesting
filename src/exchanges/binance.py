from typing import *

import logging
import requests

logger = logging.getLogger()


class BinanceClient:
    def __init__(self, futures=False):

        self.futures = futures

        if self.futures:
            self._base_url = "https://fapi.binance.com"
        else:
            self._base_url = "https://api.binance.com"

        self.symbols = self._get_symbols()

    #
    # Method to request data from the Binance API
    #
    def _make_requests(self, endpoint: str, query_parameters: Dict):
        try:
            response = requests.get(self._base_url + endpoint, params=query_parameters)
        except Exception as ex:
            logger.error(
                "Connection error while making request to %s: %s", endpoint, ex
            )
            return None

        if response.status_code:
            return response.json()
        else:
            logger.error(
                "Error while making request to %s: %s  (status code = %s)",
                endpoint,
                response.json(),
                response.status_code,
            )
            return None

    #
    # Request symbols from the Binance API
    #
    def _get_symbols(self) -> List[str]:

        params = dict()  # empty params, none required

        endpoint = "/fapi/v1/exchangeInfo" if self.futures else "/api/v3/exchangeInfo"
        data = self._make_requests(endpoint, params)

        # Extract symbols from response data
        symbols = [x["symbol"] for x in data["symbols"]]

        # print(symbols)

        return symbols

    #
    # Request historical candle stick data
    # Doc: https://developers.binance.com/en/docs/catalog/core-trading-derivatives-trading-usd-s-m-futures/api/rest-api/market-data#kline-candlestick-data
    def get_historical_data(
        self,
        symbol: str,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
    ):

        params = dict()

        params["symbol"] = symbol
        params["interval"] = "1m"
        params["limit"] = 1500

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        endpoint = "/fapi/v1/klines" if self.futures else "/api/v3/klines"
        raw_candles = self._make_requests(endpoint, params)

        candles = []  # candles holder!

        if raw_candles is not None:
            # parse the data and create a list of tuples
            # with the data we need
            for c in raw_candles:
                candles.append(
                    (
                        float(c[0]),  # Open time
                        float(c[1]),  # Open
                        float(c[2]),  # High
                        float(c[3]),  # Low
                        float(c[4]),  # Close
                        float(c[5]),  # Volume
                    )
                )

            return candles
        else:
            return None
