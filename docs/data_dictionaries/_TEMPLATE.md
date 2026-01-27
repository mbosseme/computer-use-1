# Data Dictionary: `<TABLE_NAME>`

- **Full Path:** `<project>.<dataset>.<table>`
- **Description:** <Brief description of what this table contains and its purpose>
- **Estimated Rows:** ~<N>
- **Generated:** <Date or method>

---

## Overview

<Optional: High-level notes about the table, its source, update frequency, key relationships, etc.>

---

## Columns

<!-- 
Column sections follow this format:

### column_name
- Type: `DTYPE`
- Description: <What this column represents>
- Nulls: N (X.XX%)
- Distinct: N
- Top values: val1 (count), val2 (count), ...

The profiling script (tools/bigquery-profiling/update_dictionary.py) will inject/update:
  - Type, Nulls, Distinct, Top values

You should manually provide:
  - Description (what the column means, business context)
  - Any enum/code mappings (e.g., "0: Active, 1: Inactive")
  - Relationships to other tables

For grouped/related columns, you can use combined headers:
### col1 / col2 / col3
- Description: These columns represent X, Y, Z respectively.

Note: Grouped headers are NOT automatically updated by the profiling script.
-->

### example_column
- Description: <What this column represents>

### example_id
- Description: Unique identifier for <entity>. Foreign key to `<other_table>`.

### example_status_code
- Description: Status indicator.
  - `0`: Active
  - `1`: Inactive
  - `2`: Pending

### example_amount
- Description: <Currency/quantity> in <units>.

---

## Notes

<!-- Optional: Known issues, data quality notes, deprecated columns, etc. -->

---

## Changelog

<!-- Optional: Track major changes to the table structure -->

| Date | Change |
|------|--------|
| YYYY-MM-DD | Initial dictionary created |
