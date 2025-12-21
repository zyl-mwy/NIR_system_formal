#!/bin/bash
# Build script to compile libtorch and install to zyl_libtorch folder

set -e  # Exit on error
# Download libtorch source code
echo "==========================================="
echo "Download libtorch souece code"
cd ~
git clone --recursive https://github.com/pytorch/pytorch.git
cd pytorch

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTORCH_ROOT="$SCRIPT_DIR"
INSTALL_DIR="$PYTORCH_ROOT/zyl_libtorch"
BUILD_DIR="$PYTORCH_ROOT/build_libtorch"

echo "=========================================="
echo "Building libtorch for aarch64"
echo "=========================================="
echo "PyTorch root: $PYTORCH_ROOT"
echo "Build directory: $BUILD_DIR"
echo "Install directory: $INSTALL_DIR"
echo ""

# Set CMAKE_PREFIX_PATH for conda environment if available
if [ -n "$CONDA_PREFIX" ]; then
    export CMAKE_PREFIX_PATH="$CONDA_PREFIX:$CMAKE_PREFIX_PATH"
    echo "Using conda environment: $CONDA_PREFIX"
elif command -v conda &> /dev/null; then
    CONDA_DIR=$(dirname $(which conda))/..
    export CMAKE_PREFIX_PATH="$CONDA_DIR:$CMAKE_PREFIX_PATH"
    echo "Using conda installation: $CONDA_DIR"
fi

# Create build directory
echo "Creating build directory..."
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Disable linker script optimization to avoid build issues
export USE_PRIORITIZED_TEXT_FOR_LD=0

# Configure CMake
echo ""
echo "Configuring CMake..."
cmake "$PYTORCH_ROOT" \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX="$INSTALL_DIR" \
    -DBUILD_PYTHON=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DBUILD_TEST=OFF \
    -DUSE_CUDA=OFF \
    -DUSE_ROCM=OFF \
    -DUSE_XPU=OFF \
    -DUSE_MKLDNN=ON \
    -DUSE_NNPACK=ON \
    -DUSE_OPENMP=ON \
    -DUSE_DISTRIBUTED=OFF \
    -DUSE_PRIORITIZED_TEXT_FOR_LD=OFF \
    -DCMAKE_CXX_STANDARD=17

# Build
echo ""
echo "Building libtorch (this may take a while)..."
cmake --build . --target install -j$(nproc)

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "libtorch has been installed to: $INSTALL_DIR"
echo "=========================================="
echo ""
echo "Contents of $INSTALL_DIR:"
ls -lh "$INSTALL_DIR" || true
echo ""
if [ -d "$INSTALL_DIR/lib" ]; then
    echo "Libraries in $INSTALL_DIR/lib:"
    ls -lh "$INSTALL_DIR/lib" | head -20
fi

echo "The $PYTORCH_ROOT/build_libtorch is the libtorch, please copy and rename it by yourself"
