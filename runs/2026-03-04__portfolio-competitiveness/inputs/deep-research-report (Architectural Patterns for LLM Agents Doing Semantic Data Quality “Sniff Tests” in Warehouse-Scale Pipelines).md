# Architectural Patterns for LLM Agents Doing Semantic Data Quality “Sniff Tests” in Warehouse-Scale Pipelines

## Why semantic data quality needs an agentic layer
Traditional data-quality tooling is strong at **structural integrity** (schema, nullability, type checks, uniqueness, referential integrity), but weak at **contextual plausibility**—the exact failure mode you described (e.g., $0 benchmarks causing artificial “savings,” UOM mismatches creating 800% price inflation that looks “valid” numerically). This gap shows up because the data can be *syntactically valid* while violating *business semantics* that live across columns, joins, and rollups.

Two broader trends are relevant:

First, the modern “data reliability” ecosystem has increasingly treated DQ as **coverage + triage + resolution** (not just tests). That is: detect issues, explain likely root cause, and prevent downstream impact—often with human-in-the-loop decisions for business logic. citeturn9view0turn2search36

Second, major data-observability vendors have started shipping “agentic” capabilities (LLM + metadata + sampling + query logs) not merely for alerting, but for **hypothesis-driven investigation** (e.g., “is it source data, transformation logic, or downstream usage?”). citeturn9view0turn9view2

That’s the same mental model as your “Contract Director hat”: a domain expert doesn’t eyeball every row—they **form a hypothesis**, run a couple of targeted slices/aggregations, then decide whether the output “smells wrong.”

## State of the art methodology for agentic tabular sniff tests and LLM-as-a-judge
### Agentic data feasibility as a loop, not a single prompt
In practice, the most effective “semantic QA agent” implementations look less like “LLM reads a table” and more like an **iterative control loop**:

1. **Observe**: get schema + a small set of computed summaries (counts, null rates, quantiles, top categories, join cardinalities, key ratios).
2. **Hypothesize**: propose specific failure hypotheses (e.g., “benchmark missing for these vendors,” “UOM conversion broken,” “join duplication inflates spend”).
3. **Act**: generate targeted SQL/Pandas (aggregations + stratified slices) to test hypotheses.
4. **Judge**: decide *severity* and *confidence*, then request deeper drilldowns only where needed.
5. **Report**: write a structured anomaly report with top issues + evidence + suspected causes + recommended next checks.

This loop is consistent with published “LLM agents for cleaning tabular datasets” findings: LLMs can often identify **row-level illogical values** (single-row reasoning) but struggle with **multi-row distribution issues** unless you explicitly give them tools to compute distributional evidence. citeturn6view4

It’s also consistent with the direction of modern agentic observability tooling: agents that “test hundreds of hypotheses” over relevant tables and isolate likely causes. citeturn9view0

### What “LLM-as-a-judge” means in tabular DQ
“LLM-as-a-judge” is the pattern where an LLM produces a **decision** (score, label, ranking, critique) using a rubric, rather than producing the primary artifact. The research literature frames it as scalable evaluation, but the same mechanics apply to DQ:

- The **candidate issues** come from computed metrics / rules / anomaly detectors.
- The LLM judge decides: *Is this abnormal for this domain? Is it likely a bug vs a real-world shift? Is it dashboard-blocking?*

There are now multiple surveys that systematize “LLM-as-a-judge” design choices, reliability strategies, and evaluation methods. citeturn6view0turn6view1

For tabular anomaly detection specifically, recent benchmarks emphasize anomalies beyond simple univariate outliers—e.g., **logical anomalies** (violations of relationships between columns), **calculation-based anomalies**, and **temporal anomalies**—which maps cleanly to “sniff tests” on derived measures like price-to-benchmark and rollups. citeturn6view3

There are also LLM-based anomaly detection approaches that serialize tables and compute anomaly scores via language-model likelihood (e.g., “AnoLLM”), positioning LLMs as anomaly scorers especially for mixed-type tables with text. This is useful for long-tail detection and mixed columns, but it still benefits from warehouse-side summarization for scale. citeturn11view0

### Reliability limits you should plan around
For a production “sniff test agent,” the most important LLM-as-judge research results translate into operational guardrails:

- **Domain expertise gap**: LLM judges can diverge from subject-matter experts on specialized tasks; studies show meaningful disagreement rates in expert-knowledge evaluation settings, implying you should keep “human override + feedback” in your workflow for business-critical pipelines. citeturn7search1
- **Ambiguity / indeterminacy**: Some judgments don’t have a single “gold label” (e.g., whether a price shift is a real market move vs a pipeline issue). Work on “rating indeterminacy” argues you need validation methods that preserve disagreement rather than forcing single labels—practically, this supports multi-tier severity (“FYI / investigate / block”) instead of pass/fail. citeturn7search3turn7search2
- **Frontier limitations**: At the “evaluation frontier” (when what you’re judging is as strong/new as the judge), there are theoretical limits on how much LLM-as-judge reduces the need for ground truth. For your use case, this implies you should treat the agent’s output as **decision support** backed by evidence, not an oracle. citeturn11view3

The upshot: your strongest architecture is **LLM-as-a-judge over computed evidence**, not LLM-as-a-mind-reader of raw rows.

## Patterns and frameworks for autonomous SQL/Pandas exploration without loading huge tables into context
### The core scaling pattern: progressive disclosure + evidence budgets
Most practical “SQL agents” follow a tool-driven pattern:

- fetch available tables + schemas
- select relevant fields
- generate a query
- double-check query correctness
- execute
- summarize results and iterate

This is explicit in common SQL-agent tutorials. citeturn10search2

A newer, more production-oriented phrasing is **progressive disclosure**: the agent loads only the context it needs *on demand* via tool calls (schemas, “skills,” samples), rather than front-loading everything into the system prompt. citeturn10search30turn0search18

For your “sniff test agent,” progressive disclosure should be paired with two budgets:

- **Compute budget**: cap bytes scanned / query cost per investigation step.
- **Evidence budget**: cap returned rows; prefer aggregates, quantiles, and stratified slices.

BigQuery supports cost estimation and guardrails such as dry runs, query validator estimates, and “maximum bytes billed” so you can enforce a hard ceiling on agent-generated SQL. citeturn12search0turn12search1turn12search26

### BigQuery-native primitives that fit agentic sniff tests
Because your data lives in BigQuery, warehouse-native computation is your friend; the agent should rarely “pull data out” except for tiny diagnostic slices.

Key primitives:

- **Schema introspection** via `INFORMATION_SCHEMA` views (e.g., `COLUMNS`, nested fields). citeturn5search0turn5search11
- **Job metadata** via `INFORMATION_SCHEMA.JOBS` / `JOBS_BY_PROJECT` for monitoring what ran and how much it processed. citeturn5search3turn5search4
- **Sampling** via `TABLESAMPLE` (and related tooling patterns) to get representative subsets while avoiding full scans. citeturn12search2turn5search1
- **Approximate distribution summaries** (`APPROX_QUANTILES`, approximate aggregates) for fast “shape checks” on huge tables. citeturn5search2turn5search6
- **Built-in drift tooling** (if you want “yesterday vs today” distribution comparisons) via BigQuery ML’s drift validation function. citeturn12search21

Also note: BigQuery’s own guidance stresses that `LIMIT` often **doesn’t reduce bytes scanned** on non-clustered tables, so your agent needs to rely on partition pruning, clustering, or explicit sampling/filters—not naïve `LIMIT`. citeturn12search0turn12search13

### Tooling options: orchestration frameworks vs platform-native tool calling
You can implement the loop (hypothesize → query → judge → drill down) in multiple ways:

**Option A: agent orchestration frameworks (Python-first)**
- A “SQL agent” built on agent scaffolding that already supports schema retrieval, query generation, and self-correction is common. citeturn10search2turn10search5
- Structured-data agent toolkits like entity["organization","LlamaIndex","llm data framework"] include Text-to-SQL components (e.g., `NLSQLTableQueryEngine`, table retrievers) and examples combining SQL with in-process engines like DuckDB—useful for local prototyping or “small extracts,” but your production path will still be BigQuery-executed SQL. citeturn10search0turn10search6turn10search1
- entity["organization","DuckDB","in-process database"] can run SQL over Pandas efficiently (handy if you export a small diagnostic slice and want flexible local joins/logic). citeturn10search16

**Option B: platform-native tool calling + controlled executors**
If you’re already building on the entity["company","OpenAI","ai company"] platform, the “modern” pattern is:

- Use the **Responses API** + tool calling and give the model access to:
  - a hardened BigQuery query executor tool
  - optional Code Interpreter for local analysis on returned aggregates/small extracts
  - structured outputs for deterministic report schemas

OpenAI explicitly supports Code Interpreter and remote MCP servers as built-in tools in its agentic stack (Responses API), which is relevant when you want the model to alternate between running SQL “in the warehouse” and doing small local computations. citeturn3search2turn3search0

For deterministic artifact generation (your anomaly report), **Structured Outputs** lets you enforce a JSON schema so the agent emits consistent fields like “issue_type,” “severity,” “evidence_queries,” “affected_partitions,” etc. citeturn4search0turn4search8

In enterprise settings, OpenAI also documents governance patterns: guardrails, tracing, and policy enforcement around agent tool usage—directly applicable if you’re letting an agent generate and execute SQL. citeturn4search1

### MCP database tools: when and how they fit
The Model Context Protocol (MCP) exists to standardize “models ↔ tools/data sources” connections and reduce bespoke integration overhead. MCP is positioned as a general connector standard, similar to “USB‑C for tools.” citeturn0search6turn0search12turn0search3

For your scenario, MCP is compelling if you want:
- a standardized way to expose “run SQL,” “list datasets,” “get schema,” “fetch sample,” “write findings” as tools
- the flexibility to swap hosts (different clients, models, or agent runners)

OpenAI has added support for remote MCP servers in the Responses API, so you can host your “BigQuery tools” as an MCP server and connect them with minimal glue. citeturn3search2turn3search6

But: production guidance increasingly emphasizes MCP security risks (e.g., tool poisoning / tool shadowing and trust boundaries). citeturn0search29turn0news52  
So if you use MCP, your design should include explicit tool allowlists, authn/z, and strict query constraints.

## How to draft a cynical domain-expert “Sniff Test” system prompt
### Design principles for this persona prompt
A “Cynical Data QA Analyst / Domain Expert” prompt works best when you **encode investigative behavior**, not just tone. Three practices matter most:

**Ground the persona in evidence-seeking**
Your prompt should force a pattern like: “No claims without a query or computed stat.” This matters because LLMs will otherwise default to generic anomaly heuristics.

**Make relationships first-class**
Your primary anomaly class is *relational / derived* (price-to-benchmark, UOM conversions, spend rollup sanity, join duplication). Your prompt should explicitly prioritize:
- ratio anomalies
- rule-of-thumb constraints (e.g., price per each vs per case)
- reconciliation checks (sum of lines vs header totals)
- schema-to-business meaning mapping (“benchmark missing” → “$0 target” → “baseline inflation”)

**Separate detection from adjudication**
In production, treat the agent as:
- a **detective** (generate hypotheses + evidence queries)
- a **judge** (severity + confidence + recommended next steps)

This mirrors research caution about relying on LLM judges without domain calibration and human oversight. citeturn7search1turn7search3

### A practical system prompt template
Below is a template that has worked well in production-style “data detective” agents. It assumes tool access to:
- `get_schema(table)`
- `run_sql(query, max_bytes_billed, dry_run_allowed)`
- `fetch_sample(query, max_rows)`
- `write_finding(json)`
- `send_email(to, subject, html_body)`

```text
SYSTEM: You are “The Sniff Test Analyst,” a cynical healthcare supply-chain data QA expert.

Mission:
- Determine whether the output table is business-plausible for contract/catalog/spend analytics.
- Find relationship anomalies that would mislead an executive dashboard or savings model.

Operating rules (non-negotiable):
1) Never assume: every claim must be backed by a computed metric or a query result.
2) Prefer aggregates to raw rows. Only pull rows after you’ve localized a suspicious slice.
3) Focus on semantic failures:
   - price vs benchmark ratios
   - UOM mismatches / conversion logic
   - missing benchmarks leading to $0 targets
   - join duplication that inflates spend
   - inconsistent contract tier logic across vendors/categories
4) Optimize for “high-dollar risk per minute.” If the table is huge, find the 5 riskiest anomalies first.
5) Every issue must include:
   - severity (blocker / investigate / FYI)
   - confidence (high/med/low)
   - evidence (queries run + key numbers)
   - suspected cause (source vs transform vs reference data)
   - suggested next query to confirm

Style:
- Be blunt. Use concise, auditable language.
- Prefer “Here’s the evidence” over speculation.
```

Why this structure works:
- It compels tool-driven evidence gathering rather than “LLM vibes.”
- It narrows the search space to your business logic.
- It forces an “audit trail” (queries + numbers), which is essential if you later integrate into CI/CD gating.

OpenAI’s agent tooling explicitly supports “instructions” for personality plus tool usage, and Structured Outputs to make these findings machine-consumable downstream. citeturn3search11turn4search0

### A note on tool reliability and retries
Whichever tool interface you expose (functions or MCP), implement it as if the model may retry calls. OpenAI’s MCP/server guidance explicitly warns to make handlers idempotent because models may retry tool calls. citeturn4search2

That matters for DQ agents because you don’t want duplicate writes (multiple alerts, duplicate emails) or accidental expensive reruns.

## How data teams embed LLM-driven anomaly reports into CI/CD and ETL
### Baseline pattern: deterministic tests in CI, semantic report post-run
Most teams already have a “quality gate” pattern:

- **CI stage**: validate transformation changes before merge (build/test changed models, run data tests/unit tests).
- **Runtime stage**: run scheduled jobs; execute checks at materialization time; notify on failures.

For example, dbt’s CI guidance builds and tests modified assets and dependencies in an isolated schema before merging. citeturn8search4turn8search0  
dbt also supports both data tests and unit tests; unit tests validate modeling logic on small static inputs, and can run during development/CI. citeturn8search1turn8search5turn8search36

Traditional validation frameworks like entity["organization","Great Expectations","data validation framework"] support “Checkpoints” that run validations and take Actions like email or Slack notifications, which is the standard “insert into pipeline + alert” mechanism. citeturn8search21turn8search6turn8search10

Orchestrators increasingly treat DQ as first-class:
- entity["organization","Dagster","data orchestrator"] asset checks run when assets materialize, enabling proactive validation before downstream consumption. citeturn8search7turn8search3

### Where LLM-driven reports are being added
Modern “LLM-driven anomaly reports” typically appear in one of three insertion points:

**Post-materialization semantic audit (non-blocking at first)**
- Run the agent after critical mart tables materialize.
- Email/Slack a ranked list of anomalies + evidence queries.
- Don’t block dashboards initially; use it to build trust and collect feedback labels.

This matches how agentic observability vendors position early deployment: accelerate monitoring coverage and troubleshooting without automatically changing production data. citeturn9view0turn2search16

**Auto-generated monitors + monitors-as-code (shift-left)**
Some platforms now recommend monitors/rules by analyzing metadata, samples, and query logs; users can deploy recommendations and codify them. citeturn9view0turn9view2turn2search20

A concrete example: entity["organization","Monte Carlo","data observability company"] describes “observability agents” including a Monitoring Agent that recommends rules/thresholds and a Troubleshooting Agent that investigates root cause via hypothesis testing, using data samples, metadata, and query logs. citeturn9view0turn9view2

**AI-assisted contracts and record-level diagnostics**
Vendors like entity["organization","Soda","data quality company"] position AI features around AI-generated data contracts, anomaly detection, and record-level diagnostics—useful framing if you want the agent to propose contractual checks (“this ratio should be between X and Y”) and then produce record-level examples for review. citeturn9view4turn1search11

### Why teams still keep conventional DQ alongside the agent
Even “AI-native DQ” toolchains still rely on deterministic validation for foundational hygiene (schema, completeness) and use AI/agent layers for:
- coverage expansion (suggest monitors)
- triage acceleration (summarize evidence)
- semantics-aware investigation

That’s consistent with BigQuery/Dataplex’s own “data quality scans” approach: you define rules, run automated scans, and emit alerts/reports—useful baseline, but not a substitute for domain-specific sniff tests unless you encode those semantics explicitly. citeturn12search27

## Proposed end-to-end architecture for a BigQuery Sniff Test Agent that emails an anomaly report
This section is intentionally concrete and “buildable.” The goal is the smallest production architecture that (a) scales to millions of rows, (b) captures your business-logic failure modes, and (c) produces an auditable report.

### Core components
**Sniff Test Orchestrator (your pipeline runner)**
- Runs after your final mart / rollup table lands (end-of-pipeline hook).
- Could be implemented in your existing orchestrator (Airflow/Dagster/dbt jobs) as a terminal task, or as a separate job triggered by table materialization (e.g., scheduled after pipeline completion).

**BigQuery Evidence Extractor (deterministic)**
- A curated library of *warehouse-side* profiling queries that produce a compact “evidence bundle,” typically on the order of:
  - tens to hundreds of numbers
  - a handful of small grouped tables (top 20 offenders)
  - optionally 20–50 example rows for each flagged slice

Use schema introspection first (so queries adapt to changing tables):
- `INFORMATION_SCHEMA.COLUMNS` to learn field names/types. citeturn5search0

Use compute guardrails:
- dry run to estimate bytes processed. citeturn12search0turn12search1
- “maximum bytes billed” to fail fast if the model proposes an expensive query. citeturn12search0

Use distribution summaries rather than scans:
- `APPROX_QUANTILES` / approximate aggregates. citeturn5search2turn5search6
- sampling (`TABLESAMPLE`) for “row examples.” citeturn12search2turn5search1

**LLM Agent (planner + hypothesis generator + judge)**
- Input: schema + evidence bundle + your domain “QA playbook.”
- Output: structured anomaly report + optional next-step queries.

Implementation choices:
- If you want a clean “tools + structured outputs” path, implement using OpenAI Responses tool calling + Structured Outputs. citeturn3search2turn4search0
- If you want standards-based tool plumbing, expose BigQuery operations via an MCP server and let the agent call them; OpenAI supports remote MCP servers in Responses. citeturn3search2turn0search6turn4search2

**Findings Store (optional but recommended)**
- Write every run’s results into a BigQuery table (e.g., `dq_findings`) so you can trend:
  - counts of anomalies by type
  - recurring offenders (vendors, categories)
  - false positive rate (based on your feedback)

This mirrors the “incident management” posture in modern data observability. citeturn9view0turn5search25

**Delivery**
- Email the report to you (and optionally Slack/Jira).
- Ensure idempotency to prevent duplicate notifications on retries. citeturn4search2

### Recommended workflow: what the agent does step-by-step
**Step one: establish context cheaply**
1. Pull schema from `INFORMATION_SCHEMA.COLUMNS`.
2. Compute table-level metrics:
   - row count
   - count of distinct keys
   - null rates for critical columns
   - min/max and quantiles for spend/price/benchmark columns
   - top categories/vendors by spend
3. Compute “semantic ratios” your business cares about, as grouped summaries:
   - distribution of `price / benchmark_price` by UOM, vendor, category
   - spend rollup reconciliation checks (sum of lines vs header totals)
   - join cardinality checks (e.g., count of lines per contract item key)

**Step two: hypothesis-driven drilldown**
4. For the top suspicious segments, run targeted drilldowns:
   - show top 20 rows by “excess spend contribution”
   - retrieve a small sample of rows for each anomaly bucket (using sampling and strict row caps)

**Step three: LLM-as-a-judge with structured outputs**
5. Feed the evidence bundle to the agent (not the raw table).
6. The agent produces structured JSON like:
   - `issue_id`, `issue_type`, `severity`, `confidence`
   - `business_impact_estimate` (e.g., “potential baseline inflation: $X”)
   - `evidence` (query outputs + key numbers)
   - `likely_root_cause` (missing reference data vs transformation vs source)
   - `recommended_fix` (what to check in code or reference tables)
7. Render to HTML and email.

Structured Outputs is directly designed to keep these report schemas stable across runs and avoid malformed JSON. citeturn4search0turn4search25

### Concrete “evidence bundle” query patterns for your domain
Below are examples of *patterns* (not full SQL) that map to your exact failure modes:

**Benchmark-missing baseline inflation**
- Compute `% of spend where benchmark is null or zero`
- Identify top spend contributors in that segment
- Estimate impact: spend where target benchmark used in baseline logic

This kind of issue is exactly why “semantic gap” discussions argue schema checks aren’t enough; business meaning matters. citeturn0search8

**UOM mismatch / conversion explosions**
- Group by `(item_id, vendor, uom)` and compute:
  - median unit price
  - median benchmark
  - median `price/benchmark`
- Flag where ratio exceeds domain thresholds, but *also* where UOM differs from reference UOM (join to UOM map table)

**Join duplication / rollup anomalies**
- For key joins, compute:
  - distribution of “child rows per parent key”
  - ratio of spend pre-join vs post-join
- Flag spikes localized to a vendor/category/contract

### Security, privacy, and governance requirements
Given healthcare context, treat this as “enterprise agent” posture:

- Keep data movement minimal: compute in BigQuery, export only tiny slices. BigQuery itself stresses avoiding exploratory full scans and using safer preview/sampling patterns. citeturn12search0turn5search20
- Lock down tool permissions: the agent should be **read-only** for warehouse tables and only write to a dedicated findings table.
- If using MCP, follow platform warnings about tool trust and verification. citeturn0search29turn0news52
- If using OpenAI APIs, understand and configure data controls; OpenAI documents that API data is not used to train models unless you opt in. citeturn4search16

### A pragmatic build recommendation
If your goal is “ship something useful in weeks,” the lowest-risk architecture is:

- Deterministic evidence extractor in Python (BigQuery client) with strict guardrails (dry run + max bytes billed).
- LLM agent used primarily for:
  - selecting which evidence queries to run next (within a whitelist)
  - interpreting results into a ranked anomaly report
  - proposing candidate new checks (“monitors”) for you to codify

This matches where agentic observability tooling is landing: accelerate coverage and troubleshooting, with human control over what becomes a hard gate. citeturn9view0turn2search16turn2search20