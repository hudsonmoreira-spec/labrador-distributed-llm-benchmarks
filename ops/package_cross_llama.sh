#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BUILD=${1:?usage: package_cross_llama.sh BUILD_DIR VERSIONED_PACKAGE_DIR}
PKG=${2:?usage: package_cross_llama.sh BUILD_DIR VERSIONED_PACKAGE_DIR}
SYSROOT="$ROOT/ops/toolchain/sysroot-debian12"
rm -rf "$PKG"
mkdir -p "$PKG/bin" "$PKG/lib" "$PKG/metadata"
cp -a "$BUILD/bin/llama-cli" "$BUILD/bin/ggml-rpc-server" "$BUILD/bin/"lib*.so* "$PKG/bin/"
cp -a "$SYSROOT/usr/lib/aarch64-linux-gnu/libstdc++.so.6.0.30" "$PKG/lib/"
ln -s libstdc++.so.6.0.30 "$PKG/lib/libstdc++.so.6"
cp -a "$SYSROOT/lib/aarch64-linux-gnu/libgcc_s.so.1" "$PKG/lib/"
printf 'source_commit=%s\ntarget_cpu=cortex-a53\nGGML_NATIVE=OFF\nGGML_RPC=ON\nOpenMP=OFF\n' \
  "${LLAMA_COMMIT:-68e79bd8cd6b7995f8fce8da252b249bbf237e63}" > "$PKG/metadata/build-manifest.txt"
(cd "$PKG" && find bin lib -type f -o -type l | sort | xargs sha256sum > SHA256SUMS)
echo "package complete: $PKG"
