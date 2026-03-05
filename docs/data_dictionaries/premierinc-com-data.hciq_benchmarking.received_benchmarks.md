# Data Dictionary: `received_benchmarks`

- Description: Healthcare IQ (HCIQ) benchmarking snapshots providing discrete percentile price benchmarks (low, 50th, 75th, 90th, high) for products aligned to manufacturer and catalog configurations. Note that HCIQ benchmarks exclude rebates.
- Estimated rows: 1,662,301
- Snapshots: 2025-11-13 to 2026-02-09

## Columns

### manufacturer_entity_code
- Type: `STRING`
- Description: Alpha-numeric vendor/manufacturer identifier
- Nulls: 0 (0.00%)
- Distinct: 12,615


### manufacturer_name
- Type: `STRING`
- Description: Name of the manufacturer
- Nulls: 0 (0.00%)
- Distinct: 12,699
- Top values: W.W. GRAINGER, INC. (71,873), MEDLINE INDUSTRIES, LP (65,639), HOWMEDICA OSTEONICS CORP. DBA STRYKER ORTHOPAEDICS (44,828), DEPUY SYNTHES (41,159), STERIS CORPORATION (29,592)


### manufacturer_catalog_number
- Type: `STRING`
- Description: Manufacturer catalog or part number
- Nulls: 43,098 (2.59%)
- Distinct: 447,012


### contract_category
- Type: `STRING`
- Description: Contract category assignment
- Nulls: 0 (0.00%)
- Distinct: 863
- Top values: GENERAL ORTHOPEDIC TRAUMA PRODUCTS (125,569), MAINTENANCE REPAIR AND OPERATIONS (95,302), SURGICAL INSTRUMENTS (91,814), SPINAL IMPLANTS AND RELATED PRODUCTS (77,737), ORTHOPEDIC TOTAL JOINT IMPLANTS (77,022)


### hciq_manufacturer_name
- Type: `STRING`
- Description: Normalized manufacturer name from HCIQ
- Nulls: 337,140 (20.28%)
- Distinct: 4,569
- Top values: None (337,140), JOHNSON & JOHNSON HEALTHCARE (77,730), STRYKER CORPORATION (75,024), MEDLINE INDUSTRIES INC (63,852), MEDTRONIC USA INC (43,121)


### hciq_manufacturer_catalog_number
- Type: `STRING`
- Description: Normalized manufacturer catalog number from HCIQ
- Nulls: 337,140 (20.28%)
- Distinct: 367,450


### hciq_item_description
- Type: `STRING`
- Description: Product description from HCIQ
- Nulls: 337,144 (20.28%)
- Distinct: 370,251


### hciq_low_benchmark
- Type: `FLOAT`
- Description: Low price benchmark mark from HCIQ
- Nulls: 337,140 (20.28%)
- Distinct: 64,150


### hciq_90_benchmark
- Type: `FLOAT`
- Description: 90th percentile price benchmark (Note: Inverted scale, comparable to internal 10th)
- Nulls: 337,140 (20.28%)
- Distinct: 226,480


### hciq_75_benchmark
- Type: `FLOAT`
- Description: 75th percentile price benchmark (Note: Inverted scale, comparable to internal 25th)
- Nulls: 337,140 (20.28%)
- Distinct: 208,293


### hciq_50_benchmark
- Type: `FLOAT`
- Description: 50th percentile price benchmark (Median)
- Nulls: 337,140 (20.28%)
- Distinct: 191,313


### hciq_high_benchmark
- Type: `FLOAT`
- Description: High price benchmark mark from HCIQ
- Nulls: 337,140 (20.28%)
- Distinct: 75,274


### abi_snapshot_date
- Type: `DATE`
- Description: Date of the given snapshot capture
- Nulls: 0 (0.00%)
- Distinct: 4


### abi_load_date
- Type: `DATE`
- Description: Date the snapshot was loaded into ABI
- Nulls: 0 (0.00%)
- Distinct: 3

