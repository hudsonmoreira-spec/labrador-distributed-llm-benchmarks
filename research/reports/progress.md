# Experimental progress

Last updated: 2026-10-02

## Weighted status

The working weights are: inventory and selection (15%), runtime and environment preparation (20%), pilot validation (20%), protocol freeze (10%), full matrix collection (25%), and analysis/article update (10%). A percentage is counted as validated only when its evidence is recorded; preparation in progress is not counted as complete.

**Validated: 35%**

## Completed evidence

- Repository synchronized with `origin/main` at commit `aa36242` before this run.
- Fresh read-only discovery completed for all 24 authorized hosts: `research/data/runs/20261001T180524Z/`.
- Fresh inventory confirms 24/24 SSH accesses and 24/24 passwordless sudo checks.
- Controller build of `llama.cpp` RPC reference succeeded for `llama-cli` and `ggml-rpc-server`.
- Runtime source is fixed at commit `68e79bd8cd6b7995f8fce8da252b249bbf237e63`.
- Cross-compilation preparation succeeded on the controller with GCC 12, a verified Debian 12 arm64 sysroot, `GGML_NATIVE=OFF`, Cortex-A53 flags, RPC enabled, and OpenMP/CUDA/Vulkan/Metal disabled.
- The first GCC 15 package was rejected after ELF inspection because it required GLIBC 2.38/GLIBCXX 3.4.32; no node received it.
- Final package `llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp` passed ELF and ABI checks and has SHA-256 manifest `research/data/preparation/llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp/SHA256SUMS`.
- The final package was hash- and help-validated on node02 (`192.168.50.118`) and node04 (`192.168.50.140`). Local libraries resolve through `LD_LIBRARY_PATH`; system glibc remains in use.
- The fixed pilot GGUF was identified on node03 (`192.168.50.129`) and copied to node02 with matching SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`.

## In progress

- The node01 native build line is abandoned for future preparation after the SSH drop; it was not used for the final artifact and was not restarted.
- Model transfer from node03 to node04 is in progress; the source `llama-server` remains running and untouched.
- Two-node RPC pilot is pending the second model hash and launch logs.

## Not yet validated

- Local single-node inference with a fixed model and prompt.
- Distributed RPC inference proving that one request uses both nodes.
- Frozen 1/2/4/8/16-node protocol and full matrix.
- Scientific performance results and paper tables/figures.

## Failures and mitigations

- The fresh inventory found no LLM runtime on any host. This is an environment gap, not a benchmark result.
- `node01` initially lacked compiler tools. Only `build-essential`, `cmake`, and `git` were installed there; SSH access remained available and no reboot was performed.
- The first ARM CMake configuration generated no `llama-cli` target because `LLAMA_BUILD_SERVER=OFF`; that failed build was preserved as `build-labrador-rpc-failed-20261002`.
- Native node01 builds hit GCC 12 ICEs and Clang 14 crashes; those logs remain preserved but are not comparable to the final cross-compiled artifact.
- The controller's Ubuntu GCC 15 cross-build was rejected by the ABI audit; the final GCC 12/sysroot build corrected both compiler-library and fixed-include leakage.
- The controller cannot resolve Hugging Face for optional UI assets; the protocol does not use the UI, so the package is built without embedded UI assets and this is recorded.

## Next action

Finish the node04 model hash, launch a short single-node inference on node02, then launch a two-node RPC request between node02 and node04 with RPC debug logs proving remote graph work. Freeze the protocol only after those logs are preserved.
