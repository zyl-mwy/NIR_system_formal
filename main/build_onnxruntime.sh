#!/bin/bash
# Build script to compile libtorch and install to zyl_libtorch folder

set -e  # Exit on error

# Prepare environment
echo "==========================================="
echo "Prepare environment"
sudo apt install build-essential cmake git libpython3-dev python3-pip
# pip install scikit-learn
# pip install skl2onnx
# pip install numpy
# pip install onnxruntime

# Download onnxruntime source code
echo "==========================================="
echo "Download onnxruntime souece code"
cd ~
git clone --recursive https://github.com/Microsoft/onnxruntime
cd onnxruntime

# problem
echo "==========================================="
echo "How to solve the problem about anaconda when building onnxruntime with ./build.sh"
echo "Disable the anaconda environment by editing the \"~./bashrc\" and removing code about ananconda path. And then reboot your Ubuntu System."

# Compire from source code
echo "==========================================="
echo "Download onnxruntime souece code"
/build.sh --skip_tests --config Release --build_shared_lib --parallel

echo "After compilation, the library files will be generated in the onnxruntime/build/Linux/Release/ directory. In the CMakeLists.txt, set ONNXRUNTIME_ROOT_PATH to this path."

echo "The lib/ is the onnxruntime/build/Linux/Release/, please copy and rename it"
echo "The include/ is the onnxruntime/include/onnxruntime/core/session/, please copy and rename it"


