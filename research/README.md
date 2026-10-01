# Labrador Cluster Inventory

This repository contains read-only discovery and lightweight diagnostics for the Labrador testbed. Discovery does not run inference, install packages, start services, reboot boards, or perform destructive tests.

## Reproduction

```bash
./scripts/discover.sh
./scripts/diagnostics.sh
python3 scripts/build_reports.py
```

Hosts are listed in `config/hosts.txt`. Raw data is stored in `data/runs/<UTC>/hosts/` and `data/runs/<UTC>/controller/`; each host has `metadata.txt`, `raw.txt`, and `error.txt`. The `known_hosts` file used during collection is stored in `data/ssh/` and contains no private keys.

The default configuration uses user `caninos`, `ConnectTimeout=6`, `ServerAliveInterval=5`, `ServerAliveCountMax=1`, non-interactive mode, and up to four concurrent connections. Remote discovery uses read-only commands and `sudo -n`; a failure does not block the other hosts.

Short diagnostics should be run after discovery and do not replace long-running benchmarks. The final report and selection are stored in `reports/`.
