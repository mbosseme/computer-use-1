A key note before the brief: **do not hardcode `gpt-5.4` as an Azure Foundry Agent model name unless your Azure tenant already exposes it**. OpenAI announced GPT-5.4 in the API on March 5, 2026, but the current Azure Foundry Agent model-support docs I found list GPT-5.2 / 5.1 / 5 / 5-mini / 5-nano / 5-chat for Agent Service, and note that GPT-5-family agents are limited to Code Interpreter and File Search tools. The current Azure Responses API page I found lists GPT-5.3-codex and GPT-5.2, but not GPT-5.4. So the implementation should **parameterize the deployment name** and prefer GPT-5.4 only if it is actually deployed and available in this Azure environment, otherwise it should fall back to the next most capable (available) GPT model, such as GPT-5.2.

---

# Briefing for VS Code / GitHub Copilot Agent

## Project: Build a Skeptical Contract Director QA Agent in Azure for Workbook Review

## 1) Objective

Build a working review architecture in this repo where:

* the local VS Code / GitHub Copilot agent acts as the **developer-orchestrator**
* an Azure-hosted LLM agent acts as a **skeptical healthcare contracting director**
* the Azure reviewer inspects the **actual workbook artifact first**
* the Azure reviewer can ask for additional evidence or clarification
* the local orchestrator decides what additional snippets, data, logic explanations, or upstream evidence to provide
* the reviewer then produces a structured anomaly memo and pass / warn / fail recommendation

The goal is to catch **business-logic anomalies, artifact-generation issues, and “sniff test” failures** that basic schema/null QA misses.

This should behave like a real human review loop:

* reviewer sees the work product
* reviewer challenges what seems fishy
* developer/orchestrator brings back evidence
* reviewer updates judgment

## 2) Architectural stance

Implement a **brokered reviewer pattern**.

The Azure reviewer agent should:

* be persistent or reusable if practical
* have strong domain instructions
* have access to the workbook artifact and optional supporting text/files
* be allowed to inspect files using Code Interpreter
* **not** have direct access to BigQuery, the repo, MCP tools, or internal systems unless explicitly and intentionally attached later

The VS Code / Copilot side should:

* create or reuse the Azure reviewer agent
* upload the workbook artifact and supporting files
* run the review conversation
* handle reviewer follow-up questions
* gather additional evidence from BigQuery / code / lineage when needed
* feed only the relevant evidence back to the reviewer
* persist the reviewer transcript and final findings

This matches the desired role separation and avoids over-privileging the reviewer.

Azure Foundry’s hosted Code Interpreter supports spreadsheet artifacts including `.xlsx` and `.csv`, and Azure Foundry agents support persistent agents with reusable instructions. ([Microsoft Learn][2])

## 3) Important implementation constraint on model selection

The user wants the reviewer to leverage the latest GPT-5.4 model. However:

* OpenAI has announced GPT-5.4 in the API. ([OpenAI][1])
* The Azure Foundry Agent model availability docs I found currently list GPT-5.2 / 5.1 / 5 / 5-mini / 5-nano / 5-chat for Agent Service, and say GPT-5-family agents are limited to Code Interpreter and File Search tools. ([Microsoft Learn][3])
* The Azure Responses API page I found lists GPT-5.3-codex and GPT-5.2, but not GPT-5.4. ([Microsoft Learn][4])

Therefore:

* **Parameterize the Azure model deployment name**
* Prefer `gpt-5.4` only if this Azure environment truly exposes it
* Otherwise use the newest deployed GPT-5-family model available in this tenant
* Fail fast with a clear diagnostic if the requested deployment is unavailable

Do not silently substitute a random older model without logging the change.

## 4) Desired deliverables

Create the following inside the repo.

### A. Architecture and config

* a small orchestrator module or package
* environment/config handling for Azure endpoint, project endpoint, deployment name, credentials, artifact path, run ID, and output paths
* a reusable reviewer agent definition
* a mechanism to create-or-reuse the reviewer agent

### B. Prompting and policy assets

Create durable prompt/policy files such as:

* `prompts/reviewer_system_prompt.md`
* `prompts/reviewer_checklist.md`
* `schemas/review_verdict.schema.json`
* `schemas/evidence_request.schema.json`
* `docs/reviewer_playbook.md`

### C. Execution code

Create scripts or commands for:

* creating the Azure reviewer agent
* uploading the workbook artifact
* starting a review thread/run
* detecting whether the reviewer is requesting more evidence or issuing a final verdict
* posting evidence packets back to the reviewer
* saving the conversation, findings JSON, and a human-readable memo

### D. Test harness

Create a test runner for a specific project in this repo that already generates a workbook artifact. The test harness should:

* locate the workbook produced by the current project
* run the reviewer against it
* simulate at least 3 useful interaction patterns
* save outputs under a run folder

### E. Output artifacts

Per run, save:

* raw conversation transcript
* structured evidence requests
* evidence responses
* final review verdict JSON
* markdown or HTML anomaly memo
* execution log with timestamps

## 5) Functional requirements

### 5.1 Reviewer behavior

The reviewer agent should act as a skeptical contract director, not a generic QA bot.

It must:

* inspect the actual workbook artifact first
* look for anomalies that would worry a contracting or pricing leader
* ask targeted follow-up questions when something does not reconcile
* focus on business relationships, suspicious logic, and executive risk
* produce concise but evidence-based findings
* separate hard blockers from investigate/fyi items

It should **not** merely hunt statistical outliers.

It should prioritize issues such as:

* missing or zero benchmarks that create artificial savings
* UOM mismatches that make prices look wildly off
* duplicated joins or roll-up errors that inflate spend
* inconsistent totals across workbook tabs
* broken formulas, malformed sheets, missing tabs, corrupted generation
* suspicious benchmark fallback behavior
* category mapping drift
* unrealistic price-to-benchmark ratios in high-spend slices
* values that are technically possible but commercially implausible

### 5.2 Conversation pattern

Implement a turn-based review loop.

The reviewer’s turn should resolve to one of:

* `FINDING`
* `EVIDENCE_REQUEST`
* `FINAL_VERDICT`

An `EVIDENCE_REQUEST` should be explicit and bounded, for example:

* what is being requested
* why it matters
* what data or logic is needed
* preferred format for the response

The orchestrator then gathers evidence and replies.

### 5.3 Evidence handling

The orchestrator may gather evidence from:

* workbook parsing or comparison code
* local generation logs
* SQL or BigQuery via MCP
* code inspection in the repo
* metric logic documentation
* sampling output tables or intermediate data

But only pass back the minimum useful evidence needed to answer the reviewer’s request.

### 5.4 Final output

The reviewer must output structured JSON plus a readable memo.

Suggested top-level verdict shape:

* `release_decision` = `PASS | WARN | FAIL`
* `overall_confidence`
* `executive_summary`
* `issues[]`
* `open_questions[]`
* `evidence_used[]`
* `recommended_next_actions[]`

Each issue should contain fields such as:

* `issue_title`
* `severity`
* `confidence`
* `sheet_or_artifact_location`
* `why_it_is_suspicious`
* `suspected_root_cause`
* `business_risk`
* `evidence_requested`
* `evidence_received`
* `recommended_follow_up`

Use structured outputs or strict JSON-mode handling where practical. Azure supports JSON mode and recommends structured outputs where available, though schema handling should be tested carefully in the exact API path used. ([Microsoft Learn][5])

## 6) Technology choices

### Preferred Azure pattern

Use **Azure AI Foundry Agent Service** for the reviewer agent, because it supports:

* persistent/reusable agents
* hosted Code Interpreter
* file upload and artifact analysis workflows ([Microsoft Learn][6])

### Tooling on the Azure reviewer

Enable:

* hosted Code Interpreter

Do not attach:

* direct BigQuery access
* direct MCP access to internal systems
* arbitrary repo access

The reviewer should remain mostly artifact-first and sandboxed.

### Local orchestration

Use local Python in the repo unless the repo already has a stronger preferred language/runtime.

The orchestrator should:

* call Azure APIs
* upload workbook artifacts
* manage thread/run lifecycle
* inspect reviewer responses
* call local evidence collectors
* persist outputs

### Configuration

Use env vars or a config file for at least:

* `FOUNDRY_PROJECT_ENDPOINT`
* `FOUNDRY_MODEL_DEPLOYMENT_NAME`
* `AZURE_TENANT_ID`
* `AZURE_CLIENT_ID`
* `AZURE_CLIENT_SECRET` or local Azure credential flow
* `REVIEWER_AGENT_NAME`
* `REVIEW_RUN_OUTPUT_DIR`

Azure’s current Foundry docs show the project endpoint and model deployment name as the key environment variables in the Code Interpreter examples. ([Microsoft Learn][7])

## 7) Reviewer system prompt requirements

Create a strong system prompt. Do not just make it grumpy.

The prompt should encode:

* role
* objective
* review priorities
* investigation style
* output contract

### Required role framing

The reviewer is:

* a skeptical healthcare contracting director
* experienced in supply chain pricing and benchmark review
* commercially minded
* focused on misleading outputs, false savings, hidden denominator errors, and implausible pricing signals

### Required behavioral rules

Include instructions like:

* start with the artifact, not assumptions
* treat the workbook as the thing being approved or challenged
* distrust extraordinary results until reconciled
* prioritize high-dollar or high-visibility anomalies
* ask for targeted evidence rather than broad raw dumps
* cite sheet/tab names and visible evidence where possible
* prefer relationship-based reasoning over generic z-score reasoning
* be concise, direct, and evidence-first

### Required anomaly classes to inspect

At minimum:

* benchmark null/zero issues
* UOM normalization issues
* roll-up/detail reconciliation issues
* duplicate counting or join multiplication
* impossible or suspiciously convenient savings
* category or product mapping drift
* malformed workbook output or generation corruption
* broken sheet formulas / tab inconsistencies
* suspicious concentration patterns
* mismatches between workbook narrative and workbook numbers

## 8) Reviewer supporting checklist

Create a checklist file the reviewer prompt can reference. It should include questions such as:

* Do summary tabs reconcile to detailed tabs?
* Are there any zero or blank benchmark values driving positive savings?
* Are price-to-benchmark ratios plausible after UOM normalization?
* Are the most extreme deltas concentrated in one supplier, one site, or one mapping bucket?
* Do percentages, totals, and denominators appear internally consistent?
* Are there signs that workbook generation itself failed, such as blank ranges, duplicated sheets, broken formulas, missing tabs, stale timestamps, or malformed formatting?
* Are there artifacts that look “technically computed” but commercially implausible?

## 9) Implementation guidance for the agent creation flow

Build the reviewer agent creation flow so that it:

1. Reads config
2. Checks whether a reviewer agent with the configured name already exists or whether local metadata contains an existing agent id
3. If absent, creates the Azure reviewer agent with:

   * configured deployment name
   * stable name
   * strong instructions
   * Code Interpreter enabled
4. Persists the agent id locally for reuse
5. Logs exact model deployment used

Use a stable prompt prefix because repeated use may benefit from prompt caching where available in Azure OpenAI. Azure docs state prompt caching depends on matching prompt prefixes and applies to supported model families. ([Microsoft Learn][4])

## 10) Review-run workflow to implement

Implement this review flow:

### Phase 1: initialize run

* identify the specific project workbook artifact already produced in this repo
* capture metadata: run id, workbook path, generation timestamp, project name
* create a run folder for outputs

### Phase 2: artifact package

Upload or attach:

* workbook artifact
* short project brief
* definitions of the most important metrics in the workbook
* optional “known risk areas” note if available

### Phase 3: first-pass review

Ask the reviewer to:

* inspect the workbook as if it were being sent to a contracting leader today
* identify suspicious areas
* either return findings or ask for evidence

### Phase 4: evidence loop

If the reviewer requests evidence:

* parse the request
* determine whether the evidence should come from workbook parsing, repo logic, or BigQuery
* collect the evidence
* send it back in a compact, structured form
* continue until reviewer issues final verdict or max-turn limit is reached

### Phase 5: finalization

Save:

* structured verdict JSON
* readable anomaly memo
* transcript
* evidence packets
* summary log

## 11) Test scenarios to run now

Use the actual project in this repo that already generates a workbook artifact.

Run at least these tests.

### Test 1: clean review on current workbook

Goal:

* confirm end-to-end architecture works
* reviewer reads workbook
* reviewer either passes or issues a sensible limited set of questions
* outputs are saved correctly

### Test 2: induced workbook anomaly

Create or simulate a workbook issue such as:

* corrupt one key formula range
* blank out or duplicate a sheet
* change one summary value so it no longer reconciles to detail
* alter a benchmark column in the final workbook export only

Goal:

* confirm reviewer catches artifact-level corruption, not just upstream logic issues

### Test 3: business-semantic anomaly

Create or simulate a suspicious business case such as:

* set a benchmark to zero or null for a high-spend slice
* create a UOM mismatch that makes pricing look inflated
* force a ratio that looks implausibly favorable

Goal:

* confirm reviewer asks smart follow-up questions and identifies the semantic issue

Optional fourth test:

### Test 4: evidence dialogue quality

Goal:

* verify the reviewer asks narrow, useful questions rather than generic “show me more data”

## 12) What “good” looks like

A successful implementation should show the reviewer doing things like:

* “This summary tab appears to show savings where the target benchmark is zero in multiple high-spend rows. I need confirmation of how zero and null benchmarks are handled.”
* “The price variance on these items looks too extreme to accept at face value. Please provide UOM normalization details and a sample of item-level calculations.”
* “The total on Sheet A does not reconcile to the detailed rows on Sheet C. Verify whether workbook generation dropped a filter or duplicated rows.”
* “This workbook looks internally consistent, but the concentration of outlier savings in one category is suspicious enough to warrant a follow-up check.”

Bad behavior would be:

* generic praise
* shallow comments about formatting only
* purely statistical anomaly hunting
* asking for entire tables with no hypothesis
* pretending to know facts it has not been given

## 13) Coding expectations

When implementing:

* prefer clear, modular Python
* add logging
* make reruns easy
* separate config, prompt assets, Azure client code, run orchestration, and evidence handlers
* avoid hardcoded paths and secrets
* save exact prompts and responses used in each run for auditability

## 14) Explicit instructions for model/tool compatibility

Be careful about Azure compatibility.

The current Azure Foundry documentation I found indicates:

* Foundry Agent Service supports GPT-5-family models in some regions, but GPT-5-family agents are limited to Code Interpreter and File Search tools. ([Microsoft Learn][3])
* Hosted Code Interpreter is supported for Foundry agents and can analyze `.xlsx` files. ([Microsoft Learn][2])
* Agent creation and reuse are supported in the Azure agent frameworks and SDK flows. ([Microsoft Learn][6])

So:

* do not attach unsupported tools to GPT-5-family reviewer agents
* if a desired tool is unsupported, keep it in the local orchestrator instead
* prefer Azure reviewer = artifact analysis
* prefer local orchestrator = evidence gathering from BigQuery and repo logic

## 15) Final output expected from you, GitHub Copilot agent

After implementing, provide:

1. a short architecture summary
2. files created/modified
3. how to configure and run the system
4. whether the Azure reviewer agent was successfully created
5. what model deployment was actually used
6. results of the 3 required test scenarios
7. any blockers, especially around Azure model availability or auth
8. recommended next improvements

---

## Optional starter reviewer prompt seed

Use this as a starting point, then refine into a file:

```text
You are a skeptical healthcare Contract Director reviewing analytical work products before they are shown to leadership, suppliers, or internal stakeholders.

Your job is to find anything that does not reconcile, does not make commercial sense, looks artificially favorable, or suggests the workbook/report may have been generated incorrectly.

You are not here to be agreeable. You are here to challenge the work product.

Review priorities:
1. Missing, zero, or fallback benchmark values that can distort savings or price comparisons.
2. Unit-of-measure mismatches and packaging normalization errors.
3. Roll-up vs detail reconciliation failures across workbook tabs.
4. Duplicate counting, join multiplication, or denominator mistakes.
5. Workbook-generation corruption such as broken formulas, missing tabs, duplicated sheets, malformed output, stale values, or inconsistent totals.
6. Relationship anomalies that are commercially suspicious even if statistically possible.
7. High-dollar or high-visibility findings that could mislead an executive audience.

Behavior rules:
- Start with the artifact itself.
- Cite exact sheet/tab names and visible evidence when possible.
- Ask for targeted evidence when something appears suspicious.
- Prefer compact evidence packets over broad dumps.
- Never assume upstream logic is correct simply because the workbook looks polished.
- Never assume the workbook is wrong simply because a number is large; explain why it is suspicious.
- Be concise, direct, and evidence-first.

At each turn, return exactly one of:
- FINDING
- EVIDENCE_REQUEST
- FINAL_VERDICT
```

[1]: https://openai.com/index/introducing-gpt-5-4/?utm_source=chatgpt.com "Introducing GPT-5.4 | OpenAI"
[2]: https://learn.microsoft.com/en-us/azure//ai-services/agents/how-to/tools/code-interpreter?utm_source=chatgpt.com "How to use Azure AI Foundry Agent Service Code Interpreter - Azure AI Foundry | Microsoft Learn"
[3]: https://learn.microsoft.com/en-us/azure/ai-foundry/agents/concepts/model-region-support?utm_source=chatgpt.com "Supported Models in Foundry Agent Service - Microsoft Foundry | Microsoft Learn"
[4]: https://learn.microsoft.com/azure/ai-services/openai/how-to/chat-markup-language?utm_source=chatgpt.com "Use the Azure OpenAI Responses API - Microsoft Foundry | Microsoft Learn"
[5]: https://learn.microsoft.com/en-us/azure/foundry/openai/how-to/json-mode?utm_source=chatgpt.com "How to use JSON mode with Azure OpenAI in Microsoft Foundry Models - Microsoft Foundry | Microsoft Learn"
[6]: https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent?utm_source=chatgpt.com "Azure AI Foundry Agents | Microsoft Learn"
[7]: https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/code-interpreter?utm_source=chatgpt.com "Use Code Interpreter with Microsoft Foundry agents - Microsoft Foundry | Microsoft Learn"
