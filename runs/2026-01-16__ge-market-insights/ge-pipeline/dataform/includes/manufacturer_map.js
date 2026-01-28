const aliases = {
  GE: [
    "GE",
    "GE HEALTHCARE",
    "GENERAL ELECTRIC",
    "GE MEDICAL SYSTEMS",
    "GE PRECISION HEALTHCARE LLC",
    "GE MEDICAL SYSTEMS INFORMATION TECHNOLOGIES, INC.",
    "GE HEALTHCARE MEDICAL DIAGNOSTICS",
    "GE HEALTHCARE INC.",
    "DATEX-OHMEDA, INC.",
    "GE HEALTHCARE TECHNOLOGIES INC."
  ],
  SIEMENS: [
    "SIEMENS",
    "SIEMENS HEALTHINEERS",
    "SIEMENS MEDICAL SOLUTIONS USA, INC.",
    "SIEMENS INDUSTRY, INC.",
    "SIEMENS HEALTHCARE DIAGNOSTICS INC.",
    "SIEMENS AG"
  ],
  PHILIPS: [
    "PHILIPS",
    "ROYAL PHILIPS",
    "PHILIPS HEALTHCARE",
    "PHILIPS MEDICAL SYSTEMS",
    "PHILIPS NORTH AMERICA LLC",
    "ROYAL PHILIPS ELECTRONICS N.V.",
    "PHILIPS RS NORTH AMERICA LLC",
    "PHILIPS DS NORTH AMERICA LLC",
    "PHILIPS MEDICAL SYSTEMS (ATL ULTRASOUND SUPPLIES)"
  ],
  CANON: [
    "CANON",
    "CANON MEDICAL",
    "CANON MEDICAL SYSTEMS USA, INC.",
    "TOSHIBA",
    "CANON INC."
  ],
  "NIHON KOHDEN": [
    "NIHON KOHDEN AMERICA, LLC",
    "NIHON KOHDEN",
    "NIHON KOHDEN CORPORATION"
  ],
  SPACELABS: [
    "SPACELABS HEALTHCARE, L.L.C.",
    "SPACELABS",
    "OSI SYSTEMS, INC."
  ],
  MINDRAY: [
    "MINDRAY DS USA INC",
    "MINDRAY"
  ],
  SAMSUNG: [
    "NEUROLOGICA CORP",
    "SAMSUNG"
  ]
};

const buildCaseExpression = (fieldName) => {
  const upperField = `UPPER(${fieldName})`;
  const clauses = Object.entries(aliases).map(([canonical, names]) => {
    const values = names.map((name) => `'${name.replace(/'/g, "''")}'`).join(", ");
    return `    WHEN ${upperField} IN (${values}) THEN '${canonical}'`;
  });
  return ["CASE", ...clauses, "    ELSE 'OTHER'", "END"].join("\n");
};

module.exports = {
  manufacturerAliases: aliases,
  buildCaseExpression
};
