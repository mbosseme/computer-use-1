# Skill: Analytical Decision Modeling

## Context
Use this skill when asked to perform a complex analysis, underwriting, or trade-off decision where:
1.  **Multiple variables** are uncertain (e.g., "What if rent is lower?", "What if usage is higher?").
2.  **Evidence** needs to be gathered from external sources to ground the assumptions.
3.  **Auditable logic** is required (not just a text-generated answer).

## The Workflow Pattern
Do not guess. Do not produce a single point estimate. Follow this 4-step loop:
1.  **Evidence Ledger**: Create a markdown file to log sources and extracted facts.
2.  **Data/Logic Split**: Define `inputs.json` (assumptions) and `model.py` (logic) separately.
3.  **Scenario Grid**: Use Python to generate a Cartesian product of all reasonable inputs.
4.  **Decision Memo**: Write a synthesized report focusing on "Boundary Conditions" (e.g., "This works ONLY IF X > Y").

---

## 1. The Evidence Ledger (`research/EVIDENCE_LEDGER.md`)
**Why:** Prevents hallucinations and provides an audit trail for where numbers came from.

### Template
```markdown
# Evidence Ledger

## 1. Market Rates (Source A)
*   **Source:** [Link Title](URL)
*   **Date:** YYYY-MM-DD
*   **Extract:** "Text quote from page..."
*   **Derived Input:** `rent_low` = $2,400

## 2. Regulatory / Rules
*   **Source:** [Doc Link](URL)
*   **Status:** Verified / Unverified
*   **Key Constraint:** "30-day minimum stay required."
```

## 2. Data/Logic Separation
**Why:** Allows iteration on assumptions without breaking code. Allows the user to review assumptions easily.

### `inputs/model_inputs.json`
```json
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
```

## 3. The Scenario Grid Script (`scripts/model.py`)
**Why:** Answers "Under what conditions does this fail?" instead of "What is the answer?"

### Python Pattern
```python
import itertools
import json
import csv

def run_scenario_grid():
    with open("inputs/model_inputs.json") as f:
        data = json.load(f)
    
    # create Cartesian product of variables
    keys = data["scenarios"].keys()
    values = data["scenarios"].values()
    combinations = list(itertools.product(*values))
    
    results = []
    for combo in combinations:
        scenario = dict(zip(keys, combo))
        
        # --- CORE LOGIC HERE ---
        # accessing constants: data["constants"]["tax_rate"]
        # result = calculate_metric(scenario)
        # -----------------------
        
        scenario["result_metric"] = 123 # calculated value
        results.append(scenario)
        
    # Export to CSV for audit
    # Write to Markdown Summary for user
```

## 4. The Decision Memo (`decision_memo.md`)
**Why:** The user acts on *insight*, not just raw data.

### Template
```markdown
# Decision Memo: [Topic]

**Status:** GO / NO-GO / CAUTION
**Critical Gate:** [The #1 variable that kills the deal]

## Executive Summary
This works financially **IF AND ONLY IF** [Condition A] is met.
If [Condition B] happens, the project yields negative value.

## The Economics (Range)
We modeled [N] scenarios.
*   **Best Case:** Result X (Requires: [Conditions])
*   **Stress Case:** Result Y (Happens if: [Conditions])

## Critical Operating Gates (Must Verify)
Before proceeding, confirm:
1.  [Gate 1]
2.  [Gate 2]

## Recommendation
Proceed only if you are comfortable with [Risk Factor].
```
