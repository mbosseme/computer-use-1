# Email to Jen — IV Solutions Sample Data for B. Braun

**To:** Jen  
**Subject:** IV Solutions Sample Data Extract — Fresenius Kabi Products for B. Braun Analysis

---

Hi Jen,

Please see the attached workbook (`Fresenius_IV_Solutions_Data_Pack_FY27.xlsx`) containing the sample data extract based on the IV Solutions product list you provided. We have pulled together a comprehensive View covering 24 months of purchasing activity (January 2024 through December 2025).

## Workbook Overview

The file contains three tabs:

1.  **Data Dictionary**: Definitions for all columns (e.g., `ndc11`, `spend`, `blinded_facility_id`).
2.  **Requested Products (Extract 1)**: Purchasing data for the specific list of NDCs you provided.
3.  **Gap Products (Extract 2)**: Transactional data for *additional* Fresenius IV Fluid products that were not in your original list but appear to be highly relevant.

## What We Found

### 1. Requested Products (Tab 2)
We located spend for the majority of the products on your original list:
-   **Total Spend:** ~$10.3 million (Jan 2024 – Dec 2025)
-   **Coverage:** 69 of the 71 products had activity.
-   **Source Split:** ~$7.1M from Provider Direct (ERP) data and ~$3.2M from Wholesaler data.

### 2. Gap Analysis (Tab 3)
While analyzing the data, we noticed that your requested list covered only about half of the Fresenius products in this specific category (`IV FLUIDS BAG-BASED DRUG DELIVERY`). Some high-volume products appeared to be missing.

For example, we found **0.9% Sodium Chloride IV Solution (1000ml Injection Bag)**, Manufacturer Part # `060-10109`. This item alone accounted for **over $2.4 million** in spend over the two-year period but was not included in your original request.

Because these items seemed highly related to your analysis, we pulled all other Fresenius products in this category into a separate tab ("Gap Products") to ensure you have a complete picture without mixing them with your specific request.

-   **Total Gap Spend:** ~$124.8 million
-   **Products Identified:** 35 additional Reference Numbers (including high-volume items like Smoflipid and Omegaven).

## About the Sample
The underlying sample represents approximately **25% of the US acute and non-acute care market**, covering a diverse mix of facility types and geographies broadly representative of the total US healthcare provider population.

As a rough guide, you can extrapolate from these sample figures to estimate total US purchasing volume by **dividing by 0.25** (or equivalently, multiplying by 4). For example, the $42.7M in this sample would suggest approximately $170M in total US healthcare provider purchasing for these products over the 24-month period.

## Attached Files

I'm attaching two files:

1. **iv_solutions__external_sample_enriched.csv** — The main data extract containing all transaction-level records. Each row represents a facility/month/product combination with spend amounts and product attributes.

2. **iv_solutions__external_sample_enriched_dictionary.md** — A data dictionary explaining each column in the extract, including notes on data sources and de-identification.

### Key Notes on the Data:

- **Facility identifiers are blinded** — We've replaced actual facility IDs with anonymous identifiers (FAC_00001, etc.) and removed facility names, addresses, and IDN affiliations.
- **Geographic data retained** — State and 3-digit ZIP are included to support regional analysis.
- **Product metadata** — All product attributes (brand name, description, manufacturer, etc.) are sourced from Premier's Primary Item Master for consistency across data sources.
- **Dual data sources** — The `source` column indicates whether each row came from ERP (provider direct) or Wholesaler data.

## Questions?

Let me know if you have any questions about the data or need any adjustments to the extract. Happy to discuss the findings or pull additional cuts if helpful for the B. Braun analysis.

Best,  
Matt

---

**Attachments:**
1. `iv_solutions__external_sample_enriched.csv` (17 MB)
2. `iv_solutions__external_sample_enriched_dictionary.md`
