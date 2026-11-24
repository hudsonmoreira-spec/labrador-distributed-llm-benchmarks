# Exploratory prompt diagnostic — 23 November 2026

This separate follow-up reuses eight existing DEVELOPMENT cases, one repetition each. It does not replace or regrade any of the original 240 reserved quality attempts. Prompts/assignments were recorded before dispatch. Qwen2.5-1.5B-Instruct Q5_K_M, original audited b9584 runtime, CPU 4 threads, ctx512, max128, seed801, temperature0, no prompt caching, original JSON schema throughout.

| Instructions | Success | Clear instructions | Valid structure | Median HTTP latency | Prompt tokens |
|---|---|---|---|---|---|
| original_en | 1/8 | 0/3 | 8/8 | 78.5 s | 123–133 |
| pt_zero_shot | 3/8 | 2/3 | 8/8 | 93.2 s | 160–170 |
| pt_two_examples | 4/8 | 3/3 | 8/8 | 124.0 s | 272–282 |

English baseline uses the unchanged original system prompt. Portuguese zero-shot translates/explicates the same policy. Portuguese two-example adds one off-command example and one missing-room clarification example; their phrasings differ from development requests. See the original frozen plan for exact text.

## Limits and interruptions

The initial campaign stopped two host queues after SSH memory-snapshot timeouts. It retained 18 completed inference records. The first resume ran no inference because lab8 became unreachable. Six missing requests were then resumed, preserving prompts and settings. Three originally assigned to lab8 were reassigned to lab2. Host reassignment, single repetition, and development reuse preclude causal attribution, generalization or a validated model ranking. No new six-board scaling measurement was made. Missing memory instrumentation is disclosed rather than reconstructed.

All 24 unique planned requests are checked by summarize_prompt_diagnostic.py; completed records are never overwritten. Existing port8080 services are preserved; temporary supplementary servers were stopped on reachable hosts after use. Server cleanup on the unreachable lab8 cannot be verified until connectivity returns.

These observations test configuration sensitivity; they do not establish a size-dependent explanation of the original 1.5B result or validate a rules-first hybrid. The four original assisted clarification judgments remain a separate human-review requirement.
