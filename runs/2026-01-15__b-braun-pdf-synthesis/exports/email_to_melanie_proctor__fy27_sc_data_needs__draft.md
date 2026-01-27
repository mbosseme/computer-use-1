# Draft email to Melanie — FY27 SC Data Management data needs

Subject: FY27 Capital Budget Planning — consolidated data needs (Audrey / Elise / Bethany)

Hi Melanie,

Following up on the FY27 Capital Budget Planning thread (“SC Data Management – what are your data needs?”), I pulled together the inputs I received back from Audrey, Elise, and Bethany into one consolidated list below. Each item includes the requester and the work area they were representing.

## Consolidated FY27 data needs (with attribution)

1) **Kit bills of material (BOM) — collection + standardization**
   - **Requested by:** Audrey Siepiela (**Supplier lane**)
   - **Details:** Data collection and standardization of kit BOMs (noted this may already be planned but was delayed in FY26).

2) **Pharmacy data matching — visibility + planned enhancements**
   - **Requested by:** Audrey Siepiela (**Supplier lane**)
   - **Details:** More clarity on what pharmacy data matching looks like today and a placeholder/plan for enhancements as the work progresses.

3) **Product matching alignment: Clinical OR Log → TSA product descriptions**
   - **Requested by:** Audrey Siepiela (**Supplier lane**)
   - **Details:** Align product matching efforts from the Clinical OR Log process to TSA product descriptions (details TBD; Audrey flagged Michael Boyle to weigh in as scope becomes clearer).

4) **Brand name standardization / multi-level brand fields**
   - **Requested by:** Audrey Siepiela (**Supplier lane**)
   - **Details:** Add standardized brand name and/or multi-level brand fields. Rationale: taxonomy/contract category often don’t align, and brand is a more intuitive drill-down for national accounts + marketing users (also expected to help clinical product matching).

5) **Sensitive-field masking in TSA (and future sources)**
   - **Requested by:** Elise Prete-Adams (**Supply Analytics / data platform hygiene**) 
   - **Details:** Ensure masking of sensitive information in TSA and future data sources. She noted Spend Dashboard masks to “UNKNOWN,” but wasn’t confident the same is true for Supply Analytics data.

6) **GUDID reference data source (replace web scraping dependency)**
   - **Requested by:** Elise Prete-Adams (**Supply Analytics / reference data**) 
   - **Details:** Establish a durable data source for GUDID. They currently obtain it via web scraping after Google discontinued the public dataset they had been using.

7) **PIM attribute population (including GTIN attributes)**
   - **Requested by:** Elise Prete-Adams (**Supply Analytics / PIM enrichment**) 
   - **Details:** Additional population of PIM attributes; Elise referenced GTIN attributes (mentioned by Jesse).

8) **Daily TSA data load / storage**
   - **Requested by:** Elise Prete-Adams (**Supply Analytics / operations**) 
   - **Details:** Loading and storage of daily TSA data.

9) **New data feeds from the PID spec**
   - **Requested by:** Elise Prete-Adams (**Supply Analytics / integrations**) 
   - **Details:** Establishing new data feeds from the PID spec.

10) **Operational support for Workday / Infor feeds**
   - **Requested by:** Elise Prete-Adams (**Supply Analytics / integrations + ops**) 
   - **Details:** Operational support to be established for new Workday/Infor feeds.

11) **GL data for executive-level KPIs**
   - **Requested by:** Bethany Downs (**Palantir (SCS) / Margin Improvement Technology**) 
   - **Details:** GL data to support executive-level KPI reporting.

12) **ERP formulary intake / repository (member-specific) for compliance measurement**
   - **Requested by:** Bethany Downs (**Palantir (SCS) / Margin Improvement Technology**) 
   - **Details:** ERP formulary intake/repository to measure compliance to member-specific formularies.

13) **Product attributes (e.g., discontinued status, country of origin) for disruption forecasting**
   - **Requested by:** Bethany Downs (**Palantir (SCS) / Margin Improvement Technology**)
   - **Also related to:** Elise Prete-Adams (**Supply Analytics / PIM enrichment**) (GTIN attribute population)
   - **Details:** Bethany specifically cited discontinued status + country of origin as examples needed to support supply disruption forecasting.

14) **Recent contract PCLF data from sourcing in PIM (status/category changes/new items)**
   - **Requested by:** Bethany Downs (**Palantir (SCS) / Margin Improvement Technology**) 
   - **Details:** Recent contract PCLF data from sourcing in PIM to identify whether items on new contracts are discontinued, moved categories, excluded, or whether a new item was added—used for compliance and savings tracking.

## Note on Palantir funding
Bethany also shared that she confirmed with Donielle that they do **not** need to submit additional requests to your team for the Palantir roadmap items, since funding for that work is already in place.

If helpful, I can set up a short working session with you to:
- confirm which of the above are already on the FY27 roadmap,
- identify gaps / sequencing,
- and align owners and success criteria for each.

Thanks,
Matt
