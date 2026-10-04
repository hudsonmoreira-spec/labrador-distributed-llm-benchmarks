#!/usr/bin/env bash
set -u

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
CLIENT="$ROOT/research/runtime/llama.cpp/build-labrador-rpc/bin/llama-cli"
LIBDIR="$ROOT/research/runtime/llama.cpp/build-labrador-rpc/bin"
MODEL="$ROOT/models/qwen2.5-1.5b-instruct-q5_k_m/qwen2.5-1.5b-instruct-q5_k_m.gguf"
RUN_ID=${RPC_REPLICATES_ID:-$(date -u +%Y%m%dT%H%M%SZ)}
OUT="$ROOT/research/data/runs/$RUN_ID/rpc-replicates"
REPS=${RPC_REPLICATES_N:-5}
TIMEOUT_S=${RPC_REPLICATES_TIMEOUT_S:-240}
TOKENS=${RPC_REPLICATES_TOKENS:-64}

HOSTS=(
  192.168.50.42 192.168.50.118 192.168.50.231 192.168.50.74
  192.168.50.44 192.168.50.75 192.168.50.71 192.168.50.241
)

if [[ ! -x "$CLIENT" || ! -f "$MODEL" ]]; then
  echo "missing client or model" >&2
  exit 2
fi

mkdir -p "$OUT"
{
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'utc_start=%s\n' "$(date -u +%FT%TZ)"
  printf 'client=%s\n' "$CLIENT"
  printf 'client_commit=%s\n' "$(git -C "$ROOT/research/runtime/llama.cpp" rev-parse HEAD)"
  printf 'model=%s\n' "$MODEL"
  sha256sum "$MODEL"
  printf 'client_sha256='; sha256sum "$CLIENT" | awk '{print $1}'
  printf 'replicates=%s\n' "$REPS"
  printf 'timeout_s=%s\n' "$TIMEOUT_S"
  printf 'parameters=context=512,threads=4,ngl=99,prompt=Generate a short sentence about distributed computing.,tokens=%s\n' "$TOKENS"
} > "$OUT/manifest.txt"

rpc_list() {
  local n=$1 out=() i
  for ((i=0; i<n; i++)); do out+=("${HOSTS[$i]}:50052"); done
  local IFS=,
  printf '%s' "${out[*]}"
}

snapshot_hosts() {
  local label=$1
  : > "$OUT/hosts-$label.tsv"
  local h free listen
  for h in "${HOSTS[@]}"; do
    free=$(ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" "free -m | awk 'NR==2{print \$2,\$3,\$7}'" 2>/dev/null || echo unavailable)
    listen=$(ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" "ss -lnt 2>/dev/null | grep -q ':50052 ' && echo listening || echo not-listening" 2>/dev/null || echo unreachable)
    printf '%s\t%s\t%s\n' "$h" "$free" "$listen" >> "$OUT/hosts-$label.tsv"
  done
}

run_case() {
  local rep=$1 n=$2 label="rep-${rep}-rpc-${n}" log="$OUT/rep-${rep}-rpc-${n}.log"
  local timing="$OUT/rep-${rep}-rpc-${n}.time" status="$OUT/rep-${rep}-rpc-${n}.status"
  local args=("-m" "$MODEL" "-ngl" "99" "-c" "512" "-t" "4" "-n" "$TOKENS" "-p" "Generate a short sentence about distributed computing." "--no-display-prompt")
  if (( n > 0 )); then args+=("--rpc" "$(rpc_list "$n")"); fi
  {
    echo "case=$label"
    echo "rpc_hosts=$n"
    echo "started_utc=$(date -u +%FT%TZ)"
    /usr/bin/time -p timeout --foreground -k 10s "$TIMEOUT_S" env LD_LIBRARY_PATH="$LIBDIR" "$CLIENT" "${args[@]}"
    echo "command_exit=$?"
    echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$log" 2>&1
  awk '/^(real|user|sys) /{print}' "$log" > "$timing"
  if grep -q 'command_exit=0' "$log" && grep -Eq 'tokens/s|t/s' "$log"; then
    echo success > "$status"
  else
    echo failed_or_timeout > "$status"
  fi
}

snapshot_hosts initial
for ((rep=1; rep<=REPS; rep++)); do
  for n in 0 2 4 6; do
    run_case "$rep" "$n"
  done
  snapshot_hosts "rep-${rep}-after"
  printf 'completed_rep=%s utc=%s\n' "$rep" "$(date -u +%FT%TZ)" >> "$OUT/progress.log"
done
printf 'utc_end=%s\n' "$(date -u +%FT%TZ)" >> "$OUT/manifest.txt"
echo "$OUT"
