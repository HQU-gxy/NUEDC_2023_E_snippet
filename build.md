# Simple OpenCV demo

## Build

Don't forget to clone the submodules

```bash
git submodule update --init --recursive
```

### Build in Windows

I assume you have installed [MSYS2](https://www.msys2.org/) and [Ninja](https://ninja-build.org/).
You will get the `OpenCV` by installing `mingw-w64-x86_64-opencv` package.

In the `MSYS2 MinGW x64` terminal, run the following commands:

```bash
pacman -Syu
pacman -S base-devel cmake ninja # maybe clang
pacman -S mingw-w64-x86_64-opencv
```

I assume you install your `MSYS2` in `C:\msys64`. You could add `C:\msys64\mingw64\bin` to your `PATH`
environment variable. Maybe it would make your life easier.

```powershell
mkdir build
cd build
# clang which comes with Visual Studio 2019 is not happy with Mingw-w64
cmake .. -G Ninja -DOpenCV_DIR="C:\msys64\mingw64" -DCMAKE_CXX_COMPILER=g++ -DCMAKE_C_COMPILER=gcc
ninja -j (Invoke-Expression [Environment]::ProcessorCount)
```

I'm not sure whether OpenCV installed by the [Official Installer](https://opencv.org/releases/)
or [`vcpkg`](https://vcpkg.io/) would work. 

See also

- [CMakeLists for OpenCV that installed using Vcpkg ](https://gist.github.com/UnaNancyOwen/5061d8c966178b753447e8a9f9ac8cf1)
- [Use Windows Terminal with MSYS2](https://www.msys2.org/docs/terminals/)

### Build in Linux

#### Install dependencies

##### Ubuntu/Debian

```bash
sudo apt install build-essential cmake ninja-build
sudo apt install libopencv-dev
```

##### Arch Linux

```bash
pacman -S base-devel cmake ninja
pacman -S opencv
```

##### Build

This is a typical out-of-source build. Trivially, you can run the following commands:

```bash
mkdir build
cd build
cmake .. -G Ninja
ninja -j$(nproc)
```
