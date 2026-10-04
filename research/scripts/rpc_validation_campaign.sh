#!/usr/bin/env bash
set -u

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
CLIENT="$ROOT/research/runtime/llama.cpp/build-labrador-rpc/bin/llama-cli"
LIBDIR="$ROOT/research/runtime/llama.cpp/build-labrador-rpc/bin"
MODEL="$ROOT/models/qwen2.5-1.5b-instruct-q5_k_m/qwen2.5-1.5b-instruct-q5_k_m.gguf"
RUN_ID=${RPC_VALIDATION_ID:-$(date -u +%Y%m%dT%H%M%SZ)}
OUT="$ROOT/research/data/runs/$RUN_ID/rpc-validation"
TIMEOUT_S=${RPC_VALIDATION_TIMEOUT_S:-240}
N_PREDICT=${RPC_VALIDATION_N:-32}
PROMPT='Write exactly one short sentence about distributed computing.'
HOSTS=(192.168.50.42 192.168.50.118)
REMOTE_LOG_DIR=/tmp

if [[ ! -x "$CLIENT" || ! -f "$MODEL" ]]; then
  echo "missing client or model" >&2
  exit 2
fi
mkdir -p "$OUT"

model_sha=$(sha256sum "$MODEL" | awk '{print $1}')
client_sha=$(sha256sum "$CLIENT" | awk '{print $1}')
source_diff_sha=$(git -C "$ROOT/research/runtime/llama.cpp" diff -- common/CMakeLists.txt vendor/cpp-httplib/CMakeLists.txt | sha256sum | awk '{print $1}')
{
  printf 'run_id=%s\n' "$RUN_ID"
  printf 'utc_start=%s\n' "$(date -u +%FT%TZ)"
  printf 'git_commit=%s\n' "$(git -C "$ROOT" rev-parse HEAD)"
  printf 'llama_source_commit=%s\n' "$(git -C "$ROOT/research/runtime/llama.cpp" rev-parse HEAD)"
  printf 'client=%s\nclient_sha256=%s\n' "$CLIENT" "$client_sha"
  printf 'model=%s\nmodel_sha256=%s\n' "$MODEL" "$model_sha"
  printf 'source_patch_sha256=%s\n' "$source_diff_sha"
  printf 'workers=%s\n' "${HOSTS[*]}"
  printf 'parameters=ctx=512,threads=4,ngl=99,n_predict=%s,prompt=%q,temp=0,seed=42,ignore_eos=true,warmup=false,perf=true,verbose=true,timeout_s=%s\n' "$N_PREDICT" "$PROMPT" "$TIMEOUT_S"
  printf 'runtime_options=client_backend_limit=32; GGML_RPC=ON; worker_artifact=llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp\n'
} > "$OUT/manifest.txt"

remote_snapshot() {
  local label=$1 h
  printf 'utc\tns\tlabel\tip\thost\tpid\tstarttime_ticks\trss_bytes\tutime_ticks\tstime_ticks\tmem_available_kb\tswap_free_kb\trx_bytes\ttx_bytes\n' > "$OUT/hosts-${label}.tsv"
  for h in "${HOSTS[@]}"; do
    ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" \
      "set -u; p=\$(pgrep -o -f 'ggml-rpc-server.*50052' || true); start=; rss=; ut=; st=; [ -n \"\$p\" ] && start=\$(awk '{print \$22}' /proc/\$p/stat 2>/dev/null || true); [ -n \"\$p\" ] && rss=\$(awk '{print \$24*4096}' /proc/\$p/stat 2>/dev/null || true); [ -n \"\$p\" ] && ut=\$(awk '{print \$14}' /proc/\$p/stat 2>/dev/null || true); [ -n \"\$p\" ] && st=\$(awk '{print \$15}' /proc/\$p/stat 2>/dev/null || true); mem=\$(awk '/MemAvailable:/{print \$2}' /proc/meminfo); swap=\$(awk '/SwapFree:/{print \$2}' /proc/meminfo); rx=\$(awk '{iface=\$1; sub(/:/,\"\",iface); if (iface != \"lo\") a+=\$2} END{print a+0}' /proc/net/dev); tx=\$(awk '{iface=\$1; sub(/:/,\"\",iface); if (iface != \"lo\") a+=\$10} END{print a+0}' /proc/net/dev); printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' \"\$(hostname)\" \"\$p\" \"\$start\" \"\$rss\" \"\$ut\" \"\$st\" \"\$mem\" \"\$swap\" \"\$rx\" \"\$tx\"" \
      2>/dev/null | awk -v h="$h" -v l="$label" -v t="$(date -u +%FT%TZ)" -v s="$(date +%s%N)" '{print t"\t"s"\t"l"\t"h"\t"$0}' >> "$OUT/hosts-${label}.tsv" || \
      printf '%s\t%s\t%s\tunreachable\n' "$(date -u +%FT%TZ)" "$h" "$label" >> "$OUT/hosts-${label}.tsv"
  done
}

remote_log_size() {
  local h=$1
  ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" \
    "wc -c < '$REMOTE_LOG_DIR/rpc-pilot-20261004-$h.log' 2>/dev/null || echo 0" < /dev/null 2>/dev/null | tr -d '[:space:]'
}

run_case() {
  local case_id=$1 rpc=$2
  local log="$OUT/${case_id}.log" srvlog="$OUT/${case_id}.server.log"
  local start_offset h
  remote_snapshot "${case_id}-before"
  for h in "${HOSTS[@]}"; do
    start_offset=$(remote_log_size "$h")
    printf '%s\t%s\t%s\n' "$case_id" "$h" "${start_offset:-0}" >> "$OUT/server-offsets.tsv"
  done
  {
    echo "case_id=$case_id"
    echo "rpc=$rpc"
    echo "started_utc=$(date -u +%FT%TZ)"
    /usr/bin/time -p timeout --foreground -k 10s "$TIMEOUT_S" env LD_LIBRARY_PATH="$LIBDIR" \
      "$CLIENT" -m "$MODEL" --rpc "$rpc" --perf --verbose --log-timestamps \
      -ngl 99 -c 512 -t 4 -n "$N_PREDICT" -p "$PROMPT" --temp 0 --seed 42 \
      --ignore-eos --no-warmup --no-display-prompt
    echo "command_exit=$?"
    echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$log" 2>&1
  remote_snapshot "${case_id}-after"
  : > "$srvlog"
  while IFS=$'\t' read -r cid h offset; do
    [ "$cid" = "$case_id" ] || continue
    end=$(remote_log_size "$h")
    printf '\n--- host=%s offset=%s end=%s ---\n' "$h" "$offset" "$end" >> "$srvlog"
    ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" \
      "f='$REMOTE_LOG_DIR/rpc-pilot-20261004-$h.log'; [ -f \"\$f\" ] && tail -c +$((offset + 1)) \"\$f\"" < /dev/null >> "$srvlog" 2>/dev/null || true
  done < "$OUT/server-offsets.tsv"
  awk '/^(real|user|sys) /{print}' "$log" > "$OUT/${case_id}.time"
  if grep -q 'command_exit=0' "$log"; then echo valid > "$OUT/${case_id}.status"; else echo failed_or_incomplete > "$OUT/${case_id}.status"; fi
}

remote_snapshot initial
run_case pilot-2-rpc "${HOSTS[0]}:50052,${HOSTS[1]}:50052"
printf 'utc_end=%s\n' "$(date -u +%FT%TZ)" >> "$OUT/manifest.txt"
echo "$OUT"
