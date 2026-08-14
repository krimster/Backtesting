#include <iostream>
#include <memory>

#include "Database.h"

int main(int argc, char* argv[])
{
    const auto db = std::make_unique<database>("binance");
    db->close_file();

    return 0;
}
