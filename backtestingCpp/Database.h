#include <string>

#include <H5Ipublic.h>

class database
{
public:
    explicit database(const std::string& file_name);

    void close_file();

    double** get_data(const std::string& symbol, const std::string& exchange);

private:
    hid_t h5_file_;
};

int compare(const void* pa, const void* pb);