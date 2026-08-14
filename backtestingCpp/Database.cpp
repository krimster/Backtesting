#include "Database.h"

#include <H5Fpublic.h>
#include <H5Ipublic.h>
#include <H5Ppublic.h>
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

void database::close_file()
{
    H5Fclose(h5_file_);
}