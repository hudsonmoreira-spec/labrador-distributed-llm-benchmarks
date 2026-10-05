# Preliminary Protocol

Status: draft. Not frozen for the main campaign.

## Conditions

A. Rule-based automation with explicit notebook logic.

B. Single Labrador agent with complete simulated context.

C. Three specialized Labrador agents collaborating over structured messages: comfort, energy, and routine.

The same model must be used in B and C. A later equivalent-generation-budget condition is required to separate collaboration effects from extra inference budget.

## Scenario Requirements

Development set: 12 scenarios for implementation validation only.

Evaluation set: at least 48 reserved scenarios across:

- simple and clear requests;
- multi-room requests;
- comfort versus consumption conflicts;
- different resident preferences;
- ambiguous requests requiring clarification;
- missing or contradictory data.

Each scenario must define initial state, resident request, per-agent information, allowed and forbidden actions, success conditions, and acceptable non-action or clarification cases.

## Metrics

Each run records task success, proposed violations, blocked actions, executed actions, clarifications, wall-clock time, model queries, messages, rounds, tokens when available, communication failures, invalid output, timeouts, and process memory collection method.

Model conditions require at least five repetitions per evaluation case. Repetitions are grouped under the scenario and are not treated as independent scenarios.

## Current Pilot

The original `dev-001-simple-light` pilot from commit `aeff69b` is pre-correction evidence only and must not be used as campaign evidence.

The corrected single-agent pilot uses four development scenarios and a resident `llama-server`. It separates execution completion, structured response validity, action permission, action application, and task completion. The evaluator checks scenario-defined final state, unchanged fields, prohibited actions, and clarification/no-action policy. Sensor fields named `luminosity_lux_initial` are initial readings only; the simulator does not update them after light actions and does not use them as final illumination measurements.

Before expanding to three agents, the single-agent output contract must be improved because the 2026-10-05 resident-server pilot completed transport successfully but produced 0/12 structurally valid responses.
