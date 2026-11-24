# Recovery of the original experimental cluster — 2026-11-23

Read-only discovery used the user-provided 192.168.50.0/24 addresses. Selected boards contain the original study directory and both model files, with matching runtime and model hashes across the five currently available hosts. Hostname alone is insufficient: cloned images reuse names and machine-id. This inventory is evidence of the recovered configuration, not a fresh six-host replication measurement.

| Hostname | Current Ethernet address | end0 MAC | Original study directory |
|---|---|---|---|
| lab1 | 192.168.50.129 | a2:32:dd:a5:08:52 | Present |
| lab2 | 192.168.50.89 | ea:0e:48:7f:0c:1b | Present |
| lab3 | 192.168.50.169 | aa:fa:5a:c3:1d:cb | Present |
| lab7 | 192.168.50.240 | 6a:5a:ed:60:07:55 | Present |
| lab8 | 192.168.50.195 | 3e:b1:de:25:6a:41 | Present |

The original protocol also lists lab5 at 192.168.50.54. That address was unavailable; the current board named lab5 at .142 does not contain the original study/runtime/models, so it has not been assumed to be the missing board. Five boards suffice for the independent development-only diagnostic; no new six-board scaling result is claimed.

Hudson confirmed on 2026-11-23 that all experiment connections used Ethernet. Administration and supplementary HTTP traffic use the Ethernet addresses above. No network configuration has been changed.

## Artifacts

- `inventory/`: per-host discovery and SHA-256 audit records.
- `prompt_diagnostic_v1/`: pre-dispatch plan and original follow-up attempts.
- `resume_prompt_diagnostic.py`: resumes only missing summaries after SSH memory instrumentation failure, preserving all completed records.
- `../../../../paper/smarthome_agents/camera_ready_20261123/`: separate revised working manuscript.

## Integrity

The original quality and replication run directories and frozen scientific scripts are preserved. Existing port-8080 services remain unchanged. Supplementary inference runs on temporary port 19115, and its processes are stopped after the campaign.

## Reservas preparadas

lab4 (192.168.50.85) e lab6 (192.168.50.200), via Ethernet: runtime, bibliotecas e modelos Qwen 0,5B / 1,5B conferidos por SHA-256; carregamento e inferência de um token verificados em ambas as placas e modelos. Ver `backup_pool.json`, `backup_validation/`, `backup_validation_05/` e `BACKUP_OPERATIONS.md`. Não representam novos resultados de qualidade.
