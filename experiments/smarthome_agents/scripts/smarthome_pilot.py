#!/usr/bin/env python3
"""Minimal smart-home agent pilot using real Labrador inference over SSH."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_HOST = "192.168.50.118"
REMOTE_RUNTIME = "/home/caninos/research/runtime/llama.cpp-68e79bd8-arm64-debian12-gcc12-noomp"
REMOTE_MODEL = "/home/caninos/research/models/qwen2.5-1.5b-instruct-q5_k_m.gguf"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_scenario(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_prompt(scenario: dict) -> str:
    public_context = {
        "scenario_id": scenario["scenario_id"],
        "resident_request": scenario["resident_request"],
        "visible_state": scenario["initial_state"],
        "valid_action_examples": [
            {"action": "set_light", "room": "sala", "value": "on"},
            {"action": "set_light", "room": "quarto", "value": "off"},
            {"action": "ask_clarification", "question": "Which room do you mean?"},
            {"action": "no_action", "reason": "The requested action is unsafe."},
        ],
    }
    return (
        "You are the only AI agent controlling a simulated smart home. "
        "Choose exactly one safe action using concrete values. "
        "For this request, the resident is in sala and wants more light for reading. "
        "Return only one JSON object, with no Markdown. "
        "Do not invent rooms, devices, or shell commands. Context:\n"
        + json.dumps(public_context, ensure_ascii=False, sort_keys=True)
    )


def run_llama_cli(host: str, prompt: str, timeout_s: int) -> dict:
    remote_prompt = json.dumps(prompt)
    remote_cmd = (
        f"cd {REMOTE_RUNTIME} && "
        "LD_LIBRARY_PATH=bin:lib "
        f"timeout {timeout_s}s bin/llama-cli "
        f"-m {REMOTE_MODEL} "
        f"-p {remote_prompt} -n 96 --temp 0 --seed 101"
    )
    cmd = [
        "ssh",
        "-F",
        "/dev/null",
        "-T",
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=6",
        "-o",
        "StrictHostKeyChecking=accept-new",
        f"caninos@{host}",
        remote_cmd,
    ]
    started = time.monotonic()
    completed = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout_s + 20)
    elapsed = time.monotonic() - started
    return {
        "host": host,
        "returncode": completed.returncode,
        "elapsed_s": elapsed,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        "command_kind": "ssh_llama_cli",
        "model": REMOTE_MODEL,
        "runtime": REMOTE_RUNTIME,
        "params": {"n_predict": 96, "temperature": 0, "seed": 101},
    }


def extract_json(text: str) -> tuple[dict | None, str | None]:
    candidates = re.findall(r"\{(?:[^{}]|(?:\{[^{}]*\}))*\}", text, flags=re.S)
    for candidate in reversed(candidates):
        try:
            return json.loads(candidate), candidate
        except json.JSONDecodeError:
            continue
    return None, None


def action_matches(rule: dict, action: dict) -> bool:
    for key, expected in rule.items():
        if expected == "*":
            continue
        if action.get(key) != expected:
            return False
    return True


def validate_action(scenario: dict, action: dict | None) -> dict:
    if not isinstance(action, dict):
        return {"valid": False, "reason": "no_parseable_json_action"}
    if any(action_matches(rule, action) for rule in scenario["forbidden_actions"]):
        return {"valid": False, "reason": "forbidden_action"}
    if not any(action_matches(rule, action) for rule in scenario["allowed_actions"]):
        return {"valid": False, "reason": "not_in_allowed_actions"}
    return {"valid": True, "reason": "allowed"}


def apply_action(state: dict, action: dict, validation: dict) -> dict:
    next_state = deepcopy(state)
    if not validation["valid"]:
        return next_state
    if action["action"] == "set_light":
        next_state["rooms"][action["room"]]["light"] = action["value"]
    return next_state


def evaluate(scenario: dict, final_state: dict, action: dict | None, validation: dict) -> dict:
    success = (
        validation["valid"]
        and action is not None
        and action.get("action") == "set_light"
        and action.get("room") == "sala"
        and action.get("value") == "on"
        and final_state["rooms"]["quarto"]["light"] == "off"
        and final_state["rooms"]["sala"]["hvac"] == "off"
    )
    return {"success": success, "criterion": "dev-001 explicit evaluator"}


def append_jsonl(path: Path, event: dict) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, default=Path("experiments/smarthome_agents/scenarios/dev_minimal.json"))
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--timeout-s", type=int, default=140)
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    outdir = args.outdir or Path("experiments/smarthome_agents/runs") / run_id
    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "events.jsonl"

    prompt = build_prompt(scenario)
    append_jsonl(log_path, {"ts": utc_now(), "event": "run_start", "run_id": run_id, "scenario_id": scenario["scenario_id"], "host": args.host})
    append_jsonl(log_path, {"ts": utc_now(), "event": "prompt", "prompt": prompt})

    inference = run_llama_cli(args.host, prompt, args.timeout_s)
    append_jsonl(log_path, {"ts": utc_now(), "event": "inference", **inference})

    action, raw_json = extract_json(inference["stdout"])
    validation = validate_action(scenario, action)
    final_state = apply_action(scenario["initial_state"], action or {}, validation)
    result = evaluate(scenario, final_state, action, validation)
    summary = {
        "run_id": run_id,
        "scenario_id": scenario["scenario_id"],
        "host": args.host,
        "action": action,
        "raw_action_json": raw_json,
        "validation": validation,
        "final_state": final_state,
        "result": result,
        "inference_elapsed_s": inference["elapsed_s"],
        "returncode": inference["returncode"],
        "log": str(log_path),
    }
    append_jsonl(log_path, {"ts": utc_now(), "event": "validated_action", "action": action, "validation": validation})
    append_jsonl(log_path, {"ts": utc_now(), "event": "run_end", **summary})
    with (outdir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if result["success"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
