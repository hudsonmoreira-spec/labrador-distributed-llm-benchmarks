#!/usr/bin/env python3
"""Smart-home single-agent pilot with strict validation and HTTP inference."""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
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
    "ask_clarification": {"required": {"action": str, "missing_field": str, "question": str}},
    "no_action": {"required": {"action": str, "reason": str}},
}

ACTION_JSON_SCHEMA = {
    "oneOf": [
        {
            "type": "object",
            "additionalProperties": False,
            "required": ["action", "room", "value"],
            "properties": {
                "action": {"const": "set_light"},
                "room": {"type": "string"},
                "value": {"enum": ["on", "off"]},
            },
        },
        {
            "type": "object",
            "additionalProperties": False,
            "required": ["action", "missing_field", "question"],
            "properties": {
                "action": {"const": "ask_clarification"},
                "missing_field": {"enum": ["room"]},
                "question": {"type": "string", "minLength": 1},
            },
        },
        {
            "type": "object",
            "additionalProperties": False,
            "required": ["action", "reason"],
            "properties": {
                "action": {"const": "no_action"},
                "reason": {"type": "string", "minLength": 1},
            },
        },
    ]
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def append_jsonl(path: Path, event: dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def build_messages(scenario: dict[str, Any]) -> list[dict[str, str]]:
    compact_state = {
        "rooms": {
            room: {"occupied_by": data.get("occupied_by", []), "light": data.get("light"), "hvac": data.get("hvac")}
            for room, data in scenario["initial_state"]["rooms"].items()
        },
        "known_location": scenario["initial_state"].get("known_location", "not_provided"),
    }
    system = (
        "You control only a simulated smart home. Return exactly one JSON object that matches "
        "the supplied response schema. Do not include Markdown or prose. Do not execute shell "
        "commands or operate real devices. Use set_light only for a room present in the state. "
        "Use ask_clarification when required information is missing; for this pilot the only "
        "supported missing_field is room. Use no_action only when the request is unsafe or cannot "
        "be represented by the available actions."
    )
    user = (
        f"Resident request: {scenario['resident_request']}\n"
        f"Visible state JSON: {json.dumps(compact_state, ensure_ascii=False, sort_keys=True)}"
    )
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def build_prompt(scenario: dict[str, Any]) -> str:
    return "\n".join(f"{message['role']}: {message['content']}" for message in build_messages(scenario))


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


def query_llama_server(server_url: str, messages: list[dict[str, str]], timeout_s: float, params: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "messages": messages,
        "temperature": params["temperature"],
        "max_tokens": params["max_tokens"],
        "seed": params["seed"],
        "cache_prompt": False,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "smart_home_action", "strict": True, "schema": ACTION_JSON_SCHEMA},
        },
    }
    started = time.monotonic()
    result: dict[str, Any] = {
        "transport": "http_chat_completions",
        "schema_constrained": True,
        "server_url": server_url,
        "request_payload": payload,
        "completed": False,
        "http_status": None,
        "elapsed_s": None,
        "raw_response": "",
        "model_content": "",
        "usage": {},
        "timings": {},
        "finish_reason": None,
        "limit_reached": False,
        "error": None,
    }
    try:
        status, parsed, raw_body = _http_json(f"{server_url.rstrip('/')}/v1/chat/completions", payload, timeout_s)
        result["http_status"] = status
        result["raw_response"] = raw_body
        if status != 200:
            result["error"] = f"http_status_{status}"
            return result
        result["completed"] = True
        result["usage"] = parsed.get("usage", {})
        result["timings"] = parsed.get("timings", {})
        choices = parsed.get("choices", [])
        if choices:
            result["finish_reason"] = choices[0].get("finish_reason")
            result["limit_reached"] = result["finish_reason"] in {"length", "max_tokens"}
            result["model_content"] = choices[0].get("message", {}).get("content", "")
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
    if name == "ask_clarification" and action["missing_field"] != "room":
        return {"valid": False, "reason": "invalid_missing_field"}
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
        # Operational policy only: the evaluator must never reach this function.
        request_text = normalize_text(scenario["resident_request"])
        named = [r for r in scenario["initial_state"]["rooms"]
                 if re.search(r"\b" + re.escape(normalize_text(r)) + r"\b", request_text)]
        location = scenario["initial_state"].get("known_location")
        if not named and location not in scenario["initial_state"]["rooms"]:
            return {"allowed": False, "reason": "insufficient_room_information",
                    "policy": "room_evidence_v1"}
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


def normalize_text(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", text.lower())
                   if unicodedata.category(c) != "Mn")


def clarification_question_review(action: dict[str, Any], evaluator: dict[str, Any]) -> dict[str, Any]:
    question = normalize_text(action.get("question", "")).strip()
    if action.get("missing_field") not in evaluator.get("missing_fields", []):
        return {"status": "fail", "reason": "missing_field_not_expected"}
    if not question:
        return {"status": "fail", "reason": "empty_question"}
    # Conservative full-question patterns; mere room words are never sufficient.
    patterns = [
        r"(?:em )?qual (?:ambiente|comodo|local)(?: (?:voce quer|deseja|devo|para) .+)?\??",
        r"(?:em )?qual (?:ambiente|comodo|local) (?:a |as |esta |estao |fica |ficam ).+\?",
        r"onde (?:devo|voce quer|deseja) (?:acender|apagar|ligar|desligar|alterar) (?:a |as )?(?:luz|luzes|iluminacao)\?",
        r"(?:sala ou quarto|quarto ou sala)\?",
    ]
    if any(re.fullmatch(pattern, question) for pattern in patterns):
        return {"status": "pass", "reason": "explicit_request_for_missing_room", "method": "conservative_fullmatch_v1"}
    return {"status": "pending_manual_review", "reason": "semantic_question_review_required",
            "question": action.get("question"), "method": "conservative_fullmatch_v1"}


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
    manual_review = None
    if action is not None and action["action"] == "ask_clarification":
        review = clarification_question_review(action, evaluator)
        manual_review = {"clarification_question": review}
        checks.append({"name": "clarification_allowed", "passed": bool(evaluator.get("clarification_is_success", False))})
        checks.append({"name": "clarification_missing_field", "passed": review["status"] == "pass", "review": review})
    if action is not None and action["action"] == "no_action":
        checks.append({"name": "no_action_policy", "passed": bool(evaluator.get("no_action_is_success", False))})
    pending = any((item.get("review") or {}).get("status") == "pending_manual_review" for item in checks)
    return {"review_pending": pending, "task_completed": bool(checks) and all(item["passed"] for item in checks) and not pending, "checks": checks, "manual_review": manual_review}


def run_scenario(
    scenario: dict[str, Any],
    server_url: str,
    timeout_s: float,
    params: dict[str, Any],
) -> dict[str, Any]:
    messages = build_messages(scenario)
    prompt = "\n".join(f"{message['role']}: {message['content']}" for message in messages)
    inference = query_llama_server(server_url, messages, timeout_s, params)
    if inference["completed"] and not inference.get("limit_reached"):
        parsed = parse_model_action(inference["model_content"])
    else:
        reason = "generation_limit_reached" if inference.get("limit_reached") else inference["error"] or "incomplete_execution"
        parsed = {"structured_valid": False, "action": None, "reason": reason}
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
        "messages": messages,
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
