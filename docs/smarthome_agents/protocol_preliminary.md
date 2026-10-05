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

The first pilot scenario is `dev-001-simple-light`. The resident asks for more light in the occupied room. The successful action is turning the `sala` light on, without changing the `quarto` or HVAC state.
