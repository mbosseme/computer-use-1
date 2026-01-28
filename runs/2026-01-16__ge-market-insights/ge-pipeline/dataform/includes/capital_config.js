const vars = (dataform.projectConfig && dataform.projectConfig.vars) || {};

const parseList = (value, fallback) => {
  if (!value) {
    return fallback;
  }
  return value
    .split("|")
    .map((item) => item.trim())
    .filter((item) => item.length > 0);
};

const escapeSqlLiteral = (value) => value.replace(/'/g, "''");

const toSqlArray = (values) => `[${values.map((v) => `'${escapeSqlLiteral(v)}'`).join(", ")} ]`;

module.exports = {
  capitalPriceThreshold: Number(vars.capital_price_threshold || 25000),
  primaryCategoryTerms: parseList(vars.capital_primary_categories, [
    "MAGNETIC RESONANCE",
    "COMPUTED TOMOGRAPHY",
    "PHYSIOLOGICAL MONITORING",
    "ULTRASOUND RADIOLOGY CARDIOLOGY HAND CARRIED"
  ]),
  positiveKeywords: parseList(vars.capital_positive_keywords, [
    "MRI",
    "CT",
    "TOMOGRAPHY",
    "RESONANCE",
    "MONITORING",
    "ULTRASOUND",
    "HAND CARRIED"
  ]),
  negativeKeywords: parseList(vars.capital_negative_keywords, [
    "SERVICE",
    "MAINTENANCE",
    "WARRANTY",
    "AGREEMENT",
    "REPAIR",
    "SOFTWARE",
    "LICENSE",
    "RENEWAL",
    "LABOR",
    "SOFTWARE SUPPORT",
    "INSTALLATION"
  ]),
  toSqlArray
};
