# Complementary failure analysis (2026-10-28)

Post-hoc aggregation of frozen checks, not a new evaluator or causal classification. No success is newly awarded. Unit: one attempt per grouped criterion; indicators overlap and must not be summed.

## Totals

| Condition | Success/80 | Clarifications proposed/correct | Provisional assisted failures |
|---|---:|---:|---:|
| rules | 42/80 | 2/2 | 0 |
| 05 | 30/80 | 12/0 | 4 |
| 15 | 12/80 | 0/0 | 0 |

## Failed attempts by criterion

| Criterion | Rules | 0.5B | 1.5B |
|---|---:|---:|---:|
| operational | 0/80 observed (0 absent; 0 provisional) | 0/80 observed (0 absent; 0 provisional) | 0/80 observed (0 absent; 0 provisional) |
| format | 0/80 observed (0 absent; 0 provisional) | 0/80 observed (0 absent; 0 provisional) | 0/80 observed (0 absent; 0 provisional) |
| expected_action | 14/32 observed (48 absent; 0 provisional) | 28/32 observed (48 absent; 0 provisional) | 30/32 observed (48 absent; 0 provisional) |
| expected_steps | 24/48 observed (32 absent; 0 provisional) | 18/48 observed (32 absent; 0 provisional) | 38/48 observed (32 absent; 0 provisional) |
| final_state | 24/48 observed (32 absent; 0 provisional) | 18/48 observed (32 absent; 0 provisional) | 22/48 observed (32 absent; 0 provisional) |
| preservation | 0/64 observed (16 absent; 0 provisional) | 8/64 observed (16 absent; 0 provisional) | 14/64 observed (16 absent; 0 provisional) |
| clarification | 0/2 observed (78 absent; 0 provisional) | 12/12 observed (68 absent; 4 provisional) | 0/0 observed (80 absent; 0 provisional) |
| no_action | 38/54 observed (26 absent; 0 provisional) | 4/4 observed (76 absent; 0 provisional) | 20/22 observed (58 absent; 0 provisional) |
| executor_permission | 0/80 observed (0 absent; 0 provisional) | 14/80 observed (0 absent; 0 provisional) | 12/80 observed (0 absent; 0 provisional) |
| prohibited_steps | 0/80 observed (0 absent; 0 provisional) | 26/80 observed (0 absent; 0 provisional) | 24/80 observed (0 absent; 0 provisional) |

## Grouping and applicability

Selectors ending in `:` use startswith; every other selector uses exact equality. A group fails if ANY matching check fails; absent matching checks yield `absent`, never `passed`. Counts include observed, passed, failed, absent and provisional_failed. Multiple failed paths in a group count once. Operational/format indicators use explicit recorded fields, documented in summary.json.

- **expected_action**: `['expected_action']`. Only ambiguity/invalid cases: study.evaluate deliberately exempts set_light/set_lights wrappers; step equivalence is assessed separately.

- **expected_steps**: `['exact_proposed_steps']`. Clear/paraphrase/routine: sorted (room,value) steps must equal expected_steps, with no omissions/extras; single-action/one-step-plan wrappers equivalent.

- **final_state**: `['final:']`. Any final_state_equals path differs; only clear/paraphrase/routine. Does not count unchanged paths.

- **preservation**: `['unchanged:']`. Any unchanged path differs. Clear/paraphrase preserve unrelated light; ambiguity/invalid preserve both; routine has no unchanged light.

- **clarification**: `['clarification_allowed', 'clarification_missing_field']`. Only when ask_clarification was proposed: allowed in scenario AND question requests expected missing field. Pending semantic checks are not automatic passes; four assisted failure judgments remain provisional.

- **no_action**: `['no_action_policy']`. Only when no_action was proposed: no_action_is_success must be true (invalid requests). Failure means an undue no_action, including ambiguity needing clarification.

- **executor_permission**: `['action_allowed']`. Returned permission allowed=false. Intervention is not an independent causal explanation or a correction of a wrong proposal.

- **prohibited_steps**: `['prohibited:', 'no_prohibited_plan_steps']`. Union of legacy top-level prohibited: checks and plan-aware no_prohibited_plan_steps; top-level check alone can miss a set_lights wrapper. No-prohibited check exists even with an empty prohibited set; observed pass is not evidence of a prohibition challenge.

`smarthome_pilot.evaluate_scenario` defines final/unchanged, top-level prohibition, conditional clarification and no_action checks. `study_v1.evaluate` adds exact step equality, non-light expected action and plan-aware prohibited steps. These are correlated contractual checks, not independent causes. A blocked wrong proposal remains a proposal error. no_action is correct for invalid requests, incorrect for valid commands and missing-room requests.

Raw pending clarification checks and all four ledger entries are retained in attempts.json. Counts treating them as unsuccessful follow the existing published totals, provisionally. If all four were accepted, 0.5B success would become 34/80; clarification-check failures 8/12 rather than 12/12; ambiguity success 4/16 rather than 0/16. Nothing is regraded here.

## Files and reproduction

Run from repository root: `python3 experiments/smarthome_agents/scripts/analyze_failure_criteria.py`. Optional `--out` and `--tex-out` permit temporary reconstruction. `criteria_by_attempt.csv` links every check group to summary.json; attempts.json preserves exact checks and review details. criteria_by_condition.csv gives denominators, categories.csv groups two repetitions per scenario (8 scenarios, 16 attempts per category). examples.json preserves all original requests, outputs, state, permission and failed checks. Paper excerpts retain original Portuguese text; full JSON is in examples.json.

Command-level action_steps.csv and action_summary.json are reconstructed in memory and compared exactly, separately from attempt indicators. Existing attempts/categories/failure inventory/metrics are cross-checked. Inputs are hashed in input_manifest.json; all 18 frozen hashes verified. No network or inference is used.

## Illustrative examples


### rules-held-paraphrase-01-rep1-169

Source: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/rules-held-paraphrase-01-rep1-169/summary.json`; raw HTTP: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/rules-held-paraphrase-01-rep1-169/response.txt`

Request: Por favor, deixe a luz da sala ligada.

Recorded output: `{"action":"no_action","reason":"Pedido fora das regras explícitas."}`

Executor: `{"allowed": true, "reason": "allowed"}`; final state: `{"known_location": null, "rooms": {"quarto": {"light": "on"}, "sala": {"light": "off"}}}`

Failed checks: `['final:rooms.sala.light', 'no_action_policy', 'exact_proposed_steps']`. Full expected/initial state and assisted status: examples.json.


### 05-held-ambiguity-01-rep1-169

Source: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/05-held-ambiguity-01-rep1-169/summary.json`; raw HTTP: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/05-held-ambiguity-01-rep1-169/response.txt`

Request: Ligue a luz, por favor.

Recorded output: `{"action":"set_light","room":"sala","value":"on"}`

Executor: `{"allowed": false, "policy": "room_evidence_v1", "reason": "insufficient_room_information"}`; final state: `{"known_location": null, "rooms": {"quarto": {"light": "on"}, "sala": {"light": "off"}}}`

Failed checks: `['action_allowed', "prohibited:{'action': 'set_light', 'room': '*', 'value': '*'}", 'expected_action', 'no_prohibited_plan_steps']`. Full expected/initial state and assisted status: examples.json.


### 05-held-ambiguity-03-rep1-240

Source: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/05-held-ambiguity-03-rep1-240/summary.json`; raw HTTP: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/05-held-ambiguity-03-rep1-240/response.txt`

Request: Quero a luz acesa.

Recorded output: `{"action":"ask_clarification","missing_field":"room","question":"Quero a luz acender."}`

Executor: `{"allowed": true, "reason": "allowed"}`; final state: `{"known_location": null, "rooms": {"quarto": {"light": "on"}, "sala": {"light": "off"}}}`

Failed checks: `['clarification_missing_field']`. Full expected/initial state and assisted status: examples.json.


### 15-held-clear-01-rep1-240

Source: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/15-held-clear-01-rep1-240/summary.json`; raw HTTP: `experiments/smarthome_agents/runs/20261006-study-v1-quality/attempts/15-held-clear-01-rep1-240/response.txt`

Request: Ligue a luz na sala.

Recorded output: `{"action":"set_lights","steps":[{"action":"set_light","room":"sala","value":"on"},{"action":"set_light","room":"quarto","value":"off"}]}`

Executor: `{"allowed": true, "reason": "allowed"}`; final state: `{"known_location": null, "rooms": {"quarto": {"light": "off"}, "sala": {"light": "on"}}}`

Failed checks: `['unchanged:rooms.quarto.light', 'exact_proposed_steps']`. Full expected/initial state and assisted status: examples.json.
