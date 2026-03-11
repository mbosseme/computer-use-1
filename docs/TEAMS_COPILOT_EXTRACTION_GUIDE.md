# Teams Copilot Meeting Extraction Guide

## Overview
When capturing knowledge from Microsoft Teams meetings using Copilot, simple generative summarization inevitably leads to truncation and loss of critical details (such as specific dollar amounts, project metrics, system names, or subtle friction points). This guide documents the "Loss-Less Extraction" methodology to force Teams Copilot out of "summarization" mode and into an "exhaustive data extraction" mode.

## The Strategy: Loss-Less Extraction
Instead of prompting Teams Copilot for a summary or asking for specific entities (e.g., "Find the $1B metric"), the most effective strategy is to provide a comprehensive structural meta-prompt that forces the model to recursively dump every fact it can find across specific dimensions.

By demanding a structured breakdown, Teams Copilot accurately highlights nuanced data points (e.g., $1B pharmacy distribution spend, specific vendor software like *Sarah* and *US Foods' DOS-based systems*, etc.) without requiring prior knowledge of the meeting's exact contents.

## Best Practice Prompts

When running a custom summary in the Teams Recap tab via Playwright automation or manually, use the following template to guarantee high-fidelity extraction:

```markdown
Please perform a LOSS-LESS EXTRACTION of the meeting transcript. DO NOT summarize. I need all specifics, data points, constraints, and metrics preserved exactly as stated.

Please organize the exhaustive data dump into the following strict structure:

1. EXHAUSTIVE TOPIC EXTRACTION
(List every single topic discussed, preserving all technical specs, system names, file names, or process steps mentioned).

2. SYSTEM NAMES, TOOLS, AND PROJECTS
(Provide a bulleted list of any software, platforms, scripts, tools, or internal project code-names referenced).

3. METRICS, KPIS, AND SPEND FIGURES
(List every single numerical figure, dollar amount, duration, or date. Do not skip any numbers).

4. STRATEGIC INSIGHTS & CONSTRAINTS
(Extract all blockers, architectural limitations, or high-level strategic directives discussed).

5. SPEAKER ATTRIBUTION & FRICTION POINTS
(Detail who advocated for what, where there was pushback, debate, or disagreement, and what the ultimate resolution or next steps were for those friction points).
```

## Implementation via Playwright MCP
When automating this via the Playwright MCP server against the Teams web UI:
1. Navigate to the meeting Recap.
2. Intercept the custom template modal: `getByTestId('template-actions-menu-button')` -> `getByTestId('template-edit-action')`.
3. Fill the `getByTestId('set-template-prompt')` textbox with the prompt above.
4. Save and execute.
5. Extract the output from the DOM. Note that Teams Copilot markdown formatting may strip ordered list numbers (e.g., "1. EXHAUSTIVE TOPIC EXTRACTION" may render just as "EXHAUSTIVE TOPIC EXTRACTION" in headers), so DOM evaluation scripts should use loose substring matching or rely on clipboard extraction (`getByRole('button', {name: 'Copy all'})` and `navigator.clipboard.readText()`).

## Context & Efficacy
This approach was validated as highly effective compared to both naive summarization (which stripped a critical "$1 Billion" spend figure reference) and targeted extraction (which required brittle, hardcoded prompts). The exhaustive loss-less prompt consistently retains high-density context, friction points among speakers, and all discrete financial/system metrics.
