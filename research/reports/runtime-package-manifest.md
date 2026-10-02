# Cross-compiled runtime package

- Version: `llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp`
- Source commit: `68e79bd8cd6b7995f8fce8da252b249bbf237e63`
- Package archive SHA-256: `7f312b05110ae904a56943e71042165b3d72f32000b9820d07831746e5441148`
- Target: aarch64 Linux, Debian 12, Cortex-A53 (`fp asimd evtstrm crc32 cpuid`)
- ABI audit: loader `/lib/ld-linux-aarch64.so.1`; maximum GLIBC 2.34; maximum GLIBCXX 3.4.30.
- Build controls: GCC 12 cross compiler, signed Debian 12 arm64 sysroot, `GGML_NATIVE=OFF`, `GGML_RPC=ON`, RDMA/CUDA/Vulkan/Metal/OpenMP disabled.
- Runtime validation: node02 (`192.168.50.118`) and node04 (`192.168.50.140`) passed package SHA-256, `llama-cli --help`, and `ggml-rpc-server --help`.
- Pilot model: `qwen2.5-1.5b-instruct-q5_k_m.gguf`, 1,285,494,304 bytes, SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.

The full per-file `SHA256SUMS` is retained in the ignored versioned package directory under `research/data/preparation/` and is checked on every destination before execution.
