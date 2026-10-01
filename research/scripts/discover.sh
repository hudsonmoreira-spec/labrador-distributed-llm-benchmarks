#!/usr/bin/env bash
set -u
ROOT=$(cd "$(dirname "$0")/.." && pwd)
RUN_ID=$(date -u +%Y%m%dT%H%M%SZ)
RUN="$ROOT/data/runs/$RUN_ID"
mkdir -p "$RUN/hosts" "$RUN/controller" "$ROOT/data/ssh"
cp "$ROOT/config/hosts.txt" "$RUN/hosts.txt"
date -u +%FT%TZ > "$RUN/controller/start_utc"
{ date -u; hostname; ip -br addr 2>&1; ip -br link 2>&1; ip route 2>&1; free -h 2>&1; lscpu 2>&1; df -hT 2>&1; command -v python3 git gcc clang cmake make iperf3 2>&1; } > "$RUN/controller/inventory.txt" 2>&1
: > "$ROOT/data/ssh/known_hosts"
while read -r h; do [ -z "$h" ] && continue; ssh-keygen -F "$h" -f "${HOME}/.ssh/known_hosts" 2>/dev/null >> "$ROOT/data/ssh/known_hosts" || true; done < "$ROOT/config/hosts.txt"
collect_one() {
  h="$1"; out="$RUN/hosts/$h"; mkdir -p "$out"
  printf 'host=%s\nstart_utc=%s\n' "$h" "$(date -u +%FT%TZ)" > "$out/metadata.txt"
  timeout 18s ssh -T -o BatchMode=yes -o StrictHostKeyChecking=accept-new -o UserKnownHostsFile="$ROOT/data/ssh/known_hosts" -o ConnectTimeout=6 -o ConnectionAttempts=1 -o ServerAliveInterval=5 -o ServerAliveCountMax=1 caninos@"$h" 'bash -s' > "$out/raw.txt" 2> "$out/error.txt" <<'REMOTE'
set +e
printf 'UTC=%s\n' "$(date -u +%FT%TZ)"
printf '%s\n' '---ACCESS---'; id; sudo -n true >/dev/null 2>&1; printf 'sudo_n=%s\n' "$?"
printf '%s\n' '---IDENTITY---'; hostname; hostnamectl 2>&1; cat /etc/hostname 2>&1; cat /etc/machine-id 2>&1
printf '%s\n' '---NETWORK---'; ip -j addr 2>&1; ip -j link 2>&1; ip -j route 2>&1; for f in /sys/class/net/*/address; do printf '%s=' "$f"; cat "$f"; done
printf '%s\n' '---DEVICE_TREE---'; tr '\0' ' ' </proc/device-tree/model 2>&1; echo; cat /proc/device-tree/compatible 2>&1 | tr '\0' '\n'; echo; cat /proc/device-tree/serial-number 2>&1 | tr '\0' ' '; echo
printf '%s\n' '---CPU---'; uname -a; lscpu 2>&1; grep -E '^(processor|model name|Features|BogoMIPS)' /proc/cpuinfo 2>&1; for f in /sys/devices/system/cpu/cpu*/cpufreq/{scaling_cur_freq,scaling_min_freq,scaling_max_freq,scaling_governor}; do [ -r "$f" ] && printf '%s=' "$f" && cat "$f"; done
printf '%s\n' '---OS---'; cat /etc/os-release 2>&1; uname -r; uptime -s 2>&1; uptime 2>&1; date -u +%FT%TZ
printf '%s\n' '---MEMORY---'; free -b 2>&1; swapon --show 2>&1; cat /proc/meminfo 2>&1 | head -30
printf '%s\n' '---STORAGE---'; lsblk -O 2>&1; df -hT 2>&1; find / -maxdepth 3 -type f \( -iname '*.gguf' -o -iname '*.ggml' -o -iname '*.safetensors' -o -iname '*.bin' \) -printf '%p %s\n' 2>/dev/null | head -200
printf '%s\n' '---THERMAL---'; for f in /sys/class/thermal/thermal_zone*/{type,temp}; do [ -r "$f" ] && printf '%s=' "$f" && cat "$f"; done; for f in /sys/class/hwmon/hwmon*/{name,temp*_input}; do [ -r "$f" ] && printf '%s=' "$f" && cat "$f"; done
printf '%s\n' '---LOAD---'; cat /proc/loadavg; ps -eo pid,comm,pcpu,pmem,etime,args --sort=-pcpu | head -25; systemctl list-units --type=service --state=running --no-pager 2>&1
printf '%s\n' '---LINK_STATS---'; for n in /sys/class/net/*; do n=${n##*/}; printf 'IF=%s\n' "$n"; ethtool "$n" 2>&1; ip -s link show "$n" 2>&1; done
printf '%s\n' '---TOOLS---'; for c in gcc g++ clang make cmake python3 python git pip3 llama-cli llama-server ollama vllm torchrun mpirun iperf3; do printf 'CMD=%s PATH=' "$c"; command -v "$c" 2>&1; "$c" --version 2>&1 | head -2; done; find /usr/local /opt /home /root -maxdepth 4 -type f \( -iname '*llama*' -o -iname '*ollama*' -o -iname '*vllm*' \) -printf '%p %s\n' 2>/dev/null | head -100
printf '%s\n' '---LOG_EVIDENCE---'; dmesg --ctime 2>&1 | tail -300 | grep -Ei 'oom|out of memory|I/O error|ext4|mmc|nvme|thrott|thermal|link is|carrier|crc|error' | tail -100; journalctl -k -b --no-pager 2>&1 | grep -Ei 'oom|out of memory|I/O error|ext4|mmc|nvme|thrott|thermal|link is|carrier|crc|error' | tail -100
REMOTE
  printf 'end_utc=%s\nssh_exit=%s\n' "$(date -u +%FT%TZ)" "$?" >> "$out/metadata.txt"
}
export ROOT RUN
export -f collect_one
tr '\n' '\0' < "$ROOT/config/hosts.txt" | xargs -0 -r -n1 -P4 bash -c 'collect_one "$0"'
date -u +%FT%TZ > "$RUN/controller/end_utc"
printf '%s\n' "$RUN"
