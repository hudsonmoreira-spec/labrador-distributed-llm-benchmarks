#!/usr/bin/env python3
"""Check the RPC manuscript's quantitative/provenance claims without hardware access."""
import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re
import statistics
from verify_icce_artifact import verify

ROOT = Path(__file__).resolve().parents[2]


def audit():
    evidence = verify(ROOT, ROOT / "paper/icce2027/artifact/evidence-manifest.json")
    rows = list(csv.DictReader((ROOT / "research/data/derived/rpc-validation-20261004.csv").open()))
    selected = [r for r in rows if r["selected"] == "1" and r["valid"] == "1"]
    inputs = {}

    def read(relative):
        path = ROOT / relative
        data = path.read_bytes()
        inputs[relative] = hashlib.sha256(data).hexdigest()
        return data.decode(errors="replace")

    manifests = {}
    rpc_cases = []
    for row in selected:
        folder = f'research/data/runs/{row["run"]}/rpc-validation/'
        log = read(folder + row["case"] + ".log")
        assert "command_exit=0" in log
        assert re.search(r"n_threads = 4", log)
        assert "n_ctx" in log and "512" in log
        if row["run"] not in manifests:
            text = read(folder + "manifest.txt")
            manifest = dict(line.split("=", 1) for line in text.splitlines() if "=" in line)
            for parameter in ["ctx=512", "threads=4", "ngl=99", "n_predict=32", "temp=0", "seed=42", "ignore_eos=true", "warmup=false"]:
                assert parameter in manifest["parameters"]
            assert "no model-resident repeat" in manifest["cache_policy"]
            manifests[row["run"]] = manifest
        if row["mode"] == "rpc2":
            for layer in range(29):
                device = "RPC0" if layer < 15 else "RPC1"
                assert re.search(rf"layer\s+{layer} assigned to device {device}\b", log)
            assert re.search(r"n_layer\s+= 28", log)
            server = read(folder + row["case"] + ".server.log")
            counts = []
            for host in re.split(r"(?=--- host=)", server):
                if not host.startswith("--- host="):
                    continue
                events = {name: len(re.findall(r"\[" + name + r"\]", host)) for name in ["graph_compute", "graph_recompute", "get_tensor", "set_tensor"]}
                assert all(events.values())
                counts.append(events)
            assert len(counts) == 2
            rpc_cases.append({"run": row["run"], "case": row["case"], "layers": {"RPC0": "0-14", "RPC1": "15-28"}, "worker_events": counts})
    for field in ["llama_source_commit", "client_sha256", "model_sha256", "source_patch_sha256"]:
        assert len({m[field] for m in manifests.values()}) == 1

    hardware = []
    for host in ["192.168.50.42", "192.168.50.118"]:
        name = f"research/data/runs/20261001T150951Z/hosts/{host}/raw.txt"
        text = read(name)
        assert "Cortex-A53" in text and "Debian GNU/Linux 12" in text and "6.1.76" in text
        assert re.search(r"CPU\(s\):\s+4", text)
        assert "100Mbps/Full" in text
        memory = int(re.search(r"MemTotal:\s+(\d+) kB", text)[1])
        swap = int(re.search(r"SwapTotal:\s+(\d+) kB", text)[1])
        assert memory == 1986400 and swap == 0
        hardware.append({"record": name, "memtotal_kib": memory, "os_visible_gib": memory / 1024**2, "swap_kib": swap, "link_evidence": "dated 100Mbps/Full kernel records; no throughput measurement"})
    metrics = {}
    for mode in ["notebook", "arm", "rpc2"]:
        group = [r for r in selected if r["mode"] == mode]
        values = [float(r["real_s"]) for r in group]
        metrics[mode] = {"n": len(group), "mean_process_s": statistics.mean(values), "sample_sd_s": statistics.stdev(values), "min_s": min(values), "max_s": max(values), "prompt_s": statistics.mean(float(r["prompt_ms"]) / 1000 for r in group), "generation_s": statistics.mean(float(r["generation_ms"]) / 1000 for r in group), "remainder_s": statistics.mean(float(r["real_s"]) - float(r["prompt_ms"]) / 1000 - float(r["generation_ms"]) / 1000 for r in group), "runtime_generation_tok_s": statistics.mean(float(r["runtime_predicted_per_second"]) for r in group)}
    ratios = {k: metrics["rpc2"][k] / metrics["arm"][k] for k in ["mean_process_s", "prompt_s", "generation_s"]}
    assert [round(ratios[k], 2) for k in ratios] == [3.85, 1.95, 1.91]
    shares = {mode: metrics[mode]["remainder_s"] / metrics[mode]["mean_process_s"] * 100 for mode in ["arm", "rpc2"]}
    assert round(shares["arm"], 1) == 19.5 and round(shares["rpc2"], 1) == 59.7
    representative = next(r for r in rpc_cases if r["run"] == "20261004T-matrix-validation-7" and r["case"] == "rep-3-rpc-2")
    assert [h["set_tensor"] for h in representative["worker_events"]] == [345, 356]
    assert all(h["graph_compute"] == 3 and h["graph_recompute"] == 30 and h["get_tensor"] == 33 for h in representative["worker_events"])
    return {"status": "pass", "evidence_commit": evidence["evidence_commit"], "inventory_attempts": len(rows), "valid_attempts_all_campaigns": sum(r["valid"] == "1" for r in rows), "selected_attempts": len(selected), "selection_by_campaign": dict(Counter(r["run"] for r in selected)), "metrics": metrics, "rpc_to_arm_ratios": ratios, "remainder_percent_of_mean_process": shares, "hardware": hardware, "rpc_case_checks": rpc_cases, "source_sha256": inputs, "scope": "Preserved-log reconstruction; not an independent hardware rerun or causal identification of network overhead."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(audit(), indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")


if __name__ == "__main__":
    main()
