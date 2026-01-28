# Dataform Setup

This directory contains Dataform definitions for BigQuery data transformations used in the demand forecasting pipeline.

## Overview

Dataform enables SQL-based data transformation workflows with dependency management, testing, and documentation. It's configured to work with BigQuery and follows a standard data warehouse pattern:

- `definitions/sources/` - External data source declarations
- `definitions/staging/` - Initial transformations and cleaning
- `definitions/marts/` - Business-logic tables for analytics
- `definitions/assertions/` - Data quality tests

## Configuration

**Project Settings** (`dataform.json`):
- Database: `matthew-bossemeyer`
- Default schema: `ge_sample_staging`
- Assertion schema: `ge_sample_assertions`
- Location: `US`
- Config vars (override via `dataform.json`):
  - `capital_price_threshold` default 25000 (system price filter)
  - `capital_primary_categories` pipe-delimited list of Contract_Category keywords
  - `capital_positive_keywords` pipe list for description mining when category is UNKNOWN
  - `capital_negative_keywords` pipe list of exclusion terms (service, maintenance, etc.)

Update these values if using a different GCP project or dataset naming convention.

**Variables** (`dataform.json` → `vars`):
Define project-wide constants here. Access them in definitions via:
```javascript
const { myVar } = require("../includes/constants");
```

## Getting Started

### Installation
```bash
cd dataform
npm install
```

### Authentication
Uses Application Default Credentials (same as main pipeline):
```bash
gcloud auth application-default login
```

### Running Transformations

> **⚠️ CRITICAL: Always use the local binary, NOT `npx`**
> 
> `npx @dataform/cli` can hang for 30+ minutes due to npm package resolution issues.
> Use `./node_modules/.bin/dataform` instead — compile should take < 1 second.

```bash
# Compile definitions (check for errors) — should take < 1 second
./node_modules/.bin/dataform compile

# Run all transformations
./node_modules/.bin/dataform run

# Run specific tag/path
./node_modules/.bin/dataform run --tags staging
./node_modules/.bin/dataform run --tags parity
./node_modules/.bin/dataform run --include-deps definitions/staging/stg_example
```

### Development Workflow

1. **Declare sources** in `definitions/sources/` for external tables
2. **Create staging views** in `definitions/staging/` to clean/standardize data
3. **Build marts** in `definitions/marts/` for business-logic tables
4. **Add assertions** in `definitions/assertions/` to validate data quality

## Example Definition

Create `definitions/staging/stg_example.sqlx`:

```sqlx
config {
  type: "view",
  schema: "ge_sample_staging",
  description: "Example staging transformation",
  tags: ["staging"]
}

SELECT
  id,
  LOWER(name) as name,
  created_date
FROM ${ref("raw_source_table")}
WHERE created_date >= '2024-01-01'
```

## Best Practices

- Use `ref()` to reference other Dataform definitions (handles dependencies)
- Use `${ref("table_name")}` in SQL for automatic dependency resolution
- Tag definitions by layer (sources, staging, marts) for selective runs
- Add descriptions to all tables for documentation
- Create assertions to validate data quality assumptions
- Centralize shared config/logic in `includes/`. The repo provides `includes/capital_config.js` (thresholds & keywords driven by `dataform.json` vars) and `includes/manufacturer_map.js` for consistent manufacturer normalization across models.

## GE Capital Models

The following definitions implement the PRD artifacts:

- `stg_ge_capital_systems` — staging view (ge_sample_staging) applying modality filters, price threshold, spend-type heuristics, manufacturer normalization, and privacy-safe projections.
- `mart_validation_mapping` — table (ge_sample_marts) aggregated by manufacturer + SKU + description + category with total spend & transaction counts for Artifact 1 CSV.
- `mart_observed_trends` — table (ge_sample_marts) summarizing quarterly spend, share, and YoY growth by modality + manufacturer for Artifact 2 CSV.
- Assertions under `definitions/assertions/` guard required fields (`assert_validation_mapping_required_fields`) and ensure trends metrics stay within expected ranges (`assert_observed_trends_share_range`).

## VS Code Integration

Install the [Dataform extension](https://marketplace.visualstudio.com/items?itemName=Dataform.dataform) for:
- Syntax highlighting for `.sqlx` files
- Inline compilation and validation
- Dependency graph visualization

## Documentation

- [Dataform Documentation](https://cloud.google.com/dataform/docs)
- [SQLX Reference](https://cloud.google.com/dataform/docs/reference/dataform-core)
- [Best Practices](https://cloud.google.com/dataform/docs/best-practices)
