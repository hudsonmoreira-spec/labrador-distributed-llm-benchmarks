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

## 2026-10-05 Follow-up

Branch: `smarthome-multiagent`.

Implemented:

- Corrected the single-agent pilot after reviewing commit `aeff69b`.
- Replaced SSH `llama-cli` calls with HTTP requests to a resident `llama-server`.
- Added four development scenarios and a generic evaluator.
- Added local software tests for prompt echo, timeout, malformed JSON, unexpected fields, contradictory fixed hints, wrong-room action, unchanged-state checks, clarification, and no-action handling.
- Started an isolated resident server on `192.168.50.89:18089`.

Verified:

- Local tests: 7/7 passed.
- Resident server startup: 72 s until `/health` returned `ok`.
- Corrected 12-attempt pilot: 12/12 HTTP executions completed and preserved.

Pilot outcome:

- Structured valid responses: 0/12.
- Actions applied: 0/12.
- Tasks completed: 0/12.
- This is a valid infrastructure result: malformed or non-contract model outputs were rejected rather than counted as success.

Evidence:

- Server configuration: `docs/smarthome_agents/server_resident_20261005.md`.
- Pilot report: `docs/smarthome_agents/single_agent_pilot_20261005.md`.
- Campaign data: `experiments/smarthome_agents/runs/20261005T1332-single-agent-resident-1p5b/`.

Next step:

Do not start multi-board collaboration yet. First improve the single-agent output contract, likely with llama.cpp grammar or JSON schema constraints, then rerun a new identified development campaign.
