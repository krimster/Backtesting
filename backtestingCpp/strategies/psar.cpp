
#include "psar.h"

#include <algorithm>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <numeric>

#include "../Database.h"
#include "../utils.h"

namespace stg
{
    psar::psar(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time)
        : exchange { exchange_c }
        , symbol { symbol_c }
        , timeframe { timeframe_c }
    {

        const auto db         = std::make_unique<database>(exchange);
        int        array_size = 0;
        double**   res        = db->get_data(symbol, exchange, array_size);
        db->close_file();

        // start debug code
        // std::cout << "array_size: " << array_size << '\n';

        // for (int i = 0; i < std::min(array_size, 5); ++i)
        // {
        //     std::cout << "res[" << i << "][0] = "
        //               << res[i][0] << '\n';
        // }

        // std::cout << "last timestamp = "
        //           << res[array_size - 1][0] << '\n';
        // end debug code

        // convert result to vectors
        std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, timeframe, from_time, to_time, array_size);
        // printf("Close size %i\n", close.size());
    }

    double psar::get_pnl() const
    {
        return pnl;
    }
    double psar::get_max_dd() const
    {
        return max_dd;
    }

    void psar::execute_backtest(double initial_acc, double acc_increment, double max_acc)
    {
        pnl                     = 0.0;
        max_dd                  = 0.0;

        double entry_price      = 0;
        double max_pnl          = 0.0;
        int    current_position = 0;

        int    trend[2]         = { 0, 0 };
        double sar[2]           = { 0.0, 0.0 };
        double ep[2]            = { 0.0, 0.0 };
        double af[2]            = { 0.0, 0.0 };

        double temp_sar         = 0.0;

        // Initial values
        trend[0] = close[1] > close[0] ? 1 : -1;
        sar[0]   = trend[0] > 0 ? high[0] : low[0];
        ep[0]    = high[0] > 0 ? high[1] : low[1];
        af[0]    = initial_acc;

        for (int i = 2; i < ts.size(); i++)
        {

            // Trend

            temp_sar = sar[0] + af[0] * (ep[0] - sar[0]);

            if (trend[0] < 0)
            {
                if (trend[0] <= -2)
                {
                    temp_sar = std::max(temp_sar, std::max(high[i - 1], high[i - 2]));
                }
                trend[1] = temp_sar < high[i] ? 1 : trend[0] - 1;
            }
            else
            {
                if (trend[0] >= 2)
                {
                    temp_sar = std::min(temp_sar, std::min(low[i - 1], low[i - 2]));
                }
                trend[1] = temp_sar > low[i] ? -1 : trend[0] + 1;
            }

            // EP (Extreme Point)

            if (trend[1] < 0) // downward trend
            {
                ep[1] = trend[1] != -1 ? std::min(low[i], ep[0]) : low[i];
            }
            else
            {
                ep[1] = trend[1] != 1 ? std::max(high[i], ep[0]) : high[i];
            }

            // AF / SAR

            if (abs(trend[1]) == 1) // if the trend just changed
            {
                sar[1] = ep[0];
                af[1]  = initial_acc; // reset af everytime we have a trend reversal
            }
            else
            {
                sar[1] = temp_sar;
                if (ep[1] == ep[0])
                {
                    af[1] = af[0];
                }
                else
                {
                    af[1] = std::min(max_acc, af[0] + acc_increment);
                }
            }

            // Long signal
            if (trend[1] == 1 && trend[0] < 0)
            {
                if (current_position == -1)
                {
                    double pnl_tmp = (entry_price / close[i] - 1) * 100;
                    pnl += pnl_tmp;
                    max_pnl = std::max(max_pnl, pnl);
                    max_dd  = std::max(max_dd, max_pnl - pnl);
                }

                current_position = 1;
                entry_price      = close[i];
            }
            // short signal
            else if (trend[1] == -1 && trend[0] > 0)
            {
                if (current_position == 1)
                {
                    double pnl_tmp = (close[i] / entry_price - 1) * 100;
                    pnl += pnl_tmp;
                    max_pnl = std::max(max_pnl, pnl);
                    max_dd  = std::max(max_dd, max_pnl - pnl);
                }

                current_position = -1;
                entry_price      = close[i];
            }

            trend[0] = trend[1];
            sar[0]   = sar[1];
            ep[0]    = ep[1];
            af[0]    = af[1];

        } // end for loop
    }
} // namespace stg