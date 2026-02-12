// Shared constants for the Portfolio Expansion Dataform pipeline
// All .sqlx files should reference these for consistency

const PROJECT = "matthew-bossemeyer";
const DATASET = "wt_2026_02_10__portfolio_expansion";

// CY2025 fiscal period range (TSA Spend_Period_YYYYQMM format)
const CY2025_START = 2025101;
const CY2025_END = 2025412;

// Outlier guard-rails for TSA Landed_Spend
const SPEND_FLOOR = -50000;
const SPEND_CEILING = 100000000;

// Alliance/GPO entity codes to exclude from health-system cohort
// These are purchasing cooperatives, not individual health systems
const ALLIANCE_EXCLUSION_PATTERNS = [
  "ACURITY",
  "ALLSPIRE",
  "YANKEE ALLIANCE",
  "CONDUCTIV",
  "ALLIANT",
  "HOSPITAL SHARED SERVICES",
  "HEALTH ENTERPRISES",
  "PRAIRIE HEALTH VENTURES",
  "WELLLINK",
  "MHS PURCHASING",
  "OPTUM",
];

module.exports = {
  PROJECT,
  DATASET,
  CY2025_START,
  CY2025_END,
  SPEND_FLOOR,
  SPEND_CEILING,
  ALLIANCE_EXCLUSION_PATTERNS,
};
