# GE Market Insights Pilot: Medical Device Demand Analysis

> **Status:** **Active / Validation Complete (Charity CT Phase).** This repository contains a fully automated pipeline for analyzing medical device demand, aligning provider transactions with manufacturer sales, and generating stakeholder-ready reports.

## 0. Quick Orientation (Handoff Notes)

**Where to start (fast):**
1. `docs/PRODUCT_REQUIREMENTS.md` — business rules / acceptance criteria (treat as law).
2. `docs/ARCHITECTURE.md` — pipeline flow, table roles, repo layout.
3. `PARITY_ALIGNMENT_APPROACH.md` — how Transaction Analysis and Supplier Spend were aligned.
4. `docs/PREMIER_DATA_MODELS_HANDOFF.md` — data model reference for agent handoff.
5. `snapshots/20260122T122915Z/` — deliverables (PPTX/PDF/CSVs/PNGs).
6. `SUMMARY_OF_RECENT_ITERATION.md` — chronological run log + decisions.

**Latest artifacts (single authoritative snapshot):**
- Deck: `snapshots/20260122T122915Z/GE_PILOT_Validation.pptx` and `.pdf`
- CT Charity validation: `snapshots/20260122T122915Z/ct_charity_presence_summary.csv`
- Q4 timing reconciliation visuals included in deck

**Key analysis documentation:**
- `docs/PARITY_AUDIT_FINDINGS.md` — Philips-specific audit confirming coverage (CT: 142%, MRI: 171%, Monitoring: 105%)
- `docs/CHARITY_CT_FINDINGS_SUMMARY.md` — CT product validation results

**BigQuery access (non-negotiable): ADC only**
- Auth is **Application Default Credentials** only (no embedded secrets; no committed keys):
    - `gcloud auth application-default login`
- For interactive BigQuery exploration inside Copilot Chat, use the workspace MCP server:
    - Server name: `bigquery_ge_sample`
    - Guide: `docs/MCP_TOOLBOX_GUIDE.md`
    - Example: `/mcp bigquery_ge_sample callTool execute_sql sql="SELECT 1"`

**Test command (import path):**
- `PYTHONPATH=. pytest -q`

## 1. Project Mission & Core Questions
The **GE Market Insights Pilot** aims to bridge the gap between two disparate views of the medical device market:
1.  **Provider Reality:** What health systems actually record in their ERPs (POs and Invoices).
2.  **Manufacturer Reality:** What GE (and competitors) report in their sales tracings (Supplier Spend).

**Key Questions Addressed:**
*   How much "Big Capital" (MRI, CT, Patient Monitoring) does Premier actually see in transaction feeds?
*   How do we align "Dark Facilities" (those reporting sales to manufacturers but not sending transactions to Premier)?
*   Can we validate the presence of specific GE product lines (e.g., Revolution CT, Optima, CardioGraphe) within the noise of global transactions?

---

## 2. Data Sources & Architecture

### Data Sources
*   **Transaction Analysis (TA):** `transaction_analysis_expanded`. This is the Primary "Provider-Reported" source. It contains PO and Invoice data, often lacking clean item master mapping for high-dollar capital.
*   **Supplier Spend (Sales Tracings):** "Manufacturer-Reported" sales data. Used as the benchmark for parity analysis.

### The Transformation Stack
1.  **Dataform (BigQuery/SQL):** Handles heavy lifting. Materializes "Gold" tables that perform:
    *   Entity normalization.
    *   Categorization of "UNKNOWN" capital using text-mining ($25k+ price thresholds).
    *   Parity alignment between TA and Supplier Spend.
2.  **Python Pipeline:** Orchestrates the workflow:
    *   **Extraction:** Pulls BigQuery data to local CSV artifacts.
    *   **Visualization:** Generates trend charts (Capital, Parity, Share).
    *   **Branded PPTX:** Builds a professional deck using `python-pptx` and the `brand/` template. (**See [docs/PPTX_GENERATION_GUIDE.md](docs/PPTX_GENERATION_GUIDE.md)** for formatting rules).
    *   **PDF Export:** Automated conversion for distribution.

---

## 3. Methodology: Parity & Alignment Logic
To ensure "apples-to-apples" comparisons, we implement strict rules documented in `docs/PRODUCT_REQUIREMENTS.md`:

### The "Dark Facility" Filter (Alignment)
We exclude a facility from the Supplier Spend (Comparison) benchmark if it isn't also reporting into the Transactional feed. This prevents "phantom gaps" where the manufacturer reports sales to a facility that simply doesn't share data with Premier.
*   **Safety Net:** We keep System-level reporting if the parent entity is active in the transaction feed, even if specific facility codes aren't.

### Capital Identification ("Big Iron" Heuristic)
Capital equipment often bypasses standard GPO item masters. We isolate it using:
*   **Price Signal:** Transactions > $25,000.
*   **Text Mining:** Scanning descriptions for modality keyterms (MRI, CT, RESONANCE).
*   **Exclusion:** Filtering out "SERVICE", "WARRANTY", and "SOFTWARE" to isolate hardware.

---

## 4. Feature Workstream: Charity CT Validation
A major focus has been the **Charity CT Product Presence** workstream.
*   **Recall Maximization:** We search across **20 distinct identity fields** (including backfilled descriptions, facility catalog numbers, and replacement IDs) to find specific GE models.
*   **Proof of Absence:** For missing models (e.g., CardioGraphe), we implemented a "discovery" search to rule out naming variations, effectively proving their absence in the current 24-month window (Oct 2023 - Sep 2025).
*   **GE Gating:** All validation is "GE Gated," meaning we only credit matches where the manufacturer or vendor is identified as GE Healthcare.

---

## 5. Quick Start & Handoff (For Agents)

### Environment Setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
gcloud auth application-default login
```

### Running the Pipeline
The entire end-to-end flow is encapsulated in one command:
```bash
python scripts/run_full_pipeline.py
```
This produces a timestamped folder in `snapshots/` containing:
*   `GE_PILOT_Validation.pptx` (Branded Presentation)
*   `GE_PILOT_Validation.pdf`
*   `ct_charity_presence_summary.csv` (Validation proof)
*   `manifest.json` (Full run metadata)

### Exploration via MCP
Use the `bigquery_ge_sample` MCP server for interactive discovery:
```
/mcp bigquery_ge_sample callTool execute_sql sql="SELECT ... FROM ..."
```

---

## 6. Project Structure
- `src/pptx_builder/`: Logic for the branded PowerPoint generation.
- `dataform/`: SQL definitions for BigQuery transformations.
- `scripts/`: Implementation-specific scripts (Charity outputs, Sanity checks).
- `docs/`:
    - `CHARITY_CT_FINDINGS_SUMMARY.md`: The definitive results of the CT validation.
    - `ARCHITECTURE.md`: Technical stack detail.
    - `PRODUCT_REQUIREMENTS.md`: Compliance and business logic rules.
- `snapshots/`: **The Source of Truth for Deliverables.** Always look here for the latest results.

---

## 7. Notes for Success
*   **ADC Only:** Never commit keys. Use Application Default Credentials.
*   **Snapshot Reproducibility:** Every run is unique. If you change a config, run the pipeline and look in the new `snapshots/` folder.
*   **Stability:** The Charity CT work is **COMPLETED**. New requests should likely focus on extending this methodology to MRI or Patient Monitoring categories.

