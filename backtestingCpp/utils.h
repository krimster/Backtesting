#ifndef UTILS_H
#define UTILS_H

#include <string>
#include <tuple>
#include <vector>

// Tuple of
// time
// open
// close
// high
// low
// volume
std::tuple<
    std::vector<double>,
    std::vector<double>,
    std::vector<double>,
    std::vector<double>,
    std::vector<double>,
    std::vector<double>>
rearrange_candles(double** candles, const std::string& timeframe, long long from_time, long long to_time, int array_size);
#endif