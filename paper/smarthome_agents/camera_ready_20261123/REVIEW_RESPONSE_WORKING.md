# Working revision response — updated 24 November 2026

This is an internal response checklist, not an uploaded camera-ready version. Original scientific records, 240 quality attempts and 108 replication attempts are unchanged. The separate prompt diagnostic uses only the eight existing development cases; its results cannot replace reserved-set scores.

| Review concern | Revision and evidence | Status |
|---|---|---|
| Four clarification judgments require human review | Four explicit author assessments saved with rationale, timestamps and source hashes in `author_review_20261124/assessment.json`; all four confirm failure to ask the missing room. Single-author, non-blinded assessment; not independent inter-rater agreement. Historical assisted ledger and all original metrics preserved. | Completed; 0/4 adequate clarifications; no new success credit |
| Explain 1.5B failure on clear instructions | State 0/16 and the distinction between correct target state and exact proposed steps/preservation. Completed 24 development-only requests: original English 1/8, Portuguese 3/8, Portuguese plus two examples 4/8; all structurally valid. Added controlled notebook replay of the eight original development requests: identical response text/JSON in 8/8, success 1/8 on both platforms, median HTTP 78.48 s on SBCs and 9.48 s on notebook. Same model hash, runtime commit and inference settings; architecture/compiler/transport/time limitations disclosed. This does not replace reserved scores or isolate a unique cause. | Prompt diagnostic and hardware replay added; no general model-size conclusion |
| Show prompt and describe constraints | Print the complete original system prompt. Original request records already include JSON-schema response format; grammar constraints are not presented as a new intervention. Runtime source handling located in server-common.cpp/server-task.cpp. | Draft revised |
| Describe architecture and network | Notebook Python client/evaluator, HTTP/IPv4 over Ethernet; independent complete replicas, no sharding or collaboration within a decision. Ethernet confirmed by Hudson. | Draft revised |
| Explain input and local execution | Text-only measured path; offline availability and local request handling motivate deployment. No measured privacy guarantee or cloud comparison claimed. | Draft revised |
| Discuss practical latency | Explicitly describe 36.848 s / 94.663 s medians as an obstacle to interactive control. Smaller/distilled models, shorter prompts, caching and acceleration remain proposed interventions, not measured speedups. | Draft revised |
| Limited scope of authored two-light tasks | Limit conclusions to 40 constructed request/state combinations; do not generalize to homes, users, real actuators or safety. | Draft revised |
| Replication and unusually large rules/min rate | Condense replication results, distinguish fixed closed batches from capacity, omit rules/min from the main comparison because 9–11 ms windows amplify instrumentation effects. Preserve raw records. | Draft revised |
| Rules-first hybrid | Separate rules-first0.5B fallback controller completed24 development and240 comparative executions on the known40-scenario set: rules42/80, model30/80, hybrid44/80; hybrid used54/80 model calls but rejected0/16 invalid requests versus16/16 for rules. Frozen plans, raw evidence, reassignment and audits are in `hybrid_comparison_20261125/`. | Implemented in Method III-E, Results IV-D/Table V, discussion, abstract and conclusion; immutable supplementary evidence cited |
| Presentation and organization | Separate syntax, proposals, executor intervention and task success; retain concise tables and representative cases; explain methodological relation to related work without incomparable numerical rankings. | Draft revised |

## Integrity and validation

`verify_failure_review.py` passed after editing the separate working copy: 498 scientific input hashes, 240 quality attempts, 18 deterministic outputs; historical four assisted reviews remain unchanged; four subsequent author assessments now resolve the semantic-review pendency in the working revision. The revised PDF compiles to five pages and all five pages were visually checked. On 24 November, the author-assessment verifier passed, all 8 persistence/hybrid-rule tests passed, and the updated five-page PDF was rendered and visually checked again. Further additions require recompile and visual review.

## Submission status

No EDAS upload has been performed. This revision and its separate evidence are being released to the research branch with the author-assessment update. Hudson approved replacing “Replication” with “Parallel Replicas” on 25 November; the manuscript is updated. Alignment with conference metadata remains pending. The clarification assessment is complete. Final author/professor approval, conference requirements and the remaining reviewer checklist must still be checked before any submission; this commit is not an EDAS upload.

## Author-assessment procedure

Hudson explicitly submitted four judgments on 24 November 2026. He reports forming his own interpretations and comparing them with assistant explanations; assistant-suggested wording was used in the rationales. We describe author assessment, not blinded validation or agreement between independent raters. The finding is 0/4 informative questions among these four selected records, not a new overall-model estimate. The primary scores (42/80, 30/80, 12/80) are unchanged. The additional interactive tests are exploratory and are not merged into the reserved results.

## Audit against the acceptance email — 24 November 2026

The acceptance notification dated 22 November was reread in full, including all five reviews. Acceptance is explicit; oral/poster assignment remains undecided. The message includes reviewer comments, not a separate list declaring every suggested experiment a formal condition of acceptance.

Confirmed in the draft/evidence: four explicit author judgments; 24 exploratory requests comparing original, Portuguese and Portuguese-plus-examples prompts; full original prompt; original schema-constrained generation clarified; Ethernet/HTTP/text-only architecture; local-execution rationale; practical latency discussion; condensed replica results and removal of the misleading rules/min comparison; clearer abstract/conclusion and scope limits.

At that audit date, two content decisions remained (item 1 is now completed by the supplementary experiment and manuscript integration below):

1. Reviewer 3 explicitly asks to evaluate rules-first control with model fallback. The current intent-plus-rules notebook prototype and its targeted development tests do not constitute that matched evaluation. Either perform a separate, clearly defined rules-first comparison or explicitly explain its deferral and retain it as an unresolved reviewer request; discussing it alone does not complete the requested experiment.
2. Reviewer 3 recommends “Parallel Replicas” instead of “Replication” in the title. At the audit date the title was unchanged. On 25 November Hudson approved the suggestion, now implemented in the manuscript. EDAS metadata alignment remains pending.

The larger user-written workload, more devices and varied initial states were not implemented. Their limits and future-work status are disclosed; this addresses scope in writing, not the requested expansion experimentally. Similarly, sustained load was not measured; the reviewer offered condensation as an alternative, which the draft implements. The original request already used JSON-schema-constrained decoding, so no new GBNF experiment is claimed.

The prior conversational statement that only final approval/upload remained was too broad. The two decisions above must be closed or explicitly justified before the final response is considered complete. No new action or deadline requirement beyond the email was inferred.

## 25 November: interpreting the 1.5B result

The discussion now combines the existing prompt diagnostic (1/8 original, 3/8 Portuguese, 4/8 Portuguese plus examples) with the controlled notebook replay (8/8 identical outputs, 1/8 task success on each platform). This directly addresses Reviewers 1 and 3 concerning prompt/setup effects, and Reviewer 2 concerning poor performance and possible improvements. Faster notebook responses did not improve correctness in these eight cases. The article makes no claim that board hardware is universally irrelevant, that the 1.5B model is intrinsically inferior, or that the cause has been isolated. Raw evidence is in `experiments/smarthome_agents/revision_20261123/hardware_comparison/pc_exact_replay_v1/`. This addition does not resolve the separate rules-first fallback request or the title decision.

## 25 November: rules-first comparison completed

See `experiments/smarthome_agents/hybrid_comparison_20261125/REPORT.md`. All240 comparative executions and24 development executions completed without dispatched infrastructure failures. Hybrid44/80 versus rules42/80 and model30/80; model calls54/80. Invalid-request rejection is0/16 for hybrid versus16/16 for rules. This is a descriptive comparison on known authored cases, with two pre-dispatch host substitutions. Eight automatic semantic flags exactly match original request/response evidence already rejected by the author; the cross-reference adds no success credit and does not claim new independent review. The experiment and manuscript integration are complete. Method III-E, Results IV-D/Table V, discussion, abstract and conclusion report the comparison and its limitations. Citation [9] points to immutable evidence snapshot 4cfbb483ddb5b53201c73c7f48f73cee03a85615. The title decision is now resolved as recorded below; metadata alignment and final author/conference checks remain.

## Final verification — 25 November 2026

All 240 comparison and 24 development attempts were reconstructed offline again; three controller routing tests passed. The final five-page PDF was rendered and visually inspected, with the complete original system prompt and all five tables preserved. No unresolved references or overfull boxes were reported. The original submitted PDF and frozen study outputs were not modified. This release is a Git update, not an EDAS upload.

## Title suggestion implemented — 25 November 2026

Hudson approved Reviewer 3's suggested wording. The working manuscript now reads “Simulated Smart-Home Control with Small Language Models on SBCs: Task Success, Latency, and Parallel Replicas”. The wording identifies complete model copies serving independent requests in parallel. The original submitted manuscript remains preserved. Conference/EDAS metadata was not changed in this step.

## Separate response completed — 25 November 2026

RESPONSE_TO_REVIEWERS_EN.tex/pdf is the prepared point-by-point response for author/professor review, based on a fresh reading of all five reviews in the 22 November acceptance message. It contains 18 response items with manuscript locations, completed experiments, and explicit explanations for unperformed workload expansion/sustained-load tests. This checklist remains an internal history; the separate document has not been uploaded or sent.
