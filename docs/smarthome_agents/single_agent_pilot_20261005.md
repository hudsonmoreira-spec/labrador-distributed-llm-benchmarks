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
