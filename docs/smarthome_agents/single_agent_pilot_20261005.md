# Corrected Single-Agent Pilot 2026-10-05

Status: development pilot, not main-campaign evidence.

## Corrections Since Commit `aeff69b`

- Removed the fixed prompt sentence that disclosed the correct room and intent.
- Removed scenario-specific answer examples from the prompt.
- Replaced SSH `llama-cli` inference with HTTP JSON requests to a resident `llama-server`.
- Extracted candidate actions only from the model response content, not from prompt echo, logs, banners, or server metadata.
- Added strict response validation for action names, required keys, unexpected fields, value domains, unknown rooms, and action permissions.
- Split result flags into execution completed, structured response valid, action permitted, action applied, and task completed.
- Replaced the fixed sala-light evaluator with scenario-defined state checks, unchanged-state checks, prohibited action checks, clarification policy, and no-action policy.
- Preserved old pilot logs and treated them as pre-correction evidence only.

## Local Software Verification

Command:

```bash
python3 -m unittest experiments/smarthome_agents/tests/test_pilot_logic.py -v
```

Result: 7 tests passed.

The tests cover prompt echo rejection, timeout failure, malformed JSON, unexpected fields, absence of contradictory fixed hints for "acenda" and "apague", wrong-room evaluation failure, unchanged-state checks, clarification success policy, and no-action failure policy for the ambiguous scenario. These are software tests with simulated responses, not model inference results.

## Real Pilot Campaign

Campaign directory:

`experiments/smarthome_agents/runs/20261005T1332-single-agent-resident-1p5b/`

Summary files:

- `summary.csv`
- `summary.md`

Scenarios:

- `dev-light-on-sala`
- `dev-light-off-sala`
- `dev-light-quarto-preserve-sala`
- `dev-ambiguous-light-clarify`

Each scenario was executed three times against the resident server on `192.168.50.89:18089`, for 12 preserved attempts.

## Results

| Metric | Count |
|---|---:|
| HTTP executions completed | 12/12 |
| Structured responses valid | 0/12 |
| Actions permitted | 0/12 |
| Actions applied | 0/12 |
| Tasks completed | 0/12 |

The failures were correctly classified by the infrastructure. Common model behaviors included emitting multiple JSON objects, using a nested `data` shape not in the allowed contract, emitting state-like JSON instead of a function call, or adding prose after JSON. None of those were accepted as successful actions.

Latency with the resident model remained high: approximately 71 to 79 seconds per request in this pilot. Server timings show prompt evaluation around 2.4 tokens/s and generation around 1.65 tokens/s on the selected Labrador.

## Interpretation Boundary

This pilot demonstrates the corrected infrastructure and evaluator, not useful smart-home task performance. The negative task outcome is expected to inform prompt/schema/runtime work before any collaboration among boards or larger campaigns.

## Chat-Template and Schema Follow-up

A follow-up corrected campaign used `/v1/chat/completions`, the Qwen chat template exposed by the local server, and `response_format` with a JSON Schema. This changed the input/output configuration and must not be compared as a model-only improvement against the previous `/completion` pilot.

Intermediate campaign directory, preserved because it exposed a validator issue:

`experiments/smarthome_agents/runs/20261005T1422-single-agent-chat-schema-1p5b/`

Final campaign directory for this step:

`experiments/smarthome_agents/runs/20261005T1445-single-agent-chat-schema-1p5b-validatorfix/`

Summary files in the final directory:

- `summary.csv`
- `summary.md`

Configuration:

- Endpoint: `/v1/chat/completions`.
- Messages: one `system` message with general instructions and one `user` message with resident request and visible state.
- Output contract: exactly one JSON object for `set_light`, `ask_clarification`, or `no_action`.
- Schema-constrained generation: `response_format.type=json_schema`, with nested `json_schema.schema`.
- Temperature: `0`.
- Seeds: `601`, `602`, `603`.
- `max_tokens`: `128`.

Final results:

| Metric | Count |
|---|---:|
| HTTP executions completed | 12/12 |
| Finish reason `stop` | 12/12 |
| Generation limit reached | 0/12 |
| Structured responses valid | 12/12 |
| Actions permitted | 9/12 |
| Actions applied | 9/12 |
| Tasks completed | 9/12 |

The three task failures are all from the ambiguous-room scenario. The model produced valid JSON, but chose `{"action":"set_light","room":"quarto","value":"on"}` instead of asking which room should be changed. After the validator fix, that action is blocked by the scenario's `prohibited_actions`; the home state is not changed and the task is not counted as complete. These are decision errors, not format or transport errors.

Mean request latency was 91.912 s, with observed range 89.142 s to 96.766 s in the final campaign. Temperature zero means the three repetitions primarily test operational stability and deterministic behavior under repeated requests; they do not provide decision diversity.

Manual clarification review did not produce any successful clarification in this campaign, because the model never emitted `ask_clarification` for the ambiguous scenario. The evaluator now requires `missing_field=room`, a question about the missing room/ambiente/comodo, unchanged home state, and no prohibited action match.
