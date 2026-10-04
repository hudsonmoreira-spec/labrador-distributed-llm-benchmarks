# Runtime reproduction record

- Source: `llama.cpp` commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`.
- Patch: [`llama.cpp-local.patch`](llama.cpp-local.patch), applied before configuration.
- ARM toolchain: GCC 12 cross compiler with Debian 12 arm64 sysroot; target Cortex-A53.
- Effective ARM options: `GGML_NATIVE=OFF`, `GGML_RPC=ON`, `GGML_RPC_RDMA=OFF`, `GGML_CUDA=OFF`, `GGML_VULKAN=OFF`, `GGML_METAL=OFF`, OpenMP disabled, tests disabled, examples and server enabled.
- Client build: x86 reference client with `GGML_RPC=ON`, `LLAMA_BUILD_SERVER=ON`, and `-DGGML_SCHED_MAX_BACKENDS=32`.
- ARM package SHA-256: `7f312b05110ae904a56943e71042165b3d72f32000b9820d07831746e5441148`.
- Client SHA-256: `13b3c2e9b45a75615bf9ea11d1c98e182cfcd37e505c7aae9df2e332b5348d69`.
- Model SHA-256: `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.
- ABI: maximum observed GLIBC 2.34 and GLIBCXX 3.4.30.

The executable recipe is preserved in [`ops/cross_compile_llama.sh`](../../../ops/cross_compile_llama.sh) and [`ops/package_cross_llama.sh`](../../../ops/package_cross_llama.sh). The package contains `llama-cli`, `ggml-rpc-server`, the required shared libraries, and the per-file `SHA256SUMS` manifest.

The benchmark starts a new process for every case but does not flush the operating-system disk cache. Therefore, “cold process” is accurate; “cold disk” is not.
