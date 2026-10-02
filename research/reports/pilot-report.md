# Pilot status

## Completed single-node run

- Host: node02 (`192.168.50.118`)
- Runtime: `llama.cpp` commit `68e79bd8`, cross-compiled package `llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp`
- Model: `qwen2.5-1.5b-instruct-q5_k_m.gguf`, Q5_K_M, SHA-256 `b46661073c18e5b56a41fa320975f866a00def1ff08feef4718e013258896f8c`
- Parameters: 4 threads, 4 batch threads, context 512, temperature 0, seed 42, 16 requested tokens.
- Outcome: completed; elapsed 39.07 s. Raw log: `data/runs/20261001T180524Z/pilot/single-node02.log`.

## Distributed RPC attempts

- Client: node02; worker: node04 (`192.168.50.140:50052`); `GGML_RPC_DEBUG=1`.
- The worker accepted repeated client connections and logged many `init_tensor` events plus `set_tensor`, which proves work was sent to the second node.
- Attempt 1 timed out at 150 s while loading/offloading.
- Retry requested four output tokens and timed out at 600 s while still in model loading/offload.
- Raw client/server logs and SHA-256 values are in `data/runs/20261001T180524Z/pilot/`.
- Status: distributed pilot not validated as a completed inference; no latency, throughput, or synchronization metric is reported.

All processes started for these attempts were cleaned up. The fixed runtime, model, prompt, and parameters were not changed between attempts.
