from utils import STRAT_PARAMS, resample_timeframe, get_library
from database import Hdf5Client


class Nsga2:
    def __init__(
        self,
        exchange: str,
        symbol: str,
        strategy: str,
        tf: str,
        from_time: int,
        to_time: int,
        population_size: int,
    ):
        self.exchange = exchange
        self.symbol = symbol
        self.strategy = strategy
        self.tf = tf
        self.from_time = from_time
        self.to_time = to_time
        self.population_size = population_size

        self.params_data = STRAT_PARAMS[strategy]

        # check if strategy coded in python
        if self.strategy in ["obv", "ichimoku", "sup_res"]:
            h5_db = Hdf5Client(exchange)
            self.data = h5_db.get_data(symbol, from_time, to_time)
            self.data = resample_timeframe(data, tf)

        # else if coded in C++
        elif self.strategy in ["psar", "sma"]:

            self.lib = get_library()

            if self.strategy == "sma":
                self.obj = self.lib.sma_new(
                    exchange.encode(),
                    symbol.encode(),
                    tf.encode(),
                    from_time,
                    to_time,
                )

            elif self.strategy == "psar":
                self.obj = self.lib.psar_new(
                    exchange.encode(),
                    symbol.encode(),
                    tf.encode(),
                    from_time,
                    to_time,
                )
