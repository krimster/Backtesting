#include "Database.h"

#include <chrono>
#include <cstdlib>

#include <H5Dpublic.h>
#include <H5Fpublic.h>
#include <H5Ipublic.h>
#include <H5Ppublic.h>
#include <H5Spublic.h>
#include <H5Tpublic.h>
#include <H5public.h>

database::database(const std::string& file_name)
{
    const auto FILE_NAME = "../../data/" + file_name + ".h5";
    printf("Opening %s\n", FILE_NAME.c_str());

    hid_t fapl    = H5Pcreate(H5P_FILE_ACCESS);

    herr_t status = H5Pset_libver_bounds(fapl, H5F_LIBVER_LATEST, H5F_LIBVER_LATEST);
    status        = H5Pset_fclose_degree(fapl, H5F_CLOSE_STRONG);

    h5_file_      = H5Fopen(FILE_NAME.c_str(), H5F_ACC_RDONLY, fapl);

    if (h5_file_ < 0)
    {
        printf("Error while opening %s\n", FILE_NAME.c_str());
    }
}

double** database::get_data(const std::string& symbol, const std::string& exchange)
{
    double** results = { };

    hid_t dataset    = H5Dopen2(h5_file_, symbol.c_str(), H5P_DEFAULT);

    // check dataset opened successfuly
    if (dataset == -1)
    {
        return results;
    }

    const auto start_ts = std::chrono::high_resolution_clock::now();

    hid_t   data_space  = H5Dget_space(dataset);
    hsize_t dims[2];

    H5Sget_simple_extent_dims(data_space, dims, nullptr);

    results = new double*[dims[0]];

    for (size_t i = 0; i < dims[0]; ++i)
    {
        results[i] = new double[dims[1]];
    }

    double* candles_array = new double[dims[0] * dims[1]];

    H5Dread(dataset, H5T_NATIVE_DOUBLE, H5S_ALL, H5S_ALL, H5P_DEFAULT, candles_array);

    int j = 0;

    for (int i = 0; i < dims[0] * dims[1]; i += 6)
    {
        results[j][0] = candles_array[i];
        results[j][1] = candles_array[i + 1];
        results[j][2] = candles_array[i + 2];
        results[j][3] = candles_array[i + 3];
        results[j][4] = candles_array[i + 4];
        results[j][5] = candles_array[i + 5];

        j++;
    }

    delete[] candles_array;

    qsort(results, dims[0], sizeof(results[0]), compare);

    H5Sclose(data_space);
    H5Sclose(dataset);

    const auto end_ts  = std::chrono::high_resolution_clock::now();

    auto read_duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_ts - start_ts);

    printf("Fetched %i %s %s data in %i ms\n", (int)dims[0], exchange.c_str(), symbol.c_str(), int(read_duration.count()));

    return results;
}

void database::close_file()
{
    H5Fclose(h5_file_);
}

int compare(const void* pa, const void* pb)
{
    const double* a = *(const double**)pa;
    const double* b = *(const double**)pb;

    if (a[0] == b[0])
    {
        return 0;
    }
    else if (a[0] < b[0])
    {
        return -1;
    }
    else
    {
        return 1;
    }
}