# Skill: BigQuery Data Exploration

This skill covers patterns for querying BigQuery tables for data discovery, validation, and analysis. It focuses on cross-project access, schema discovery, and product/entity matching patterns.

## 1. Context & Use Cases

**Trigger:** User requests to:
- Query BigQuery tables for data analysis
- Find specific products, manufacturers, or entities in transaction data
- Compare or validate data between different data models (e.g., `transaction_analysis_expanded` vs `supplier_spend`)
- Investigate market share, spend patterns, or product hierarchies

**Common Data Models:**
| Model | Location | Description |
|-------|----------|-------------|
| Transaction Analysis Expanded | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | Raw provider transaction feed with full product/vendor detail |
| Supplier Spend | Various | Aggregated supplier-level spend summaries |

## 2. Authentication (ADC-First)

**Canonical approach:** Always use Application Default Credentials (ADC) from the user's gcloud login.

```bash
# One-time setup (if not already authenticated)
gcloud auth application-default login
```

**Critical rule:** Do NOT set `GOOGLE_APPLICATION_CREDENTIALS` in the environment — it overrides ADC and breaks cross-project access.

### Cross-Project Query Requirements

When querying tables in a different project than your billing/job project:
1. The **user** (ADC identity) must have read access to the target project's tables
2. The **job project** (where queries run) must be authorized; typically your personal project works
3. Never use a service account JSON for interactive work — ADC is always preferred

**Python client initialization (recommended):**
```python
from google.cloud import bigquery
import os

# Ensure no service account override is present
for key in ["GOOGLE_APPLICATION_CREDENTIALS", "BIGQUERY_PROJECT"]:
    os.environ.pop(key, None)

# Default client uses ADC
client = bigquery.Client()  # Will use quota_project_id from ADC
```

## 3. Schema Discovery Pattern

Before building queries, discover what fields are actually available:

```python
def get_available_fields(client: bigquery.Client, table_fqn: str) -> set[str]:
    """Return set of field names available in a table."""
    try:
        table = client.get_table(table_fqn)
        return {field.name for field in table.schema}
    except Exception as e:
        print(f"WARNING: Could not fetch schema for {table_fqn}: {e}")
        return set()
```

**Why this matters:**
- Different data feeds have different columns populated
- Build queries dynamically based on available fields
- Avoid hard errors from missing columns

## 4. Product/Entity Matching Patterns

### 4.1 Multi-Field Text Search (Coalesce Pattern)

When searching for products or entities, search across all relevant text fields:

```sql
-- Build a searchable text blob from multiple columns
WITH search_base AS (
  SELECT *,
    UPPER(CONCAT(
      IFNULL(CAST(Product_Description AS STRING), ''), ' | ',
      IFNULL(CAST(Facility_Product_Description AS STRING), ''), ' | ',
      IFNULL(CAST(Manufacturer_Name AS STRING), ''), ' | ',
      IFNULL(CAST(Brand_Name AS STRING), '')
    )) AS search_text
  FROM `project.dataset.table`
)
SELECT * FROM search_base
WHERE REGEXP_CONTAINS(search_text, r'(?i)YOUR_PATTERN_HERE')
```

### 4.2 Manufacturer Identity (Fallback Hierarchy)

Match manufacturers using a priority cascade:

```sql
-- Priority: Structured manufacturer fields -> Fallbacks -> Description text
CASE 
  WHEN Manufacturer_Top_Parent_Name IS NOT NULL 
       AND TRIM(Manufacturer_Top_Parent_Name) != ''
    THEN UPPER(Manufacturer_Top_Parent_Name)
  WHEN Manufacturer_Name IS NOT NULL 
       AND TRIM(Manufacturer_Name) != ''
    THEN UPPER(Manufacturer_Name)
  WHEN Facility_Manufacturer_Name IS NOT NULL
    THEN UPPER(Facility_Manufacturer_Name)
  ELSE UPPER(COALESCE(Brand_Name, Vendor_Name, 'UNKNOWN'))
END AS manufacturer_resolved
```

### 4.3 YAML-Driven Term Matching

For complex term matching (e.g., product categories, charity terms), use a YAML config:

```yaml
# config/terms.yaml
terms:
  - term_key: ct_scanner
    term_label: "CT Scanner"
    pattern: "(?i)\\bCT\\b|COMPUTED\\s+TOMOGRAPHY"
    term_order: 1
  - term_key: mri
    term_label: "MRI"
    pattern: "(?i)\\bMRI\\b|MAGNETIC\\s+RESONANCE"
    term_order: 2
```

Then generate SQL dynamically:

```python
def render_terms_cte(terms: list[dict]) -> str:
    """Build a CTE of term definitions for SQL."""
    selects = []
    for t in terms:
        selects.append(
            f"SELECT {t['term_order']} AS term_order, "
            f"'{t['term_key']}' AS term_key, "
            f"'{t['term_label']}' AS term_label, "
            f"r'{t['pattern']}' AS pattern"
        )
    return "\n    UNION ALL\n".join(selects)
```

## 5. Spend Aggregation Patterns

### 5.1 Quarterly Aggregation

```sql
SELECT
  DATE_TRUNC(DATE(Transaction_Date), QUARTER) AS quarter_start,
  FORMAT_DATE('%Y-Q%Q', DATE(Transaction_Date)) AS year_quarter,
  category,
  manufacturer_normalized,
  SUM(Base_Spend) AS total_spend,
  COUNT(DISTINCT premier_entity_code) AS facility_count,
  SUM(Quantity) AS total_units
FROM `project.dataset.table`
WHERE Base_Spend > 0 AND Quantity > 0
GROUP BY 1, 2, 3, 4
ORDER BY quarter_start, category, total_spend DESC
```

### 5.2 Market Share Calculation

```sql
WITH category_totals AS (
  SELECT 
    year_quarter, 
    category, 
    SUM(total_spend) AS category_spend
  FROM aggregated_data
  GROUP BY 1, 2
)
SELECT
  a.*,
  SAFE_DIVIDE(a.total_spend, c.category_spend) AS share_of_category
FROM aggregated_data a
JOIN category_totals c USING (year_quarter, category)
```

## 6. Dataform SQL Transformations

For repeatable transformations, use Dataform `.sqlx` files:

**Structure:**
```
dataform/
├── definitions/
│   ├── staging/          # Source cleaning, field mapping
│   │   └── stg_*.sqlx
│   ├── marts/            # Business-level aggregations
│   │   └── mart_*.sqlx
│   └── assertions/       # Data quality checks
│       └── assert_*.sqlx
├── dataform.json         # Project config
└── .df-credentials.json  # ADC credentials (minimal)
```

**Dataform credentials for ADC:**
```json
{
  "projectId": "your-project-id",
  "location": "US"
}
```

**Run commands:**
```bash
# Compile (validate syntax)
npx @dataform/cli compile

# Run specific tags
npx @dataform/cli run --tags your_tag
```

## 7. Recovery Rules

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| `403 Access Denied: User does not have permission to query table` | Service account override or wrong project | Unset `GOOGLE_APPLICATION_CREDENTIALS`; use ADC |
| `403 User does not have bigquery.jobs.create permission` | Job project mismatch | Ensure ADC has quota_project_id set to your project |
| `Column not found` | Schema varies between feeds | Use schema discovery pattern; build queries dynamically |
| Query returns no rows | Regex pattern too strict or field empty | Test patterns on sample rows first; check for nulls |

## 8. Reference Implementation

See `runs/2026-01-16__ge-market-insights/ge-pipeline/` for:
- `src/bigquery_client.py` — ADC-first client wrapper
- `scripts/ct_charity_outputs.py` — Term matching + schema discovery patterns
- `dataform/definitions/` — Dataform SQL transformations
