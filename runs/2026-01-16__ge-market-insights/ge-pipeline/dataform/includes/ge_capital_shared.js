const capitalConfig = require("./capital_config");
const { buildCaseExpression } = require("./manufacturer_map");

const uppercaseLike = (fieldName, needle) => `UPPER(${fieldName}) LIKE '%${needle.replace(/'/g, "''")}%'`;
const regexFromList = (values) => values.map((value) => value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("|");

const categoryClauses = capitalConfig.primaryCategoryTerms.map((term) => uppercaseLike("Contract_Category", term));
const categoryMatchExpression = categoryClauses.length > 0
  ? categoryClauses.map((clause) => `(${clause})`).join(" OR ")
  : "FALSE";

const positiveRegex = regexFromList(capitalConfig.positiveKeywords);
const negativeRegex = regexFromList(capitalConfig.negativeKeywords);
const capitalPriceThreshold = capitalConfig.capitalPriceThreshold;
const manufacturerCase = buildCaseExpression("Manufacturer_Name");
const reportCategoryCase = `CASE
    WHEN ${uppercaseLike("Contract_Category", "MAGNETIC RESONANCE")} OR REGEXP_CONTAINS(UPPER(Product_Description), r'(MRI|MAGNETIC\\s+RESONANCE)') THEN 'MRI'
    WHEN ${uppercaseLike("Contract_Category", "COMPUTED TOMOGRAPHY")} OR REGEXP_CONTAINS(UPPER(Product_Description), r'(CT|COMPUTED\\s+TOMOGRAPHY|TOMOGRAPHY)') THEN 'CT'
    WHEN ${uppercaseLike("Contract_Category", "PHYSIOLOGICAL MONITORING")} OR REGEXP_CONTAINS(UPPER(Product_Description), r'(MONITORING|PATIENT\\s+MONITOR)') THEN 'Monitoring'
    WHEN ${uppercaseLike("Contract_Category", "ULTRASOUND RADIOLOGY CARDIOLOGY HAND CARRIED")} OR REGEXP_CONTAINS(UPPER(Product_Description), r'(ULTRASOUND|HAND\\s+CARRIED)') THEN 'Ultrasound HC'
    ELSE NULL
  END`;

module.exports = {
  categoryMatchExpression,
  positiveRegex,
  negativeRegex,
  capitalPriceThreshold,
  manufacturerCase,
  reportCategoryCase
};
