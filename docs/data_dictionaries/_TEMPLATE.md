# Data Dictionary: <TABLE_SHORT_NAME>
**Table**: `<PROJECT>.<DATASET>.<TABLE>`
**Description**: <Table Description>
**Total Records**: <COUNT>

## Columns

### <COLUMN_NAME>
- **Type**: `<TYPE>`
- **Description**: <Description>
- **Distinct Values**: <N>
- **Nulls**: <N> (<PCT%>)
- **Top Values**:
  - `<VALUE>`: <COUNT> (<PCT%>)
  - `<VALUE>`: <COUNT> (<PCT%>)

---


### column_name
- Type: `DTYPE`
- Description: <What this column represents>
- Nulls: N (X.XX%)
- Distinct: N
- Top values: val1 (count), val2 (count), ...

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
