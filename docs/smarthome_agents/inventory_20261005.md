# Inventory 2026-10-05

Raw collection directories:

- `experiments/smarthome_agents/runs/20261005T124433Z/`
- `experiments/smarthome_agents/runs/20261005T130126Z-inventory-v2/`

The first directory is preserved but has formatting defects for empty fields. The second directory is the inventory used for this summary.

## Availability

- SSH access as `caninos`: 24/24.
- Passwordless `sudo -n true`: 24/24.
- Architecture: 24/24 `aarch64`.
- OS: 24/24 Debian GNU/Linux 12 bookworm.
- CPU count: 24/24 report 4 CPUs.
- RAM: 21 hosts report 1,986,400 kB; 3 hosts report 1,986,272 kB. This difference is small enough to treat the group as operationally homogeneous for first-pass experiments, while preserving exact values in raw logs.
- Python: 24/24 report Python 3.11.2.
- `llama-cli`: found on 24/24.
- `llama-server`: found on 8/24 under `/home/caninos/llama-offline/llama.cpp/build/bin/llama-server`.
- GGUF files: found on 10/24, but some files are tokenizer/vocabulary test files rather than model weights.

## Initial Pilot Host

The first successful pilot used `192.168.50.118`.

- Hostname: `labrador`.
- Runtime: `/home/caninos/research/runtime/llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp`.
- Model: `/home/caninos/research/models/qwen2.5-1.5b-instruct-q5_k_m.gguf`.
- `llama-cli --version`: `0.5.0-dev`, build `0`, commit unknown.
- `llama-server`: not found in the research runtime package on this host.

## Homogeneity Note

The hosts are homogeneous in architecture, operating system, CPU count, Python version, and sudo availability. They are not homogeneous in model placement or `llama-server` availability. Before the collaborative campaign, the selected agent hosts should be normalized by deploying the same model path and a common resident server/service.
