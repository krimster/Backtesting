#include "sma.h"

#include <algorithm>
#include <memory>
#include <numeric>

#include "../Database.h"
#include "../utils.h"

namespace stg
{
    sma::sma(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time)
        : exchange { exchange_c }
        , symbol { symbol_c }
        , timeframe { timeframe_c }
    {

        const auto db         = std::make_unique<database>(exchange);
        int        array_size = 0;
        double**   res        = db->get_data(symbol, exchange, array_size);
        db->close_file();

        // convert result to vectors
        std::tie(ts, open, high, low, close, volume) = rearrange_candles(res, timeframe, from_time, to_time, array_size);
    }

    void sma::execute_backtest(int slow_ma, int fast_ma)
    {
        pnl                                = 0.0;
        max_dd                             = 0.0;

        double entry_price                 = 0;
        double max_pnl                     = 0.0;
        int    current_position            = 0;

        std::vector<double> slow_ma_closes = { };
        std::vector<double> fast_ma_closes = { };

        for (int i = 0; i < ts.size(); i++)
        {
            slow_ma_closes.push_back(close[i]);
            fast_ma_closes.push_back(close[i]);

            if (slow_ma_closes.size() > slow_ma)
            {
                slow_ma_closes.erase(slow_ma_closes.begin());
            }

            if (fast_ma_closes.size() > fast_ma)
            {
                fast_ma_closes.erase(fast_ma_closes.begin());
            }

            if (slow_ma_closes.size() < slow_ma)
            {
                continue;
            }

            double sum_slow  = std::accumulate(slow_ma_closes.begin(), slow_ma_closes.end(), 0.0);
            double sum_fast  = std::accumulate(fast_ma_closes.begin(), fast_ma_closes.end(), 0.0);

            double mean_slow = sum_slow / slow_ma;
            double mean_fast = sum_fast / fast_ma;

            // Long signal

            if (mean_fast > mean_slow && current_position <= 0)
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

            // Short signal

            if (mean_fast < mean_slow && current_position >= 0)
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
        }
    }

} // namespace stg