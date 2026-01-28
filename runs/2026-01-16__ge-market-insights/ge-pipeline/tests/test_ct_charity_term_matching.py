import re
from pathlib import Path

import yaml


def _load_terms():
    path = Path(__file__).resolve().parents[1] / "config" / "ct_charity_terms.yaml"
    data = yaml.safe_load(path.read_text()) or {}
    return data.get("terms") or []


def test_cardiographe_regression_no_substring_collision():
    """Regression: old pattern matched ECHOCARDIOGRAPHY via CARDIOGRAPH substring.

    We want CardioGraphe to only match the intended token(s) and avoid
    unrelated cardiology words like ECHOCARDIOGRAPHY/CARDIOGRAPHY.
    """

    terms = _load_terms()
    term = next((t for t in terms if t.get("term_key") == "CARDIOGRAPHE"), None)
    assert term is not None

    new_pattern = term["pattern"]
    # Example of the problematic prior pattern (kept here to prove the regression).
    old_pattern = r"CARDIO\s*GRAPHE|CARDIOGRAPHE|CARDIOGRAPH"

    false_positive_text = "CONSULTING CARDIOLOGISTS - ECHOCARDIOGRAPHY LAB"
    intended_text = "GE CARDIOGRAPHE"

    assert re.search(old_pattern, false_positive_text, flags=re.IGNORECASE) is not None
    assert re.search(new_pattern, false_positive_text, flags=re.IGNORECASE) is None
    assert re.search(new_pattern, intended_text, flags=re.IGNORECASE) is not None


def test_frontier_ex_requires_frontier_and_ex_nearby():
    terms = _load_terms()
    term = next((t for t in terms if t.get("term_key") == "REVOLUTION_FRONTIER_EX"), None)
    assert term is not None
    pattern = term["pattern"]

    assert re.search(pattern, "FEDEX SHIPPING", flags=re.IGNORECASE) is None
    assert re.search(pattern, "FRONTIER LIFT FOR VCT", flags=re.IGNORECASE) is None
    assert re.search(pattern, "REVOLUTION FRONTIER EX", flags=re.IGNORECASE) is not None

    # Alias support (only meaningful if present in real data, but safe regardless):
    assert re.search(pattern, "REVOLUTION FRONTIER EXTREME", flags=re.IGNORECASE) is not None

    # Prevent substring collisions
    assert re.search(pattern, "FRONTIER EXCHANGE", flags=re.IGNORECASE) is None

    # Guardrail: do not allow matches to span across the concatenated field separator.
    assert re.search(pattern, "FRONTIER LIFT | EX", flags=re.IGNORECASE) is None


def test_frontier_es_requires_frontier_and_es_nearby():
    terms = _load_terms()
    term = next((t for t in terms if t.get("term_key") == "REVOLUTION_FRONTIER_ES"), None)
    assert term is not None
    pattern = term["pattern"]

    assert re.search(pattern, "ES SHIPPING", flags=re.IGNORECASE) is None
    assert re.search(pattern, "FRONTIER LIFT FOR VCT", flags=re.IGNORECASE) is None
    assert re.search(pattern, "REVOLUTION FRONTIER ES", flags=re.IGNORECASE) is not None

    # Guardrail: do not allow matches to span across the concatenated field separator.
    assert re.search(pattern, "FRONTIER LIFT | ES", flags=re.IGNORECASE) is None


def test_frontier_el_requires_frontier_and_el_nearby():
    terms = _load_terms()
    term = next((t for t in terms if t.get("term_key") == "REVOLUTION_FRONTIER_EL"), None)
    assert term is not None
    pattern = term["pattern"]

    assert re.search(pattern, "EL SHIPPING", flags=re.IGNORECASE) is None
    assert re.search(pattern, "FRONTIER LIFT CT UPGRADE", flags=re.IGNORECASE) is None
    assert re.search(pattern, "REVOLUTION FRONTIER EL", flags=re.IGNORECASE) is not None

    # Alias support (only meaningful if present in real data, but safe regardless):
    assert re.search(pattern, "REVOLUTION FRONTIER ELITE", flags=re.IGNORECASE) is not None

    # Prevent substring collisions
    assert re.search(pattern, "FRONTIER ELEMENT", flags=re.IGNORECASE) is None

    # Guardrail: do not allow matches to span across the concatenated field separator.
    assert re.search(pattern, "FRONTIER LIFT | EL", flags=re.IGNORECASE) is None
