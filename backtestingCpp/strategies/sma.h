#pragma once

#include <string>
#include <vector>

namespace stg
{
    class sma
    {
    public:
        sma(char* exchange_c, char* symbol_c, char* timeframe_c, long long from_time, long long to_time);

        void execute_backtest(int slow_ma, int fast_ma);

        [[nodiscard]] double get_pnl() const;
        [[nodiscard]] double get_max_dd() const;

    private:
        std::string exchange;
        std::string symbol;
        std::string timeframe;

        std::vector<double> ts, open, high, low, close, volume;

        double pnl    = 0.0;
        double max_dd = 0.0;
    };

} // namespace stg
