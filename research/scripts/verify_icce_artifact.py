#!/usr/bin/env python3
"""Verify published ICCE evidence offline; never contacts or starts the testbed."""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from collections import Counter

EVIDENCE_COMMIT = "7d94be29fe4e8069f2c916cb8cd0350acf338f1e"
CSV_NAMES = ["rpc-validation-20261004" + suffix + ".csv" for suffix in ("", "-summary", "-failures")]


def verify(source, manifest):
    records = json.loads(manifest.read_text())
    assert records["evidence_commit"] == EVIDENCE_COMMIT
    for name, expected in records["sha256"].items():
        actual = hashlib.sha256((source / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Evidence hash mismatch: {name}")
    with tempfile.TemporaryDirectory(prefix="icce-reconstruction-") as folder:
        isolated = Path(folder)
        for name in records["sha256"]:
            target = isolated / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / name, target)
        subprocess.run([sys.executable, str(isolated / "research/scripts/analyze_rpc_validation.py")], check=True, capture_output=True, text=True)
        derived = isolated / "research/data/derived"
        for name in CSV_NAMES:
            if (source / "research/data/derived" / name).read_bytes() != (derived / name).read_bytes():
                raise ValueError(f"Reconstructed CSV differs: {name}")
        rows = list(csv.DictReader((derived / CSV_NAMES[0]).open()))
        selected = [r for r in rows if r["selected"] == "1" and r["valid"] == "1"]
        counts = Counter(r["mode"] for r in selected)
        assert len(rows) == 55 and counts == {"notebook": 5, "arm": 5, "rpc2": 5}
        for row in selected:
            assert row["exit_code"] == "0"
            assert float(row["prompt_tokens"]) == 38
            assert float(row["generated_tokens"]) == 32
            if row["mode"] == "rpc2":
                hosts = row["server_event_counts"].split(";")
                assert len(hosts) == 2
                for host in hosts:
                    events = dict(part.split("=") for part in host.split(":", 1)[1].split(","))
                    assert int(events["graph_compute"]) > 0 and int(events["graph_recompute"]) > 0
                    assert int(events["get_tensor"]) > 0 and int(events["set_tensor"]) > 0
        summary = list(csv.DictReader((derived / CSV_NAMES[1]).open()))
        means = {r["condition"]: round(float(r["mean"]), 2) for r in summary if r["metric"] == "real_s"}
        assert means == {"notebook": 5.69, "arm": 43.86, "rpc2": 168.67}
        failures = Counter()
        for r in csv.DictReader((derived / CSV_NAMES[2]).open()):
            failures[r["failure_class"]] += int(r["count"])
        assert sum(failures.values()) == 32
    return {"status": "pass", "evidence_commit": EVIDENCE_COMMIT,
            "hashed_files": len(records["sha256"]), "csv_files_reconstructed_byte_for_byte": 3,
            "attempts": len(rows), "selected_valid": dict(counts),
            "rpc_requests_with_two_active_workers": 5, "mean_process_seconds": means,
            "excluded_failure_inventory": dict(failures),
            "scope": "Offline reconstruction of preserved evidence; no new inference or independent hardware rerun."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path(__file__).resolve().parents[2], help="Root of the extracted published evidence snapshot")
    parser.add_argument("--manifest", type=Path, default=Path(__file__).resolve().parents[2] / "paper/icce2027/artifact/evidence-manifest.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = json.dumps(verify(args.source.resolve(), args.manifest.resolve()), indent=2) + "\n"
    if args.output:
        args.output.write_text(result)
    print(result, end="")


if __name__ == "__main__":
    main()
