# Progress Log

## 2026-10-05

Branch: `smarthome-multiagent`.

Implemented:

- Created isolated areas under `experiments/smarthome_agents/`, `docs/smarthome_agents/`, and `paper/smarthome_agents/`.
- Added preliminary research plan and draft protocol.
- Added `dev-001-simple-light` scenario with explicit state, allowed actions, forbidden actions, and success criteria.
- Added `smarthome_pilot.py`, a notebook-side coordinator/simulator that calls a real Labrador model through SSH, extracts JSON, validates actions, applies only valid simulated actions, and writes JSONL logs.
- Added a separate LaTeX skeleton for the future paper. Results and conclusions are intentionally pending.

Verified:

- 24/24 hosts reachable by SSH as `caninos`.
- 24/24 hosts allow `sudo -n true`.
- Hardware/SO baseline is homogeneous for architecture, OS, CPU count, and Python version.
- One complete pilot succeeded on `192.168.50.118` using Qwen2.5-1.5B Q5_K_M through `llama-cli`.

Pilot evidence:

- Failed preserved attempt: `experiments/smarthome_agents/runs/20261005T124755Z-7d2cf383/`.
- Successful attempt: `experiments/smarthome_agents/runs/20261005T125801Z-0491ebdf/`.
- Successful action: `{"action":"set_light","room":"sala","value":"on"}`.
- Validator result: allowed.
- Final simulated result: sala light on, quarto unchanged, HVAC unchanged.
- End-to-end inference wrapper time: 171.776 s. This includes model load, because the pilot used `llama-cli` per request rather than a resident server.

Problems found:

- `git switch -c research/smarthome-multiagent` failed because the environment could not create that ref path. The branch was created as `smarthome-multiagent`.
- The first inventory attempt had malformed empty-field output and is preserved. A corrected v2 inventory was collected.
- The first model attempt echoed schema-like values and timed out; the parser/prompt were fixed and the failed run was preserved.
- The pilot host lacks `llama-server` in the research runtime package. Several other hosts have a separate `llama-offline` `llama-server`, but this must be normalized before protocol freeze.

Next step:

Move from per-call `llama-cli` to a resident lightweight agent service, preferably backed by `llama-server`, then run the same scenario through the single-agent HTTP path before expanding to three agents.
