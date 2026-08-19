#include <cstring>
#include <iostream>
#include <memory>

#include "Database.h"
#include "strategies/psar.h"
#include "utils.h"

int main(int argc, char* argv[])
{
    // const auto db       = std::make_unique<database>("binance");

    // int      array_size = 0;
    // double** res        = db->get_data("BTCUSDT", "binance", array_size);

    // std::vector<double> ts, open, high, low, close, volume;
    // std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, "5m", 0, 1630074127000, array_size);

    // for (int i = 0; i < 100; i++)
    // {
    //     printf("%f %f %f %f %f %f\n", ts[i], open[i], high[i], low[i], close[i], volume[i]);
    // }

    // printf("Size %i\n", ts.size());
    // db->close_file();

    // return 0;

    // SMA example
    std::string symbol    = "BTCUSDT";
    std::string exchange  = "binance";
    std::string timeframe = "5m";

    char* symbol_char     = strcpy((char*)malloc(symbol.length() + 1), symbol.c_str());
    char* exchange_char   = strcpy((char*)malloc(exchange.length() + 1), exchange.c_str());
    char* timeframe_char  = strcpy((char*)malloc(timeframe.length() + 1), timeframe.c_str());

    stg::psar s(exchange_char, symbol_char, timeframe_char, 0, 1787140000000);
    s.execute_backtest(0.02, 0.02, 0.2);
    printf("%f | %f\n", s.get_pnl(), s.get_max_dd());

    return 0;
}
