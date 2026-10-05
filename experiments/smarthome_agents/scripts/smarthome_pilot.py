#!/usr/bin/env python3
"""Smart-home single-agent pilot with strict validation and HTTP inference."""

from __future__ import annotations

import argparse
import json
import time
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib import error, request


DEFAULT_SERVER_URL = "http://192.168.50.89:18089"

ACTION_SCHEMAS = {
    "set_light": {"required": {"action": str, "room": str, "value": str}},
    "ask_clarification": {"required": {"action": str, "question": str}},
    "no_action": {"required": {"action": str, "reason": str}},
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def build_prompt(scenario: dict[str, Any]) -> str:
    compact_state = {
        "rooms": {
            room: {"occupied_by": data.get("occupied_by", []), "light": data.get("light"), "hvac": data.get("hvac")}
            for room, data in scenario["initial_state"]["rooms"].items()
        },
        "known_location": scenario["initial_state"].get("known_location", "not_provided"),
    }
    return (
        "Return one strict JSON object only. Actions: set_light(room,value on/off), "
        "ask_clarification(question), no_action(reason). No extra keys. Use only rooms in state. "
        f"Request: {scenario['resident_request']} "
        f"State: {json.dumps(compact_state, ensure_ascii=False, sort_keys=True)} "
        "JSON:"
    )


def _http_json(url: str, payload: dict[str, Any], timeout_s: float) -> tuple[int, dict[str, Any], str]:
    data = json.dumps(payload).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with request.urlopen(req, timeout=timeout_s) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, json.loads(body), body
    except error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            parsed = {}
        return exc.code, parsed, body


def query_llama_server(server_url: str, prompt: str, timeout_s: float, params: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "prompt": prompt,
        "temperature": params["temperature"],
        "n_predict": params["max_tokens"],
        "seed": params["seed"],
        "cache_prompt": False,
        "stop": ["\n\n", "<|im_end|>"],
    }
    started = time.monotonic()
    result: dict[str, Any] = {
        "transport": "http_completion",
        "server_url": server_url,
        "request_payload": payload,
        "completed": False,
        "http_status": None,
        "elapsed_s": None,
        "raw_response": "",
        "model_content": "",
        "usage": {},
        "error": None,
    }
    try:
        status, parsed, raw_body = _http_json(f"{server_url.rstrip('/')}/completion", payload, timeout_s)
        result["http_status"] = status
        result["raw_response"] = raw_body
        if status != 200:
            result["error"] = f"http_status_{status}"
            return result
        result["completed"] = True
        result["usage"] = {k: parsed.get(k) for k in ("tokens_cached", "tokens_evaluated", "tokens_predicted", "timings") if k in parsed}
        result["model_content"] = parsed.get("content", "")
    except Exception as exc:  # noqa: BLE001 - all communication failures must be recorded.
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        result["elapsed_s"] = time.monotonic() - started
    return result


def validate_action_shape(action: Any) -> dict[str, Any]:
    if not isinstance(action, dict):
        return {"valid": False, "reason": "response_is_not_object"}
    name = action.get("action")
    if name not in ACTION_SCHEMAS:
        return {"valid": False, "reason": "unknown_action"}
    schema = ACTION_SCHEMAS[name]
    allowed_keys = set(schema["required"])
    extra = sorted(set(action) - allowed_keys)
    if extra:
        return {"valid": False, "reason": "unexpected_fields", "fields": extra}
    missing = sorted(allowed_keys - set(action))
    if missing:
        return {"valid": False, "reason": "missing_fields", "fields": missing}
    for key, expected_type in schema["required"].items():
        if not isinstance(action[key], expected_type):
            return {"valid": False, "reason": "wrong_type", "field": key}
    if name == "set_light" and action["value"] not in {"on", "off"}:
        return {"valid": False, "reason": "invalid_light_value"}
    if name in {"ask_clarification", "no_action"}:
        text_field = "question" if name == "ask_clarification" else "reason"
        if not action[text_field].strip():
            return {"valid": False, "reason": "empty_text"}
    return {"valid": True, "reason": "ok"}


def parse_model_action(content: str) -> dict[str, Any]:
    stripped = content.strip()
    if not stripped:
        return {"structured_valid": False, "action": None, "reason": "empty_response"}
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        return {"structured_valid": False, "action": None, "reason": f"json_decode_error: {exc.msg}"}
    validation = validate_action_shape(parsed)
    return {
        "structured_valid": validation["valid"],
        "action": parsed if validation["valid"] else None,
        "reason": validation["reason"],
        "shape": validation,
    }


def validate_action_permissions(scenario: dict[str, Any], action: dict[str, Any] | None) -> dict[str, Any]:
    if action is None:
        return {"allowed": False, "reason": "no_structured_action"}
    if action["action"] == "set_light":
        room = action["room"]
        if room not in scenario["initial_state"]["rooms"]:
            return {"allowed": False, "reason": "unknown_room"}
        permitted = scenario.get("permissions", {}).get("set_light", {})
        allowed_rooms = permitted.get("rooms", [])
        allowed_values = permitted.get("values", ["on", "off"])
        if room not in allowed_rooms:
            return {"allowed": False, "reason": "room_not_permitted"}
        if action["value"] not in allowed_values:
            return {"allowed": False, "reason": "value_not_permitted"}
    return {"allowed": True, "reason": "allowed"}


def apply_action(state: dict[str, Any], action: dict[str, Any] | None, permission: dict[str, Any]) -> dict[str, Any]:
    next_state = deepcopy(state)
    if not permission["allowed"] or action is None:
        return next_state
    if action["action"] == "set_light":
        next_state["rooms"][action["room"]]["light"] = action["value"]
    return next_state


def path_get(data: dict[str, Any], dotted: str) -> Any:
    current: Any = data
    for part in dotted.split("."):
        current = current[part]
    return current


def _rule_matches(rule: dict[str, Any], action: dict[str, Any]) -> bool:
    return all(rule.get(key) == "*" or action.get(key) == rule.get(key) for key in rule)


def evaluate_scenario(
    scenario: dict[str, Any],
    initial_state: dict[str, Any],
    final_state: dict[str, Any],
    action: dict[str, Any] | None,
    execution_completed: bool,
    structured_valid: bool,
    permission: dict[str, Any],
) -> dict[str, Any]:
    if not execution_completed:
        return {"task_completed": False, "checks": [{"name": "execution_completed", "passed": False}]}
    if not structured_valid:
        return {"task_completed": False, "checks": [{"name": "structured_response", "passed": False}]}

    evaluator = scenario["evaluator"]
    checks: list[dict[str, Any]] = []
    if action is not None and action["action"] == "ask_clarification":
        passed = bool(evaluator.get("clarification_is_success", False))
        checks.append({"name": "clarification_policy", "passed": passed})
        return {"task_completed": passed, "checks": checks}
    if action is not None and action["action"] == "no_action":
        passed = bool(evaluator.get("no_action_is_success", False))
        checks.append({"name": "no_action_policy", "passed": passed})
        return {"task_completed": passed, "checks": checks}

    checks.append({"name": "action_allowed", "passed": permission["allowed"], "detail": permission["reason"]})
    for dotted, expected in evaluator.get("final_state_equals", {}).items():
        actual = path_get(final_state, dotted)
        checks.append({"name": f"final:{dotted}", "passed": actual == expected, "expected": expected, "actual": actual})
    for dotted in evaluator.get("unchanged", []):
        initial = path_get(initial_state, dotted)
        final = path_get(final_state, dotted)
        checks.append({"name": f"unchanged:{dotted}", "passed": final == initial, "expected": initial, "actual": final})
    for rule in evaluator.get("prohibited_actions", []):
        matched = action is not None and _rule_matches(rule, action)
        checks.append({"name": f"prohibited:{rule}", "passed": not matched})
    return {"task_completed": bool(checks) and all(item["passed"] for item in checks), "checks": checks}


def run_scenario(
    scenario: dict[str, Any],
    server_url: str,
    timeout_s: float,
    params: dict[str, Any],
) -> dict[str, Any]:
    prompt = build_prompt(scenario)
    inference = query_llama_server(server_url, prompt, timeout_s, params)
    if inference["completed"]:
        parsed = parse_model_action(inference["model_content"])
    else:
        parsed = {"structured_valid": False, "action": None, "reason": inference["error"] or "incomplete_execution"}
    permission = validate_action_permissions(scenario, parsed["action"])
    final_state = apply_action(scenario["initial_state"], parsed["action"], permission)
    action_applied = permission["allowed"] and parsed["action"] is not None and parsed["action"]["action"] == "set_light"
    evaluation = evaluate_scenario(
        scenario,
        scenario["initial_state"],
        final_state,
        parsed["action"],
        inference["completed"],
        parsed["structured_valid"],
        permission,
    )
    return {
        "prompt": prompt,
        "inference": inference,
        "model_content": inference["model_content"],
        "parse": parsed,
        "validation": permission,
        "action_applied": action_applied,
        "final_state": final_state,
        "evaluation": evaluation,
        "result_flags": {
            "execution_completed": inference["completed"],
            "structured_response_valid": parsed["structured_valid"],
            "action_permitted": permission["allowed"],
            "action_applied": action_applied,
            "task_completed": evaluation["task_completed"],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=Path, required=True)
    parser.add_argument("--server-url", default=DEFAULT_SERVER_URL)
    parser.add_argument("--outdir", type=Path, default=None)
    parser.add_argument("--timeout-s", type=float, default=120)
    parser.add_argument("--max-tokens", type=int, default=96)
    parser.add_argument("--temperature", type=float, default=0)
    parser.add_argument("--seed", type=int, default=101)
    args = parser.parse_args()

    scenario = load_json(args.scenario)
    run_id = f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
    outdir = args.outdir or Path("experiments/smarthome_agents/runs") / run_id
    outdir.mkdir(parents=True, exist_ok=True)
    log_path = outdir / "events.jsonl"

    params = {"max_tokens": args.max_tokens, "temperature": args.temperature, "seed": args.seed}
    append_jsonl(log_path, {"ts": utc_now(), "event": "run_start", "run_id": run_id, "scenario_id": scenario["scenario_id"], "server_url": args.server_url, "params": params})
    try:
        result = run_scenario(scenario, args.server_url, args.timeout_s, params)
    except Exception as exc:  # noqa: BLE001 - every attempt must finish with a result record.
        result = {
            "prompt": None,
            "inference": {"completed": False, "error": f"{type(exc).__name__}: {exc}", "elapsed_s": None},
            "model_content": "",
            "parse": {"structured_valid": False, "action": None, "reason": "unhandled_exception"},
            "validation": {"allowed": False, "reason": "unhandled_exception"},
            "action_applied": False,
            "final_state": scenario.get("initial_state"),
            "evaluation": {"task_completed": False, "checks": [{"name": "unhandled_exception", "passed": False}]},
            "result_flags": {
                "execution_completed": False,
                "structured_response_valid": False,
                "action_permitted": False,
                "action_applied": False,
                "task_completed": False,
            },
        }
    summary = {"run_id": run_id, "scenario_id": scenario["scenario_id"], "log": str(log_path), **result}
    append_jsonl(log_path, {"ts": utc_now(), "event": "run_end", **summary})
    with (outdir / "summary.json").open("w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2, sort_keys=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if summary["result_flags"]["task_completed"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
