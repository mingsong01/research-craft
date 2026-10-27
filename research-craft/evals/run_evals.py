#!/usr/bin/env python3
"""Validate compact behavioral eval contracts without calling an external model."""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
scenarios = json.loads((HERE / "scenarios.json").read_text(encoding="utf-8"))
trigger_scenarios = json.loads((HERE / "trigger_scenarios.json").read_text(encoding="utf-8"))
forward_cases = json.loads((HERE / "forward_cases.json").read_text(encoding="utf-8"))
market_craft_cases = json.loads((HERE / "market_craft_cases.json").read_text(encoding="utf-8"))
failures = []
required_ids = set("ABCDEFGHIJKLMNOPQRSTU")
ids = {scenario.get("id") for scenario in scenarios}
if ids != required_ids:
    failures.append(f"scenario IDs differ: {sorted(ids)}")

for scenario in scenarios:
    sid = scenario["id"]
    if scenario["record_level"] not in {"QUICK", "TRACKED", "FORMAL"}:
        failures.append(f"{sid}: invalid record level")
    if scenario.get("record_level") == "QUICK" and scenario.get("create_records"):
        failures.append(f"{sid}: QUICK must not create records by default")
    if "do not modify" in scenario["request"].lower() and scenario.get("implementation_allowed"):
        failures.append(f"{sid}: analysis-only request permits implementation")
    if "gb" in scenario["request"].lower() and scenario.get("context_strategy") != "compute-before-expand":
        failures.append(f"{sid}: large input lacks computation-first handling")
    if "unpublished" in scenario["request"].lower() and scenario.get("externalize_private_data") is not False:
        failures.append(f"{sid}: private data could be externalized")
    if "raw" in scenario["request"].lower() and scenario.get("raw_immutable") is not True:
        failures.append(f"{sid}: raw artifact immutability missing")
    if "expensive" in scenario["request"].lower() and scenario.get("requires_confirmation") is not True:
        failures.append(f"{sid}: high-cost action lacks confirmation")
    if "continue" in scenario["request"].lower() and (scenario.get("context_strategy") != "state-one-row-one-detail" or scenario.get("forbid_full_history_scan") is not True):
        failures.append(f"{sid}: resume path loads excess context")
    if "token" in scenario["request"].lower() and scenario.get("redact_secrets") is not True:
        failures.append(f"{sid}: secret redaction missing")
    if "upload" in scenario["request"].lower() and (scenario.get("externalize_private_data") is not False or scenario.get("requires_confirmation") is not True):
        failures.append(f"{sid}: external upload safety missing")
    if "causal" in scenario["request"].lower() and scenario.get("separate_significance_effect_causality") is not True:
        failures.append(f"{sid}: statistical significance is conflated with causality")
    if "figure" in scenario["request"].lower() and (scenario.get("honest_visualization") is not True or scenario.get("figure_provenance") is not True):
        failures.append(f"{sid}: visualization integrity or provenance missing")
    if "latest" in scenario["request"].lower() and (scenario.get("fresh_primary_search") is not True or scenario.get("bounded_novelty_claim") is not True):
        failures.append(f"{sid}: frontier or novelty workflow missing")
    if "speedup" in scenario["request"].lower() and (scenario.get("correctness_before_speed") is not True or scenario.get("regression_required") is not True):
        failures.append(f"{sid}: software research verification missing")
    if "dashboards disagree" in scenario["request"].lower() and (scenario.get("separate_data_quality_from_analysis") is not True or scenario.get("reconcile_grain_definition_freshness") is not True):
        failures.append(f"{sid}: source quality and analysis validation are conflated")
    if "systematic literature review" in scenario["request"].lower() and (scenario.get("review_protocol_required") is not True or scenario.get("search_log_required") is not True):
        failures.append(f"{sid}: systematic review lacks protocol or reproducible search log")
    if "broadly investigate" in scenario["request"].lower() and (scenario.get("maximum_initial_lanes", 99) > 3 or scenario.get("router_owns_synthesis") is not True):
        failures.append(f"{sid}: broad request lacks minimum-lane routing")
    if "validate this report" in scenario["request"].lower() and scenario.get("analysis_readiness_required") is not True:
        failures.append(f"{sid}: report validation lacks decision-readiness outcome")
    if not scenario.get("claim_policy"):
        failures.append(f"{sid}: claim policy missing")

trigger_ids = [item.get("id") for item in trigger_scenarios]
if len(trigger_scenarios) != 20 or len(trigger_ids) != len(set(trigger_ids)):
    failures.append("trigger scenarios must contain 20 unique cases")
if sum(1 for item in trigger_scenarios if item.get("should_trigger") is True) != 10:
    failures.append("trigger scenarios must contain 10 positive cases")
if sum(1 for item in trigger_scenarios if item.get("should_trigger") is False) != 10:
    failures.append("trigger scenarios must contain 10 negative cases")

for case in forward_cases:
    cid = case.get("id", "unknown")
    if case.get("expected_level") not in {"QUICK", "TRACKED", "FORMAL"}:
        failures.append(f"{cid}: invalid expected level")
    if not case.get("required_behaviors") or not case.get("forbidden_behaviors"):
        failures.append(f"{cid}: behavior contract missing")
    weights = [item.get("weight") for item in case.get("rubric", [])]
    if not weights or any(not isinstance(weight, int) or weight <= 0 for weight in weights) or sum(weights) != 100:
        failures.append(f"{cid}: rubric weights must be positive integers summing to 100")

expected_craft = {
    "hypothesis-rivals", "pseudoreplication", "factorial-interaction",
    "statistics-equivalence", "debug-root-cause", "literature-boundary",
    "writing-evidence", "reviewer-disagreement", "data-lineage",
    "visual-artifact",
}
craft_ids = {case.get("id") for case in market_craft_cases}
if craft_ids != expected_craft:
    failures.append(f"market craft IDs differ: {sorted(craft_ids)}")
for case in market_craft_cases:
    cid = case.get("id", "unknown")
    if not case.get("hidden_trap"):
        failures.append(f"{cid}: missing hidden trap")
    if len(case.get("required_behaviors", [])) < 3:
        failures.append(f"{cid}: fewer than three required behaviors")
    if not case.get("hard_failures"):
        failures.append(f"{cid}: hard-failure contract missing")
    if case.get("artifact_required") and not case.get("inspection_required"):
        failures.append(f"{cid}: artifact case lacks inspection requirement")

if failures:
    print(json.dumps({"ok": False, "failures": failures}, indent=2))
    sys.exit(1)
print(json.dumps({"ok": True, "policy_scenarios": len(scenarios), "trigger_scenarios": len(trigger_scenarios), "forward_cases": len(forward_cases), "market_craft_cases": len(market_craft_cases), "quality_gates": {"research_rigor": True, "data_quality": True, "analysis_validation": True, "systematic_review": True, "statistics_causality": True, "literature_frontier": True, "visualization": True, "software_reproducibility": True, "artifact_qa": True, "trigger_precision": True, "token_context": True, "safety": True, "usability": True}}, indent=2))
