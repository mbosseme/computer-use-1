# BigQuery Data Dictionaries

This folder contains detailed column-level documentation for BigQuery tables used by agents in this workspace.

## Naming Convention

Data dictionary files follow this naming pattern:
```
<project>.<dataset>.<table>.md
```

For filtered/scoped versions of tables:
```
<project>.<dataset>.<table>__<filter_description>.md
```

Examples:
- `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md`
- `abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join__dhc_firm_type=Hospital.md`

## Structure of Each Dictionary

Each data dictionary markdown file should include:

1. **Table Overview** — Purpose, source, approximate row count, update frequency
2. **Column Reference** — For each column:
   - Column name
   - Data type
   - Description / business meaning
   - Null rate (if known)
   - Distinct count (if known)
   - Sample values (if helpful)
3. **Common Filters** — Standard WHERE clauses (e.g., exclude test entities)
4. **Key Relationships** — Foreign keys, join patterns to other tables
5. **Example Queries** — Representative SQL for common use cases

## How Agents Use These Dictionaries

Before writing SQL against a BigQuery table:
1. Check if a data dictionary exists in this folder
2. Read the dictionary to understand column semantics, types, and gotchas
3. Apply recommended filters (e.g., exclude TEST/DEMO entities)
4. Use example queries as templates

For MCP toolbox interaction patterns and authentication setup, see:
- [BigQuery Data Models Skill](../../.github/skills/bigquery-data-models/SKILL.md)
- [MCP Toolbox Guide](../MCP_TOOLBOX_GUIDE.md)
- [Premier Data Models Handoff](../PREMIER_DATA_MODELS_HANDOFF.md)

## Current Dictionaries

| Table | Dictionary File | Description |
|-------|-----------------|-------------|
| Transaction Analysis Expanded | [abi-inbound-prod...transaction_analysis_expanded.md](abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded.md) | Provider-submitted POs/Invoices (~820M rows); 7-year rolling transactional purchase feed |
| Supplier Spend | [abi-inbound-prod...supplier_spend.md](abi-inbound-prod.abi_inbound_bq_stg_purchasing_supplier_sales.supplier_spend.md) | Manufacturer-reported contract sales tracings (~87M rows); comprehensive scope including non-acute |
| SASF DHC Join (Hospitals) | [abi-xform-dataform-prod...sa_sf_dhc_join__dhc_firm_type=Hospital.md](abi-xform-dataform-prod.cdx_sample_size.sa_sf_dhc_join__dhc_firm_type=Hospital.md) | Definitive Healthcare hospital enrichment (~7K hospitals); IDN rollups, bed counts, facility metadata |
| Report Builder (Pharma) | [abi-inbound-prod...report_builder.md](abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder.md) | Pharma wholesaler tracings (~690M rows); Acute & Non-Acute purchasing view |

---

*Add new dictionaries as tables are documented.*
