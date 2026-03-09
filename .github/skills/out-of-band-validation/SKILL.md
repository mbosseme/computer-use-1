---
name: out-of-band-validation
description: **PROCESS SKILL** — Execute an isolated, context-blind QA validation against a structured artifact (e.g., .xlsx, .csv, PDF). USE FOR: verifying data engineering pipeline outputs; checking math aggregations; ensuring business logic plausibility; identifying structural anomalies. DO NOT USE FOR: writing production code; deploying pipelines. INVOKES: file system tools, python execution environment, validation runner CLI.
---

# Out-of-Band Data Validation Skill

## When to use this skill
When a user asks you to "validate", "QA", "audit", or "sanity check" a freshly built artifact (like a dashboard export or a summary `.xlsx`). This skill is designed to prevent the agent from trusting the logic of the pipeline it just built.

## Core Directives
1. **Context Clean Room:** Do not assume the pipeline logic was correct. Look at the numbers exactly as a stakeholder would.
2. **Blind Verification:** Read the raw file directly via Python/pandas/openpyxl rather than relying on previous query summaries.
3. **Continuous Learning:** Always review the known traps before validating. If you find a new logic hole, document it.

## The Runner CLI
A universal tool exists at `tools/validation_agent/runner.py`. This script dynamically injects personas, schemas, and historical lessons learned into a single, cohesive prompt.

### How to execute the validation
1. Ensure the user has provided the required files (an artifact, a persona markdown file, and optionally a schema file).
2. Generate the validation instructions by executing:
```sh
python tools/validation_agent/runner.py \
  --artifact <path/to/artifact.xlsx> \
  --persona <path/to/persona.md> \
  --schema <path/to/schema.md> \
  --heuristics tools/validation_agent/known_traps.md
```
3. Read the resulting `tmp_validation_prompt.md`.
4. Assume the persona defined in the prompt, read the artifact, and execute the audit.
5. If the user asks to "generalize" or "save" a new learning, add it immediately to `tools/validation_agent/known_traps.md`.

## Recovery Rules
- If the file is too large to load in one pass, randomly sample rows or only check aggregated subtotal lines.
- If a specific column is missing, check the injected schema file; the pipeline may have renamed it or dropped it.