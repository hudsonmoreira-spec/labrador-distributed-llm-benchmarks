# Smart-Home Multi-Agent Research Plan

Working title: Collaborative AI Agents on Low-Cost SBCs: An Evaluation in a Simulated Smart Home.

The title is provisional. The final wording must follow the evidence collected in this activity.

## Research Question

Does collaboration among small-model agents running on Labrador SBCs improve completion of simulated domestic tasks compared with a single agent, and what is the cost in time and processing?

The study does not assume that collaboration is superior. The experiment uses real hardware and real network communication, but the house, residents, sensors, appliances, and actions are simulated.

## Initial Architecture

- Notebook simulator: owns the virtual home state and applies only validated actions.
- Notebook coordinator: routes structured messages, limits rounds, records logs, and uses explicit rules only.
- Labrador agents: run the model locally and receive role-specific prompts.
- Initial pilot: one Labrador, one model call, one validated action.
- Planned collaboration: comfort, energy, and routine agents on three Labradors.

The first pre-correction pilot used `llama-cli` over SSH. The corrected pilot uses a resident `llama-server` on a single Labrador and HTTP JSON transport. Multi-board collaboration is paused until the single-agent output contract is reliable enough for development scenarios.

## Current Model Candidate

- Model file observed on Labrador: `/home/caninos/research/models/qwen2.5-1.5b-instruct-q5_k_m.gguf`.
- Runtime observed on Labrador: `/home/caninos/research/runtime/llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp`.
- llama.cpp version reported by `llama-cli`: `0.5.0-dev`, build `0`, commit unknown.
- Initial decoding: temperature `0`, seed `101`, 96 predicted tokens.

Qwen2.5-0.5B-Instruct GGUF remains the preferred next candidate to evaluate for lower memory and latency. Model origin, license, hash, quantization, and compatibility must be documented from primary sources before the protocol freeze.

## Phases

1. Inventory and plan: create isolated repository area, verify hosts, record hardware and runtime state.
2. Simulator: execute rule-based scenarios without models.
3. Single agent: run a complete Labrador inference and validated action.
4. Collaboration: integrate three Labrador agents with structured messages.
5. Pilot: run development scenarios, fix implementation issues, and freeze protocol.
6. Main campaign: run rule baseline, single-agent, and collaborative configurations.
7. Failure and scale: unavailable agent, delayed response, invalid message, round exhaustion, and replicated teams.
8. Analysis and paper: derive tables, figures, limitations, and manuscript text only from preserved data.

## Safety and Scope Limits

Models cannot execute shell commands. The coordinator exposes only simulated home actions with explicit validation. Invalid proposals are logged separately from actions that are actually applied.

Claims must be limited to the evaluated scenarios. This activity will not claim real-home validation or real energy savings unless those measurements are added later.
