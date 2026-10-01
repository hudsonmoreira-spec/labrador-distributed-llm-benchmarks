# IEEE Publication Supplement

This directory defines the presentation of the experimental artifact without inventing results that have not yet been measured. Its structure follows a sequence familiar to experimental-paper readers: objective, protocol, environment, data, reproduction, limitations, and evidence.

## Mapping to a paper

| Paper section | Evidence in this repository |
|---|---|
| Experimental environment | `research/reports/inventory_report.md` and `research/data/inventory.csv` |
| Discovery method | `research/scripts/discover.sh` |
| Diagnostics | `research/scripts/diagnostics.sh` and `research/data/runs/*/diagnostics/` |
| Testbed selection | `research/reports/selection.md` |
| Planned protocol | `research/reports/pilot_1_2.md` |
| Failure handling | `research/reports/contingency.md` |
| Primary evidence | `research/data/runs/*/hosts/*/raw.txt` |

The inventory report should be cited as environment characterization, not as a performance result. Throughput, latency, energy, scalability, or quality results should be added only after an explicitly identified experimental run.

## Recommended conventions

- record all timestamps in UTC;
- associate each result with the code commit, model hash, quantization, parameters, and run identifier;
- clearly distinguish configuration, observation, derived metric, and interpretation;
- preserve primary logs and generate tables/figures with versioned scripts;
- report failures, exclusions, and replaced nodes without silently replacing evidence.
