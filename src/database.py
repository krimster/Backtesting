from typing import *

import h5py
import time
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger()


class Hdf5Client:
    def __init__(self, exchange: str):
        self.hf_ = h5py.File(f"data/{exchange}.h5", "a")  # a: read write mode
        self.hf_.flush()  # write to the disc even if we don't close the file
        # self.hf_.close()

    def create_dataset(self, symbol: str):
        # check symbol exists
        if symbol not in self.hf_.keys():
            # maxshape for rows we put None as we don't know how many rows we will have so None= unlimited
            # and we know we have 6 columns
            # float64 is a Numpy type equivalent to double in other languages
            self.hf_.create_dataset(symbol, (0, 6), maxshape=(None, 6), dtype="float64")
            self.hf_.flush()

    def write_data(self, symbol: str, data: List[Tuple]):

        # check data is not already present
        min_ts, max_ts = self.get_fitst_last_timestamp(symbol)

        if min_ts is None:
            min_ts = float("inf")
            max_ts = 0

        filtered_data = []

        for d in data:
            if d[0] < min_ts:
                filtered_data.append(d)
            elif d[0] > max_ts:
                filtered_data.append(d)

        if len(filtered_data) == 0:
            logger.warning("%s: No data to insert", symbol)
            return

        # tranform data to a numpy data array
        data_array = np.array(filtered_data)

        # resize the data space to fit the new data
        self.hf_[symbol].resize(self.hf_[symbol].shape[0] + data_array.shape[0], axis=0)
        self.hf_[symbol][-data_array.shape[0] :] = data_array
        self.hf_.flush()

    def get_data(
        self, symbol: str, from_time: int, to_time: int
    ) -> Union[None, pd.DataFrame]:

        start_query = time.time()

        existing_data = self.hf_[symbol][:]

        if len(existing_data) == 0:
            return None

        # sort the data on timestamp ie first element = x[0]
        # the sorted function returns a List
        data = sorted(existing_data, key=lambda x: x[0])

        # convert List to numpy array as it is easier
        # to transform to a pandas Dataframe
        data = np.array(data)

        # create the Dataframe and spcify the column names
        df = pd.DataFrame(
            data, columns=["timestamp", "open", "high", "low", "close", "volume"]
        )

        # now we filter on the timestamps parameters
        df = df[(df["timestamp"] >= from_time) & (df["timestamp"] <= to_time)]

        # convert timestamps to datetime, we get back a List.
        # We stored the timestamps as floating numbers but the to_datetime
        # expects integers so we convert them. also we specify that our
        # timestamps are in milliseconds
        df["timestamp"] = pd.to_datetime(
            df["timestamp"].values.astype(np.int64), unit="ms"
        )

        # specify that the index columm is the timestamps
        # also specify that we drop dont want it in the dataframe
        # but just keep it as an index for the dataframe.
        # We add inplace=True which is a shorter version of assignement,
        # equivalent to: df = df.set_index("timestamp", drop=True)
        df.set_index("timestamp", drop=True, inplace=True)

        query_time = round((time.time() - start_query), 2)

        logger.info(
            "Retrieved %s %s data from the database in %s seconds",
            len(df.index),
            symbol,
            query_time,
        )

        # return dataframe
        return df

    def get_fitst_last_timestamp(
        self, symbol: str
    ) -> Union[Tuple[None, None], Tuple[float, float]]:

        # copy existing data for given symbol
        # to a variable
        existing_data = self.hf_[symbol][:]

        if len(existing_data) == 0:
            return None, None

        # get the minimun timestamp, for the key we want to filter on
        # we pass x[0] which is the timestamp column
        first_ts = min(existing_data, key=lambda x: x[0])[0]

        last_ts = max(existing_data, key=lambda x: x[0])[0]

        return first_ts, last_ts
