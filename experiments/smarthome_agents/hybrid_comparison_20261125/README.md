# Supplementary rules-first comparison — 25 November 2026

This experiment addresses Reviewer 3's request for a rules-first controller with language-model fallback. It is distinct from the earlier intent-classification-plus-rules notebook demonstration. It does not replace the original paper's quality or replication results.

## Frozen design

Conditions: original finite rules; original Qwen2.5-0.5B-Instruct Q5_K_M; original rules followed by the same 0.5B model only when the grammar does not recognise the request. The original `rule_response` has a single `no_action` branch meaning unrecognised. That branch triggers fallback; it is not an independently recognised invalid-request detector. Recognised clarification/actions are returned as-is, without retrying after executor blocking. Unsupported requests may therefore reach the model. No new rejection heuristic was tuned on the comparison set.

Each controller receives only request, initial virtual state and permissions. Scenario labels and evaluator criteria remain in the notebook coordinator and are used only after receiving a proposal. The original simulator, executor and conservative evaluator remain unchanged. Newly pending semantic judgments remain pending; no human judgments are invented or copied into the new results.

The eight existing development cases were run once per condition (24 attempts) to check routing and deployment, without changing the controller in response to their quality scores. The 40 existing authored scenarios are then repeated twice per condition (240 new attempts). These are known, previously inspected scenarios, not an unseen held-out evaluation. The comparison is descriptive and supplementary; limitations of the small authored workload remain.

`development/plan_before_dispatch.json` and `comparison/plan_before_dispatch.json` store complete task plans, deterministic random order, seeds, assignment and code/data hashes before inference. Model and runtime settings are identical between model-only and fallback: original English prompt and JSON-schema response format, seed801/802, temperature0, cache_promptfalse, max128, CPU, four compute/batch threads, context512, one slot.

## Infrastructure and measurement

Five primary Labradors (lab1, lab2, lab3, lab7, lab8) execute serial queues, one active comparison request per board. Lab4 and lab6 are idle reserves. The excluded host192.168.50.141 is never selected. All model profiles were validated in `../cluster_ready_20261125/`. Each SBC runs the same HTTP comparison wrapper on19121, using the model on local loopback19115. Rules also execute on the SBC. The notebook times the complete HTTP response and then evaluates virtual execution. Thus all three new conditions share the wrapper, but their latency path differs from the original direct-HTTP experiment. Do not claim a speedup over the old paper's latency from this new measurement.

Conditions are randomly interleaved with a fixed order seed. The three conditions for a scenario/repetition share an assigned board; repetitions use different boards. Models remain resident; OS caches are not cleared, and no sustained-load or energy experiment is claimed. SSH readiness checks occur outside timed dispatch. Users were asked not to run manual tests concurrently.

A failed preparation may switch to an unused verified reserve before dispatch. A failed/timed-out dispatched inference is saved and not silently replayed. The endpoint is quarantined for later tasks, which may move to a reserve; any reassignment is logged. If no reserve is available the remaining work blocks rather than silently disappearing. No original results are overwritten. This is not migration of an inference already in progress.

## Artifacts and verification

- `controller.py`: routing and SBC HTTP wrapper; no evaluator input.
- `test_controller.py`: routing and unchanged model-payload checks.
- `deploy.py`, `deployment.json`: byte-identical wrapper/original module deployment across seven boards.
- `run.py`: plan-first, append-only runner.
- `development/`, `comparison/`: planned tasks, dispatches, exact operational requests, raw wrapper/model replies, executor outcomes, evaluation and summaries.
- `audit.py`: independently reconstructs routing, requests, final states and evaluation; checks frozen hashes and absence of evaluator fields in dispatch.

Aggregate success requires the complete task, not just valid JSON or a correct light among extra actions. Pending manual judgments receive no success credit. Latencies include all successfully dispatched requests regardless of decision correctness. Report infrastructure failures separately. Counts are repeated observations of40 scenarios, not240 independent scenarios.
