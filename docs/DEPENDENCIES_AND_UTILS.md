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

Keep utilities:
- deterministic and reviewable
- small and composable
- explicit about inputs/outputs

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
