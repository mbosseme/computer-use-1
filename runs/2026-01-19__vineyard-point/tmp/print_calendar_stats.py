import importlib.util
import json
from pathlib import Path
import sys

script_path = Path("runs/2026-01-19__vineyard-point/scripts/vineyard_point_model.py")
spec = importlib.util.spec_from_file_location("vp_model", script_path)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)

inputs = json.loads(Path("runs/2026-01-19__vineyard-point/inputs/model_inputs.json").read_text())

base = {
    "down_payment_pct": 0.2,
    "interest_rate": 0.07,
    "term_years": 30,
    "furnish_budget": 25000,
    "monthly_rent": 2800,
    "fill_rate": 0.75,
    "horizon_years": 7,
}

for owner_key in inputs["owner_use"]["scenarios"].keys():
    scenario = dict(base)
    scenario["owner_use_scenario"] = owner_key
    r = mod.compute_metrics(inputs, scenario, model_year=2026)
    print(owner_key)
    print(f"  owner_days: {r['owner_days']}")
    print(f"  leasable_days (calendar): {r['leasable_days']}")
    print(f"  lease_count (30d segments): {r['lease_count']}")
    print(f"  tenant_months @ fill 0.75: {r['tenant_months']:.2f}")
