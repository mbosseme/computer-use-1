# Run Handoff Journal — 2026-01-15__b-braun-pdf-synthesis

## Run Status: ACTIVE — CRITICAL FINDING: Clarification Needed on Product Scope

## Latest Work (2026-01-28)
**CRITICAL FINDING — Product List Manufacturer Mismatch**

The 71 NDCs Jen provided are **Fresenius Kabi / Hikma products**, NOT B. Braun products:
- **65219-xxx-xx** (46 products) = Fresenius Kabi labeler code
- **63323-xxx-xx** (25 products) = Hikma Pharmaceuticals labeler code

When validated against CAMS (manufacturer-reported contract sales):
- These products are reported under **Fresenius Group (entity 616951)**, NOT B. Braun (entity 606326)
- Only 7 of 49 mapped Reference Numbers appear in CAMS at all under the validation period

**B. Braun DOES have IV Solutions in CAMS** under entity 606326 with $182M+ in IV Fluids Bag-Based Solutions.

**CLARIFICATION NEEDED FROM JEN:**
1. Does she want data for the 71 **Fresenius Kabi products** she listed? (These would validate against Fresenius Group in CAMS, not B. Braun)
2. Or does she want data for **B. Braun's own IV Solutions products**? (Different NDCs, catalog numbers like L8002, L7500, etc.)

### Evidence
- Extracted full product table from Jen's Jan 23, 2026 email via Microsoft Graph
- Parsed 71 products with SKUs and NDCs → saved to `exports/jen_sku_list.csv`
- Converted to 11-digit format → saved to `tmp/jen_ndcs_11digit.txt`
- CAMS validation query confirmed products report under Fresenius Group (616951)

### Artifacts Created This Session
| File | Purpose |
|------|---------|
| `exports/jen_sku_list.csv` | Complete product list from Jen's email (71 rows) |
| `tmp/jen_ndcs_11digit.txt` | 11-digit NDCs for TAE matching |
| `tmp/jen_email_sku_list.html` | Raw HTML email body |
| `scripts/search_jen_emails.py` | Graph email search script |
| `scripts/parse_sku_table.py` | HTML table parser |
| `scripts/convert_ndcs.py` | NDC format converter |

---

## Previous Summary (pre-2026-01-28)
This run synthesized 16 B. Braun documents (PDFs/EMLs) into actionable business intelligence, drafted follow-up emails, and produced a CAPS/503B category validation slice sample data cut integrating two data feeds.

### What was accomplished
1. **Document Synthesis Pipeline**
   - Extracted text from 16 documents (PDF/EML) in B. Braun OneDrive folder
   - Used `PyPDF2` for PDF extraction; Python `email` module for EML
   - Implemented per-document summarization loop with GPT-5.2 (Responses API)
   - Handled rate limits (429) with exponential backoff
   - Resolved context-length issues for redundant PDFs (transcript repeated per page)

2. **Outputs Generated**
   - `exports/b-braun_synthesis.md` — Global thematic synthesis (8 key themes, strategic takeaways)
   - `exports/meeting_analysis_confirmed_demo.md` — Detailed action items from Jan 9 demo
   - `exports/follow_up_email_draft.md` — Initial follow-up email draft
   - `exports/jake_feedback_refinement.md` — Refined "Proposed Solution" section addressing Jake's feedback

3. **Core Repo Promotion (MERGED)**
   - New skill: `.github/skills/document-synthesis-llm/SKILL.md`
   - New utility: `agent_tools/llm/document_extraction.py`
   - Updated: Skills index, `agent_tools/llm/__init__.py`, `docs/DEPENDENCIES_AND_UTILS.md`
   - PR #8 merged to `main`

## Artifacts (run-local)
| File | Purpose |
|------|---------|
| `exports/b-braun_synthesis.md` | Global synthesis with 8 themes |
| `exports/meeting_analysis_confirmed_demo.md` | Demo meeting action items |
| `exports/follow_up_email_draft.md` | Initial email draft |
| `exports/jake_feedback_refinement.md` | Jake-specific refinements |
| `scripts/extract_and_synthesize.py` | Main extraction/synthesis script |
| `scripts/analyze_meeting_transcript.py` | Transcript-specific analysis |
| `scripts/draft_follow_up_email.py` | Email drafting script |
| `scripts/refine_email_jake_feedback.py` | Refinement script |

## User's Final Email (Approved Draft)
```
Hi Tracy and Jen,

Thank you again for the time last Friday. I'm checking in as you complete your internal debrief to see where you're leaning on an engagement approach so we can move toward a more detailed proposal.

Based on our conversation, it sounds like the strongest near-term fit for the marketing group is the Custom Analytics Services focused on the 6 Category IV Ecosystem. Our aim would be to combine hospital ERP + Rx wholesaler data into a complete picture of a hospital's spend across these categories. We discussed two primary use cases on Friday: targeting leakage / cross-selling / compliance gap opportunities to drive near-term revenue growth, and separately, identifying portfolio gaps where competitors had momentum to help ensure longer term growth.

Regarding our next steps, I have noted a few specific follow-ups:

Initial Engagement: What are the top use cases your team would like to scope in detail?
CAPS SKU List (Claire/Jake): Do you have any update on the SKU list for the CAPS/compounding sample data cut? Once we have that, we can produce the sample quickly to validate our coverage across the ERP and Rx wholesaler data. We'll include a data dictionary with the sample.

Would you be open to a 30-minute sync next week to finalize initial use cases, including whether you would like us to include the Capital Refresh or DEHP/PVC-Free add-ons from the initial proposal?

Slides from Friday attached for ease of reference.

Best,
Matt Bossemeyer
```

## Pending User Actions
- [ ] **Deliver sample data cut to Jen** — artifacts ready in `exports/caps_503b_validation_slice__*`
- [ ] Optionally export integrated comparison to JSONL if flat-file deliverable needed
- [ ] Prepare Data Dictionary if Jen requests column definitions
- [ ] Send the follow-up email to Tracy/Jen (user approved draft in earlier session)
- [ ] Await B. Braun response on next steps

## Next Session Continuity
If resuming this run:
1. Check if Jen/Tracy responded to the sample data cut
2. If they request JSONL export, run integrated comparison query and save to `exports/*.jsonl`
3. If they request Data Dictionary, create column definitions doc
4. Consider preparing a "Portfolio Gap Heatmap" mockup if engagement advances

## Blockers
- None.

## Git State
- Branch: `run/2026-01-15__b-braun-pdf-synthesis`
- Worktree: `/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis`
- Core promotion: PR #8 merged to `main`

---

## 2026-01-16 — Single-document re-synthesis (Confirmed demo PDF)

### Summary
- Generated a fresh, single-document synthesis for the OneDrive PDF “Re: Confirmed-BBraun MI Demo - virtual .pdf”.

### Artifacts
- `runs/2026-01-15__b-braun-pdf-synthesis/exports/confirmed_demo_virtual__synthesis.md`
- `runs/2026-01-15__b-braun-pdf-synthesis/tmp/confirmed_demo_virtual__extracted.txt` (sanitized + truncated extraction used for the prompt)

### Repro
- Script: `runs/2026-01-15__b-braun-pdf-synthesis/scripts/summarize_confirmed_demo_virtual_pdf.py`
- Run: `.venv/bin/python runs/2026-01-15__b-braun-pdf-synthesis/scripts/summarize_confirmed_demo_virtual_pdf.py`

### Verification
- Script printed “Wrote synthesis: …/exports/confirmed_demo_virtual__synthesis.md” and output file has non-empty content.

---

## 2026-01-16 — Chunked full-document synthesis (large PDFs)

### Summary
- Implemented and validated a chunked map-reduce synthesizer for large PDFs (local-first, deterministic chunk packing + explicit coverage/limit warnings).
- Discovered that `PyPDF2` text extraction for “Confirmed-BBraun MI Demo - virtual.pdf” appears to duplicate identical extracted text across pages (page 1 == page 2 == page 3), so “full coverage” depends on extractor fidelity.

### Artifacts
- `runs/2026-01-15__b-braun-pdf-synthesis/exports/confirmed_demo_virtual__full_synthesis.md`
- `runs/2026-01-15__b-braun-pdf-synthesis/exports/confirmed_demo_virtual__full_synthesis.manifest.json`
- `runs/2026-01-15__b-braun-pdf-synthesis/tmp/confirmed_demo_virtual__chunks/` (per-chunk summaries from the large-PDF run)

### Repro
- Script (single-PDF entrypoint): `runs/2026-01-15__b-braun-pdf-synthesis/scripts/summarize_confirmed_demo_virtual_pdf.py`
- Run: `.venv/bin/python runs/2026-01-15__b-braun-pdf-synthesis/scripts/summarize_confirmed_demo_virtual_pdf.py`

### Notes
- The synthesizer emits a `PDF_REDUNDANCY_DEDUPED` warning when many pages extract identically; this is a strong signal of an extractor artifact rather than truly redundant content.

---

## 2026-01-16 — Full folder re-synthesis (all docs)

### Summary
- Re-ran extraction + synthesis for every document in the B Braun folder using chunked map-reduce PDF synthesis (no naive truncation), and re-generated the global synthesis.

### Artifacts
- Global synthesis: `runs/2026-01-15__b-braun-pdf-synthesis/exports/b-braun_synthesis.md`
- Per-document syntheses: `runs/2026-01-15__b-braun-pdf-synthesis/exports/docs/*__synthesis.md`
- Per-document manifests: `runs/2026-01-15__b-braun-pdf-synthesis/exports/docs/*__synthesis.manifest.json`
- Per-document chunk summaries (PDFs): `runs/2026-01-15__b-braun-pdf-synthesis/tmp/docs/*__chunks/`

### Repro
- Script: `runs/2026-01-15__b-braun-pdf-synthesis/scripts/extract_and_synthesize.py`
- Run: `.venv/bin/python runs/2026-01-15__b-braun-pdf-synthesis/scripts/extract_and_synthesize.py`

---

## 2026-01-27 — Graph email search + FY27 thread extraction + Outlook draft creation

### Summary
- Located a specific FY27 email thread (“FY27 Capital Budget Planning for SC Data Management - what are your data needs?”) and extracted what Audrey, Elise, and Bethany sent back.
- Drafted a consolidated email to Melanie (saved as a Markdown draft) and created an Outlook draft message via Microsoft Graph.
- Promoted reusable “create Outlook draft from Markdown via Graph” tooling into core and merged it to `main` (PR #13).

### Artifacts (run-local)
- `runs/2026-01-15__b-braun-pdf-synthesis/exports/email_to_melanie_proctor__fy27_sc_data_needs__draft.md`
- `runs/2026-01-15__b-braun-pdf-synthesis/tmp/find_fy27_capital_budget_thread_responses.py`
- `runs/2026-01-15__b-braun-pdf-synthesis/scripts/create_outlook_draft_from_md.py` (run-local precursor; core CLI exists on `main`)

### Core promotion (already merged to main)
- Core helper module: `agent_tools/graph/drafts.py`
- Core CLI: `agent_tools/graph/create_draft_from_md.py`
- Skill doc update: `.github/skills/graph-email-search/SKILL.md` (includes Inbox subfolder warning + Draft creation section)

### Notes / gotchas
- Inbox queries can miss messages routed into Inbox subfolders; prefer mailbox-wide search first, then fall back to scanning Inbox subtree.
- Graph `$search` support varies by tenant; if AQS field queries error, use phrase search + local filtering.
- Recipient resolution can be ambiguous when display names are “Last, First”; the core helper resolves by token-based matching.

### Repro (core: create an Outlook draft from a Markdown file)
- Run from repo root (after configuring Graph env):
   - `python -m agent_tools.graph.create_draft_from_md --md <path/to/draft.md> --resolve-to-name "First Last"`

---

## 2026-01-27 — CAPS/503B Category Validation Slice Sample Data Cut

### Summary
Produced the sample data cut Jen requested for validating CAPS/compounding 503B category coverage. This integrates **two distinct data feeds**:
- **Provider ERP purchasing** (Transaction Analysis Expanded) — hospital purchasing transactions
- **Wholesaler Tracing** (Report Builder) — wholesaler distribution/sales data

The goal is to cross-reference facility-month-NDC aggregates from both feeds to identify coverage alignment and gaps.

### NDC Cohort
- **71 NDCs** extracted from Jen's PDF ("Re: Confirmed-BBraun MI Demo - virtual.pdf")
- Normalized to 11-digit digits-only format (stripped hyphens/dashes)
- Stored at: `runs/2026-01-27__fy27-email-handoff/tmp/re_confirmed_bbraun_mi_demo_virtual__39e24a0260__ndcs_11.txt`
- Manufacturers: **Fresenius Kabi** (65219* prefix) and **Hikma/APP** (63323* prefix)

### Data Model Integration Approach

#### Tables Used
| Feed | Table | Row Count | Key Columns |
|------|-------|-----------|-------------|
| Provider ERP | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded` | ~839M rows, ~2.41TB | `Transaction_Date`, `Premier_Entity_Code`, `Ndc`, `Landed_Spend`, `Base_Spend`, `Quantity`, `Health_System_Name`, `Contract_Category` |
| Wholesaler | `abi-inbound-prod.abi_inbound_bq_stg_purchasing_rx_wholesaler_sales.report_builder` | ~690M rows | `month_year` (TIMESTAMP), `facility_id`, `ndc`, `total_spend`, `total_units`, `wholesaler`, `supplier`, `premier_award_status` |

#### Join Key (Empirically Validated)
- **Correct join**: `Premier_Entity_Code` (provider) → `facility_id` (wholesaler)
- Validation query showed: 117 of 2,180 wholesaler facility_ids matched via `Premier_Entity_Code`; **0 matched via `Facility_Code`**
- Note: Provider table has both `Facility_Code` (sometimes = "Aggregated Above Facility Level") and `Premier_Entity_Code`; only the latter is valid for cross-feed joins

#### Timeframe & Filters
- **Date range**: 24 months (2024-01-01 to 2026-01-01)
- **Provider exclusions**: `NOT REGEXP_CONTAINS(UPPER(Health_System_Name), r'(\bTEST\b|\bDEMO\b|PREMIER)')`
- **Wholesaler exclusions**: `facility_id != '00'`
- **NDC normalization**: `REGEXP_REPLACE(CAST(ndc AS STRING), r'[^0-9]', '')`

### Key Findings

#### Coverage Distribution
| Coverage Type | Description | Prevalence |
|---------------|-------------|------------|
| **PROVIDER_ONLY** | Facility has ERP purchasing data but no wholesaler tracing | **Dominant** |
| **WHOLESALER_ONLY** | Facility has wholesaler tracing but no ERP purchasing data | Moderate |
| **BOTH** | Cross-feed overlap on (facility, month, NDC) | **Rare** |

#### Top Health Systems by Feed
- **Provider ERP (PROVIDER_ONLY)**: ECU Health, Baptist Health South Florida, UPMC Health System, Summa Health, Methodist Health System, Baptist Healthcare System
- **Wholesaler Tracing (WHOLESALER_ONLY)**: Northwestern Memorial Healthcare, Conductiv, St Luke's University Health Network, CommonSpirit Health
- **Cross-Feed Overlap (BOTH)**: Texas Health Resources, H. Lee Moffitt Cancer Center, TidalHealth Inc, Acurity (fka GNYHA)

#### Spend Alignment (Where BOTH Exist)
- **Perfect match examples**: TX0226 (Texas Health Resources) → $4,069.15 provider = $4,069.15 wholesaler (delta = $0)
- **Large divergence examples**: 714817 (ECU Health) → $228,750 provider vs $1,647 wholesaler (delta = $227K+)

### Artifacts Created

| File | Purpose |
|------|---------|
| `exports/caps_503b_validation_slice__integrated_comparison.sql` | FULL OUTER JOIN query: provider ↔ wholesaler on (facility_id, month_year, ndc11) with coverage flags and spend delta |
| `exports/caps_503b_validation_slice__provider_sample.sql` | Provider-only aggregate query (500-row sample) |
| `exports/caps_503b_validation_slice__wholesaler_sample.sql` | Wholesaler-only aggregate query (500-row sample) |
| `exports/caps_503b_validation_slice__summary.md` | Human-readable summary with key findings |

### Sample Query Structure (Integrated Comparison)

```sql
WITH ndc_cohort AS (SELECT ndc11 FROM UNNEST([...71 NDCs...]) AS ndc11),

provider_agg AS (
  SELECT
    Premier_Entity_Code AS facility_id,
    FORMAT_TIMESTAMP('%Y-%m-01', Transaction_Date) AS month_year,
    REGEXP_REPLACE(CAST(Ndc AS STRING), r'[^0-9]', '') AS ndc11,
    SUM(Landed_Spend) AS provider_landed_spend,
    SUM(Quantity) AS provider_qty
  FROM transaction_analysis_expanded
  WHERE Transaction_Date >= '2024-01-01' AND Transaction_Date < '2026-01-01'
    AND ndc11 IN (SELECT ndc11 FROM ndc_cohort)
  GROUP BY 1, 2, 3
),

wholesaler_agg AS (
  SELECT
    facility_id,
    FORMAT_TIMESTAMP('%Y-%m-01', month_year) AS month_year,
    REGEXP_REPLACE(CAST(ndc AS STRING), r'[^0-9]', '') AS ndc11,
    SUM(total_spend) AS wholesaler_total_spend,
    SUM(total_units) AS wholesaler_total_units
  FROM report_builder
  WHERE month_year >= '2024-01-01' AND month_year < '2026-01-01'
    AND ndc11 IN (SELECT ndc11 FROM ndc_cohort)
  GROUP BY 1, 2, 3
)

SELECT
  COALESCE(p.facility_id, w.facility_id) AS facility_id,
  COALESCE(p.month_year, w.month_year) AS month_year,
  COALESCE(p.ndc11, w.ndc11) AS ndc11,
  p.provider_landed_spend,
  w.wholesaler_total_spend,
  CASE WHEN p.facility_id IS NOT NULL AND w.facility_id IS NOT NULL THEN 'BOTH'
       WHEN p.facility_id IS NOT NULL THEN 'PROVIDER_ONLY'
       ELSE 'WHOLESALER_ONLY'
  END AS data_source_coverage,
  p.provider_landed_spend - w.wholesaler_total_spend AS spend_delta
FROM provider_agg p
FULL OUTER JOIN wholesaler_agg w
  ON p.facility_id = w.facility_id
  AND p.month_year = w.month_year
  AND p.ndc11 = w.ndc11;
```

### Next Steps for Continuation

1. **Export to JSONL**: If Jen needs a flat-file deliverable, run the integrated comparison query and export results to JSONL
2. **Add Data Dictionary**: Prepare column definitions for the output fields
3. **NDC Category Enrichment**: Map NDCs to product descriptions (currently just raw 11-digit codes)
4. **Investigate Sparse Overlap**: Why do high-spend provider facilities (ECU, Baptist South Florida) have minimal wholesaler coverage?
5. **Temporal Trend Charts**: Visualize month-over-month spend patterns if requested

### Repro

To re-run the integrated comparison query:
1. Open BigQuery console or use MCP BigQuery tool
2. Execute `exports/caps_503b_validation_slice__integrated_comparison.sql`
3. Results show coverage flags + spend deltas for all facility-month-NDC combinations

### Notes for Next Agent

- The **join key validation was critical** — do not assume `Facility_Code` works; only `Premier_Entity_Code` aligns with wholesaler `facility_id`
- Provider table is **partitioned by `Transaction_Date`** — always filter on this column first for performance
- Wholesaler table is **clustered by `wholesaler_purchase_type`** — useful for purchase type breakdowns but not required for this query
- NDC normalization is essential — both tables store NDCs differently (some with hyphens, some without)


