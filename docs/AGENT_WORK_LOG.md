# Agent Work Log

Running log of actions performed by Copilot Agent in this repo.

## Entry
- Date/time: 2025-12-22 13:44:02 EST
- Goal: Implement and commit Checkpoint B (MCP config + minimal Python venv + README).
- Commands executed:
  - `python3 -m venv .venv`
  - `git status`
  - `git add -A`
  - `git status --porcelain=v1`
  - `git diff --cached --name-only`
  - `git diff --cached --stat`
  - `git commit -m "Checkpoint B: MCP config + venv + README"`
- Files changed:
  - `.vscode/mcp.json`
  - `README.md`
  - `requirements.txt`
- Decisions/notes:
  - Training URLs are treated as session-only and must not be written to repo files; use `<TRAINING_URL>` placeholders.
  - `.venv/` is gitignored; venv is created locally without installing packages.
  - If the Playwright MCP server fails to start, switch to `@microsoft/mcp-server-playwright` and record what worked.
- Next steps:
  - Add PRD + guardrails docs.
  - Align README/instructions to reference docs.
  - Stage docs changes and propose a new commit for approval.
