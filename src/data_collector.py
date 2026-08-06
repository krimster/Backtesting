from typing import *

import logging
import time

from database import Hdf5Client
from utils import *
from exchanges.binance import BinanceClient

logger = logging.getLogger()


def collect_all(client: Union[BinanceClient], exchange: str, symbol: str):

    # instatiate the db
    h5_db = Hdf5Client(exchange)
    h5_db.create_dataset(symbol)

    # TESTING DATA RETRIEVAL FUNCTION ONLY!
    # data = h5_db.get_data(symbol, from_time=0, to_time=int(time.time() * 1000))
    # data = resample_timeframe(data, "15m")
    # print(data)
    # return

    oldest_ts, most_recent_ts = h5_db.get_fitst_last_timestamp(symbol)
    print(oldest_ts, most_recent_ts)

    # Initial request

    if oldest_ts is None:
        data = client.get_historical_data(
            symbol, end_time=int(time.time() * 1000) - 60000
        )

        if len(data) == 0:
            logger.warning("%s %s: no initial data found", exchange, symbol)
            return
        else:
            logger.info(
                "%s %s: Collected %s intial data from %s to %s",
                exchange,
                symbol,
                len(data),
                ms_to_dt(
                    data[0][0]
                ),  # 0 first element of the list and first element of the tuple
                ms_to_dt(
                    data[-1][0]
                ),  # last element of the list andfirst element of the tuple
            )

            # insert data to the database
            h5_db.write_data(symbol, data)

            # now update the oldestand most recent timestamps
            oldest_ts = data[0][0]
            most_recent_ts = data[-1][0]

    data_to_insert = []

    # Most recent data

    while True:
        data = client.get_historical_data(
            symbol, start_time=int(most_recent_ts + 60000)
        )

        if data is None:
            time.sleep(4)  # pause in case of an error during the request
            continue

        if len(data) < 2:
            break

        data = data[:-1]  # remove the current candle stick

        # add to the data to insert
        data_to_insert = data_to_insert + data

        if len(data_to_insert) > 10000:
            # write the data to disk and clear the list
            h5_db.write_data(symbol, data_to_insert)
            data_to_insert.clear()

        if data[-1][0] > most_recent_ts:
            most_recent_ts = data[-1][0]

        logger.info(
            "%s %s: Collected %s recent data from %s to %s",
            exchange,
            symbol,
            len(data),
            ms_to_dt(
                data[0][0]
            ),  # 0 first element of the list and first element of the tuple
            ms_to_dt(
                data[-1][0]
            ),  # last element of the list andfirst element of the tuple
        )

        # pause a little to avoid hitting the rate limit
        time.sleep(1.1)

    # write the data to disk and clear the list
    h5_db.write_data(symbol, data_to_insert)
    data_to_insert.clear()

    # Older data

    while True:
        data = client.get_historical_data(symbol, end_time=int(oldest_ts - 60000))

        if data is None:
            time.sleep(4)  # pause in case of an error during the request
            continue

        if len(data) == 0:
            logger.warning(
                "%s %s: Stopped older data collection because no data was found before %s",
                exchange,
                symbol,
                ms_to_dt(oldest_ts),
            )
            break

        # add to the data to insert
        data_to_insert = data_to_insert + data

        if len(data_to_insert) > 10000:
            # write the data to disk and clear the list
            h5_db.write_data(symbol, data_to_insert)
            data_to_insert.clear()

        if data[0][0] < oldest_ts:
            oldest_ts = data[0][0]

        logger.info(
            "%s %s: Collected %s older data from %s to %s",
            exchange,
            symbol,
            len(data),
            ms_to_dt(
                data[0][0]
            ),  # 0 first element of the list and first element of the tuple
            ms_to_dt(
                data[-1][0]
            ),  # last element of the list andfirst element of the tuple
        )

        # pause a little to avoid hitting the rate limit
        time.sleep(1.1)

    # write the data to disk and clear the list
    h5_db.write_data(symbol, data_to_insert)
    data_to_insert.clear()
