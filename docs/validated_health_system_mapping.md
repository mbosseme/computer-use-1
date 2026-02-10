# Validated Health System Mapping (Top 9 Pilot)

This artifact captures the explicit name-based mapping logic used to validate spend data between the new `provider_invoice_workflow_history` table and the legacy `transaction_analysis_expanded` table.

**Date**: 2026-02-10
**Purpose**: Bridge the gap caused by missing `health_system_entity_code` in the new table by using high-confidence string matches.

| Mapping Key | Workflow Name (New Source) | TSA Name (Legacy Source) | Notes |
|---|---|---|---|
| **ADVOCATE** | Advocate Health | ADVOCATE HEALTH SUPPLY CHAIN ALLIANCE | |
| **ADVENTHEALTH** | AdventHealth (AHS Florida) | ADVENTHEALTH | **Variation Alert**: New table volume ~226% of Legacy. |
| **OSF** | EM_OSF | OSF HEALTHCARE SYSTEM | **Variation Alert**: New table volume ~272% of Legacy. |
| **UHS** | EM_UHS | UHS OF DELAWARE, INC. | |
| **RENOWN** | EM_Renown | RENOWN HEALTH | |
| **ADVENTIST** | Adventist Health (California HQ) | ADVENTIST HEALTH | |
| **HONORHEALTH** | EM_HonorHealth | HONORHEALTH | |
| **UVM** | EM_Fletcher | THE UNIVERSITY OF VERMONT HEALTH NETWORK | **Parent Mapping**: `EM_Fletcher` is a child of UVM. |
| **UCI** | EM_UCI | UNIVERSITY OF CALIFORNIA IRVINE | |

## Usage
These mappings are hardcoded in `scripts/gen_mapped_spend_comparison.sql` to execute the variance analysis.

## Variation Summary
Initial analysis shows that for the mapped systems, the New Source often captures significantly *more* spend than the Legacy Source (Over-capture), suggesting broader data inclusion (e.g. Remitra + ERP) or potential duplication.
