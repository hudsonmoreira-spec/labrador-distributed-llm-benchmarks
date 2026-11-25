# Rules-first hybrid comparison — 25 November 2026

Supplementary experiment on the existing known authored workload. Original study results were not replaced.

## Results

| Controller | Complete-task successes | Success | Model calls | Median HTTP (s) | Mean HTTP (s) | p95 HTTP (s) |
|---|---:|---:|---:|---:|---:|---:|
| Original rules | 42/80 | 52.5% | 0 | 0.006 | 0.007 | 0.007 |
| Qwen 0.5B only | 30/80 | 37.5% | 80 | 23.740 | 23.464 | 27.609 |
| Rules first + Qwen 0.5B fallback | 44/80 | 55.0% | 54 | 21.466 | 15.880 | 27.184 |

All 240 planned attempts completed normally, with structurally valid outputs and zero infrastructure failures after dispatch. The 24 separate development attempts also completed without infrastructure failures.

| Category (16 attempts each) | Rules | Qwen 0.5B | Hybrid |
|---|---:|---:|---:|
| clear | 16/16 | 8/16 | 16/16 |
| paraphrase | 0/16 | 14/16 | 14/16 |
| routine | 8/16 | 8/16 | 12/16 |
| ambiguity | 2/16 | 0/16 | 2/16 |
| invalid | 16/16 | 0/16 | 0/16 |

## Interpretation

The hybrid gained 14 successes over the model alone and 2 over rules in this workload. It retained rule coverage for clear instructions, gained paraphrase coverage from the model and improved routine coverage. However, it lost all 16 correct invalid-request rejections that rules alone achieved: unrecognised requests were delegated without a separate validity classifier. Thus the small aggregate improvement does not establish dominance or practical safety. A grammar rejection is not enough to distinguish a valid paraphrase from an invalid request.

The hybrid avoided 26 of 80 model calls (32.5%). Its mean latency was 15.88 s versus 23.46 s for the model alone, but its median remained 21.47 s and latency on model-routed requests remains high. These measurements do not establish acceptable interactive control. Rules remain much faster.

## Semantic-review references

The unchanged conservative evaluator flagged four clarification outputs for model-only and four for hybrid. All eight exactly match both the original model-request object and response text of cases already rejected explicitly by the author on24 November. `annotation_references.json` maps those duplicates to the four original author-review records and source hashes. No new human or independent review is claimed, and no success credit is added. Raw pending flags are preserved rather than edited; there are zero newly flagged outputs without an exact prior author-assessment reference.

## Deployment and limits

Two primary queues moved before dispatch: lab1(.129) to lab4(.85), and lab8(.195) to lab6(.200). A single readiness check triggered each change; the exact failing subcheck was not retained, so no physical fault is inferred. A subsequent lab1 check was healthy. The plan allowed pre-dispatch replacement; no dispatched inference was silently replayed. Actual assignments are saved per attempt. This reassignment weakens strict within-board pairing for affected observations and is disclosed.

The existing40 scenarios have already been inspected, cover two simulated lights and use two near-deterministic repetitions. They are not unseen data or240 independent scenarios. The original English prompt and schema were unchanged for both model-using conditions; the controller was not tuned on new comparison outcomes. Conditions share a new SBC HTTP wrapper and local model-call path. Absolute latency must not be compared directly with the earlier direct-HTTP study as a measured speedup. OS caches were not cleared, energy and sustained arrivals were not tested, and no real actuators were used.

## Verification

Routing unit tests passed. Offline audits reconstructed all24 development and240 comparison evaluations, confirmed unchanged frozen inputs and operational-only dispatch, and checked every model request against the original prompt/schema/decoding configuration. The historical verifier still passes498 scientific hashes,240 original quality attempts and18 deterministic artifacts. The seven-board post-run health check is recorded separately.

No paper upload, commit or push was performed by this experiment. The result is ready for incorporation into the working manuscript and reviewer response; it does not resolve the separate title decision.
