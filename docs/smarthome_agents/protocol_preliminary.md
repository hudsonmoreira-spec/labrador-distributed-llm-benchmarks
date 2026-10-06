> Registro histórico: o escopo abaixo foi substituído pelo estudo reduzido congelado em `experiments/smarthome_agents/study_v1/protocol.md`. Colaboração entre agentes não foi executada; versões atuais do artigo estão em `paper/smarthome_agents/study_v1/`.

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

Before expanding to three agents, the single-agent output contract must remain schema-constrained through `/v1/chat/completions`. A follow-up schema-constrained development campaign, after fixing scenario-prohibited action blocking, produced 12/12 structurally valid responses and 9/12 task completions, with all failures concentrated in the ambiguous-room case. This confirms that the remaining blocker is decision behavior for missing information, not basic transport or parser correctness.
