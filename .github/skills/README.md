# Skills Index

This directory contains reusable "skills" (workflows, heuristics, and recovery rules) for the GitHub Copilot Agent.

## Available Skills

- **[_template](_template/SKILL.md)**: Structure for creating new skills. Use when a new recurring workflow emerges.
- **[training-navigation](training-navigation/SKILL.md)**: Specialized logic for navigating gated training modules (timers, videos, quizzes).
- **[browser-automation-core](browser-automation-core/SKILL.md)**: **(Start here for web tasks)** General-purpose browser automation patterns (selectors, waiting, scrolling, overlays, HITL).

## How Copilot should use skills

1.  **At task start**:
    - Open this index (`.github/skills/README.md`).
    - Identify 1–3 relevant skills.
    - Open those skill files to load them into context.
    - *Then* proceed with the task.

2.  **When stuck**:
    - Re-open the relevant skill file.
    - Check the "Recovery rules" section before trying random fixes.

3.  **After a workaround is learned**:
    - Update the relevant skill file immediately (vendor-agnostic rules).
    - Add a run note referencing the update.
