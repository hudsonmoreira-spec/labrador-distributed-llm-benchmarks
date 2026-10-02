#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
COMMIT=${LLAMA_COMMIT:-68e79bd8cd6b7995f8fce8da252b249bbf237e63}
BUILD=${CROSS_BUILD_DIR:-/tmp/labrador-llama-cross-build-${COMMIT}-gcc12-debian12-final2}
SRC=${CROSS_SOURCE_DIR:-/tmp/labrador-llama-cross-src-${COMMIT}}

test -x "$(command -v aarch64-linux-gnu-gcc-12)"
test -x "$(command -v aarch64-linux-gnu-g++-12)"
test -d "$ROOT/ops/toolchain/sysroot-debian12"
if [[ ! -d "$SRC" ]]; then
  mkdir -p "$SRC"
  git -C "$ROOT/research/runtime/llama.cpp" archive "$COMMIT" | tar -xf - -C "$SRC"
fi

SYSROOT="$ROOT/ops/toolchain/sysroot-debian12"
CFLAGS="-mcpu=cortex-a53 -mno-outline-atomics -nostdinc -isystem$SYSROOT/usr/include/aarch64-linux-gnu -isystem$SYSROOT/usr/include -isystem/usr/lib/gcc-cross/aarch64-linux-gnu/12/include"
CXXFLAGS="$CFLAGS -nostdinc++ -isystem$SYSROOT/usr/include/c++/12 -isystem$SYSROOT/usr/include/aarch64-linux-gnu/c++/12"
cmake -S "$SRC" -B "$BUILD" \
  -DCMAKE_TOOLCHAIN_FILE="$ROOT/ops/toolchain/labrador-aarch64-debian12.cmake" \
  -DCMAKE_C_FLAGS="$CFLAGS" -DCMAKE_CXX_FLAGS="$CXXFLAGS" \
  -DGGML_CCACHE=OFF -DGGML_NATIVE=OFF -DGGML_RPC=ON -DGGML_RPC_RDMA=OFF \
  -DGGML_CUDA=OFF -DGGML_VULKAN=OFF -DGGML_METAL=OFF \
  -DLLAMA_BUILD_TESTS=OFF -DLLAMA_BUILD_EXAMPLES=ON -DLLAMA_BUILD_SERVER=ON
cmake --build "$BUILD" --parallel "${CROSS_JOBS:-2}" --target llama-cli ggml-rpc-server
echo "cross build complete: $BUILD"
