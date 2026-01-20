# Vineyard Point Analysis Guide & Definitions

**Date:** 2026-01-19
**Purpose:** To clearly define the financial metrics used in the Vineyard Point analysis and prevent misinterpretation of "Cost" vs "Premium".

## 1. Key Metric Definitions

### A. Total Cost of Ownership (Wealth Drag)
*   **Variable Name:** `avg_annual_cost`
*   **Definition:** The absolute amount your net worth decreases each year by owning this asset.
*   **Formula:** `Total Net Cost / Horizon Years`
    *   `Total Net Cost` = (Simulated Sale Proceeds - Upfront Investment - Cumulative Cash Flows - Tax Benefits)
*   **What it tells you:** "How much poorer am I for owning this?"
*   **Typical Value:** ~$13,500/year (Moderate Case).

### B. Cost to Rent Instead
*   **Variable Name:** `rent_instead_cost`
*   **Definition:** The amount you would spend on rent for the *exact same* usage period if you didn't own.
*   **Formula:** `(Owner Weeks / 2) * Anchor Price per 2-Week Block`
*   **Assumption:** Uses "Equivalent Quality" rental rates (e.g., Airbnb fees included).
*   **Typical Value:** ~$12,500/year (for 6 weeks usage).

### C. Ownership Premium (The "True" Cost)
*   **Variable Name:** `ownership_premium_economic`
*   **Definition:** The *difference* between owning and renting.
*   **Formula:** `Total Cost of Ownership - Cost to Rent Instead`
*   **Interpretation:**
    *   Positive (+): You pay extra for the privilege of ownership (Lifestyle Fee).
    *   Negative (-): You save money by owning vs. renting (Investment Gain).
*   **Typical Value:** ~$1,000/year (Moderate Case).
*   **Crucial Lesson:** Do not confuse "Total Cost" with "Premium". Most of the "Cost" is simply prepaying for your own vacations.

---

## 2. Key Input Assumptions (Source of Truth)

### Management & Operations (MTR Specifics)
*   **Fee Structure:** 18% of Gross Rent (Source: Legacy Rose / Local MTR Comps).
*   **Leasing Fee:** $250 per lease turnover (Assumption: 30+ day stays require more vetting).
*   **Cleaning:** $220 per turn (Pass-through to tenant usually, but modeled as expense for conservatism).

### Furnishing & Reserves
*   **Upfront FF&E:** $20,000 (Median budget). Defines the "Quality Tier" needed for $2,800/mo rents.
*   **Reserve Strategy:** Sinking Fund.
    *   Instead of $5k upfront cash reserve, we model $1,000/year expense.
    *   Concept: You replace the couch in Year 5, not Day 1.

### Tax Strategy (SALT Cap Play)
*   **Status:** Confirmed Headroom.
*   **Logic:**
    *   User has ~$32k other state taxes + $2k Prop Tax < $40k SALT Cap (2026+ limit).
    *   Mortgage interest is deductible.
    *   Result: Marginal benefit of ~20-30% on every dollar of interest/tax paid.
*   **Impact:** Reduces net cost by ~$2,700/year.

---

## 3. Analysis Version History

### v1: "Initial Skepticism"
*   Focus: Can it cash flow?
*   Result: No. Negative cash flow confirmed.

### v2: "Expensive Luxury" (Wait, wrong math)
*   Error: Interpreted `avg_annual_cost` ($13.5k) as the "Premium".
*   Incorrect Conclusion: "This costs $13.5k/yr *more* than renting."

### v3: "Break-Even Lifestyle" (Final)
*   Correction: Subtracted `rent_instead_cost` ($12.5k) from `avg_annual_cost` ($13.5k).
*   Correct Conclusion: "This costs ~$1k/yr *more* than renting."
*   Pivot: Decision is now operational (hassle factor), not financial.
