#!/usr/bin/env python3
"""Reconstruct per-case validation metrics without treating incomplete runs as valid."""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = [
    ROOT / "research/data/runs/20261004T-matrix-validation-1/rpc-validation",
    ROOT / "research/data/runs/20261004T-matrix-validation-5/rpc-validation",
    ROOT / "research/data/runs/20261004T-matrix-validation-7/rpc-validation",
    ROOT / "research/data/runs/20261004T-rpc2-complete-1/rpc-validation",
]
OUT = ROOT / "research/data/derived/rpc-validation-20261004.csv"

def number(value):
    if not value:
        return ""
    try:
        return float(value.replace(",", "."))
    except ValueError:
        return ""

def metric(text, name):
    m = re.search(rf"{name}.*?=\s*([0-9.,]+)\s*ms\s*/\s*([0-9]+) tokens", text)
    return (number(m.group(1)), int(m.group(2))) if m else ("", "")

def cases():
    for run in RUNS:
        for log in sorted(run.glob("*.log")):
            if ".server." in log.name or log.name.endswith("launcher.log"):
                continue
            case = log.stem
            status_file = log.with_suffix(".status")
            status = status_file.read_text().strip() if status_file.exists() else "missing_status"
            text = log.read_text(errors="replace")
            if "-local" in case:
                mode = "notebook"
            elif "-arm" in case:
                mode = "arm"
            elif "-rpc-2" in case:
                mode = "rpc2"
            else:
                continue
            prompt_ms, prompt_tokens = metric(text, "prompt eval time")
            gen_ms, generated = metric(text, r"(?<!prompt )eval time")
            total_ms, total_tokens = metric(text, "total time")
            real = number((re.findall(r"^real ([0-9.,]+)", text, re.M) or [""])[-1])
            exit_match = re.findall(r"command_exit=([0-9]+)", text)
            exit_code = int(exit_match[-1]) if exit_match else ""
            predicted = re.findall(r'"tokens_predicted":([0-9]+)', text)
            server = log.with_name(log.stem + ".server.log")
            server_text = server.read_text(errors="replace") if server.exists() else ""
            hosts = re.findall(r"--- host=([0-9.]+)", server_text)
            graph = len(re.findall(r"\[graph_(?:compute|recompute)\]", server_text))
            valid = status == "valid" and exit_code == 0 and generated != ""
            yield {
                "run": run.parent.name, "case": case, "mode": mode,
                "status": status, "valid": int(valid), "exit_code": exit_code,
                "real_s": real, "prompt_ms": prompt_ms, "prompt_tokens": prompt_tokens,
                "generation_ms": gen_ms, "generated_tokens": generated,
                "total_ms": total_ms, "total_tokens": total_tokens,
                "tokens_predicted": int(predicted[-1]) if predicted else "",
                "server_hosts_observed": ",".join(dict.fromkeys(hosts)),
                "server_graph_ops": graph,
            }

def main():
    rows = list(cases())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)
    print(OUT)

if __name__ == "__main__":
    main()
