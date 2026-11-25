# Readiness check — 25 November 2026

Ethernet network 192.168.50.0/24; notebook 192.168.50.1. Hosts identified by end0 MAC, not cloned hostname alone.

| Board | IP | Readiness |
|---|---|---|
| lab2 | 192.168.50.89 | Verified runtime/model hashes, 0.5B inference smoke passed, original 1.5B service healthy |
| lab3 | 192.168.50.169 | Verified runtime/model hashes, 0.5B inference smoke passed, original 1.5B service healthy |
| lab7 | 192.168.50.240 | Verified runtime/model hashes, 0.5B inference smoke passed, original 1.5B service healthy |

These boards have four ARM64 cores, approximately 1.89 GiB RAM, about 1.56–1.58 GiB available at inspection and 100 Mbps Ethernet link. Both original model files are installed. SHA-256 of the 0.5B Q5_K_M and llama-server binary matched the study. The temporary 0.5B runtime used localhost port 19120, context512, four threads, CPU and a one-token request; generation worked on each board. This verifies execution, not task accuracy or long-run stability. All temporary processes stopped; original port8080 services were preserved and returned healthy.

Lab4 (.85) accepts TCP22 connections but SSH login did not complete on two attempts; not considered ready. Lab1 (.129), lab6 (.200), original lab8 (.195), and original lab5 (.54) were not found as reachable prepared study hosts in the subnet scan. Other accessible boards with repeated hostnames lack the study runtime/models. Hosts .91/.141 timed out after discovery; .96 did not accept key authentication. No physical failure is inferred from missing connectivity.

The existing interactive console remains configured for lab4 (.85); no console reconfiguration was performed by this inspection. The available original study boards store the 0.5B model under study_v1/models, whereas the console's reserve path points to revision_20261123_backup/models. Use the correct model path when preparing the hybrid comparison.

Raw inventory and smoke records are retained here, separately from research results. No benchmark battery, paper edit, commit or push was performed in this check.
