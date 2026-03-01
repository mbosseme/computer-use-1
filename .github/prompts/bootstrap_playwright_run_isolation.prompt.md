---
agent: agent
---

TASK
Bootstrap per-run Playwright MCP isolation in THIS worktree window by configuring `@playwright/mcp` with a per-run user data dir and output dir.

CONSTRAINTS
- Do not store sensitive URLs/tokens/secrets.
- This prompt is a shared/core workflow, but the changes it applies are run-branch-only (do not promote the resulting `runs/<RUN_ID>/**` artifacts or `.vscode/**` edits back to `main`).
- Do not start the actual task; only set up isolation.

PRECONDITIONS
- You are running inside a run worktree window (not the launcher).
- The current git branch is expected to be `run/<RUN_ID>` where `RUN_ID` is `YYYY-MM-DD__short-slug`.

STEPS
1) Verify worktree context
- Run:
  - `git status --porcelain=v1`
  - `git branch --show-current`
- If there are uncommitted changes, stop and ask the user whether to proceed.

2) Determine `RUN_ID`
- If the current branch matches `run/<RUN_ID>`, parse `<RUN_ID>`.
- Validate `<RUN_ID>` is in the format `YYYY-MM-DD__short-slug`.
- If the branch does not match, ask the user for the intended RUN_ID (do not guess).

3) Create run-local directories (inside this worktree)
- Create:
  - `runs/<RUN_ID>/playwright-profile/`
  - `runs/<RUN_ID>/playwright-output/`
- Do NOT create any other directories unless needed.

4) Update the MCP config in this worktree ONLY
- Edit `.vscode/mcp.json` so the **workspace** `playwright` server invokes:
  - `npx --yes --package @playwright/mcp@latest playwright-mcp --user-data-dir runs/<RUN_ID>/playwright-profile --output-dir runs/<RUN_ID>/playwright-output`
- Do NOT enable `--shared-browser-context`.

Config shape note:
- Some VS Code versions/UI flows write `.vscode/mcp.json` using a top-level `servers` object (recommended for this repo).
- If you see an older `mcpServers` shape, update it to the `servers` shape (or ensure the effective workspace server config uses the args above).

Path note:
- Prefer repo-relative paths (`runs/<RUN_ID>/...`) over absolute `/Users/...` paths so the config is portable across machines/worktrees.

Important (instance-specific binding):
- Ensure VS Code is actually running the **workspace-scoped** `playwright` MCP server for this window/worktree. If a global/shared Playwright MCP server is running, the agent may bind to that instance and ignore these per-run dirs.
- If you created a workspace MCP server via UI, confirm the server id/name is `playwright` (so tool calls bind to the correct server).

If you suspect the wrong server instance is being used:
- Stop/disable any global/shared Playwright MCP server in VS Code.
- Restart the workspace `playwright` server for this window.

5) Restart MCP server / reload window
- In VS Code, restart the MCP server or reload the window so the new args take effect.
- Then validate isolation quickly:
  - Navigate to `https://example.com`
  - Report the title
  - Take a screenshot (use a simple filename like `mcp-validation.png`)

Verification (must pass):
- `runs/<RUN_ID>/playwright-profile/` becomes non-empty after the first navigation.
- A running Chrome process includes `--user-data-dir=.../runs/<RUN_ID>/playwright-profile`.
- Screenshot file is written under `runs/<RUN_ID>/playwright-output/`.

Output-dir filename rule:
- When `--output-dir` is set, provide screenshot/save filenames relative to that directory (e.g., `mcp-validation.png`), not a path that already includes `runs/<RUN_ID>/playwright-output/`.

PRINT (mandatory)
bootstrap_playwright_isolation=true
RUN_ID=<RUN_ID>
user_data_dir=runs/<RUN_ID>/playwright-profile
output_dir=runs/<RUN_ID>/playwright-output
mcp_config_updated=true
next_step="Proceed with the run task in this worktree window."

STOP
After printing, stop and wait for the user.
