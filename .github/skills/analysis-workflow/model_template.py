"""
Scenario Grid Model Template
============================

A minimal, reusable pattern for "What if X/Y/Z?" analyses.

Usage:
1. Copy this file to `runs/<RUN_ID>/scripts/model.py`.
2. Edit `load_inputs()` to load your `inputs.json`.
3. Replace `compute_scenario()` with your domain logic.
4. Run: `python model.py`

Outputs:
- CSV with all scenario results (for audit).
- Markdown summary table (for decision memo).
"""

from __future__ import annotations

import csv
import itertools
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# -----------------------------------------------------------------------------
# 1. CONFIGURATION
# -----------------------------------------------------------------------------

# Path to your inputs file (relative to script location or absolute)
DEFAULT_INPUTS_PATH = Path("../inputs/model_inputs.json")
DEFAULT_OUTPUT_CSV = Path("../exports/scenario_results.csv")
DEFAULT_OUTPUT_MD = Path("../exports/scenario_summary.md")


# -----------------------------------------------------------------------------
# 2. LOAD INPUTS
# -----------------------------------------------------------------------------

def load_inputs(path: Path = DEFAULT_INPUTS_PATH) -> dict[str, Any]:
    """Load the JSON inputs file."""
    with open(path) as f:
        return json.load(f)


# -----------------------------------------------------------------------------
# 3. SCENARIO GRID GENERATION
# -----------------------------------------------------------------------------

def generate_scenario_grid(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Generate a Cartesian product of all scenario variables.
    
    Expected structure in inputs.json:
    {
      "scenarios": {
        "price_options": [100, 120, 140],
        "volume_options": [1000, 5000, 10000]
      },
      "constants": {
        "tax_rate": 0.25,
        "fixed_cost": 5000
      }
    }
    """
    scenarios_config = inputs.get("scenarios", {})
    
    if not scenarios_config:
        # No scenario variables; return a single empty scenario
        return [{}]
    
    keys = list(scenarios_config.keys())
    values = [scenarios_config[k] for k in keys]
    
    combinations = list(itertools.product(*values))
    
    return [dict(zip(keys, combo)) for combo in combinations]


# -----------------------------------------------------------------------------
# 4. CORE LOGIC (REPLACE THIS WITH YOUR DOMAIN LOGIC)
# -----------------------------------------------------------------------------

def compute_scenario(scenario: dict[str, Any], constants: dict[str, Any]) -> dict[str, Any]:
    """
    Compute the result for a single scenario.
    
    Args:
        scenario: A dict with the scenario variable values (e.g., {"price": 100, "volume": 1000}).
        constants: A dict with fixed constants (e.g., {"tax_rate": 0.25}).
    
    Returns:
        A dict with the scenario inputs + computed outputs.
    """
    # Example: Simple profit calculation
    price = scenario.get("price_options", 100)
    volume = scenario.get("volume_options", 1000)
    
    tax_rate = constants.get("tax_rate", 0.25)
    fixed_cost = constants.get("fixed_cost", 5000)
    
    revenue = price * volume
    profit_before_tax = revenue - fixed_cost
    profit_after_tax = profit_before_tax * (1 - tax_rate)
    
    # Return the scenario inputs + computed outputs
    return {
        **scenario,
        "revenue": revenue,
        "profit_before_tax": profit_before_tax,
        "profit_after_tax": profit_after_tax,
    }


# -----------------------------------------------------------------------------
# 5. RUN ALL SCENARIOS
# -----------------------------------------------------------------------------

def run_all_scenarios(inputs: dict[str, Any]) -> list[dict[str, Any]]:
    """Run all scenarios and return results."""
    constants = inputs.get("constants", {})
    scenarios = generate_scenario_grid(inputs)
    
    results = []
    for scenario in scenarios:
        result = compute_scenario(scenario, constants)
        results.append(result)
    
    return results


# -----------------------------------------------------------------------------
# 6. EXPORT RESULTS
# -----------------------------------------------------------------------------

def export_to_csv(results: list[dict[str, Any]], path: Path = DEFAULT_OUTPUT_CSV) -> None:
    """Export results to CSV for audit."""
    if not results:
        print("No results to export.")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    fieldnames = list(results[0].keys())
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Exported {len(results)} scenarios to {path}")


def export_to_markdown(results: list[dict[str, Any]], path: Path = DEFAULT_OUTPUT_MD) -> None:
    """Export a summary table to Markdown."""
    if not results:
        print("No results to export.")
        return
    
    path.parent.mkdir(parents=True, exist_ok=True)
    
    headers = list(results[0].keys())
    
    lines = [
        "# Scenario Results Summary\n",
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    
    for row in results:
        values = [str(row.get(h, "")) for h in headers]
        lines.append("| " + " | ".join(values) + " |")
    
    with open(path, "w") as f:
        f.write("\n".join(lines))
    
    print(f"Exported summary to {path}")


# -----------------------------------------------------------------------------
# 7. MAIN
# -----------------------------------------------------------------------------

def main() -> None:
    """Main entry point."""
    inputs = load_inputs()
    results = run_all_scenarios(inputs)
    
    export_to_csv(results)
    export_to_markdown(results)
    
    print(f"\nCompleted: {len(results)} scenarios evaluated.")


if __name__ == "__main__":
    main()
