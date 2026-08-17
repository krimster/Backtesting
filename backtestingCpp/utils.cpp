#include "utils.h"

#include <algorithm>
#include <cmath>
#include <iostream>

std::tuple<
    std::vector<double>,
    std::vector<double>,
    std::vector<double>,
    std::vector<double>,
    std::vector<double>,
    std::vector<double>>
rearrange_candles(double** candles, const std::string& timeframe, int array_size)
{
    std::vector<double> ts, open, high, low, close, volume;
    double              tf_ms;

    // check if timeframe is in minutes, 15m, 10m etc...
    if (timeframe.find('m') != std::string::npos)
    {
        std::string minutes = timeframe.substr(0, timeframe.find('m'));
        tf_ms               = stod(minutes) * 60.0 * 1000.0;
    }
    else if (timeframe.find('h') != std::string::npos)
    {
        std::string hours = timeframe.substr(0, timeframe.find('h'));
        tf_ms             = stod(hours) * 60.0 * 60.0 * 1000.0;
    }
    else
    {
        std::cout << "Parsing timeframe failed for " << timeframe << "\n";
        return std::make_tuple(ts, open, high, low, close, volume);
    }

    // fmod() calculates the remainder of a division
    double current_ts = candles[0][0] - std::fmod(candles[0][0], tf_ms);
    double current_o  = candles[0][1];
    double current_h  = candles[0][2];
    double current_l  = candles[0][3];
    double current_c  = candles[0][4];
    double current_v  = candles[0][5];

    // we the loop at 1 instead of zero so that we use the first
    // candle as comparison
    for (int i = 1; i < array_size; i++)
    {
        if (candles[i][0] >= current_ts + tf_ms)
        {
            // case: adding a candle

            ts.push_back(current_ts);
            open.push_back(current_o);
            high.push_back(current_h);
            low.push_back(current_l);
            close.push_back(current_c);
            volume.push_back(current_v);

            int missing_candles = (candles[i][0] - current_ts) / tf_ms;

            if (missing_candles > 0)
            {
                printf("Missing %i candle(s) from %f\n", missing_candles, current_ts);
                std::cout << "Missing " << missing_candles << " candle(s) from " << current_ts << "\n";

                for (int u = 0; u < missing_candles; u++)
                {
                    // create the missing candles
                    // we populate all columns with the close price
                    // as we assume there was no trade and we set the
                    // volume to 0
                    ts.push_back(current_ts + tf_ms * (u + 1));
                    open.push_back(current_c);
                    high.push_back(current_c);
                    low.push_back(current_c);
                    close.push_back(current_c);
                    volume.push_back(0);
                }
            }

            // update current values
            current_ts = candles[i][0] - std::fmod(candles[i][0], tf_ms);
            current_o  = candles[i][1];
            current_h  = candles[i][2];
            current_l  = candles[i][3];
            current_c  = candles[i][4];
            current_v  = candles[i][5];
        }
        else // case:  updating current candle
        {
            // check current high
            current_h = std::max(candles[i][2], current_h);
            // if (candles[i][2] > current_h)
            // {
            //     current_h = candles[i][2];
            // }

            // check current low
            current_l = std::min(candles[i][3], current_l);
            // if (candles[i][3] < current_l)
            // {
            //     current_l = candles[i][3];
            // }

            // close will always be updated
            current_c = candles[i][4];

            // the volume is summed
            current_v += candles[i][5];
        }
    }

    return std::make_tuple(ts, open, high, low, close, volume);
}
