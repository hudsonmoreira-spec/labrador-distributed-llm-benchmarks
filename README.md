# Labrador Distributed LLM Benchmarks

Repository of experimental materials for studying distributed language-model inference on a Labrador testbed.

## Current status

The material in [`research/`](research/) covers testbed characterization and reproducible RPC inference experiments. The completed replicated campaign is documented in [`research/reports/rpc-replicates-20261004.md`](research/reports/rpc-replicates-20261004.md). It validates completed requests for the notebook baseline and 2, 4, and 6 RPC workers, but does not yet prove per-worker tensor/layer participation or provide fully separated timing/token instrumentation.

The new validation attempt is documented in [`research/reports/rpc-validation-20261004.md`](research/reports/rpc-validation-20261004.md). An instrumented two-worker pilot proves effective execution on both workers, including layer assignment and graph operations. The five-repetition A/B/C validation matrix remains incomplete because of worker availability, timeout, and terminal-input failures; those cases are preserved and excluded from aggregates. No new completion percentage is assigned.

Results should be interpreted through three principles: execution traceability, separation of observation from interpretation, and reproducibility. Each run therefore preserves its raw data, UTC timestamps, and the scripts used to generate reports.

## Organization

- [`research/data/runs/`](research/data/runs/) — raw evidence for each run and node;
- [`research/data/`](research/data/) — derived CSV and JSON inventories;
- [`research/reports/`](research/reports/) — reports, preliminary selection, and contingency plan;
- [`research/scripts/`](research/scripts/) — collection and report-generation scripts;
- [`docs/ieee/`](docs/ieee/) — organization, reproducibility, and publication guide for supplementary material.

## Reproduction

```bash
cd research
./scripts/discover.sh
./scripts/diagnostics.sh
python3 scripts/build_reports.py
```

The discovery scripts use read-only commands and `sudo -n`; they do not run inference, install packages, start services, or reboot nodes.

The RPC replication artifacts are under [`research/data/runs/20261004T-replicates-rpc-3/`](research/data/runs/20261004T-replicates-rpc-3/). The run completed 20/20 cases: five notebook-only baselines and five repetitions each with 2, 4, and 6 RPC workers. The current evidence distinguishes a listening server from a worker proven to execute tensors for the same inference; the latter still requires additional instrumentation.

The current validation artifacts are under `research/data/runs/20261004T-pilot2-instrumented-6/` and `research/data/runs/20261004T-matrix-validation-{1..7}/`. Incomplete executions are not treated as valid results.

## Publication notice

The artifacts are preserved for auditability, but contain private-network addresses, hostnames, machine identifiers, and known SSH host keys. Before making the repository public or attaching it to a paper, apply the sanitization described in [`docs/ieee/publication-checklist.md`](docs/ieee/publication-checklist.md).
