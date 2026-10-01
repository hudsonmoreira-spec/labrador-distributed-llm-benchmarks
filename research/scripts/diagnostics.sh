#!/usr/bin/env bash
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
RUN=$(find "$ROOT/data/runs" -mindepth 1 -maxdepth 1 -type d -printf '%T@ %p\n' 2>/dev/null | sort -nr | head -1 | cut -d' ' -f2-)
[ -n "$RUN" ] || { echo 'Nenhuma descoberta encontrada' >&2; exit 1; }
mkdir -p "$RUN/diagnostics"
diag_one() {
  h="$1"
  [ -z "$h" ] && return
  timeout 12s ping -c 5 -W 2 "$h" > "$RUN/diagnostics/ping_$h.txt" 2>&1 || true
  timeout 12s ssh -n -T -o BatchMode=yes -o StrictHostKeyChecking=yes -o UserKnownHostsFile="$ROOT/data/ssh/known_hosts" -o ConnectTimeout=4 caninos@"$h" 'date -u +%FT%TZ; uptime; command -v stress-ng || true; command -v memtester || true; command -v iperf3 || true' > "$RUN/diagnostics/remote_$h.txt" 2>&1 || true
}
export RUN ROOT
export -f diag_one
tr '\n' '\0' < "$ROOT/config/hosts.txt" | xargs -0 -r -n1 -P4 bash -c 'diag_one "$0"'
date -u +%FT%TZ > "$RUN/diagnostics/end_utc"
echo "$RUN"
