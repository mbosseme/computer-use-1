# Run Handoff — 2026-01-06__validate_insight_flash_reports

## Summary
- Bootstrapped per-run Playwright isolation and validated output/profile dirs.
- Navigated to `<PORTAL_URL>` Tableau workbook “Supplier Growth Analysis”.
- HITL: user completed Premier SSO login.
- Opened workbook tab #2: “Sales & Market Share - Data Direct from Acute Providers”.

## Verification
- Playwright profile dir populated: `runs/2026-01-06__validate_insight_flash_reports/playwright-profile/`.
- Screenshots saved under `runs/2026-01-06__validate_insight_flash_reports/playwright-output/`:
	- `mcp-validation.png`
	- `initial-nav-check.png`
	- `hitl-sso-stop.png`
	- `dashboard-view.png`
	- `sales-market-share-tab.png`
	- `sales-market-share-tab-try-again.png`

## Next steps
- Load the “attached report” key findings and map each finding to this Tableau tab’s filters/metrics.
- Validate findings via on-screen values/tooltips and (if explicitly approved) Tableau Download exports into `runs/2026-01-06__validate_insight_flash_reports/downloads/`.

## Evidence + findings (Tab 2)

### NASAL ANTISEPTIC AND DECOLONIZATION (via table row)
- Set `Detail Limit` to `200` to reveal additional contract categories in the table.
- Evidence screenshot: `runs/2026-01-06__validate_insight_flash_reports/playwright-output/tab2-detail-limit-200.png`

Observed values from the “Performance by Contract Category and Market Segment” table row **NASAL ANTISEPTIC AND DECOLONIZATIO..**:
- **You**: Prior $3.9M; Most Recent $4.0M; Rolling 12mo YoY +3.9%; % of Total (Most Recent) 33.7%
- **Rest of Market**: Prior $7.4M; Most Recent $8.0M; Rolling 12mo YoY +7.0%; % of Total (Most Recent) 66.3%
- **Grand Total**: Prior $11.3M; Most Recent $12.0M; Rolling 12mo YoY +5.9%

Notes:
- This matches the executive summary’s NASAL Antiseptic sales + YoY growth figures (client $4.0M, total $12.0M, ROM $8.0M; market +5.9%, ROM +7.0%, client +3.9%).
- The “missed revenue” value is not directly shown in this view; may require a tooltip/alternate sheet or a Download export for calculation.

## Blockers
- Need the report content (or a list of the specific findings to validate).
