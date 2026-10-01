# Labrador Distributed LLM Benchmarks

Repository of experimental materials for studying distributed language-model inference on a Labrador testbed.

## Current status

The material in [`research/`](research/) covers testbed characterization: inventory, lightweight diagnostics, preliminary node selection, and pilot planning. It does **not yet contain language-model inference benchmark results**.

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

## Publication notice

The artifacts are preserved for auditability, but contain private-network addresses, hostnames, machine identifiers, and known SSH host keys. Before making the repository public or attaching it to a paper, apply the sanitization described in [`docs/ieee/publication-checklist.md`](docs/ieee/publication-checklist.md).
