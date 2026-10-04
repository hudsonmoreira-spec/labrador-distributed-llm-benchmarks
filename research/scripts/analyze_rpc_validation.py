#!/usr/bin/env python3
"""Reconstruct per-case validation metrics without treating incomplete runs as valid."""
import csv, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RUNS = sorted((ROOT / "research/data/runs").glob("*/rpc-validation"))
OUT = ROOT / "research/data/derived/rpc-validation-20261004.csv"
SUMMARY = ROOT / "research/data/derived/rpc-validation-20261004-summary.csv"
FAILURES = ROOT / "research/data/derived/rpc-validation-20261004-failures.csv"

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

def runtime_generation_rate(text, generated_tokens):
    """Read the final server JSON timing, not tokens/time recomputed by us."""
    if generated_tokens == "":
        return ""
    matches = re.findall(
        r'"predicted_n":([0-9]+).*?"predicted_per_second":([0-9.]+)', text
    )
    for predicted_n, rate in reversed(matches):
        if int(predicted_n) == int(generated_tokens):
            return float(rate)
    return ""

def failure_class(text, status, exit_code, valid):
    if valid:
        return "normal_completion"
    if "Failed to connect" in text:
        return "connection_failure"
    if exit_code == 127:
        return "preparation_missing_tool"
    if exit_code == 255:
        return "preparation_or_host_unavailable"
    if exit_code == 137:
        return "loading_timeout_or_kill"
    if exit_code == 124:
        return "incomplete_timeout_or_interrupt"
    if '"predicted_n":30' in text or '"tokens_predicted":30' in text:
        return "partial_generation"
    if exit_code == 134 and "wait_ready" in text:
        return "connection_or_startup_abort"
    if exit_code == 134 and "stream_line_reader" in text:
        return "post_inference_stream_abort"
    if status == "missing_status":
        return "incomplete_missing_status"
    return "other_incomplete"

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
            run_name = run.parent.name
            selected = (
                (run_name == "20261004T-matrix-validation-1" and mode == "notebook") or
                (run_name == "20261004T-matrix-validation-5" and mode == "arm") or
                (run_name == "20261004T-matrix-validation-7" and case in {"rep-3-rpc-2", "rep-4-rpc-2"}) or
                (run_name == "20261004T-rpc2-complete-1" and mode == "rpc2")
            )
            prompt_ms, prompt_tokens = metric(text, "prompt eval time")
            gen_ms, generated = metric(text, r"(?<!prompt )eval time")
            total_ms, total_tokens = metric(text, "total time")
            real = number((re.findall(r"^real ([0-9.,]+)", text, re.M) or [""])[-1])
            exit_match = re.findall(r"command_exit=([0-9]+)", text)
            exit_code = int(exit_match[-1]) if exit_match else ""
            predicted = re.findall(r'"tokens_predicted":([0-9]+)', text)
            predicted_tokens = int(predicted[-1]) if predicted else ""
            runtime_rate = runtime_generation_rate(text, generated)
            server = log.with_name(log.stem + ".server.log")
            server_text = server.read_text(errors="replace") if server.exists() else ""
            hosts = re.findall(r"--- host=([0-9.]+)", server_text)
            graph = len(re.findall(r"\[graph_(?:compute|recompute)\]", server_text))
            event_counts = []
            for part in re.split(r"(?=--- host=)", server_text):
                host_match = re.match(r"--- host=([0-9.]+)", part)
                if not host_match:
                    continue
                counts = {name: len(re.findall(r"\[" + name + r"\]", part))
                          for name in ("graph_compute", "graph_recompute", "get_tensor", "set_tensor")}
                event_counts.append(host_match.group(1) + ":" + ",".join(f"{k}={v}" for k, v in counts.items()))
            valid = status == "valid" and exit_code == 0 and generated != ""
            yield {
                "run": run_name, "case": case, "mode": mode, "selected": int(selected),
                "status": status, "valid": int(valid), "exit_code": exit_code,
                "real_s": real, "prompt_ms": prompt_ms, "prompt_tokens": prompt_tokens,
                "generation_ms": gen_ms, "generated_tokens": generated,
                "total_ms": total_ms, "total_tokens": total_tokens,
                "runtime_predicted_per_second": runtime_rate,
                "derived_tokens_per_second": (float(generated) / (float(gen_ms) / 1000)) if generated != "" and gen_ms != "" else "",
                "tokens_predicted": predicted_tokens,
                "server_hosts_observed": ",".join(dict.fromkeys(hosts)),
                "server_graph_ops": graph,
                "server_event_counts": ";".join(event_counts),
                "failure_class": failure_class(text, status, exit_code, valid),
            }

def main():
    rows = list(cases())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with OUT.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)
    import statistics
    summary_fields = ["condition", "n_attempts_included", "n_valid", "success_rate", "metric", "mean", "sample_sd", "minimum", "maximum"]
    summary_rows = []
    for condition in ("notebook", "arm", "rpc2"):
        selected = [r for r in rows if r["mode"] == condition and r["selected"] == 1]
        valid = [r for r in selected if r["valid"] == 1]
        for metric_name in ("real_s", "prompt_ms", "generation_ms", "total_ms", "generated_tokens", "runtime_predicted_per_second", "derived_tokens_per_second"):
            values = [float(r[metric_name]) for r in valid if r[metric_name] != ""]
            summary_rows.append({
                "condition": condition, "n_attempts_included": len(selected),
                "n_valid": len(valid), "success_rate": len(valid) / len(selected) if selected else "",
                "metric": metric_name,
                "mean": statistics.mean(values) if values else "",
                "sample_sd": statistics.stdev(values) if len(values) > 1 else "",
                "minimum": min(values) if values else "", "maximum": max(values) if values else "",
            })
    with SUMMARY.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_fields, lineterminator="\n")
        writer.writeheader(); writer.writerows(summary_rows)
    failure_rows = []
    from collections import Counter
    for (failure, mode), count in sorted(Counter((r["failure_class"], r["mode"]) for r in rows if r["valid"] != 1).items()):
        failure_rows.append({"failure_class": failure, "mode": mode, "count": count})
    with FAILURES.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["failure_class", "mode", "count"], lineterminator="\n")
        writer.writeheader(); writer.writerows(failure_rows)
    print(OUT)

if __name__ == "__main__":
    main()
