#include <iostream>
#include <memory>

#include "Database.h"
#include "utils.h"

int main(int argc, char* argv[])
{
    const auto db       = std::make_unique<database>("binance");

    int      array_size = 0;
    double** res        = db->get_data("BTCUSDT", "binance", array_size);

    std::vector<double> ts, open, high, low, close, volume;
    std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, "5m", array_size);

    for (int i = 0; i < 100; i++)
    {
        printf("%f %f %f %f %f %f\n", ts[i], open[i], high[i], low[i], close[i], volume[i]);
    }

    printf("Size %i\n", ts.size());
    db->close_file();

    return 0;
}
