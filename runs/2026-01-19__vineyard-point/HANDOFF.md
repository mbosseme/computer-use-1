# HANDOFF — 2026-01-19__vineyard-point

Run status: **ACTIVE**
Current Focus: **Underwriting Complete / Gate Verification Phase**

## Current target
- Property: **Vineyard Point / Dockside condos** (18861 Vineyard Point Ln, Cornelius, NC 28031)
- Goal: Owned "vacation club" usage (5 weeks/yr) + Mid-Term Rental (30+ day min)
- Decision Status: **CAUTION / LIFESTYLE ONLY** (Tax benefits are $0; Monthly Burn is ~$1,500)

## Work completed (This Session)
1.  **Tax Analysis (UPDATED: SIGNIFICANT BENEFIT)**: 
    - **Previous view:** Tax Neutral due to Section 280A loss suspension + assumed SALT/Debt caps.
    - **New Findings (2026):** SALT Cap increases to $40,400. User has ~$8k SALT headroom + Total Debt < $750k.
    - **Result:** Incremental Mortgage Interest + Property Tax deduction on Schedule A unlocks **~$2,700/year** refund benefit.
    - Model updated to reflect this (Bolton method allocation).
2.  **Economic Modeling (Finalized)**:
    - 29,160 scenarios run (`fill_rate` x `rent` x `mgmt_fee` x `leasing_fee` x `tax_status`).
    - **Best Case:** Rent $3,100, 90% Fill, 7% Mgmt → **+$2,174/yr** wealth impact vs renting.
    - **Moderate Case:** Rent $2,800, 75% Fill, 10% Mgmt → **-$2,574/yr** wealth impact vs renting.
    - **Cash Burn:** Still high ($1,200–$1,800/mo), but effectively subsidized by $2,700 annual tax refund.
3.  **Core Skill Promotion**:
    - Created and promoted `analysis-workflow/decision-modeling.md` to Core Skills.
4.  **Documentation**:
    - Final Decision Memo: `properties/vineyard_point/decision_memo.md`
    - Evidence Ledger: `runs/2026-01-19__vineyard-point/research/EVIDENCE_LEDGER.md`
    - Full Scenario Results: `runs/2026-01-19__vineyard-point/exports/scenario_results.csv`

## Critical Next Steps (Verification Gates)
The deal hinges on two variables that swing the economics by $5k–$9k/yr:
1.  **Manager Leasing Fee:** Must verify if Alarca (or similar) charges a **Flat Fee ($250-$500)** or **% of Rent ($1,500)**.
2.  **HOA Rules:** Must obtain governing docs to confirm **30-day rentals are viable** (not just "allowed" but practicable w/ keys/parking).

## Context for Next Agent
- The user knows the deal is a financial "loser" (cash burn) but potentially a "lifestyle winner" (forced savings). 
- Do **not** try to re-optimize taxes; that door is closed (Section 280A).
- Focus strictly on **Ground Truth Verification** (HOA docs + Manager quotes).
