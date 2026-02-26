# Dependencies and Utilities (Promotion Model)

This repo keeps the base reproducible while allowing optional capabilities to grow safely.

## Dependency tiers
### Tier A — Base (always installed)
Use for minimal, broadly useful dependencies.

Criteria:
- Used frequently across workflows
- Low footprint and low operational risk
- Clear versioning story

### Tier B — Optional packs (capability-based)
Use for optional capabilities installed on demand (examples: spreadsheet parsing, PDF processing, slide generation).

Criteria:
- Adds meaningful capability but not required for most runs
- Clearly scoped to a workflow family
- Documented install + usage notes

### Tier C — Run-local experiments
Use for one-off trials and prototyping.

Criteria:
- Not yet proven reusable
- May be replaced, removed, or revised without notice

Promotion rule:
- Promote Tier C → Tier B only after reuse (2+ runs) and a clear, documented reason.
- Promote Tier B → Tier A only if it becomes broadly required.

## Utilities (where code should live)
Utilities are deterministic helpers (scripts/modules) that support repeatable workflows.

Recommended locations:
- **Reusable, generic utilities**: `tools/` (or `lib/`)
- **Workflow-specific utilities**: co-locate under the relevant skill folder (e.g., `.github/skills/<skill>/`)

This repo also uses:
- **Reusable Python utilities for runs**: `agent_tools/` (e.g., the Azure OpenAI GPT-5.2 starter client under `agent_tools/llm/`)
- **Reusable Graph CLIs for scheduling/drafts**: `tools/graph/` (cross-worktree utilities for mutual slot finding and structured draft email creation)

### Screenshot / image utilities
This repo includes deterministic image transforms used to prepare evidence (e.g., cropping BI dashboard screenshots to remove empty gutters).

- Utility module: `agent_tools/images/dashboard_crop.py`
- CLI helper: `scripts/make_clean_dashboard_screenshots.py`
- Dependency: `Pillow` (installed via `requirements.txt`)

### Current `agent_tools/llm/` modules
| Module | Purpose |
|--------|---------|
| `azure_openai_responses.py` | Core Azure OpenAI Responses API client |
| `document_extraction.py` | PDF/EML text extraction + retry/backoff logic for synthesis workflows |
| `summarize_file.py` | Chunked map-reduce synthesis for PDFs and text, with coverage warnings + optional manifest |
| `summarize_folder.py` | One-command folder synthesis (PDF/EML/text) + per-doc outputs |
| `env.py` | Environment variable loading from `.env` |
| `model_registry.py` | Model config from `config/models.json` |
| `smoketest.py` | Quick validation that LLM endpoint is reachable |

Keep utilities:
- deterministic and reviewable
- small and composable
- explicit about inputs/outputs

## Validated Logic Snippets

### Report Builder "Units" Calculation
Logic to convert `wholesaler_pkg_qty` (Case Size) and `quantity_ordered` (Cases) into "Eaches" (Units), correcting for data quality issues.

```python
def process_rb_units(row):
    qty = row['quantity_ordered']
    pack = row['wholesaler_pkg_qty']
    vol = row['pkg_size'] # Check mapping: Report Builder often stores volume here
    
    factor = 1
    try:
        p = float(pack)
        v = float(vol) if vol else 0
        
        if p > 1:
            # Check for volume leakage (Pack == Volume mistake)
            if p == v:
                factor = 1 
            # Suspicious logic for large rounded numbers matching volume
            elif p > 100 and v > 0 and (p % v == 0 or v % p == 0):
                factor = 1
            else:
                factor = p
    except:
        factor = 1
        
    return qty * factor
```

## Promotion checklist (PR-friendly)
When promoting a dependency or utility into core:
- What capability it enables and why it’s needed
- Why it belongs in Tier A vs Tier B (or why it remains Tier C)
- How it was verified (commands, sample inputs/outputs)
- Safety notes (HITL gates, irreversible-action handling, and sanitization)

## Sanitization rules
- Do not store credentials.
- Do not store sensitive internal deep links/session URLs/tokens.
- Use placeholders like `<TASK_URL>` / `<TRAINING_URL>` in any durable docs/logs.
