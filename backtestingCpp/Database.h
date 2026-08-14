#include <string>

#include <H5Ipublic.h>

class database
{
public:
    explicit database(const std::string& file_name);

    void close_file();

private:
    hid_t h5_file_;
};