from __future__ import annotations

class sql:
    # Core SQL templates keyed for notebook materialization
    CORE_SQL = {
        "coverage": r"""
-- coverage (DATE month, PRD filters)
-- Canonical dimension mapping:
--   facility_id  := premier_entity_code
--   category     := contract_category
--   program_id   := program (string literal 'Surpass'/'Ascend')
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS facility_id,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT
    month_date,
    facility_id,
    category,
    contract_number,
    DATE(contract_effective_date) AS contract_effective_date,
    DATE(contract_expiration_date) AS contract_expiration_date,
    base_spend,
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program
  FROM base
),
program_in_term AS (
  SELECT
    pl.*,
    DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end
  FROM program_lines pl
  WHERE pl.program IS NOT NULL
    AND (pl.contract_effective_date IS NULL OR pl.contract_effective_date <= DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY))
    AND (pl.contract_expiration_date IS NULL OR pl.contract_expiration_date >= pl.month_date)
),
cat_month_tot AS (
  SELECT month_date, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2
),
program_contract_spend AS (
  SELECT program, category, month_date, contract_number, SUM(base_spend) AS contract_program_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
contract_metrics AS (
  SELECT
    pcs.*,
    SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date) AS program_spend,
    SAFE_DIVIDE(contract_program_spend,
                SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) AS contract_contrib_share,
    SAFE_CAST(contract_program_spend >= @anchor_contract_guard_abs_usd AS BOOL) AS passes_abs_guard,
    SAFE_CAST(SAFE_DIVIDE(contract_program_spend,
                          SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) >= @anchor_contract_guard_pp AS BOOL) AS passes_pp_guard
  FROM program_contract_spend pcs
),
contract_smoothing AS (
  SELECT
    cm.*,
    (cm.passes_pp_guard AND cm.passes_abs_guard) AS passes_threshold,
    LAG(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS prev_pass,
    LEAD(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS next_pass
  FROM contract_metrics cm
),
contract_eligible AS (
  SELECT
    cs.program,
    cs.category,
    cs.month_date,
    ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) >= 2 AS eligible_flag
  FROM contract_smoothing cs
),
eligible_contract_months AS (
  SELECT program, category, month_date, COUNTIF(eligible_flag) AS eligible_contracts
  FROM contract_eligible
  WHERE eligible_flag
  GROUP BY 1,2,3
),
coverage_by_program AS (
  SELECT
    p.program,
    p.category,
    p.month_date,
    ct.total_cat_spend,
    SAFE_DIVIDE(SUM(p.base_spend), ct.total_cat_spend) AS program_share_in_cat
  FROM program_in_term p
  JOIN cat_month_tot ct USING (month_date, category)
  GROUP BY 1,2,3, ct.total_cat_spend
)
SELECT
  cbp.program AS program,
  cbp.category AS category,
  cbp.month_date AS month,
  cbp.program_share_in_cat,
  SAFE_CAST(cbp.program_share_in_cat >= @coverage_guard AS BOOL) AS is_covered,
  COALESCE(ecm.eligible_contracts, 0) AS eligible_contract_count,
  SAFE_CAST(cbp.program_share_in_cat >= @coverage_guard AND COALESCE(ecm.eligible_contracts, 0) > 0 AS BOOL) AS is_covered_anchor
FROM coverage_by_program cbp
LEFT JOIN eligible_contract_months ecm
  ON ecm.program = cbp.program AND ecm.category = cbp.category AND ecm.month_date = cbp.month_date;
""",
        "presence": r"""
-- facility-level dataset presence by month (any spend > 0)
WITH base AS (
  SELECT
    DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
    premier_entity_code AS facility_id,
    SUM(base_spend) AS total_spend
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0
    AND quantity > 0
    AND matched_product_status IS NOT NULL
  GROUP BY 1,2
)
SELECT
  month_date AS month,
  facility_id,
  total_spend
FROM base;
""",
        "awarded_block": r"""
-- awarded OEMs per program×category×month_date (covered only)
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT
    month_date,
    category,
    manufacturer_id,
    contract_number,
    DATE(contract_effective_date) AS contract_effective_date,
    DATE(contract_expiration_date) AS contract_expiration_date,
    base_spend,
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program
  FROM base
),
program_in_term AS (
  SELECT
    pl.*,
    DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end
  FROM program_lines pl
  WHERE pl.program IS NOT NULL
    AND (pl.contract_effective_date IS NULL OR pl.contract_effective_date <= DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY))
    AND (pl.contract_expiration_date IS NULL OR pl.contract_expiration_date >= pl.month_date)
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_in_term p
  GROUP BY 1,2,3
),
covered AS (
  SELECT * FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
mfr AS (
  SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
mfr_with_tot AS (
  SELECT m.*, SUM(mfr_spend) OVER (PARTITION BY program, category, month_date) AS program_spend
  FROM mfr m
)
SELECT m.program AS program, m.category AS category, m.month_date,
       ARRAY_AGG(DISTINCT m.manufacturer_id IGNORE NULLS) AS awarded_block
FROM mfr_with_tot m
JOIN covered c USING (program, category, month_date)
WHERE SAFE_DIVIDE(m.mfr_spend, m.program_spend) >= @coverage_guard
GROUP BY 1,2,3;
""",
        "membership": r"""
-- facility×program×month_date membership (>= threshold)
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT
    month_date,
    entity_code,
    category,
    manufacturer_id,
    contract_number,
    DATE(contract_effective_date) AS contract_effective_date,
    DATE(contract_expiration_date) AS contract_expiration_date,
    base_spend,
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program
  FROM base
),
program_in_term AS (
  SELECT
    pl.*,
    DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end
  FROM program_lines pl
  WHERE pl.program IS NOT NULL
    AND (pl.contract_effective_date IS NULL OR pl.contract_effective_date <= DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY))
    AND (pl.contract_expiration_date IS NULL OR pl.contract_expiration_date >= pl.month_date)
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_in_term p
  GROUP BY 1,2,3
),
covered AS (
  SELECT * FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
fac_cat_tot AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
program_fac_spend AS (
  SELECT month_date, entity_code, program, SUM(base_spend) AS program_spend
  FROM program_in_term
  GROUP BY 1,2,3
),
covered_denoms AS (
  SELECT t.month_date, t.entity_code, c.program, SUM(t.total_cat_spend) AS denom_spend
  FROM fac_cat_tot t
  JOIN covered c USING (month_date, category)
  GROUP BY 1,2,3
),
membership AS (
  SELECT
    d.month_date,
    d.entity_code,
    d.program,
    SAFE_DIVIDE(p.program_spend, d.denom_spend) AS membership_share,
    SAFE_CAST(SAFE_DIVIDE(p.program_spend, d.denom_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM covered_denoms d
  LEFT JOIN program_fac_spend p
    ON p.month_date = d.month_date AND p.entity_code = d.entity_code AND p.program = d.program
),
membership_exclusive AS (
  SELECT * EXCEPT(rn) FROM (
    SELECT m.*, ROW_NUMBER() OVER (
      PARTITION BY month_date, entity_code
      ORDER BY member_flag DESC, membership_share DESC
    ) AS rn
    FROM membership m
  ) WHERE rn = 1
)
SELECT
  month_date AS month,
  entity_code AS facility_id,
  program,
  membership_share,
  member_flag
FROM membership_exclusive;
""",
        "shares": r"""
-- facility×category×month_date awarded_share and 6m rolling; event_month from SQL
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
months AS (
  SELECT m AS month_date
  FROM UNNEST(GENERATE_DATE_ARRAY(
                DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH),
                DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH),   INTERVAL 18 MONTH),
                INTERVAL 1 MONTH)) AS m
),
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
program_lines AS (
  SELECT
    month_date,
    entity_code,
    category,
    manufacturer_id,
    contract_number,
    DATE(contract_effective_date) AS contract_effective_date,
    DATE(contract_expiration_date) AS contract_expiration_date,
    base_spend,
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program
  FROM base
),
program_in_term AS (
  SELECT
    pl.*,
    DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end
  FROM program_lines pl
  WHERE pl.program IS NOT NULL
    AND (pl.contract_effective_date IS NULL OR pl.contract_effective_date <= DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY))
    AND (pl.contract_expiration_date IS NULL OR pl.contract_expiration_date >= pl.month_date)
),
program_contract_spend AS (
  SELECT
    program,
    category,
    month_date,
    contract_number,
    SUM(base_spend) AS contract_program_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
contract_metrics AS (
  SELECT
    pcs.*,
    SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date) AS program_spend,
    SAFE_DIVIDE(contract_program_spend,
                SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) AS contract_contrib_share,
    SAFE_CAST(contract_program_spend >= @anchor_contract_guard_abs_usd AS BOOL) AS passes_abs_guard,
    SAFE_CAST(SAFE_DIVIDE(contract_program_spend,
                          SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) >= @anchor_contract_guard_pp AS BOOL) AS passes_pp_guard,
    MIN(month_date) OVER (PARTITION BY program, category, contract_number) AS contract_start_month
  FROM program_contract_spend pcs
),
contract_smoothing AS (
  SELECT
    cm.*,
    (cm.passes_pp_guard AND cm.passes_abs_guard) AS passes_threshold,
    LAG(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS prev_pass,
    LEAD(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS next_pass
  FROM contract_metrics cm
),
contract_eligible AS (
  SELECT
    cs.*,
    ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) >= 2 AS eligible_flag,
    CASE
      WHEN NOT cs.passes_abs_guard THEN '<abs_floor'
      WHEN NOT cs.passes_pp_guard THEN '<2pp'
      WHEN ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
            (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
            (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) < 2 THEN 'fails_2of3'
      ELSE NULL
    END AS ineligible_reason
  FROM contract_smoothing cs
),
eligible_contract_months AS (
  SELECT
    program,
    category,
    month_date,
    ARRAY_AGG(contract_number ORDER BY contract_number) AS eligible_contract_numbers
  FROM contract_eligible
  WHERE eligible_flag
  GROUP BY 1,2,3
),
coverage_raw AS (
  SELECT
    p.program,
    p.category,
    p.month_date,
    SAFE_DIVIDE(SUM(p.base_spend), ANY_VALUE(ct.total_cat_spend)) AS program_share_in_cat
  FROM program_in_term p
  JOIN (
    SELECT month_date, category, SUM(base_spend) AS total_cat_spend
    FROM base
    GROUP BY 1,2
  ) ct USING (month_date, category)
  GROUP BY 1,2,3
),
coverage_logic AS (
  SELECT
    cr.*,
    SAFE_CAST(cr.program_share_in_cat >= @coverage_guard AS BOOL) AS is_covered,
    COALESCE(ARRAY_LENGTH(ecm.eligible_contract_numbers) > 0, FALSE) AS has_ccg_contract
  FROM coverage_raw cr
  LEFT JOIN eligible_contract_months ecm
    ON ecm.program = cr.program AND ecm.category = cr.category AND ecm.month_date = cr.month_date
),
coverage_with_neighbors AS (
  SELECT cl.*,
         SAFE_CAST(cl.is_covered AND cl.has_ccg_contract AS BOOL) AS is_covered_anchor,
         LAG(SAFE_CAST(cl.is_covered AND cl.has_ccg_contract AS BOOL)) OVER (PARTITION BY program, category ORDER BY month_date) AS prev_is_covered_anchor,
         LEAD(SAFE_CAST(cl.is_covered AND cl.has_ccg_contract AS BOOL)) OVER (PARTITION BY program, category ORDER BY month_date) AS next_is_covered_anchor
  FROM coverage_logic cl
),
stable_coverage AS (
  SELECT *
  FROM coverage_with_neighbors
  WHERE is_covered_anchor
    AND (COALESCE(prev_is_covered_anchor, FALSE) OR COALESCE(next_is_covered_anchor, FALSE))
),
covered AS (
  SELECT program, category, month_date, program_share_in_cat
  FROM coverage_logic
  WHERE is_covered
),
program_cat_tot AS (
  SELECT program, category, month_date, SUM(base_spend) AS program_spend
  FROM program_in_term
  GROUP BY 1,2,3
),
program_mfr_spend AS (
  SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
awarded_block AS (
  SELECT pms.program, pms.category, pms.month_date,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month_date)
  JOIN program_cat_tot pct USING (program, category, month_date)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    contract_number,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, contract_number, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
    AND program IS NOT NULL
),
eligible_contract_starts AS (
  SELECT
    ics.program,
    ics.category,
    ics.contract_number,
    MIN(ce.month_date) AS start_month
  FROM in_core_starts ics
  JOIN contract_eligible ce
    ON ce.program = ics.program
   AND ce.category = ics.category
   AND ce.contract_number = ics.contract_number
   AND ce.month_date >= ics.start_month
  WHERE ce.eligible_flag
  GROUP BY 1,2,3
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN stable_coverage sc
    ON sc.program = ab.program AND sc.category = ab.category AND sc.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM eligible_contract_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
),
pc_x_months AS (
  SELECT g.program, g.category, m.month_date AS month_date
  FROM t0_map g
  CROSS JOIN months m
),
event_map AS (
  SELECT x.program, x.category, x.month_date,
         DATE_DIFF(x.month_date, glm.go_live_month, MONTH) AS event_month
  FROM pc_x_months x
  JOIN t0_map glm USING (program, category)
),
eff_awards AS (
  SELECT g.program, g.category, m.month_date, COALESCE(ab_t0.awarded_block, []) AS awarded_block
  FROM t0_map g
  CROSS JOIN months m
  LEFT JOIN awarded_block ab_t0
    ON ab_t0.program = g.program AND ab_t0.category = g.category AND ab_t0.month_date = g.go_live_month
),
fac_cat_mfr AS (
  SELECT month_date, entity_code, category, manufacturer_id, SUM(base_spend) AS spend
  FROM base
  GROUP BY 1,2,3,4
),
fac_cat_tot AS (
  SELECT month_date, entity_code, category, SUM(spend) AS total_cat_spend
  FROM fac_cat_mfr
  GROUP BY 1,2,3
),
fac_cat_tot_for_mem AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
program_fac_spend AS (
  SELECT month_date, entity_code,
         program,
         SUM(base_spend) AS program_spend
  FROM program_in_term
  GROUP BY 1,2,3
),
covered_denoms AS (
  SELECT t.month_date, t.entity_code, c.program, SUM(t.total_cat_spend) AS denom_spend
  FROM fac_cat_tot_for_mem t
  JOIN covered c USING (month_date, category)
  GROUP BY 1,2,3
),
membership AS (
  SELECT d.month_date, d.entity_code, d.program,
         SAFE_DIVIDE(p.program_spend, d.denom_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, d.denom_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM covered_denoms d
  LEFT JOIN program_fac_spend p
    ON p.month_date = d.month_date AND p.entity_code = d.entity_code AND p.program = d.program
),
membership_exclusive AS (
  SELECT * EXCEPT(rn) FROM (
    SELECT m.*, ROW_NUMBER() OVER (PARTITION BY month_date, entity_code ORDER BY member_flag DESC, membership_share DESC) rn
    FROM membership m
  ) WHERE rn = 1
),
awarded_spend AS (
  SELECT f.month_date, f.entity_code, f.category, ea.program,
         SUM(CASE WHEN f.manufacturer_id IN UNNEST(ea.awarded_block) THEN f.spend END) AS awarded_spend
  FROM fac_cat_mfr f
  JOIN eff_awards ea
    ON ea.category = f.category AND ea.month_date = f.month_date
  GROUP BY 1,2,3,4
),
shares_panel AS (
  SELECT
    t.month_date AS month,
    t.entity_code AS facility_id,
    t.category AS category,
    a.program AS program,
    t.total_cat_spend,
    a.awarded_spend,
    SAFE_DIVIDE(a.awarded_spend, t.total_cat_spend) AS awarded_share,
    SUM(a.awarded_spend) OVER (
      PARTITION BY t.entity_code, t.category, a.program
      ORDER BY t.month_date
      ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS awarded_spend_6m,
    SUM(t.total_cat_spend) OVER (
      PARTITION BY t.entity_code, t.category, a.program
      ORDER BY t.month_date
      ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS total_cat_spend_6m,
    SAFE_DIVIDE(
      SUM(a.awarded_spend) OVER (
        PARTITION BY t.entity_code, t.category, a.program
        ORDER BY t.month_date
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
      ),
      SUM(t.total_cat_spend) OVER (
        PARTITION BY t.entity_code, t.category, a.program
        ORDER BY t.month_date
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
      )
    ) AS awarded_share_6m,
    em.event_month,
    me.member_flag,
    CASE WHEN em.event_month = 0 AND me.member_flag THEN TRUE END AS member_at_t0
  FROM fac_cat_tot t
  JOIN awarded_spend a
    ON a.month_date = t.month_date AND a.entity_code = t.entity_code AND a.category = t.category
  JOIN event_map em
    ON em.program = a.program AND em.category = t.category AND em.month_date = t.month_date
  LEFT JOIN membership_exclusive me
    ON me.program = a.program AND me.entity_code = t.entity_code AND me.month_date = t.month_date
  WHERE em.event_month BETWEEN -12 AND 18
)
SELECT
  sp.*,
  MAX(CASE WHEN sp.event_month = 0 THEN sp.total_cat_spend_6m END) OVER (
    PARTITION BY sp.facility_id, sp.category, sp.program
  ) AS t0_total_cat_spend_6m
FROM shares_panel sp;
""",
        "anchor_contracts": r"""
-- Helper panel for contract contribution guard diagnostics (Panel 2b)
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT
    month_date,
    category,
    contract_number,
    DATE(contract_effective_date) AS contract_effective_date,
    DATE(contract_expiration_date) AS contract_expiration_date,
    base_spend,
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program
  FROM base
),
program_in_term AS (
  SELECT
    pl.*,
    DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end
  FROM program_lines pl
  WHERE pl.program IS NOT NULL
    AND (pl.contract_effective_date IS NULL OR pl.contract_effective_date <= DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY))
    AND (pl.contract_expiration_date IS NULL OR pl.contract_expiration_date >= pl.month_date)
),
program_contract_spend AS (
  SELECT
    program,
    category,
    month_date,
    contract_number,
    SUM(base_spend) AS contract_program_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
contract_metrics AS (
  SELECT
    pcs.*,
    SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date) AS program_spend,
    SAFE_DIVIDE(contract_program_spend,
                SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) AS contract_contrib_share,
    SAFE_CAST(contract_program_spend >= @anchor_contract_guard_abs_usd AS BOOL) AS passes_abs_guard,
    SAFE_CAST(SAFE_DIVIDE(contract_program_spend,
                          SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) >= @anchor_contract_guard_pp AS BOOL) AS passes_pp_guard,
    MIN(month_date) OVER (PARTITION BY program, category, contract_number) AS contract_start_month
  FROM program_contract_spend pcs
),
contract_smoothing AS (
  SELECT
    cm.*,
    (cm.passes_pp_guard AND cm.passes_abs_guard) AS passes_threshold,
    LAG(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS prev_pass,
    LEAD(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS next_pass
  FROM contract_metrics cm
),
eligibility AS (
  SELECT
    cs.program,
    cs.category,
    cs.month_date,
    cs.contract_number,
    cs.contract_start_month,
    cs.contract_contrib_share,
    ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) >= 2 AS eligible_flag,
    CASE
      WHEN NOT cs.passes_abs_guard THEN '<abs_floor'
      WHEN NOT cs.passes_pp_guard THEN '<2pp'
      WHEN ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
            (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
            (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) < 2 THEN 'fails_2of3'
      ELSE NULL
    END AS reason
  FROM contract_smoothing cs
)
SELECT
  program AS program_id,
  category AS category_id,
  month_date AS month,
  contract_number,
  contract_start_month,
  contract_contrib_share,
  eligible_flag,
  reason
FROM eligibility
ORDER BY program_id, category_id, month, contract_number;
""",
    }

# Backwards-compat exports (module-level aliases)
CORE_SQL = sql.CORE_SQL

CONTROLS_SQL = r"""
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
      DATE(contract_effective_date) AS contract_effective_date,
      DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
    Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
months AS (
  SELECT month
  FROM UNNEST(GENERATE_DATE_ARRAY(
                DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH),
                DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH),   INTERVAL 18 MONTH),
                INTERVAL 1 MONTH)) AS month
),
program_lines AS (
  SELECT
    month_date,
    entity_code,
    category,
    manufacturer_id,
    contract_number,
    DATE(contract_effective_date) AS contract_effective_date,
    DATE(contract_expiration_date) AS contract_expiration_date,
    base_spend,
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program
  FROM base
),
program_in_term AS (
  SELECT
    pl.*,
    DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY) AS month_end
  FROM program_lines pl
  WHERE pl.program IS NOT NULL
    AND (pl.contract_effective_date IS NULL OR pl.contract_effective_date <= DATE_SUB(DATE_ADD(pl.month_date, INTERVAL 1 MONTH), INTERVAL 1 DAY))
    AND (pl.contract_expiration_date IS NULL OR pl.contract_expiration_date >= pl.month_date)
),
program_contract_spend AS (
  SELECT
    program,
    category,
    month_date,
    contract_number,
    SUM(base_spend) AS contract_program_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
contract_metrics AS (
  SELECT
    pcs.*,
    SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date) AS program_spend,
    SAFE_DIVIDE(contract_program_spend,
                SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) AS contract_contrib_share,
    SAFE_CAST(contract_program_spend >= @anchor_contract_guard_abs_usd AS BOOL) AS passes_abs_guard,
    SAFE_CAST(SAFE_DIVIDE(contract_program_spend,
                          SUM(contract_program_spend) OVER (PARTITION BY program, category, month_date)) >= @anchor_contract_guard_pp AS BOOL) AS passes_pp_guard,
    MIN(month_date) OVER (PARTITION BY program, category, contract_number) AS contract_start_month
  FROM program_contract_spend pcs
),
contract_smoothing AS (
  SELECT
    cm.*,
    (cm.passes_pp_guard AND cm.passes_abs_guard) AS passes_threshold,
    LAG(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS prev_pass,
    LEAD(cm.passes_pp_guard AND cm.passes_abs_guard) OVER (PARTITION BY program, category, contract_number ORDER BY month_date) AS next_pass
  FROM contract_metrics cm
),
contract_eligible AS (
  SELECT
    cs.*,
    ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
     (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) >= 2 AS eligible_flag,
    CASE
      WHEN NOT cs.passes_abs_guard THEN '<abs_floor'
      WHEN NOT cs.passes_pp_guard THEN '<2pp'
      WHEN ((CASE WHEN cs.passes_threshold THEN 1 ELSE 0 END) +
            (CASE WHEN COALESCE(cs.prev_pass, FALSE) THEN 1 ELSE 0 END) +
            (CASE WHEN COALESCE(cs.next_pass, FALSE) THEN 1 ELSE 0 END)) < 2 THEN 'fails_2of3'
      ELSE NULL
    END AS ineligible_reason
  FROM contract_smoothing cs
),
eligible_contract_months AS (
  SELECT
    program,
    category,
    month_date,
    ARRAY_AGG(contract_number ORDER BY contract_number) AS eligible_contract_numbers
  FROM contract_eligible
  WHERE eligible_flag
  GROUP BY 1,2,3
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(p.base_spend), ANY_VALUE(ct.total_cat_spend)) AS program_share_in_cat
  FROM program_in_term p
  JOIN (
    SELECT month_date, category, SUM(base_spend) AS total_cat_spend
    FROM base
    GROUP BY 1,2
  ) ct USING (month_date, category)
  GROUP BY 1,2,3
),
coverage_logic AS (
  SELECT
    c.*,
    SAFE_CAST(c.program_share_in_cat >= @coverage_guard AS BOOL) AS is_covered,
    COALESCE(ARRAY_LENGTH(ecm.eligible_contract_numbers) > 0, FALSE) AS has_ccg_contract
  FROM coverage c
  LEFT JOIN eligible_contract_months ecm
    ON ecm.program = c.program AND ecm.category = c.category AND ecm.month_date = c.month_date
),
coverage_with_neighbors AS (
  SELECT cl.*,
         SAFE_CAST(cl.is_covered AND cl.has_ccg_contract AS BOOL) AS is_covered_anchor,
         LAG(SAFE_CAST(cl.is_covered AND cl.has_ccg_contract AS BOOL)) OVER (PARTITION BY program, category ORDER BY month_date) AS prev_is_covered_anchor,
         LEAD(SAFE_CAST(cl.is_covered AND cl.has_ccg_contract AS BOOL)) OVER (PARTITION BY program, category ORDER BY month_date) AS next_is_covered_anchor
  FROM coverage_logic cl
),
stable_coverage AS (
  SELECT *
  FROM coverage_with_neighbors
  WHERE is_covered_anchor
    AND (COALESCE(prev_is_covered_anchor, FALSE) OR COALESCE(next_is_covered_anchor, FALSE))
),
covered AS (
  SELECT program, category, month_date, program_share_in_cat
  FROM coverage_logic
  WHERE is_covered
),
program_cat_tot AS (
  SELECT program, category, month_date, SUM(base_spend) AS program_spend
  FROM program_in_term
  GROUP BY 1,2,3
),
program_mfr_spend AS (
  SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_in_term
  GROUP BY 1,2,3,4
),
awarded_block AS (
  SELECT pms.program, pms.category, pms.month_date,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month_date)
  JOIN program_cat_tot pct USING (program, category, month_date)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
-- Contract-driven anchor inside core window per PRD §4.5
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    contract_number,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, contract_number, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
    AND program IS NOT NULL
),
eligible_contract_starts AS (
  SELECT
    ics.program,
    ics.category,
    ics.contract_number,
    MIN(ce.month_date) AS start_month
  FROM in_core_starts ics
  JOIN contract_eligible ce
    ON ce.program = ics.program
   AND ce.category = ics.category
   AND ce.contract_number = ics.contract_number
   AND ce.month_date >= ics.start_month
  WHERE ce.eligible_flag
  GROUP BY 1,2,3
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN stable_coverage sc
    ON sc.program = ab.program AND sc.category = ab.category AND sc.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM eligible_contract_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
),
pc_x_months AS (
  SELECT g.program, g.category, m.month AS month_date
  FROM t0_map g
  CROSS JOIN months m
),
event_map AS (
  SELECT x.program, x.category, x.month_date,
         DATE_DIFF(x.month_date, glm.go_live_month, MONTH) AS event_month
  FROM pc_x_months x
  JOIN t0_map glm USING (program, category)
),
-- Explicit members' anchor per (program, category) for aligning controls
members_anchor AS (
  SELECT program, category, go_live_month AS anchor_month_date_median
  FROM t0_map
),
-- Effective awards per month (carry forward latest award set; fallback to first for pre-go-live)
eff_awards AS (
  -- PRD t0-freeze: use the award set at go_live_month for all months
  SELECT
    g.program,
    g.category,
    m.month AS month_date,
    COALESCE(ab_t0.awarded_block, []) AS awarded_block
  FROM t0_map g
  CROSS JOIN months m
  LEFT JOIN awarded_block ab_t0
    ON ab_t0.program = g.program AND ab_t0.category = g.category AND ab_t0.month_date = g.go_live_month
),
-- Aggregate facility×cat monthly totals (needed before control cohort build)
-- Use base spend (not program_lines) to avoid dropping pre months lacking program-coded rows
fac_cat_mfr AS (
  SELECT month_date, entity_code, category, manufacturer_id, SUM(base_spend) AS spend
  FROM base
  GROUP BY 1,2,3,4
),
fac_cat_tot2 AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
-- Membership using covered-category denominator and exclusivity (consistent with PRD)
fac_cat_tot_for_mem AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
program_fac_spend AS (
  SELECT month_date, entity_code,
         program,
         SUM(base_spend) AS program_spend
  FROM program_in_term
  GROUP BY 1,2,3
),
covered_denoms AS (
  SELECT t.month_date, t.entity_code, c.program, SUM(t.total_cat_spend) AS denom_spend
  FROM fac_cat_tot_for_mem t
  JOIN covered c USING (month_date, category)
  GROUP BY 1,2,3
),
membership AS (
  SELECT d.month_date, d.entity_code, d.program,
         SAFE_DIVIDE(p.program_spend, d.denom_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, d.denom_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM covered_denoms d
  LEFT JOIN program_fac_spend p
    ON p.month_date = d.month_date AND p.entity_code = d.entity_code AND p.program = d.program
),
membership_exclusive AS (
  SELECT * EXCEPT(rn) FROM (
    SELECT m.*, ROW_NUMBER() OVER (PARTITION BY month_date, entity_code ORDER BY member_flag DESC, membership_share DESC) rn
    FROM membership m
  ) WHERE rn = 1
),
-- Control candidates: non-members of the focal program (allow National, allow other-program members)
control_candidates AS (
  SELECT DISTINCT
    em.program, em.category, em.month_date, em.event_month, t.entity_code
  FROM event_map em
  -- IMPORTANT: Use spend-based facility×category presence (fac_cat_tot_for_mem)
  -- instead of fac_cat_tot2 (which depends on manufacturer_id aggregation) so
  -- that valid pre-period facility-category months without mapped manufacturer rows
  -- are retained for control candidacy.
  JOIN fac_cat_tot_for_mem t
    ON t.month_date = em.month_date AND t.category = em.category
  -- Determine non-membership with respect to the focal program WITHOUT exclusivity
  LEFT JOIN membership me
    ON me.month_date = em.month_date AND me.entity_code = t.entity_code AND me.program = em.program
  WHERE COALESCE(me.member_flag, FALSE) = FALSE
),
-- Recompute control event month using members' anchor (explicit alignment)
controls_with_anchor AS (
  SELECT
    cc.program,
    cc.category,
    cc.month_date,
    cc.entity_code,
    -- recomputed aligned event month (equivalent to event_map join but explicit)
    DATE_DIFF(cc.month_date, ma.anchor_month_date_median, MONTH) AS aligned_event_month
  FROM control_candidates cc
  JOIN members_anchor ma
    ON ma.program = cc.program AND ma.category = cc.category
),
-- Other committed program’s awards for overlap exclusion
other_prog_commit AS (
  SELECT cc.entity_code, cc.category, cc.month_date, cc.program,
         ARRAY_CONCAT_AGG(ab.awarded_block) AS other_awarded_mfrs
  FROM control_candidates cc
  JOIN eff_awards ab
    ON ab.category = cc.category AND ab.month_date = cc.month_date AND ab.program != cc.program
  GROUP BY 1,2,3,4
),
controls_pool AS (
  SELECT cw.*
  FROM controls_with_anchor cw
  -- NOTE: LEFT JOIN to focal awards so months with empty/unknown focal award set are retained (pre months)
  LEFT JOIN eff_awards focal
    ON focal.program = cw.program AND focal.category = cw.category AND focal.month_date = cw.month_date
  LEFT JOIN other_prog_commit o
    ON o.entity_code = cw.entity_code AND o.category = cw.category AND o.month_date = cw.month_date AND o.program = cw.program
  -- Only drop controls if the facility is a member of the other performance program AND award sets overlap; keep National
  LEFT JOIN membership me_other
    ON me_other.month_date = cw.month_date AND me_other.entity_code = cw.entity_code AND me_other.program != cw.program
  WHERE (
    -- Always keep pre months regardless of overlap
    cw.aligned_event_month < 0
  ) OR (
    o.other_awarded_mfrs IS NULL
  ) OR (
    COALESCE(me_other.member_flag, FALSE) = FALSE
  ) OR (
    -- Keep when the other program's award set is NOT EXACTLY EQUAL to focal award set (PRD equality rule)
    (
      ARRAY_LENGTH(ARRAY(
        SELECT elem FROM UNNEST(ARRAY(SELECT DISTINCT a FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS a)) AS elem
        EXCEPT DISTINCT
        SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
      )) > 0
    ) OR (
      ARRAY_LENGTH(ARRAY(
        SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
        EXCEPT DISTINCT
        SELECT elem FROM UNNEST(ARRAY(SELECT DISTINCT a FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS a)) AS elem
      )) > 0
    )
  )
),
-- Aggregate facility×cat monthly totals
-- Compute awarded_spend for controls
controls_panel AS (
  SELECT
    cp.program, cp.category, cp.month_date, cp.entity_code,
    cp.aligned_event_month,
    t.total_cat_spend,
    COALESCE((
      SELECT SUM(fcm.spend)
      FROM UNNEST(COALESCE(focal.awarded_block, [])) AS m
      JOIN fac_cat_mfr fcm
        ON fcm.month_date = cp.month_date
       AND fcm.entity_code = cp.entity_code
       AND fcm.category   = cp.category
       AND fcm.manufacturer_id = m
    ), 0.0) AS awarded_spend
  FROM controls_pool cp
  JOIN fac_cat_tot2 t
    ON t.month_date = cp.month_date AND t.entity_code = cp.entity_code AND t.category = cp.category
  LEFT JOIN eff_awards focal
    ON focal.program = cp.program AND focal.category = cp.category AND focal.month_date = cp.month_date
),
controls_panel_roll AS (
  SELECT
    cp.program AS program,
    cp.category AS category,
    cp.month_date AS month,
    cp.entity_code AS facility_id,
    cp.total_cat_spend AS total_cat_spend,
    cp.awarded_spend AS awarded_spend,
    SUM(cp.awarded_spend) OVER (
      PARTITION BY cp.program, cp.category, cp.entity_code
      ORDER BY cp.month_date
      ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS awarded_spend_6m,
    SUM(cp.total_cat_spend) OVER (
      PARTITION BY cp.program, cp.category, cp.entity_code
      ORDER BY cp.month_date
      ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
    ) AS total_cat_spend_6m,
    SAFE_DIVIDE(
      SUM(cp.awarded_spend) OVER (
        PARTITION BY cp.program, cp.category, cp.entity_code
        ORDER BY cp.month_date
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
      ),
      SUM(cp.total_cat_spend) OVER (
        PARTITION BY cp.program, cp.category, cp.entity_code
        ORDER BY cp.month_date
        ROWS BETWEEN 5 PRECEDING AND CURRENT ROW
      )
    ) AS awarded_share_6m,
    cp.aligned_event_month AS event_month
  FROM controls_panel cp
)
SELECT
  cpr.*,
  MAX(CASE WHEN cpr.event_month = 0 THEN cpr.total_cat_spend_6m END) OVER (
    PARTITION BY cpr.facility_id, cpr.category, cpr.program
  ) AS t0_total_cat_spend_6m
FROM controls_panel_roll cpr
WHERE cpr.event_month BETWEEN -12 AND 18;
"""

CONTROLS_OVERLAP_QA_SQL = r"""
-- Return single row: excluded_count facility×category×month due to overlap exclusion (program-aware)
-- Canonical mapping: facility_id := entity_code
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         base_spend,
    Contract_Type AS contract_type,
         member_type,
         aggregation_flag,
         quantity
  FROM `{table}`
  WHERE DATE_TRUNC(DATE(Transaction_Date), MONTH) BETWEEN PARSE_DATE('%Y-%m', @START_MONTH) AND PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT month, entity_code, category, manufacturer_id, base_spend,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program
  FROM base
),
coverage AS (
  SELECT p.program, p.category, p.month,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month, category)) AS program_share_in_cat
  FROM program_lines p
  WHERE p.program IS NOT NULL
  GROUP BY 1,2,3
),
covered AS (
  SELECT * FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
program_cat_tot AS (
  SELECT program, category, month, SUM(base_spend) AS program_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3
),
program_mfr_spend AS (
  SELECT program, category, month, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3,4
),
awarded_block AS (
  SELECT pms.program, pms.category, pms.month,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month)
  JOIN program_cat_tot pct USING (program, category, month)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
-- membership and non_members per program
fac_cat_tot AS (
  SELECT month, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM program_lines
  GROUP BY 1,2,3
),
-- Facility monthly total spend across all categories
fac_tot AS (
  SELECT month, entity_code, SUM(base_spend) AS total_spend
  FROM program_lines
  GROUP BY 1,2
),
program_fac_spend AS (
  SELECT month, entity_code, program, SUM(base_spend) AS program_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3
),
membership AS (
  SELECT p.month, p.entity_code, p.program,
         SAFE_DIVIDE(p.program_spend, t.total_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, t.total_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM program_fac_spend p
  JOIN fac_tot t USING (month, entity_code)
),
membership_any AS (
  SELECT month, entity_code, MAX(CASE WHEN member_flag THEN 1 ELSE 0 END) AS any_member
  FROM membership
  GROUP BY 1,2
),
national_non_members AS (
  -- Restrict to facilities with spend in focal category-months that have an award set (anchor on awarded_block)
  SELECT ab.program, ab.category, ab.month, t.entity_code
  FROM awarded_block ab
  JOIN fac_cat_tot t
    ON t.month = ab.month AND t.category = ab.category
  LEFT JOIN membership_any ma
    ON ma.month = t.month AND ma.entity_code = t.entity_code
  WHERE IFNULL(ma.any_member, 0) = 0
),
excluded_facilities AS (
  SELECT DISTINCT nm.program, nm.category, nm.month, nm.entity_code
  FROM national_non_members nm
  JOIN awarded_block focal
    ON focal.program = nm.program AND focal.category = nm.category AND focal.month = nm.month
  JOIN UNNEST(focal.awarded_block) AS m_f
  JOIN awarded_block other
    ON other.category = nm.category AND other.month = nm.month AND other.program != nm.program
  JOIN UNNEST(other.awarded_block) AS m_o
    ON m_o = m_f
)
SELECT COUNT(*) AS excluded_count FROM excluded_facilities;
"""

CONTROLS_ATTRITION_SQL = r"""
-- Diagnostic: control cohort attrition per (program, category)
-- Counts at each stage to identify where rows drop to zero
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
      DATE(contract_effective_date) AS contract_effective_date,
      DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
    Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT month_date, entity_code, category, manufacturer_id, base_spend,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program
  FROM base
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_lines p
  WHERE p.program IS NOT NULL
  GROUP BY 1,2,3
),
covered AS (
  SELECT program, category, month_date FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
program_cat_tot AS (
  SELECT program, category, month_date, SUM(base_spend) AS program_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3
),
program_mfr_spend AS (
  SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3,4
),
awarded_block AS (
  SELECT pms.program, pms.category, pms.month_date,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month_date)
  JOIN program_cat_tot pct USING (program, category, month_date)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
months AS (
  SELECT m AS month_date
  FROM UNNEST(GENERATE_DATE_ARRAY(
                DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH),
                DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH),   INTERVAL 18 MONTH),
                INTERVAL 1 MONTH)) AS m
),
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN covered c
    ON c.program = ab.program AND c.category = ab.category AND c.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM in_core_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
),
event_map AS (
  SELECT x.program, x.category, x.month_date,
         DATE_DIFF(x.month_date, glm.go_live_month, MONTH) AS event_month
  FROM (SELECT DISTINCT program, category, month_date FROM program_lines) x
  JOIN t0_map glm USING (program, category)
),
fac_cat_tot_for_mem AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
program_fac_spend AS (
  SELECT month_date, entity_code,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program,
         SUM(base_spend) AS program_spend
  FROM base
  GROUP BY 1,2,3
),
covered_denoms AS (
  SELECT t.month_date, t.entity_code, c.program, SUM(t.total_cat_spend) AS denom_spend
  FROM fac_cat_tot_for_mem t
  JOIN covered c USING (month_date, category)
  GROUP BY 1,2,3
),
membership AS (
  SELECT d.month_date, d.entity_code, d.program,
         SAFE_DIVIDE(p.program_spend, d.denom_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, d.denom_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM covered_denoms d
  LEFT JOIN program_fac_spend p
    ON p.month_date = d.month_date AND p.entity_code = d.entity_code AND p.program = d.program
),
control_candidates AS (
  SELECT DISTINCT em.program, em.category, em.month_date, em.event_month, t.entity_code
  FROM event_map em
  JOIN fac_cat_tot_for_mem t
    ON t.month_date = em.month_date AND t.category = em.category
  LEFT JOIN membership me
    ON me.month_date = em.month_date AND me.entity_code = t.entity_code AND me.program = em.program
  WHERE COALESCE(me.member_flag, FALSE) = FALSE
),
members_anchor AS (
  SELECT program, category, go_live_month AS anchor_month_date_median
  FROM t0_map
),
controls_with_anchor AS (
  SELECT cc.program, cc.category, cc.month_date, cc.entity_code,
         DATE_DIFF(cc.month_date, ma.anchor_month_date_median, MONTH) AS aligned_event_month
  FROM control_candidates cc
  JOIN members_anchor ma USING (program, category)
),
other_prog_commit AS (
  SELECT cc.entity_code, cc.category, cc.month_date, cc.program,
         ARRAY_CONCAT_AGG(ab.awarded_block) AS other_awarded_mfrs
  FROM control_candidates cc
  JOIN awarded_block ab
    ON ab.category = cc.category AND ab.month_date = cc.month_date AND ab.program != cc.program
  GROUP BY 1,2,3,4
),
controls_pool AS (
  SELECT cw.*
  FROM controls_with_anchor cw
  LEFT JOIN awarded_block focal
    ON focal.program = cw.program AND focal.category = cw.category AND focal.month_date = cw.month_date
  LEFT JOIN other_prog_commit o
    ON o.entity_code = cw.entity_code AND o.category = cw.category AND o.month_date = cw.month_date AND o.program = cw.program
  LEFT JOIN membership me_other
    ON me_other.month_date = cw.month_date AND me_other.entity_code = cw.entity_code AND me_other.program != cw.program
  WHERE (
    cw.aligned_event_month < 0
  ) OR (
    o.other_awarded_mfrs IS NULL
  ) OR (
    COALESCE(me_other.member_flag, FALSE) = FALSE
  ) OR (
    (
      ARRAY_LENGTH(ARRAY(
        SELECT elem FROM UNNEST(ARRAY(SELECT DISTINCT a FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS a)) AS elem
        EXCEPT DISTINCT
        SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
      )) > 0
    ) OR (
      ARRAY_LENGTH(ARRAY(
        SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
        EXCEPT DISTINCT
        SELECT elem FROM UNNEST(ARRAY(SELECT DISTINCT a FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS a)) AS elem
      )) > 0
    )
  )
),
final_panel AS (
  SELECT cp.program, cp.category, cp.entity_code, COUNTIF(aligned_event_month < 0) AS pre_rows,
         COUNT(*) AS total_rows
  FROM controls_pool cp
  GROUP BY 1,2,3
)
SELECT
  g.program,
  g.category,
  (SELECT COUNT(DISTINCT entity_code) FROM control_candidates c WHERE c.program=g.program AND c.category=g.category) AS n_candidates,
  (SELECT COUNT(*) FROM control_candidates c WHERE c.program=g.program AND c.category=g.category AND c.event_month < 0) AS pre_month_rows,
  (SELECT COUNT(DISTINCT entity_code) FROM controls_pool p WHERE p.program=g.program AND p.category=g.category) AS n_after_overlap_exclusion,
  (SELECT SUM(pre_rows) FROM final_panel f WHERE f.program=g.program AND f.category=g.category) AS pre_rows_in_final
FROM t0_map g;
"""

CONTROLS_ANCHOR_QA_SQL = r"""
-- Diagnostic: count anchors (go_live_map) in controls pipeline
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
      DATE(contract_effective_date) AS contract_effective_date,
      DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
    Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT month_date, category, manufacturer_id, base_spend,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program
  FROM base
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_lines p
  WHERE p.program IS NOT NULL
  GROUP BY 1,2,3
),
covered AS (
  SELECT program, category, month_date FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
program_cat_tot AS (
  SELECT program, category, month_date, SUM(base_spend) AS program_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3
),
program_mfr_spend AS (
  SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3,4
),
awarded_block AS (
  SELECT pms.program, pms.category, pms.month_date,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month_date)
  JOIN program_cat_tot pct USING (program, category, month_date)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN covered c
    ON c.program = ab.program AND c.category = ab.category AND c.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM in_core_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
)
SELECT program, category, COUNT(*) AS anchors
FROM t0_map
GROUP BY 1,2
ORDER BY program, category;
"""

    # Staging builders
STAGING_FAC_CAT_MFR = r"""
CREATE OR REPLACE TABLE `{fac_cat_mfr}` AS
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         base_spend, quantity, member_type, aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= PARSE_DATE('%Y-%m', @START_MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
)
SELECT month_date, entity_code AS facility_id, category, manufacturer_id, SUM(base_spend) AS spend
FROM base
GROUP BY 1,2,3,4;
"""

STAGING_FAC_CAT_TOT = r"""
CREATE OR REPLACE TABLE `{fac_cat_tot}` AS
SELECT month_date, facility_id AS entity_code, category, SUM(spend) AS total_cat_spend
FROM `{fac_cat_mfr}`
GROUP BY 1,2,3;
"""

    # Variants that read from staging tables for heavy aggregations
SHARES_FROM_STAGING = r"""
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
      DATE(contract_effective_date) AS contract_effective_date,
      DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
    Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= PARSE_DATE('%Y-%m', @START_MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT month_date, category, manufacturer_id, base_spend,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program
  FROM base
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_lines p
  WHERE p.program IS NOT NULL
  GROUP BY 1,2,3
),
covered AS (
  SELECT * FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
awarded_block AS (
  -- OEMs with share of program spend ≥ coverage guard (PRD OEM threshold)
  WITH program_cat_tot AS (
    SELECT program, category, month_date, SUM(base_spend) AS program_spend
    FROM program_lines
    WHERE program IS NOT NULL
    GROUP BY 1,2,3
  ),
  program_mfr_spend AS (
    SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
    FROM program_lines
    WHERE program IS NOT NULL
    GROUP BY 1,2,3,4
  )
  SELECT pms.program, pms.category, pms.month_date,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month_date)
  JOIN program_cat_tot pct USING (program, category, month_date)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN covered c
    ON c.program = ab.program AND c.category = ab.category AND c.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM in_core_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
),
event_map AS (
  SELECT s.program, s.category, s.month_date,
         DATE_DIFF(s.month_date, glm.go_live_month, MONTH) AS event_month
  FROM (SELECT DISTINCT program, category, month_date FROM program_lines) s
  JOIN t0_map glm USING (program, category)
),
-- Effective awards per month (carry forward latest award set; fallback to first for pre-go-live)
eff_awards AS (
  -- PRD t0-freeze: use the award set at go_live_month for all months
  WITH months AS (
    SELECT DISTINCT month_date FROM `{fac_cat_tot}`
  )
  SELECT
    g.program,
    g.category,
    m.month_date,
    COALESCE(ab_t0.awarded_block, []) AS awarded_block
  FROM t0_map g
  CROSS JOIN months m
  LEFT JOIN awarded_block ab_t0
    ON ab_t0.program = g.program AND ab_t0.category = g.category AND ab_t0.month_date = g.go_live_month
),
-- membership inference & exclusivity
fac_cat_tot_for_mem AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
program_fac_spend AS (
  SELECT month_date, entity_code,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program,
         SUM(base_spend) AS program_spend
  FROM base
  GROUP BY 1,2,3
),
covered_denoms AS (
  SELECT t.month_date, t.entity_code, c.program, SUM(t.total_cat_spend) AS denom_spend
  FROM fac_cat_tot_for_mem t
  JOIN covered c USING (month_date, category)
  GROUP BY 1,2,3
),
membership AS (
  SELECT d.month_date, d.entity_code, d.program,
         SAFE_DIVIDE(p.program_spend, d.denom_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, d.denom_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM covered_denoms d
  LEFT JOIN program_fac_spend p
    ON p.month_date = d.month_date AND p.entity_code = d.entity_code AND p.program = d.program
),
membership_exclusive AS (
  SELECT * EXCEPT(rn) FROM (
    SELECT m.*, ROW_NUMBER() OVER (PARTITION BY month_date, entity_code ORDER BY member_flag DESC, membership_share DESC) rn
    FROM membership m
  ) WHERE rn = 1
),
fac_cat_mfr AS (
  SELECT month_date, entity_code, category, manufacturer_id, spend FROM `{fac_cat_mfr}`
),
fac_cat_tot AS (
  SELECT month_date, entity_code, category, total_cat_spend FROM `{fac_cat_tot}`
),
awarded_spend AS (
  SELECT f.month_date, f.entity_code, f.category, ea.program,
         SUM(CASE WHEN f.manufacturer_id IN UNNEST(ea.awarded_block) THEN f.spend END) AS awarded_spend
  FROM fac_cat_mfr f
  JOIN eff_awards ea
    ON ea.category = f.category AND ea.month_date = f.month_date
  GROUP BY 1,2,3,4
)
SELECT t.month_date AS month,
       t.entity_code,
       t.category,
       a.program,
       t.total_cat_spend,
       a.awarded_spend,
       SAFE_DIVIDE(a.awarded_spend, t.total_cat_spend) AS awarded_share,
       SAFE_DIVIDE(SUM(a.awarded_spend) OVER (
         PARTITION BY t.entity_code, t.category, a.program ORDER BY t.month_date ROWS BETWEEN 5 PRECEDING AND CURRENT ROW),
         SUM(t.total_cat_spend) OVER (
         PARTITION BY t.entity_code, t.category, a.program ORDER BY t.month_date ROWS BETWEEN 5 PRECEDING AND CURRENT ROW)
       ) AS awarded_share_6m,
  em.event_month
FROM fac_cat_tot t
JOIN awarded_spend a
  ON a.month_date = t.month_date AND a.entity_code = t.entity_code AND a.category = t.category
JOIN event_map em
  ON em.program = a.program AND em.category = t.category AND em.month_date = t.month_date
JOIN membership_exclusive me
  ON me.month_date = t.month_date AND me.entity_code = t.entity_code AND me.program = a.program
WHERE me.member_flag = TRUE
  AND em.event_month BETWEEN -12 AND 18;
"""

CONTROLS_FROM_STAGING = r"""
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
    premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= PARSE_DATE('%Y-%m', @START_MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT month_date, entity_code, category, manufacturer_id, base_spend,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program
  FROM base
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_lines p
  WHERE p.program IS NOT NULL
  GROUP BY 1,2,3
),
covered AS (
  SELECT program, category, month_date FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
awarded_block AS (
  SELECT program, category, month_date, ARRAY_AGG(DISTINCT manufacturer_id IGNORE NULLS) AS awarded_block
  FROM (
    SELECT DISTINCT pl.program, pl.category, pl.month_date, pl.manufacturer_id
    FROM program_lines pl
    JOIN covered c USING (program, category, month_date)
  ) x
  GROUP BY 1,2,3
),
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN covered c
    ON c.program = ab.program AND c.category = ab.category AND c.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM in_core_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
),
months AS (
  SELECT DISTINCT month_date AS month FROM `{fac_cat_tot}`
),
pc_x_months AS (
  SELECT g.program, g.category, m.month AS month_date
  FROM t0_map g
  CROSS JOIN months m
),
event_map AS (
  SELECT x.program, x.category, x.month_date,
         DATE_DIFF(x.month_date, glm.go_live_month, MONTH) AS event_month
  FROM pc_x_months x
  JOIN t0_map glm USING (program, category)
),
-- Effective awards per month (carry forward latest award set; fallback to first for pre-go-live)
eff_awards AS (
  -- PRD t0-freeze: use the award set at go_live_month for all months
  SELECT
    g.program,
    g.category,
    m.month AS month_date,
    COALESCE(ab_t0.awarded_block, []) AS awarded_block
  FROM t0_map g
  CROSS JOIN months m
  LEFT JOIN awarded_block ab_t0
    ON ab_t0.program = g.program AND ab_t0.category = g.category AND ab_t0.month_date = g.go_live_month
),
-- Membership and non-members per program
fac_cat_tot AS (
  SELECT month_date, entity_code, category, total_cat_spend FROM `{fac_cat_tot}`
),
-- Facility monthly total spend across all categories
fac_tot AS (
  SELECT month_date, entity_code, SUM(base_spend) AS total_spend
  FROM base
  GROUP BY 1,2
),
program_fac_spend AS (
  SELECT month_date, entity_code, program, SUM(base_spend) AS program_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3
),
membership AS (
  SELECT p.month_date, p.entity_code, p.program,
         SAFE_DIVIDE(p.program_spend, t.total_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, t.total_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM program_fac_spend p
  JOIN fac_tot t USING (month_date, entity_code)
),
membership_any AS (
  SELECT month_date, entity_code, MAX(CASE WHEN member_flag THEN 1 ELSE 0 END) AS any_member
  FROM membership
  GROUP BY 1,2
),
national_non_members AS (
  -- Restrict to facilities with spend in the focal category-month
  SELECT em.program, em.category, em.month_date, t.entity_code
  FROM pc_x_months em
  JOIN `{fac_cat_tot}` t
    ON t.month_date = em.month_date AND t.category = em.category
  LEFT JOIN membership_any ma
    ON ma.month_date = t.month_date AND ma.entity_code = t.entity_code
  WHERE IFNULL(ma.any_member, 0) = 0
),
other_prog_commit AS (
  SELECT nm.entity_code, nm.category, nm.month_date, nm.program,
         ARRAY_CONCAT_AGG(ab.awarded_block) AS other_awarded_mfrs
  FROM national_non_members nm
  JOIN eff_awards ab
    ON ab.category = nm.category AND ab.month_date = nm.month_date AND ab.program != nm.program
  GROUP BY 1,2,3,4
),
controls_pool AS (
  SELECT nm.*
  FROM national_non_members nm
  JOIN eff_awards focal
    ON focal.program = nm.program AND focal.category = nm.category AND focal.month_date = nm.month_date
  LEFT JOIN other_prog_commit o
    ON o.entity_code = nm.entity_code AND o.category = nm.category AND o.month_date = nm.month_date AND o.program = nm.program
  WHERE o.other_awarded_mfrs IS NULL
     OR ARRAY_LENGTH(ARRAY(
         SELECT elem FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS elem
         INTERSECT DISTINCT
         SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
       )) = 0
),
-- Aggregate facility×cat monthly totals from staging
fac_cat_mfr AS (
  SELECT month_date, entity_code, category, manufacturer_id, spend FROM `{fac_cat_mfr}`
),
fac_cat_tot2 AS (
  SELECT month_date, entity_code, category, total_cat_spend FROM `{fac_cat_tot}`
),
-- Compute awarded_spend for controls
controls_panel AS (
  SELECT
    cp.program, cp.category, cp.month_date, cp.entity_code,
    t.total_cat_spend,
    COALESCE((
      SELECT SUM(fcm.spend)
      FROM UNNEST(COALESCE(focal.awarded_block, [])) AS m
      JOIN fac_cat_mfr fcm
        ON fcm.month_date = cp.month_date
       AND fcm.entity_code = cp.entity_code
       AND fcm.category   = cp.category
       AND fcm.manufacturer_id = m
    ), 0.0) AS awarded_spend
  FROM controls_pool cp
  JOIN fac_cat_tot2 t
    ON t.month_date = cp.month_date AND t.entity_code = cp.entity_code AND t.category = cp.category
  LEFT JOIN eff_awards focal
    ON focal.program = cp.program AND focal.category = cp.category AND focal.month_date = cp.month_date
)
SELECT
  cp.program AS program,
  cp.category AS category,
  cp.month_date AS month,
  cp.entity_code AS entity_code,
  cp.total_cat_spend AS total_cat_spend,
  awarded_spend,
  SAFE_DIVIDE(awarded_spend, cp.total_cat_spend) AS awarded_share,
  SAFE_DIVIDE(SUM(awarded_spend) OVER (PARTITION BY cp.program, cp.category, cp.entity_code
                                       ORDER BY cp.month_date
                                       ROWS BETWEEN 5 PRECEDING AND CURRENT ROW),
              SUM(cp.total_cat_spend) OVER (PARTITION BY cp.program, cp.category, cp.entity_code
                                         ORDER BY cp.month_date
                                         ROWS BETWEEN 5 PRECEDING AND CURRENT ROW)) AS awarded_share_6m,
  em.event_month
FROM controls_panel cp
JOIN event_map em
  ON em.program = cp.program AND em.category = cp.category AND em.month_date = cp.month_date
WHERE em.event_month BETWEEN -12 AND 18;
"""

# Backwards-compat exports (module-level aliases)
CORE_SQL = sql.CORE_SQL

# Stage-count diagnostic for controls pipeline
CONTROLS_STAGE_COUNTS_SQL = r"""
-- Diagnostic: counts at key stages of CONTROLS_SQL to locate drop-offs
WITH base AS (
  SELECT DATE_TRUNC(DATE(Transaction_Date), MONTH) AS month_date,
         premier_entity_code AS entity_code,
         contract_category AS category,
         contract_number,
         DATE(contract_effective_date) AS contract_effective_date,
         DATE(contract_expiration_date) AS contract_expiration_date,
         manufacturer_top_parent_entity_code AS manufacturer_id,
         Contract_Type AS contract_type,
         base_spend,
         quantity,
         member_type,
         aggregation_flag
  FROM `{table}`
  WHERE DATE(Transaction_Date) >= DATE_SUB(PARSE_DATE('%Y-%m', @START_MONTH), INTERVAL 12 MONTH)
    AND DATE(Transaction_Date) <  DATE_ADD(PARSE_DATE('%Y-%m', @DATA_CUTOFF_MONTH), INTERVAL 1 MONTH)
    AND base_spend > 0 AND quantity > 0
    AND matched_product_status IS NOT NULL
),
program_lines AS (
  SELECT month_date, entity_code, category, manufacturer_id, base_spend,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program
  FROM base
),
coverage AS (
  SELECT p.program, p.category, p.month_date,
         SAFE_DIVIDE(SUM(base_spend), SUM(SUM(base_spend)) OVER (PARTITION BY month_date, category)) AS program_share_in_cat
  FROM program_lines p
  WHERE p.program IS NOT NULL
  GROUP BY 1,2,3
),
covered AS (
  SELECT program, category, month_date FROM coverage WHERE program_share_in_cat >= @coverage_guard
),
program_cat_tot AS (
  SELECT program, category, month_date, SUM(base_spend) AS program_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3
),
program_mfr_spend AS (
  SELECT program, category, month_date, manufacturer_id, SUM(base_spend) AS mfr_spend
  FROM program_lines
  WHERE program IS NOT NULL
  GROUP BY 1,2,3,4
),
awarded_block AS (
  SELECT pms.program, pms.category, pms.month_date,
         ARRAY_AGG(DISTINCT pms.manufacturer_id IGNORE NULLS) AS awarded_block
  FROM program_mfr_spend pms
  JOIN covered c USING (program, category, month_date)
  JOIN program_cat_tot pct USING (program, category, month_date)
  WHERE SAFE_DIVIDE(pms.mfr_spend, pct.program_spend) >= @coverage_guard
  GROUP BY 1,2,3
),
core_bounds AS (
  SELECT
    PARSE_DATE('%Y-%m', @CORE_START) AS core_start,
    PARSE_DATE('%Y-%m', @CORE_END) AS core_end
),
contract_starts AS (
  SELECT DISTINCT
    CASE
      WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
      WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
    END AS program,
    category,
    DATE_TRUNC(contract_effective_date, MONTH) AS start_month
  FROM base
  WHERE contract_effective_date IS NOT NULL
),
in_core_starts AS (
  SELECT program, category, start_month
  FROM contract_starts, core_bounds
  WHERE start_month BETWEEN core_bounds.core_start AND core_bounds.core_end
),
eligible_months AS (
  SELECT ab.program, ab.category, ab.month_date
  FROM awarded_block ab
  JOIN covered c
    ON c.program = ab.program AND c.category = ab.category AND c.month_date = ab.month_date
  JOIN core_bounds cb ON ab.month_date BETWEEN cb.core_start AND cb.core_end
),
t0_map AS (
  SELECT s.program, s.category, MIN(e.month_date) AS go_live_month
  FROM (
    SELECT program, category, MIN(start_month) AS start_month
    FROM in_core_starts
    GROUP BY 1,2
  ) s
  JOIN eligible_months e
    ON e.program = s.program AND e.category = s.category AND e.month_date >= s.start_month
  GROUP BY 1,2
),
event_map AS (
  SELECT x.program, x.category, x.month_date,
         DATE_DIFF(x.month_date, glm.go_live_month, MONTH) AS event_month
  FROM (SELECT DISTINCT program, category, month_date FROM program_lines) x
  JOIN t0_map glm USING (program, category)
),
fac_cat_tot_for_mem AS (
  SELECT month_date, entity_code, category, SUM(base_spend) AS total_cat_spend
  FROM base
  GROUP BY 1,2,3
),
program_fac_spend AS (
  SELECT month_date, entity_code,
         CASE
           WHEN UPPER(contract_number) LIKE @sp OR UPPER(contract_type) = 'SURPASS' THEN 'Surpass'
           WHEN REGEXP_CONTAINS(UPPER(contract_number), @ad_re) OR UPPER(contract_type) = 'ASCEND' THEN 'Ascend'
         END AS program,
         SUM(base_spend) AS program_spend
  FROM base
  GROUP BY 1,2,3
),
covered_denoms AS (
  SELECT t.month_date, t.entity_code, c.program, SUM(t.total_cat_spend) AS denom_spend
  FROM fac_cat_tot_for_mem t
  JOIN covered c USING (month_date, category)
  GROUP BY 1,2,3
),
membership AS (
  SELECT d.month_date, d.entity_code, d.program,
         SAFE_DIVIDE(p.program_spend, d.denom_spend) AS membership_share,
         SAFE_CAST(SAFE_DIVIDE(p.program_spend, d.denom_spend) >= @membership_threshold AS BOOL) AS member_flag
  FROM covered_denoms d
  LEFT JOIN program_fac_spend p
    ON p.month_date = d.month_date AND p.entity_code = d.entity_code AND p.program = d.program
),
-- 1) control_candidates
control_candidates AS (
  SELECT DISTINCT em.program, em.category, em.month_date, em.event_month, t.entity_code
  FROM event_map em
  JOIN fac_cat_tot_for_mem t
    ON t.month_date = em.month_date AND t.category = em.category
  LEFT JOIN membership me
    ON me.month_date = em.month_date AND me.entity_code = t.entity_code AND me.program = em.program
  WHERE COALESCE(me.member_flag, FALSE) = FALSE
),
-- 2) controls_with_anchor
members_anchor AS (
  SELECT program, category, go_live_month AS anchor_month_date_median
  FROM t0_map
),
controls_with_anchor AS (
  SELECT cc.program, cc.category, cc.month_date, cc.entity_code,
         DATE_DIFF(cc.month_date, ma.anchor_month_date_median, MONTH) AS aligned_event_month
  FROM control_candidates cc
  JOIN members_anchor ma USING (program, category)
),
-- 3) controls_pool after overlap rules
other_prog_commit AS (
  SELECT cc.entity_code, cc.category, cc.month_date, cc.program,
         ARRAY_CONCAT_AGG(ab.awarded_block) AS other_awarded_mfrs
  FROM control_candidates cc
  JOIN awarded_block ab
    ON ab.category = cc.category AND ab.month_date = cc.month_date AND ab.program != cc.program
  GROUP BY 1,2,3,4
),
controls_pool AS (
  SELECT cw.*
  FROM controls_with_anchor cw
  LEFT JOIN awarded_block focal
    ON focal.program = cw.program AND focal.category = cw.category AND focal.month_date = cw.month_date
  LEFT JOIN other_prog_commit o
    ON o.entity_code = cw.entity_code AND o.category = cw.category AND o.month_date = cw.month_date AND o.program = cw.program
  LEFT JOIN membership me_other
    ON me_other.month_date = cw.month_date AND me_other.entity_code = cw.entity_code AND me_other.program != cw.program
  WHERE (
    cw.aligned_event_month < 0
  ) OR (
    o.other_awarded_mfrs IS NULL
  ) OR (
    COALESCE(me_other.member_flag, FALSE) = FALSE
  ) OR (
    (
      ARRAY_LENGTH(ARRAY(
        SELECT elem FROM UNNEST(ARRAY(SELECT DISTINCT a FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS a)) AS elem
        EXCEPT DISTINCT
        SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
      )) > 0
    ) OR (
      ARRAY_LENGTH(ARRAY(
        SELECT elem FROM UNNEST(COALESCE(focal.awarded_block, [])) AS elem
        EXCEPT DISTINCT
        SELECT elem FROM UNNEST(ARRAY(SELECT DISTINCT a FROM UNNEST(COALESCE(o.other_awarded_mfrs, [])) AS a)) AS elem
      )) > 0
    )
  )
)
SELECT
  (SELECT COUNT(*) FROM t0_map) AS anchors,
  (SELECT COUNT(*) FROM control_candidates) AS n_control_candidates,
  (SELECT COUNT(*) FROM controls_with_anchor) AS n_controls_with_anchor,
  (SELECT COUNT(*) FROM controls_pool) AS n_controls_pool;
"""
