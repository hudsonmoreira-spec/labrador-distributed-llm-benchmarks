#!/usr/bin/env python3
"""Software checks for the smart-home pilot; these are not model results."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments" / "smarthome_agents" / "scripts"))

from smarthome_pilot import (  # noqa: E402
    build_prompt,
    evaluate_scenario,
    load_json,
    parse_model_action,
    run_scenario,
    validate_action_permissions,
)


SCENARIO_DIR = ROOT / "experiments" / "smarthome_agents" / "scenarios"


def scenario(name: str) -> dict:
    return load_json(SCENARIO_DIR / name)


class PilotLogicTests(unittest.TestCase):
    def test_prompt_echo_is_not_accepted(self) -> None:
        sc = scenario("dev_light_on_sala.json")
        parsed = parse_model_action(build_prompt(sc))
        self.assertFalse(parsed["structured_valid"])

    def test_timeout_or_execution_failure_cannot_succeed(self) -> None:
        sc = scenario("dev_light_on_sala.json")

        def fake_query(*_args, **_kwargs):
            return {"completed": False, "error": "timeout", "model_content": "", "elapsed_s": 1.0}

        import smarthome_pilot

        original = smarthome_pilot.query_llama_server
        smarthome_pilot.query_llama_server = fake_query
        try:
            result = run_scenario(sc, "http://example.invalid", 0.1, {"temperature": 0, "max_tokens": 16, "seed": 1})
        finally:
            smarthome_pilot.query_llama_server = original
        self.assertFalse(result["result_flags"]["task_completed"])
        self.assertFalse(result["result_flags"]["execution_completed"])

    def test_malformed_json_and_unexpected_fields_are_rejected(self) -> None:
        self.assertFalse(parse_model_action("{bad")["structured_valid"])
        parsed = parse_model_action('{"action":"set_light","room":"sala","value":"on","extra":1}')
        self.assertFalse(parsed["structured_valid"])
        self.assertEqual(parsed["reason"], "unexpected_fields")

    def test_light_on_and_off_prompts_have_no_fixed_contradictory_hint(self) -> None:
        on_prompt = build_prompt(scenario("dev_light_on_sala.json"))
        off_prompt = build_prompt(scenario("dev_light_off_sala.json"))
        self.assertIn("Acenda a luz da sala.", on_prompt)
        self.assertIn("Apague a luz da sala.", off_prompt)
        self.assertNotIn("resident is in sala and wants more light for reading", on_prompt)
        self.assertNotIn("resident is in sala and wants more light for reading", off_prompt)

    def test_wrong_room_action_fails_evaluation(self) -> None:
        sc = scenario("dev_light_on_sala.json")
        action = {"action": "set_light", "room": "quarto", "value": "on"}
        permission = validate_action_permissions(sc, action)
        final_state = sc["initial_state"].copy()
        evaluation = evaluate_scenario(sc, sc["initial_state"], final_state, action, True, True, permission)
        self.assertFalse(evaluation["task_completed"])

    def test_unchanged_states_are_checked(self) -> None:
        sc = scenario("dev_light_quarto_preserve_sala.json")
        bad_final = load_json(SCENARIO_DIR / "dev_light_quarto_preserve_sala.json")["initial_state"]
        bad_final["rooms"]["quarto"]["light"] = "on"
        bad_final["rooms"]["sala"]["light"] = "off"
        action = {"action": "set_light", "room": "quarto", "value": "on"}
        permission = validate_action_permissions(sc, action)
        evaluation = evaluate_scenario(sc, sc["initial_state"], bad_final, action, True, True, permission)
        self.assertFalse(evaluation["task_completed"])

    def test_clarification_and_no_action_policies(self) -> None:
        ambiguous = scenario("dev_ambiguous_light_clarify.json")
        ask = {"action": "ask_clarification", "question": "Qual ambiente?"}
        permission = validate_action_permissions(ambiguous, ask)
        ok = evaluate_scenario(ambiguous, ambiguous["initial_state"], ambiguous["initial_state"], ask, True, True, permission)
        self.assertTrue(ok["task_completed"])

        no_action = {"action": "no_action", "reason": "Ambiente desconhecido."}
        permission = validate_action_permissions(ambiguous, no_action)
        bad = evaluate_scenario(ambiguous, ambiguous["initial_state"], ambiguous["initial_state"], no_action, True, True, permission)
        self.assertFalse(bad["task_completed"])


if __name__ == "__main__":
    unittest.main()
