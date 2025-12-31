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
- Edit `.vscode/mcp.json` so the `playwright` server invokes:
  - `npx --yes --package @playwright/mcp@latest mcp-server-playwright --user-data-dir runs/<RUN_ID>/playwright-profile --output-dir runs/<RUN_ID>/playwright-output`
- Do NOT enable `--shared-browser-context`.

Important (instance-specific binding):
- Ensure VS Code is actually running the **workspace-scoped** `playwright` MCP server for this window/worktree. If a global/shared Playwright MCP server is running, the agent may bind to that instance and ignore these per-run dirs.
- If you created a workspace MCP server via UI, confirm the server id/name is `playwright` (so tool calls bind to the correct server).

5) Restart MCP server / reload window
- In VS Code, restart the MCP server or reload the window so the new args take effect.
- Then validate isolation quickly:
  - Navigate to `https://example.com`
  - Report the title
  - Take a screenshot (use a simple filename like `mcp-validation.png`)

PRINT (mandatory)
bootstrap_playwright_isolation=true
RUN_ID=<RUN_ID>
user_data_dir=runs/<RUN_ID>/playwright-profile
output_dir=runs/<RUN_ID>/playwright-output
mcp_config_updated=true
next_step="Proceed with the run task in this worktree window."

STOP
After printing, stop and wait for the user.
