#!/usr/bin/env bash
set -u

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)
CLIENT="$ROOT/research/runtime/llama.cpp/build-labrador-rpc/bin/llama-cli"
LIBDIR="$ROOT/research/runtime/llama.cpp/build-labrador-rpc/bin"
MODEL="$ROOT/models/qwen2.5-1.5b-instruct-q5_k_m/qwen2.5-1.5b-instruct-q5_k_m.gguf"
RUN_ID=${RPC_MATRIX_ID:-$(date -u +%Y%m%dT%H%M%SZ)}
OUT="$ROOT/research/data/runs/$RUN_ID/rpc-validation"
REPS=${RPC_MATRIX_REPS:-5}
TIMEOUT_S=${RPC_MATRIX_TIMEOUT_S:-240}
N_PREDICT=${RPC_MATRIX_N:-32}
SKIP_LOCAL=${RPC_MATRIX_SKIP_LOCAL:-0}
SKIP_ARM=${RPC_MATRIX_SKIP_ARM:-0}
ONLY_N=${RPC_MATRIX_ONLY_N:-}
PROMPT='Write exactly one short sentence about distributed computing.'
HOSTS=(192.168.50.42 192.168.50.118 192.168.50.231 192.168.50.74 192.168.50.44 192.168.50.75)
ARM_HOST=192.168.50.118
ARM_DIR=/home/caninos/research/runtime/llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp
REMOTE_LOG_DIR=/tmp

mkdir -p "$OUT"
model_sha=$(sha256sum "$MODEL" | awk '{print $1}')
client_sha=$(sha256sum "$CLIENT" | awk '{print $1}')
patch_sha=$(git -C "$ROOT/research/runtime/llama.cpp" diff -- common/CMakeLists.txt vendor/cpp-httplib/CMakeLists.txt | sha256sum | awk '{print $1}')
{
  printf 'run_id=%s\nutc_start=%s\n' "$RUN_ID" "$(date -u +%FT%TZ)"
  printf 'git_commit=%s\nllama_source_commit=%s\n' "$(git -C "$ROOT" rev-parse HEAD)" "$(git -C "$ROOT/research/runtime/llama.cpp" rev-parse HEAD)"
  printf 'client_sha256=%s\nmodel_sha256=%s\nsource_patch_sha256=%s\n' "$client_sha" "$model_sha" "$patch_sha"
  printf 'workers=%s\narm_baseline_host=%s\n' "${HOSTS[*]}" "$ARM_HOST"
  printf 'parameters=ctx=512,threads=4,ngl=99,n_predict=%s,prompt=%q,temp=0,seed=42,ignore_eos=true,warmup=false,perf=true,verbose=true,timeout_s=%s\n' "$N_PREDICT" "$PROMPT" "$TIMEOUT_S"
  printf 'cache_policy=cold_process_per_case; no model-resident repeat\n'
} > "$OUT/manifest.txt"

write_header() {
  printf 'utc\tns\tlabel\tip\thost\tpid\tstarttime_ticks\trss_bytes\tutime_ticks\tstime_ticks\tmem_available_kb\tswap_free_kb\trx_bytes\ttx_bytes\n'
}

rpc_list() {
  local n=$1 i out=()
  for ((i=0; i<n; i++)); do out+=("${HOSTS[$i]}:50052"); done
  local IFS=,
  printf '%s' "${out[*]}"
}

remote_snapshot() {
  local label=$1 list=${2:-"${HOSTS[*]}"} h
  write_header > "$OUT/hosts-${label}.tsv"
  for h in $list; do
    timeout 15s ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 -o ServerAliveInterval=3 -o ServerAliveCountMax=1 "caninos@$h" \
      "set -u; p=\$(pgrep -o -f 'ggml-rpc-server.*50052' || true); start=; rss=; ut=; st=; [ -n \"\$p\" ] && start=\$(awk '{print \$22}' /proc/\$p/stat 2>/dev/null || true); [ -n \"\$p\" ] && rss=\$(awk '{print \$24*4096}' /proc/\$p/stat 2>/dev/null || true); [ -n \"\$p\" ] && ut=\$(awk '{print \$14}' /proc/\$p/stat 2>/dev/null || true); [ -n \"\$p\" ] && st=\$(awk '{print \$15}' /proc/\$p/stat 2>/dev/null || true); mem=\$(awk '/MemAvailable:/{print \$2}' /proc/meminfo); swap=\$(awk '/SwapFree:/{print \$2}' /proc/meminfo); rx=\$(awk '{i=\$1; sub(/:/,\"\",i); if(i!=\"lo\") a+=\$2} END{print a+0}' /proc/net/dev); tx=\$(awk '{i=\$1; sub(/:/,\"\",i); if(i!=\"lo\") a+=\$10} END{print a+0}' /proc/net/dev); printf '%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\t%s\\n' \"\$(hostname)\" \"\$p\" \"\$start\" \"\$rss\" \"\$ut\" \"\$st\" \"\$mem\" \"\$swap\" \"\$rx\" \"\$tx\"" < /dev/null 2>/dev/null | awk -v h="$h" -v l="$label" -v t="$(date -u +%FT%TZ)" -v s="$(date +%s%N)'" '{print t"\t"s"\t"l"\t"h"\t"$0}' >> "$OUT/hosts-${label}.tsv" || true
  done
}

run_local() {
  local rep=$1 case_id="rep-${rep}-local" log="$OUT/rep-${rep}-local.log"
  remote_snapshot "${case_id}-before" "$ARM_HOST"
  {
    echo "case_id=$case_id"; echo 'mode=notebook_only'; echo "started_utc=$(date -u +%FT%TZ)"
    /usr/bin/time -p timeout --foreground -k 10s "$TIMEOUT_S" env LD_LIBRARY_PATH="$LIBDIR" "$CLIENT" \
      -m "$MODEL" --perf --verbose --log-timestamps -ngl 99 -c 512 -t 4 -n "$N_PREDICT" \
      -p "$PROMPT" --temp 0 --seed 42 --ignore-eos --no-warmup --no-display-prompt < /dev/null
    echo "command_exit=$?"; echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$log" 2>&1
  remote_snapshot "${case_id}-after" "$ARM_HOST"
  awk '/^(real|user|sys) /{print}' "$log" > "$OUT/${case_id}.time"
  if grep -q 'command_exit=0' "$log"; then echo valid > "$OUT/${case_id}.status"; else echo failed_or_incomplete > "$OUT/${case_id}.status"; fi
}

run_arm() {
  local rep=$1 case_id="rep-${rep}-arm" log="$OUT/rep-${rep}-arm.log"
  remote_snapshot "${case_id}-before" "$ARM_HOST"
  {
    echo "case_id=$case_id"; echo 'mode=arm_baseline'; echo "started_utc=$(date -u +%FT%TZ)"
    ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$ARM_HOST" \
      "time -p env LD_LIBRARY_PATH='$ARM_DIR/lib:$ARM_DIR/bin' /usr/bin/timeout --foreground -k 10s '$TIMEOUT_S' '$ARM_DIR/bin/llama-cli' -m /home/caninos/research/models/qwen2.5-1.5b-instruct-q5_k_m.gguf --perf --verbose --log-timestamps -ngl 99 -c 512 -t 4 -n '$N_PREDICT' -p '$PROMPT' --temp 0 --seed 42 --ignore-eos --no-warmup --no-display-prompt" < /dev/null
    echo "command_exit=$?"; echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$log" 2>&1
  remote_snapshot "${case_id}-after" "$ARM_HOST"
  awk '/^(real|user|sys) /{print}' "$log" > "$OUT/${case_id}.time"
  if grep -q 'command_exit=0' "$log"; then echo valid > "$OUT/${case_id}.status"; else echo failed_or_incomplete > "$OUT/${case_id}.status"; fi
}

start_rpc() {
  local h d log old
  for h in "${HOSTS[@]}"; do
    log="$REMOTE_LOG_DIR/rpc-validation-${RUN_ID}-${h}.log"
    ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" \
      "old=\$(pgrep -o -x ggml-rpc-server || true); [ -z \"\$old\" ] || kill -TERM \"\$old\" 2>/dev/null || true; for i in 1 2 3 4 5; do [ -z \"\$old\" ] || kill -0 \"\$old\" 2>/dev/null || break; sleep 1; done; d='$ARM_DIR'; : > '$log'; env GGML_RPC_DEBUG=1 LD_LIBRARY_PATH=\"\$d/lib:\$d/bin\" nohup \"\$d/bin/ggml-rpc-server\" -H 0.0.0.0 -p 50052 >'$log' 2>&1 < /dev/null & echo \"rpc_pid=\$!\"" || true
  done
}

stop_rpc_host() {
  local h=$1
  ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" \
    "p=\$(pgrep -o -x ggml-rpc-server || true); [ -z \"\$p\" ] || kill -TERM \"\$p\" 2>/dev/null || true" < /dev/null 2>/dev/null || true
}

rpc_log_size() {
  local h=$1
  ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" \
    "wc -c < '$REMOTE_LOG_DIR/rpc-validation-${RUN_ID}-${h}.log' 2>/dev/null || echo 0" < /dev/null 2>/dev/null | tr -d '[:space:]'
}

run_rpc() {
  local rep=$1 n=$2
  local case_id="rep-${rep}-rpc-${n}" log="$OUT/rep-${rep}-rpc-${n}.log" srv="$OUT/rep-${rep}-rpc-${n}.server.log" rpc h off end
  rpc=$(rpc_list "$n")
  remote_snapshot "${case_id}-before" "${HOSTS[*]:0:n}"
  : > "$OUT/${case_id}.offsets.tsv"
  for h in "${HOSTS[@]:0:n}"; do printf '%s\t%s\t%s\n' "$case_id" "$h" "$(rpc_log_size "$h")" >> "$OUT/${case_id}.offsets.tsv"; done
  {
    echo "case_id=$case_id"; echo "rpc=$rpc"; echo "started_utc=$(date -u +%FT%TZ)"
    /usr/bin/time -p timeout --foreground -k 10s "$TIMEOUT_S" env LD_LIBRARY_PATH="$LIBDIR" "$CLIENT" \
      -m "$MODEL" --rpc "$rpc" --perf --verbose --log-timestamps -ngl 99 -c 512 -t 4 -n "$N_PREDICT" \
      -p "$PROMPT" --temp 0 --seed 42 --ignore-eos --no-warmup --no-display-prompt < /dev/null
    echo "command_exit=$?"; echo "finished_utc=$(date -u +%FT%TZ)"
  } > "$log" 2>&1
  remote_snapshot "${case_id}-after" "${HOSTS[*]:0:n}"
  : > "$srv"
  while IFS=$'\t' read -r cid h off; do
    [ "$cid" = "$case_id" ] || continue
    end=$(rpc_log_size "$h")
    printf '\n--- host=%s offset=%s end=%s ---\n' "$h" "$off" "$end" >> "$srv"
    ssh -F /dev/null -o BatchMode=yes -o ConnectTimeout=5 "caninos@$h" "tail -c +$((off + 1)) '$REMOTE_LOG_DIR/rpc-validation-${RUN_ID}-${h}.log'" < /dev/null >> "$srv" 2>/dev/null || true
  done < "$OUT/${case_id}.offsets.tsv"
  awk '/^(real|user|sys) /{print}' "$log" > "$OUT/${case_id}.time"
  if grep -q 'command_exit=0' "$log"; then echo valid > "$OUT/${case_id}.status"; else echo failed_or_incomplete > "$OUT/${case_id}.status"; fi
}

remote_snapshot initial "${HOSTS[*]}"
if [[ "$SKIP_LOCAL" != 1 ]]; then
  for ((rep=1; rep<=REPS; rep++)); do run_local "$rep"; done
fi
if [[ "$SKIP_ARM" != 1 ]]; then
  stop_rpc_host "$ARM_HOST"
  for ((rep=1; rep<=REPS; rep++)); do run_arm "$rep"; done
fi
start_rpc
for n in 2 4 6; do
  [[ -n "$ONLY_N" && "$ONLY_N" != "$n" ]] && continue
  for ((rep=1; rep<=REPS; rep++)); do run_rpc "$rep" "$n"; done
done
printf 'utc_end=%s\n' "$(date -u +%FT%TZ)" >> "$OUT/manifest.txt"
echo "$OUT"
