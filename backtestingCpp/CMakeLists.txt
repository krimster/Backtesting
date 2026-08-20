cmake_minimum_required(VERSION 3.10.0)
project(backtestingCpp VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_STANDARD 17)

include(CTest)
enable_testing()


find_package(HDF5 REQUIRED COMPONENTS C)

include_directories((${HDF5_INCLUDE-DIRS}))

set(SOURCE_FILES main.cpp Database.cpp utils.cpp strategies/sma.cpp strategies/psar.cpp)

#add_executable(${PROJECT_NAME} ${SOURCE_FILES})

add_library(${PROJECT_NAME} SHARED ${SOURCE_FILES})

##target_link_libraries(${PROJECT_NAME} PRIVATE HDF5::HDF5)
target_link_libraries(${PROJECT_NAME} ${HDF5_LIBRARIES} ${HDF5_C_LIBRARIES})

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)

