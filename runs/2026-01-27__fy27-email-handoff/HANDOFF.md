# Run Handoff Journal — 2026-01-27__fy27-email-handoff

## Purpose
- Run-local continuity journal for FY27 email handoff + keeping B. Braun context up to date.
- No sensitive URLs/tokens; use placeholders like `<PORTAL_URL>`.

## 2026-01-27 — Initialize run + sync plan

### Goals
- Sync the latest local B. Braun document repository into a stable run-local “source mirror” (symlink-based).
- Run incremental synthesis so only changed/new docs are reprocessed going forward.

### Source folder (local)
- `/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/Digital Supply Chain/Market Insights/B Braun`

### Planned outputs (this run)
- `runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat/` (symlink mirror of docs)
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__incremental_index.json`
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.md`
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.manifest.json`
- `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs/per_doc/*__synthesis.md`

### Completed (sync + incremental synthesis)
- Mirrored files (recursive): 17
- Incremental synthesis stats: `files_seen=17`, `changed=17`, `synthesized=17`, `removed=0`

### Artifacts
- Source mirror map (rel paths → mirrored names): `runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_map.json`
- Flat symlink mirror (inputs): `runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat/`
- Per-doc syntheses + manifests: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs/per_doc/`
- Incremental index: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__incremental_index.json`
- Folder synthesis: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.md`
- Folder synthesis manifest: `runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.manifest.json`

### Repro (incremental re-run)
1) Re-sync mirror (updates symlinks / captures new files):
	- `/.venv/bin/python runs/2026-01-27__fy27-email-handoff/scripts/sync_b_braun_docs.py --source-root "<LOCAL_ONE_DRIVE_B_BRAUN_FOLDER>" --out-dir runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat --map-json runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_map.json --clean`
2) Re-run incremental synthesis (only new/changed docs get reprocessed):
	- `/.venv/bin/python -m agent_tools.llm.summarize_incremental --source-dir runs/2026-01-27__fy27-email-handoff/inputs/b_braun__source_flat --staging-dir runs/2026-01-27__fy27-email-handoff/inputs/b_braun_docs__staging --per-doc-dir runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs/per_doc --tmp-dir runs/2026-01-27__fy27-email-handoff/tmp/b_braun_docs__chunks --index runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__incremental_index.json --out runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.md --manifest runs/2026-01-27__fy27-email-handoff/exports/b_braun_docs__folder_synthesis.manifest.json`


