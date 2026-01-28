#!/usr/bin/env python3
"""ct_charity_outputs.py

Generates Charity CT presence + hierarchy extracts from the raw
`transaction_analysis_expanded` feed.

Outputs (written to snapshots/<RUN_ID>/):
- ct_charity_presence_summary.csv
- ct_charity_hierarchy_extract.csv
- ct_ct_text_discovery.csv
- ct_charity_term_debug_samples.csv

Auth: BigQuery Application Default Credentials (ADC).
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import yaml

# Allow running as a script without requiring PYTHONPATH=.
_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.bigquery_client import BigQueryClient

# Lock the table in code (directive requirement)
TABLE_FQN = os.getenv(
    "CT_CHARITY_TABLE_FQN",
    "abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded",
)

REQUIRED_MATCH_FIELDS = [
    "Facility_Product_Description",
    "Facility_Manufacturer_Name",
    "Facility_Vendor_Name",
    "Facility_Manufacturer_Catalog_Num",
    "Facility_Vendor_Catalog_Num",
    "Product_Description",
    "Manufacturer_Top_Parent_Name",
    "Manufacturer_Name",
    "Vendor_Top_Parent_Name",
    "Vendor_Name",
    "Brand_Name",
    "Manufacturer_Catalog_Number",
    "Vendor_Catalog_Number",
    "Contracted_Catalog_Number",
    "Current_Contracted_Catalog_Number",
    "Forecasted_Contracted_Catalog_Number",
    "Current_Contracted_Product_Description",
    "Forecasted_Contracted_Product_Description",
    "replaced_by_manufacturer_catalog_number",
    "Noiseless_Catalog_Number",
]

REQUIRED_SPEND_DATE_FIELDS = [
    "Base_Spend",
    "Quantity",
    "Transaction_Date",
    "Month",
]

HIERARCHY_CANDIDATES = [
    "Contract_Category",
    "product_group_category",
    "product_subcategory1",
    "product_subcategory2",
    "product_subcategory3",
    "UNSPSC_Segment_Code",
    "UNSPSC_Segment_Description",
    "UNSPSC_Class_Code",
    "UNSPSC_Class_Description",
    "UNSPSC_Commodity_Code",
    "UNSPSC_Commodity_Description",
]


def _load_terms(yaml_path: Path) -> list[dict[str, str]]:
    data = yaml.safe_load(yaml_path.read_text()) or {}
    terms = data.get("terms") or []
    out: list[dict[str, str]] = []
    fallback_order = 0
    for t in terms:
        if not isinstance(t, dict):
            continue
        fallback_order += 1
        term_order_raw = t.get("term_order")
        try:
            term_order = int(term_order_raw) if term_order_raw is not None else fallback_order
        except Exception:
            term_order = fallback_order
        term_key = str(t.get("term_key") or "").strip()
        term_label = str(t.get("term_label") or term_key).strip()
        pattern = str(t.get("pattern") or "").strip()
        if not term_key or not pattern:
            continue
        out.append(
            {
                "term_order": str(term_order),
                "term_key": term_key,
                "term_label": term_label,
                "pattern": pattern,
            }
        )
    return out


def _bq_escape_string(value: str) -> str:
    # BigQuery string literal escaping: single quotes are doubled.
    return value.replace("'", "''")


def _render_terms_cte(terms: Iterable[dict[str, str]]) -> str:
    rows = list(terms)
    if not rows:
        raise ValueError("No terms found. Populate config/ct_charity_terms.yaml")

    selects: list[str] = []
    for t in rows:
        term_order = _bq_escape_string(str(t.get("term_order") or "0"))
        term_key = _bq_escape_string(t["term_key"])
        term_label = _bq_escape_string(t.get("term_label") or t["term_key"])
        pattern = _bq_escape_string(t["pattern"])
        selects.append(
            f"    SELECT {term_order} AS term_order, '{term_key}' AS term_key, '{term_label}' AS term_label, r'{pattern}' AS pattern"
        )
    return "\n    UNION ALL\n".join(selects) + "\n"


def _render_any_pattern(terms: Iterable[dict[str, str]]) -> str:
    # Build a single alternation regex to prefilter rows before term-level matching.
    patterns = [t["pattern"].strip() for t in terms if (t.get("pattern") or "").strip()]
    if not patterns:
        return ""
    return "(?:" + ")|(?:".join(patterns) + ")"


def _available_fields(bq: BigQueryClient, table_fqn: str) -> set[str]:
    if not bq.client:
        raise RuntimeError("BigQuery client not initialized")

    try:
        table = bq.client.get_table(table_fqn)
    except Exception as e:
        print(f"WARNING: Could not fetch table schema for {table_fqn}: {e}")
        return set()

    return {field.name for field in table.schema}


def _warn_missing(fields: Iterable[str], available: set[str], label: str) -> None:
    missing = [f for f in fields if f not in available]
    if missing:
        print(f"WARNING: Missing {label} fields in table schema: {missing}")


def _coalesce_text_expr(available: set[str], columns: list[str]) -> str:
    # Build UPPER(CONCAT(IFNULL(col,''),' | ',...)) but only for columns that exist.
    present = [c for c in columns if c in available]
    if not present:
        return "UPPER('')"

    parts: list[str] = []
    for idx, col in enumerate(present):
        if idx > 0:
            parts.append("' | '")
        parts.append(f"IFNULL(CAST({col} AS STRING), '')")
    return "UPPER(CONCAT(" + ", ".join(parts) + "))"


def _coalesce_text_expr_from_exprs(exprs: list[str]) -> str:
    # Build UPPER(CONCAT(IFNULL(CAST(expr AS STRING),''),' | ',...)) from expressions.
    cleaned = [e.strip() for e in exprs if e and e.strip()]
    if not cleaned:
        return "UPPER('')"
    parts: list[str] = []
    for idx, expr in enumerate(cleaned):
        if idx > 0:
            parts.append("' | '")
        parts.append(f"IFNULL(CAST({expr} AS STRING), '')")
    return "UPPER(CONCAT(" + ", ".join(parts) + "))"


def _upper_text_expr(available: set[str], column: str) -> str:
    if column not in available:
        return "UPPER('')"
    return f"UPPER(IFNULL(CAST({column} AS STRING), ''))"


def _build_product_description_backfilled_expr(available: set[str]) -> str:
    # Backfilled description (manual exploration alignment):
    # Product_Description when present and not UNKNOWN/blank; else Facility_Product_Description.
    if "Product_Description" in available and "Facility_Product_Description" in available:
        return (
            "CASE WHEN Product_Description IS NOT NULL "
            "AND UPPER(TRIM(CAST(Product_Description AS STRING))) NOT IN ('UNKNOWN','') "
            "THEN Product_Description ELSE Facility_Product_Description END"
        )
    if "Product_Description" in available:
        return "Product_Description"
    if "Facility_Product_Description" in available:
        return "Facility_Product_Description"
    return "NULL"


def _build_is_ge_mfr_expr(available: set[str]) -> str:
    ge_regex = r"(?:\bGENERAL\s+ELECTRIC(?:\s+HEALTHCARE)?\b|\bGE\s+HEALTHCARE\b|\bG\s*\.?\s*E\b|\bGE\b)"

    # Prefer structured manufacturer identity; only fall back when those are missing.
    structured_fields = [
        "Manufacturer_Top_Parent_Name",
        "Manufacturer_Name",
        "Facility_Manufacturer_Name",
    ]
    structured_present = [f for f in structured_fields if f in available]

    fallback_fields = [
        # Secondary identity sources
        "Brand_Name",
        "Vendor_Top_Parent_Name",
        "Vendor_Name",
        "Facility_Vendor_Name",
        # Last resort: description text can contain explicit GE identifiers
        "Product_Description",
        "Facility_Product_Description",
    ]
    fallback_present = [f for f in fallback_fields if f in available]

    if not structured_present and not fallback_present:
        return "FALSE"

    structured_haystack = _coalesce_text_expr(available, structured_present) if structured_present else "UPPER('')"
    fallback_haystack = _coalesce_text_expr(available, fallback_present) if fallback_present else "UPPER('')"

    # Determine whether the structured manufacturer identity is populated.
    structured_has_value_checks: list[str] = []
    for f in structured_present:
        structured_has_value_checks.append(
            f"({f} IS NOT NULL AND TRIM(CAST({f} AS STRING)) != '')"
        )
    structured_has_value = "(" + " OR ".join(structured_has_value_checks) + ")" if structured_has_value_checks else "FALSE"

    return (
        "CASE "
        f"WHEN {structured_has_value} THEN REGEXP_CONTAINS({structured_haystack}, r'{ge_regex}') "
        f"ELSE REGEXP_CONTAINS({fallback_haystack}, r'{ge_regex}') "
        "END"
    )


def _render_date_where(start_date: str | None, end_date: str | None, available: set[str]) -> str:
    if "Transaction_Date" not in available:
        return ""

    clauses: list[str] = []
    if start_date:
        clauses.append(f"      AND DATE(Transaction_Date) >= DATE('{_bq_escape_string(start_date)}')")
    if end_date:
        clauses.append(f"      AND DATE(Transaction_Date) <= DATE('{_bq_escape_string(end_date)}')")
    if not clauses:
        return ""
    return "\n" + "\n".join(clauses) + "\n"


def _read_sql(path: Path) -> str:
    return path.read_text()


def _render_sql(
    template_sql: str,
    *,
    table_fqn: str,
    terms_cte: str,
    terms: list[dict[str, str]],
    available: set[str],
    start_date: str | None,
    end_date: str | None,
    any_pattern: str,
) -> str:
    # Required fields with graceful fallback
    spend_field = "Base_Spend" if "Base_Spend" in available else "Landed_Spend"
    quantity_field = "Quantity" if "Quantity" in available else "NULL"

    def _field_or_null(field: str) -> str:
        return field if field in available else "NULL"

    product_description_backfilled_expr = _build_product_description_backfilled_expr(available)

    # Facility-first matching inputs + standardized fallbacks.
    # We search ALL raw description and identity fields to maximize recall.
    match_text = _coalesce_text_expr_from_exprs(
        [
            _field_or_null("Product_Description"),
            _field_or_null("Facility_Product_Description"),
            _field_or_null("Facility_Manufacturer_Name"),
            _field_or_null("Facility_Vendor_Name"),
            _field_or_null("Facility_Manufacturer_Catalog_Num"),
            _field_or_null("Facility_Vendor_Catalog_Num"),
            _field_or_null("Manufacturer_Name"),
            _field_or_null("Manufacturer_Top_Parent_Name"),
            _field_or_null("Vendor_Name"),
            _field_or_null("Vendor_Top_Parent_Name"),
            _field_or_null("Manufacturer_Catalog_Number"),
            _field_or_null("Vendor_Catalog_Number"),
            _field_or_null("Brand_Name"),
            _field_or_null("Contracted_Catalog_Number"),
            _field_or_null("Current_Contracted_Catalog_Number"),
            _field_or_null("Forecasted_Contracted_Catalog_Number"),
            _field_or_null("Current_Contracted_Product_Description"),
            _field_or_null("Forecasted_Contracted_Product_Description"),
            _field_or_null("replaced_by_manufacturer_catalog_number"),
            _field_or_null("Noiseless_Catalog_Number"),
        ]
    )

    # Examples should use backfilled description.
    example_desc_expr = product_description_backfilled_expr

    # Manufacturer gating: restrict "anywhere" Charity presence to GE-only rows.
    is_ge_mfr_expr = _build_is_ge_mfr_expr(available)

    date_where = _render_date_where(start_date, end_date, available)

    # Hierarchy fields (only those present)
    hierarchy_fields = [c for c in HIERARCHY_CANDIDATES if c in available and c != "Contract_Category"]

    hierarchy_select = ""
    hierarchy_output = ""
    if hierarchy_fields:
        # base_raw SELECT: these fields must end with a comma because match_text follows.
        hierarchy_select = "\n      " + ",\n      ".join(hierarchy_fields) + ",\n"
        # output SELECT: prefix with a comma after Contract_Category, but do NOT trail with a comma.
        hierarchy_output = ",\n  " + ",\n  ".join(hierarchy_fields) + "\n"

    rendered = (
        template_sql
        .replace("{{TABLE_FQN}}", table_fqn)
        .replace("{{TERMS_CTE}}", terms_cte)
        .replace("{{ANY_PATTERN}}", _bq_escape_string(any_pattern))
        .replace("{{SPEND_FIELD}}", spend_field)
        .replace("{{QUANTITY_FIELD}}", quantity_field)
        .replace("{{CONTRACT_CATEGORY_FIELD}}", _field_or_null("Contract_Category"))
        .replace("{{FACILITY_PRODUCT_DESCRIPTION_FIELD}}", _field_or_null("Facility_Product_Description"))
        .replace("{{FACILITY_MANUFACTURER_NAME_FIELD}}", _field_or_null("Facility_Manufacturer_Name"))
        .replace("{{FACILITY_VENDOR_NAME_FIELD}}", _field_or_null("Facility_Vendor_Name"))
        .replace("{{PRODUCT_DESCRIPTION_FIELD}}", _field_or_null("Product_Description"))
        .replace("{{MANUFACTURER_CATALOG_NUMBER_FIELD}}", _field_or_null("Manufacturer_Catalog_Number"))
        .replace("{{MANUFACTURER_TOP_PARENT_NAME_FIELD}}", _field_or_null("Manufacturer_Top_Parent_Name"))
        .replace("{{MANUFACTURER_NAME_FIELD}}", _field_or_null("Manufacturer_Name"))
        .replace("{{VENDOR_TOP_PARENT_NAME_FIELD}}", _field_or_null("Vendor_Top_Parent_Name"))
        .replace("{{VENDOR_NAME_FIELD}}", _field_or_null("Vendor_Name"))
        .replace("{{BRAND_NAME_FIELD}}", _field_or_null("Brand_Name"))
        .replace("{{VENDOR_CATALOG_NUMBER_FIELD}}", _field_or_null("Vendor_Catalog_Number"))
        .replace(
            "{{FACILITY_MANUFACTURER_CATALOG_NUM_FIELD}}",
            _field_or_null("Facility_Manufacturer_Catalog_Num"),
        )
        .replace(
            "{{FACILITY_VENDOR_CATALOG_NUM_FIELD}}",
            _field_or_null("Facility_Vendor_Catalog_Num"),
        )
        .replace("{{IF_PRODUCT_DESCRIPTION_FIELD}}", _field_or_null("Product_Description"))
        .replace("{{IF_MANUFACTURER_TOP_PARENT_NAME_FIELD}}", _field_or_null("Manufacturer_Top_Parent_Name"))
        .replace("{{IF_MANUFACTURER_NAME_FIELD}}", _field_or_null("Manufacturer_Name"))
        .replace("{{IF_VENDOR_TOP_PARENT_NAME_FIELD}}", _field_or_null("Vendor_Top_Parent_Name"))
        .replace("{{IF_VENDOR_NAME_FIELD}}", _field_or_null("Vendor_Name"))
        .replace("{{IF_BRAND_NAME_FIELD}}", _field_or_null("Brand_Name"))
        .replace("{{PRODUCT_DESCRIPTION_BACKFILLED_EXPR}}", product_description_backfilled_expr)
        .replace("{{MATCH_TEXT_EXPR}}", match_text)
        .replace("{{EXAMPLE_DESC_EXPR}}", example_desc_expr)
        .replace("{{CONTRACTED_CATALOG_NUMBER_FIELD}}", _field_or_null("Contracted_Catalog_Number"))
        .replace("{{CURRENT_CONTRACTED_CATALOG_NUMBER_FIELD}}", _field_or_null("Current_Contracted_Catalog_Number"))
        .replace("{{FORECASTED_CONTRACTED_CATALOG_NUMBER_FIELD}}", _field_or_null("Forecasted_Contracted_Catalog_Number"))
        .replace("{{CURRENT_CONTRACTED_PRODUCT_DESCRIPTION_FIELD}}", _field_or_null("Current_Contracted_Product_Description"))
        .replace("{{FORECASTED_CONTRACTED_PRODUCT_DESCRIPTION_FIELD}}", _field_or_null("Forecasted_Contracted_Product_Description"))
        .replace("{{REPLACED_BY_MANUFACTURER_CATALOG_NUMBER_FIELD}}", _field_or_null("replaced_by_manufacturer_catalog_number"))
        .replace("{{NOISELESS_CATALOG_NUMBER_FIELD}}", _field_or_null("Noiseless_Catalog_Number"))
        .replace("{{DATE_WHERE}}", date_where)
        .replace("{{HIERARCHY_FIELDS_SELECT}}", hierarchy_select)
        .replace("{{HIERARCHY_FIELDS_OUTPUT}}", hierarchy_output)
        .replace("{{IS_GE_MFR_EXPR}}", is_ge_mfr_expr)
    )

    # Broadened CT-mapped logic: primary = Contract_Category, fallback = hierarchy cues.
    ct_checks: list[str] = ["UPPER(CAST(b.contract_category AS STRING)) = 'COMPUTED TOMOGRAPHY'"]
    if "product_group_category" in available:
        ct_checks.append(
            "REGEXP_CONTAINS(UPPER(CAST(b.product_group_category AS STRING)), r'COMPUTED\\s+TOMOGRAPHY|\\bCT\\b')"
        )
    if "UNSPSC_Class_Code" in available:
        ct_checks.append(
            "REGEXP_CONTAINS(CAST(b.UNSPSC_Class_Code AS STRING), r'422015')"
        )
    if "UNSPSC_Class_Description" in available:
        ct_checks.append(
            "REGEXP_CONTAINS(UPPER(CAST(b.UNSPSC_Class_Description AS STRING)), r'COMPUTED\\s+TOMOGRAPHY|\\bCT\\b')"
        )

    is_ct_mapped_expr = "(" + " OR ".join(ct_checks) + ")"

    # Charity CT validation inference: treat a GE-gated match for CT-like terms as CT-mapped.
    ct_like_term_keys: list[str] = []
    for t in terms:
        key = (t.get("term_key") or "").strip()
        if not key:
            continue
        if key.startswith(("REVOLUTION_", "OPTIMA_", "VCT_")) or key == "MAXIMA":
            ct_like_term_keys.append(key)
    if ct_like_term_keys:
        quoted = ", ".join([f"'{_bq_escape_string(k)}'" for k in ct_like_term_keys])
        is_ct_mapped_expr = f"({is_ct_mapped_expr} OR (b.is_ge_mfr AND t.term_key IN ({quoted})))"

    rendered = rendered.replace("{{IS_CT_MAPPED_EXPR}}", is_ct_mapped_expr)

    return rendered


def generate_zero_match_discovery(
    bq: BigQueryClient,
    table_fqn: str,
    snapshot_dir: Path,
    available_fields: set[str],
    start_date: str | None,
    end_date: str | None,
    zero_match_terms: list[dict[str, str]]
) -> None:
    if not zero_match_terms:
        print("No zero-match terms to analyze.")
        # different from previous logic, but safest is to output empty file or skip
        # User requested the artifact exists.
        pd.DataFrame(columns=["term_key", "term_label", "field_name", "search_variant", "match_count", "total_spend", "samples"]).to_csv(snapshot_dir / "ct_charity_zero_match_discovery.csv", index=False)
        return

    print(f"Running zero-match discovery for {len(zero_match_terms)} terms...")
    
    results = []
    
    # Pre-calculate common parts
    is_ge = _build_is_ge_mfr_expr(available_fields)
    date_where_clause = _render_date_where(start_date, end_date, available_fields)
    
    # Fields to check (intersection of REQUIRED and available)
    check_fields = [f for f in REQUIRED_MATCH_FIELDS if f in available_fields]
    
    for term in zero_match_terms:
        term_key = term["term_key"]
        term_label = term.get("term_label") or term_key
        pattern = term["pattern"]
        escaped_pattern = _bq_escape_string(pattern)
        
        selects = []
        for f in check_fields:
            # Check for match in this specific field
            match_expr = f"REGEXP_CONTAINS(UPPER(IFNULL(CAST({f} AS STRING), '')), r'{escaped_pattern}')"
            
            selects.append(f"""
            STRUCT(
                '{f}' AS field_name,
                COUNTIF({match_expr}) AS match_count,
                SUM(IF({match_expr}, Base_Spend, 0)) AS total_spend,
                ARRAY_AGG(IF({match_expr}, CAST({f} AS STRING), NULL) IGNORE NULLS LIMIT 10) AS samples
            ) AS {f}_stats
            """)
            
        sql = f"""
        SELECT
            {", ".join(selects)}
        FROM `{table_fqn}`
        WHERE {is_ge}
        {date_where_clause}
        """
        
        try:
            # BQ Client returns rows; extract first row
            query_job = bq.client.query(sql)
            rows = list(query_job.result())
            if not rows:
                continue
            row = rows[0]
            
            for f in check_fields:
                stats = row.get(f"{f}_stats")
                if not stats:
                    continue
                results.append({
                    "term_key": term_key,
                    "term_label": term_label,
                    "field_name": f,
                    "search_variant": pattern,
                    "match_count": stats["match_count"],
                    "total_spend": stats["total_spend"],
                    "samples": " | ".join([str(s) for s in stats["samples"]]) if stats["samples"] else ""
                })

        except Exception as e:
            print(f"Error querying discovery for {term_key}: {e}")

    df = pd.DataFrame(results)
    _write_csv(df, snapshot_dir / "ct_charity_zero_match_discovery.csv")


def _write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Wrote {path} ({len(df):,} rows)")


def _assert_no_placeholders(sql: str, label: str) -> None:
    if "{{" in sql or "}}" in sql:
        # Print a small hint to make debugging template rendering easier.
        snippet = "\n".join(sql.splitlines()[-40:])
        raise ValueError(
            f"Unrendered placeholders detected in {label} SQL. "
            f"Check template variables and _render_sql replacements.\n\nLast 40 lines:\n{snippet}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Charity CT presence + hierarchy outputs")
    parser.add_argument("--snapshot-dir", type=Path, help="Existing snapshot directory (snapshots/<RUN_ID>/)")
    parser.add_argument("--run-id", type=str, help="Run ID (used to create snapshots/<RUN_ID>/ if --snapshot-dir not set)")
    parser.add_argument("--terms", type=Path, default=Path("config/ct_charity_terms.yaml"))
    parser.add_argument("--start-date", type=str, default="2023-10-01")
    parser.add_argument("--end-date", type=str, default="2025-09-30")
    args = parser.parse_args()

    if args.snapshot_dir:
        snapshot_dir = args.snapshot_dir
    else:
        run_id = args.run_id or dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        snapshot_dir = Path("snapshots") / run_id

    snapshot_dir.mkdir(parents=True, exist_ok=True)

    terms = _load_terms(args.terms)
    terms_cte = _render_terms_cte(terms)
    any_pattern = _render_any_pattern(terms)

    bq = BigQueryClient()
    if not bq.client:
        raise SystemExit("BigQuery client not initialized (ADC).")

    available = _available_fields(bq, TABLE_FQN)

    _warn_missing(REQUIRED_MATCH_FIELDS, available, "matching")
    _warn_missing(REQUIRED_SPEND_DATE_FIELDS, available, "spend/date")
    _warn_missing(HIERARCHY_CANDIDATES, available, "hierarchy")

    sql_dir = Path("sql")

    presence_template = _read_sql(sql_dir / "ct_charity_presence_check.sql")
    presence_sql = _render_sql(
        presence_template,
        table_fqn=TABLE_FQN,
        terms_cte=terms_cte,
        terms=terms,
        available=available,
        start_date=args.start_date,
        end_date=args.end_date,
        any_pattern=any_pattern,
    )
    _assert_no_placeholders(presence_sql, "presence")

    hierarchy_template = _read_sql(sql_dir / "ct_charity_hierarchy_extract.sql")
    hierarchy_sql = _render_sql(
        hierarchy_template,
        table_fqn=TABLE_FQN,
        terms_cte=terms_cte,
        terms=terms,
        available=available,
        start_date=args.start_date,
        end_date=args.end_date,
        any_pattern=any_pattern,
    )
    _assert_no_placeholders(hierarchy_sql, "hierarchy")

    discovery_template = _read_sql(sql_dir / "ct_ct_text_discovery.sql")
    discovery_sql = _render_sql(
        discovery_template,
        table_fqn=TABLE_FQN,
        terms_cte=terms_cte,
        terms=terms,
        available=available,
        start_date=args.start_date,
        end_date=args.end_date,
        any_pattern=any_pattern,
    )
    _assert_no_placeholders(discovery_sql, "ct_text_discovery")

    debug_template = _read_sql(sql_dir / "ct_charity_term_debug_samples.sql")
    debug_sql = _render_sql(
        debug_template,
        table_fqn=TABLE_FQN,
        terms_cte=terms_cte,
        terms=terms,
        available=available,
        start_date=args.start_date,
        end_date=args.end_date,
        any_pattern=any_pattern,
    )
    _assert_no_placeholders(debug_sql, "term_debug_samples")

    print(f"Querying {TABLE_FQN} for Charity CT presence...")
    df_presence = bq.client.query(presence_sql).to_dataframe()
    _write_csv(df_presence, snapshot_dir / "ct_charity_presence_summary.csv")

    # Frontier subtype breakdown (QA artifact): answer whether EX/EL are truly absent
    # or simply recorded without subtype tokens.
    try:
        product_description_backfilled_expr = _build_product_description_backfilled_expr(available)
        is_ge_mfr_expr = _build_is_ge_mfr_expr(available)
        date_where = _render_date_where(args.start_date, args.end_date, available)

        def _term_pattern(term_key: str) -> str:
            t = next((x for x in terms if (x.get("term_key") or "").strip() == term_key), None)
            return str(t.get("pattern") if t else "").strip()

        spend_field = "Base_Spend" if "Base_Spend" in available else "Landed_Spend"
        facility_mfr_cat_field = (
            "Facility_Manufacturer_Catalog_Num" if "Facility_Manufacturer_Catalog_Num" in available else "NULL"
        )
        facility_vendor_cat_field = (
            "Facility_Vendor_Catalog_Num" if "Facility_Vendor_Catalog_Num" in available else "NULL"
        )

        match_text_expr = _coalesce_text_expr_from_exprs(
            [
                product_description_backfilled_expr,
                "Facility_Manufacturer_Name" if "Facility_Manufacturer_Name" in available else "NULL",
                "Facility_Vendor_Name" if "Facility_Vendor_Name" in available else "NULL",
                "Facility_Manufacturer_Catalog_Num" if "Facility_Manufacturer_Catalog_Num" in available else "NULL",
                "Facility_Vendor_Catalog_Num" if "Facility_Vendor_Catalog_Num" in available else "NULL",
                "Manufacturer_Name" if "Manufacturer_Name" in available else "NULL",
                "Manufacturer_Top_Parent_Name" if "Manufacturer_Top_Parent_Name" in available else "NULL",
                "Vendor_Name" if "Vendor_Name" in available else "NULL",
                "Vendor_Top_Parent_Name" if "Vendor_Top_Parent_Name" in available else "NULL",
                "Manufacturer_Catalog_Number" if "Manufacturer_Catalog_Number" in available else "NULL",
                "Vendor_Catalog_Number" if "Vendor_Catalog_Number" in available else "NULL",
                "Brand_Name" if "Brand_Name" in available else "NULL",
            ]
        )

        def _field_contains(field_expr: str, pattern: str) -> str:
            return f"REGEXP_CONTAINS(UPPER(IFNULL(CAST({field_expr} AS STRING), '')), r'{_bq_escape_string(pattern)}')"

        frontier_any = _field_contains("match_text", r"\bFRONTIER\b")

        frontier_es_pattern = _term_pattern("REVOLUTION_FRONTIER_ES")
        frontier_ex_pattern = _term_pattern("REVOLUTION_FRONTIER_EX")
        frontier_el_pattern = _term_pattern("REVOLUTION_FRONTIER_EL")
        if not (frontier_es_pattern and frontier_ex_pattern and frontier_el_pattern):
            raise ValueError("Missing Frontier term patterns in config/ct_charity_terms.yaml")

        has_es = _field_contains("match_text", frontier_es_pattern)
        has_ex = _field_contains("match_text", frontier_ex_pattern)
        has_el = _field_contains("match_text", frontier_el_pattern)

        frontier_breakdown_sql = f"""
WITH base AS (
  SELECT
    {product_description_backfilled_expr} AS product_description_backfilled,
    {facility_mfr_cat_field} AS facility_manufacturer_catalog_num,
    {facility_vendor_cat_field} AS facility_vendor_catalog_num,
        {match_text_expr} AS match_text,
    {spend_field} AS base_spend,
    {is_ge_mfr_expr} AS is_ge_mfr
  FROM `{TABLE_FQN}`
  WHERE 1 = 1
{date_where}
    AND {spend_field} IS NOT NULL
),
frontier AS (
  SELECT *
  FROM base
  WHERE is_ge_mfr
    AND {frontier_any}
),
bucketed AS (
  SELECT
    CASE
      WHEN ({has_ex}) THEN 'Frontier_EX'
      WHEN ({has_el}) THEN 'Frontier_EL'
      WHEN ({has_es}) THEN 'Frontier_ES'
      ELSE 'Frontier_unspecified'
    END AS frontier_bucket,
    base_spend
  FROM frontier
)
SELECT
  frontier_bucket,
  COUNT(1) AS match_count_anywhere,
  SUM(base_spend) AS base_spend_anywhere
FROM bucketed
GROUP BY 1
ORDER BY frontier_bucket;
"""

        df_frontier = bq.client.query(frontier_breakdown_sql).to_dataframe()
        _write_csv(df_frontier, snapshot_dir / "ct_frontier_subtype_breakdown.csv")
    except Exception as e:
        print(f"WARNING: Failed to generate ct_frontier_subtype_breakdown.csv: {e}")

    # If key terms remain zero, run new alias discovery logic
    zero_match_keys = []
    if not df_presence.empty:
        match_col = "match_count_anywhere"
        term_col = "term_key"
        # Ensure numeric conversion
        if match_col in df_presence.columns and term_col in df_presence.columns:
            zero_match_keys = df_presence.loc[
                (pd.to_numeric(df_presence[match_col], errors="coerce").fillna(0) == 0)
                & df_presence[term_col].notna(),
                term_col,
            ].astype(str).tolist()

    zero_match_terms = [t for t in terms if t["term_key"] in zero_match_keys]
    
    generate_zero_match_discovery(
        bq, TABLE_FQN, snapshot_dir, available, args.start_date, args.end_date, zero_match_terms
    )

    print(f"Querying {TABLE_FQN} for Charity CT hierarchy extract...")
    df_hierarchy = bq.client.query(hierarchy_sql).to_dataframe()
    _write_csv(df_hierarchy, snapshot_dir / "ct_charity_hierarchy_extract.csv")

    print(f"Querying {TABLE_FQN} for CT text discovery...")
    df_discovery = bq.client.query(discovery_sql).to_dataframe()
    _write_csv(df_discovery, snapshot_dir / "ct_ct_text_discovery.csv")

    print(f"Querying {TABLE_FQN} for Charity term debug samples...")
    df_debug = bq.client.query(debug_sql).to_dataframe()
    _write_csv(df_debug, snapshot_dir / "ct_charity_term_debug_samples.csv")


if __name__ == "__main__":
    main()
