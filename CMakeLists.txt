cmake_minimum_required(VERSION 3.15...3.19)
project(rect)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# https://packages.msys2.org/package/mingw-w64-x86_64-opencv
# pacman -S mingw-w64-x86_64-opencv
# in MSYS2 MinGW x64
if(DEFINED OpenCV_DIR)
    find_package(OpenCV REQUIRED PATHS ${OpenCV_DIR})
else()
    find_package(OpenCV REQUIRED)
endif()

if (NOT DEFINED CLI11_DIR)
    set(CLI11_DIR "components/CLI11" CACHE STRING "CLI11 git repository")
endif ()
include_directories(${CLI11_DIR}/include)

set(WITH_SPDLOG on)
if (WITH_SPDLOG)
    add_subdirectory(components/spdlog)
endif ()
if (NOT TARGET spdlog)
    find_package(spdlog REQUIRED)
endif ()

add_executable(demo main.cpp)
target_link_libraries(demo PRIVATE ${OpenCV_LIBS} spdlog::spdlog)
