# Working revision response — updated 24 November 2026

This is an internal response checklist, not an uploaded camera-ready version. Original scientific records, 240 quality attempts and 108 replication attempts are unchanged. The separate prompt diagnostic uses only the eight existing development cases; its results cannot replace reserved-set scores.

| Review concern | Revision and evidence | Status |
|---|---|---|
| Four clarification judgments require human review | Four explicit author assessments saved with rationale, timestamps and source hashes in `author_review_20261124/assessment.json`; all four confirm failure to ask the missing room. Single-author, non-blinded assessment; not independent inter-rater agreement. Historical assisted ledger and all original metrics preserved. | Completed; 0/4 adequate clarifications; no new success credit |
| Explain 1.5B failure on clear instructions | State 0/16 and the distinction between correct target state and exact proposed steps/preservation. Completed 24 development-only requests: original English 1/8, Portuguese 3/8, Portuguese plus two examples 4/8; all structurally valid. This does not replace reserved scores; host reassignment and instrumentation interruptions are disclosed. | Exploratory result added; independent confirmation remains future work |
| Show prompt and describe constraints | Print the complete original system prompt. Original request records already include JSON-schema response format; grammar constraints are not presented as a new intervention. Runtime source handling located in server-common.cpp/server-task.cpp. | Draft revised |
| Describe architecture and network | Notebook Python client/evaluator, HTTP/IPv4 over Ethernet; independent complete replicas, no sharding or collaboration within a decision. Ethernet confirmed by Hudson. | Draft revised |
| Explain input and local execution | Text-only measured path; offline availability and local request handling motivate deployment. No measured privacy guarantee or cloud comparison claimed. | Draft revised |
| Discuss practical latency | Explicitly describe 36.848 s / 94.663 s medians as an obstacle to interactive control. Smaller/distilled models, shorter prompts, caching and acceleration remain proposed interventions, not measured speedups. | Draft revised |
| Limited scope of authored two-light tasks | Limit conclusions to 40 constructed request/state combinations; do not generalize to homes, users, real actuators or safety. | Draft revised |
| Replication and unusually large rules/min rate | Condense replication results, distinguish fixed closed batches from capacity, omit rules/min from the main comparison because 9–11 ms windows amplify instrumentation effects. Preserve raw records. | Draft revised |
| Rules-first hybrid | Discuss as a candidate requiring its own rejection/preservation evaluation; rules rejecting a request cannot alone identify whether it is invalid or an unfamiliar paraphrase. | Discussion revised; no hybrid evaluation claimed |
| Presentation and organization | Separate syntax, proposals, executor intervention and task success; retain concise tables and representative cases; explain methodological relation to related work without incomparable numerical rankings. | Draft revised |

## Integrity and validation

`verify_failure_review.py` passed after editing the separate working copy: 498 scientific input hashes, 240 quality attempts, 18 deterministic outputs; historical four assisted reviews remain unchanged; four subsequent author assessments now resolve the semantic-review pendency in the working revision. The revised PDF compiles to five pages and all five pages were visually checked. On 24 November, the author-assessment verifier passed, all 8 persistence/hybrid-rule tests passed, and the updated five-page PDF was rendered and visually checked again. Further additions require recompile and visual review.

## Submission status

No EDAS upload has been performed. This revision and its separate evidence are being released to the research branch with the author-assessment update. A possible title change from “Replication” to “Parallel Replicas” needs alignment with submission metadata and any current conference restrictions. The clarification assessment is complete. Final author/professor approval, conference requirements and the remaining reviewer checklist must still be checked before any submission; this commit is not an EDAS upload.

## Author-assessment procedure

Hudson explicitly submitted four judgments on 24 November 2026. He reports forming his own interpretations and comparing them with assistant explanations; assistant-suggested wording was used in the rationales. We describe author assessment, not blinded validation or agreement between independent raters. The finding is 0/4 informative questions among these four selected records, not a new overall-model estimate. The primary scores (42/80, 30/80, 12/80) are unchanged. The additional interactive tests are exploratory and are not merged into the reserved results.
