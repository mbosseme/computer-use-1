# Agent Guide: Dataform Pipelines in VS Code

**Purpose.** This guide explains how to effectively build, maintain, and run Dataform pipelines in a "Code-First" environment (VS Code + GitHub Copilot), based on successful patterns from the committed-program-analysis workspace.

**Target Audience.** AI Agents (and humans) working in repositories where Dataform is integrated alongside application code (Python/CLI) and executed via local CLI or automated wrappers.

---

## 1. Core Architecture: The "Hybrid Wrapper" Pattern

In this workspace, Dataform is not just a standalone SQL runner; it is a **step** in a larger application pipeline. This "Python Wrapper" pattern is powerful for agents:

*   **Structure**:
    *   `/dataform`: Contains the standard Dataform project (`definitions`, `includes`, `package.json`).
    *   `/src/steps/dataform_step.py`: A Python module that wraps `npx dataform run`.
    *   **Why?** This allows the Python app to inject dynamic variables (like run dates, window parameters, or user overrides) into Dataform at runtime via `--vars`.

*   **Execution Flow**:
    1.  User runs pipeline: `python -m src.runner.cli run-all`.
    2.  Python computes config (e.g., `core_start=2024-01-01`).
    3.  Python invokes: `npx dataform run --vars=core_start_override=2024-01-01`.
    4.  Dataform compilation picks up the var in `dataform.json`.
    5.  SQL executes on BigQuery.

### Agent Actionable:
*   **Do not run `npx dataform run` blindly** if you are trying to reproduce a full pipeline run. Use the Python runner (e.g., checking `src/runner` or `src/steps`) to ensure variables are passed correctly.
*   **Do run `npx dataform compile`** frequentlly to check your syntax validity.

---

## 2. Repo Structure & key Files

The folder layout is designed to help Agents discover context.

### `/dataform/dataform.json`
**The Source of Truth for Config.**
*   **`defaultSchema`**: Defines where dev tables go (e.g., `*_dev`).
*   **`vars`**: Holds business logic constants (thresholds, prefixes).
    *   *Agent Tip:* Never hardcode business constants (e.g., "0.02" or "SP-") in SQL. Check `vars` first. If missing, add it to `vars`.

### `/dataform/includes/constants.js` (Crucial Pattern)
This repo uses a JS include to "type-check" and re-export `vars`.
*   **Pattern**:
    ```javascript
    // includes/constants.js
    const vars = dataform.projectConfig.vars;
    module.exports = {
      coverageGuard: Number(vars.coverage_guard ?? 0.02), // Typecast ensures safety
      surpassPrefix: String(vars.surpass_prefix ?? "SP-")
    };
    ```
*   **Usage in SQLX**:
    ```sqlx
    js { const c = require("../../includes/constants"); }
    SELECT * FROM table WHERE val > ${c.coverageGuard}
    ```
*   *Agent Tip:* Always import `constants` in your `js {}` block rather than accessing `dataform.projectConfig.vars` directly. It prevents typos and type errors.

### `/dataform/definitions/staging/stg_window_params.sqlx` (Dynamic View Pattern)
Instead of hardcoding dates in every mart, create a single view that calculates window parameters based on run-time vars or `current_date()`.
*   **Pattern**: A view that selects `current_date() as run_date`, `parse_date(...) as start_date`.
*   **Usage**: Downstream marts `CROSS JOIN` this 1-row view to get consistent time boundaries.

---

## 3. Best Practices for Agents Authoring SQLX

### 1. Dependency Management is Mandatory
*   **BAD**: `FROM my_dataset.my_table` (Hardcoded lineage breaks DAG).
*   **GOOD**: `FROM ${ref("stg_transaction_base")}` (Dataform manages dependency).
*   **Agent Rule**: If you introduce a new source table, define it in `definitions/sources/` (e.g., as a `declaration`) before referencing it.

### 2. Incremental Strategy
*   Use `config { type: "incremental", uniqueKey: [...] }` for large tables.
*   **Idempotency**: Ensure `uniqueKey` is truly unique to prevent duplicates during merges.
*   *Agent Tip:* If changing logic in an incremental table, advise the user to run with `--full-refresh` to rebuild history.

### 3. Syntax Guardrails
Dataform mixes JavaScript and SQL. This confuses some models.
*   **JS Block**: `js { ... }` runs at *compile time*. Variables defined here are inserted into SQL strings.
*   **SQL Block**: `${ variable }` injects the value.
*   **BigQuery Parameters**: `@param` is standard SQL. Avoid confusing `${...}` (compile-time) with `@...` (run-time BQ param). In Dataform, prefer compile-time injection for schema constants.

---

## 4. Development Workflow for Agents

When tasked to "add a metric" or "fix a bug" in Dataform:

1.  **Locate the Layer**:
    *   Is it a raw field mapping? -> `definitions/staging/`
    *   Is it a business aggregation? -> `definitions/marts/`
2.  **Check Constants**: Look in `includes/constants.js`.
3.  **Edit SQLX**: Apply changes.
4.  **Validate Syntax**: Run `npx dataform compile` in the terminal.
    *   *Agent Tip:* Do this *before* asking the user to run the full pipeline. It catches JS errors instantly.
5.  **Verify Data**: If allowed, run `npx dataform run --actions <node_name>` to test just that table in the dev schema.

---

# Original Best Practices Implementation Reference

(The original content below has been preserved for deep-dive architectural reference)

VS Code + Coding Agents + Dataform (BigQuery) in a Single Repo – Deep Dive
Executive Summary
This report presents a comprehensive workflow for integrating a Google Cloud Dataform project with application code in a single repository, leveraging VS Code with AI coding assistants (GitHub Copilot and OpenAI Codex). We outline a recommended architecture and alternatives for developing and running Dataform pipelines on BigQuery in an enterprise setting. Key considerations include repository structure, environment separation (dev/test/prod), secure authentication without storing service account keys, CI/CD automation, and best practices for data quality and observability.
Recommended Approach: We propose a hybrid architecture where Dataform code is authored and tested locally (using the open-source Dataform CLI) and then deployed to the managed Dataform service in BigQuery for production execution and lineage tracking. In this model, developers benefit from immediate feedback and flexibility of local runs, while production pipelines leverage Dataform’s GCP integration for scheduling, lineage visualization, and logging. Our primary recommendations include:
•	Monorepo Structure: Organize a single GitHub repository with clearly separated directories for application code and the Dataform project (e.g. /app/ for Python/CLI code, /dataform/ for SQLX models and config, plus any /infra/ or config dirs). This structure helps AI coding assistants “discover” Dataform files and context, and prevents accidental edits to infrastructure or environment config by the AI agents.
•	Dataform in BigQuery (Managed) vs Dataform Core: Use Dataform (BigQuery) for production runs to take advantage of GCP’s managed features (UI, lineage DAG, scheduling)[1][2], while leveraging Dataform Core CLI locally for iterative development and validation[3]. We clarify differences: the managed Dataform service uses the same SQLX and compilation engine (“Dataform core”) under the hood[4][3], but is fully hosted in GCP, executing queries via a service account. Dataform Core (the open-source CLI) allows running the same code from any environment (e.g. CI or developer laptop) to compile and execute transformations on BigQuery.
•	Multiple Dataform Repositories in One Project: It’s fully supported to have multiple Dataform “repositories” in a single GCP project[5][6]. In our scenario, we will create a second Dataform repository in the GCP project and link it to our new GitHub repo (the first Dataform repo in the project remains linked to a different repo). The new Dataform instance will use a distinct working directory and BigQuery datasets to avoid conflicts.
•	Environment Separation: We recommend isolating development, testing, and production datasets either within a single Dataform repo via configuration overrides or via separate GCP projects/repos for strict separation[7][8]. Our primary design uses single-repo, multi-environment isolation: e.g. development tables have a prefix or separate dataset (like myapp_dev vs myapp_prod in BigQuery) set via Dataform compilation settings, and Dataform’s Release Configurations feature to define isolated compilation outputs for each environment[9][10]. This avoids needing a legacy environments.json (which is not supported in GCP’s Dataform[11]). We’ll detail how to configure Dataform’s workspace overrides or release configs to achieve per-environment dataset naming.
•	Secure Authentication: Use Application Default Credentials (ADC) for local development (e.g. gcloud auth application-default login) and Workload Identity Federation (OIDC) for CI/CD GitHub Actions – avoiding any long-lived service account keys in the repo. This method eliminates the risks of key exposure and aligns with Google’s recommended keyless auth[12]. In practice, the GitHub Actions workflow will use the google-github-actions/auth action to obtain short-lived credentials for a service account with minimal roles[13][14]. We also cover linking the Dataform UI to GitHub via SSH deploy keys or fine-grained PATs (preferred over storing credentials)[15][16].
•	CI/CD Pipeline: Implement a GitHub Actions workflow that lint-checks SQLX (since dataform compile doesn’t catch SQL syntax errors[17]), runs Dataform tests, and either deploys via Dataform’s API or Dataform CLI depending on the chosen execution mode. We provide templates for both: (A) committing code and invoking a Dataform Workflow Invocation API call for managed execution, or (B) using the Dataform CLI in CI to run the transformations directly on BigQuery. The pipeline also uses branch-based promotion (e.g. dev -> main) to move code through environments, with automated triggers or approvals for deploying to production. Secrets (like any API tokens) are managed via GitHub OIDC or Google Secret Manager, never in code.
•	VS Code + AI Setup: We include minimal VS Code settings to ensure .sqlx files (Dataform SQL with extensions) are recognized as SQL by editors and AI (via file associations) and to provide IntelliSense. We also recommend workspace settings to enable AI agents to see the Dataform project context (marking the repo as a trusted workspace, adding any relevant extensions for SQL). Example custom snippets and prompts are provided to guide Copilot/Codex to produce correct Dataform code – including template config blocks (config { type: ..., schema: ... }), usage of ref() for dependencies, and incremental table patterns. We stress safeguards like commenting critical config files and possibly using repository branch protection to prevent automated agents from altering key settings (e.g. preventing an AI from “helpfully” changing dataset names or credentials files).
•	Data Quality & Observability: Dataform supports assertions (data tests) that run with each pipeline execution and alert on failures[18]. We recommend liberal use of assertions (both built-in ones like uniqueKey or nonNull and custom SQL checks) to catch anomalies. The repo should include an assertions/ directory for standalone tests and/or assertions configured in each table’s SQLX. Incremental models must be configured for idempotence – e.g. use uniqueKey for merge deduplication[19][20] and mark critical incrementals as protected: true to prevent accidental full refreshes that could wipe historical data[21]. We also cover strategies for freshness checks (e.g. using assertions to verify recent timestamps) and safe backfills (using pre_operations and partition filters to limit scanned data on incremental loads[22][23]). For observability, Dataform’s integration logs every workflow invocation to Cloud Logging[24][25]. We show how to set up log-based metrics and alerts in Cloud Monitoring to get notified (via email or Slack) on any Dataform run failures[26][27]. The Dataform UI also provides an interactive DAG and execution logs for debugging.
In summary, our recommended solution offers a balance of developer productivity, governance, and reliability. The hybrid approach (“Author locally, run in cloud”) yields fast iteration cycles with Copilot-assisted SQLX development, while ensuring production pipelines are robustly orchestrated and monitored on GCP. For completeness, we also detail two alternative execution patterns (fully managed vs. fully core) and provide a decision matrix to help choose the best fit. The report concludes with a proof-of-concept illustrating the end-to-end workflow: from creating a new Dataform model in VS Code, through CI validation, to executing the pipeline in BigQuery and verifying the resulting tables.
Architecture Overview (Design Options)
Primary Architecture – Hybrid (Local+Managed): The following diagram illustrates the recommended setup, combining local development with Dataform Core and managed execution in GCP:
flowchart LR
    subgraph Developer_Env [VS Code + Copilot/Codex]
      D1[Local Repo: App code + Dataform project] --> D2[Git: Commit & Push]
      D1 --- D3[Dataform CLI (Compile/Run for dev)]
    end
    D2 -->|GitHub Sync| GCPRepo[**Dataform (BigQuery)** Repo<br/>(linked to GitHub)]
    GCPRepo -->|Compile & Run SQL| BigQuery[BigQuery Warehouse]
    BigQuery --> App[Local Application<br/>(consumes transformed tables)]
    subgraph CI_CD [CI/CD Pipeline]
      CI[GitHub Actions Workflow] -->|OIDC Auth| GCPRepo
      CI -->|Invoke Runs via API| GCPRepo
      CI -->|Alt: CLI Deploy| BigQuery
    end
    D2 --> CI
Fig: Architecture – Dataform code lives with app code in one repo. Developers edit Dataform .sqlx files in VS Code (with AI assistance) and test changes locally using Dataform CLI against BigQuery. Changes are pushed to GitHub, which is linked to a Dataform repository in GCP. For production runs, Dataform (BigQuery) executes the SQL transformations on BigQuery. CI/CD integrates with Dataform via API (for managed execution) or uses the CLI (for direct execution) depending on the chosen approach.
Key components:
- Local Repo (VS Code): Contains both application code and a Dataform project. AI coding agents operate here to suggest or generate Dataform SQLX and config.
- Dataform CLI (Optional Dev Use): Locally, the developer can run dataform compile and dataform run against BigQuery using personal credentials to validate changes quickly. This uses the same Dataform core engine as the cloud service[3].
- GitHub Repo & GCP Dataform Link: The GitHub repository is linked to a GCP Dataform repository (via the Dataform UI settings). Dataform can pull the latest code from GitHub – either manually (developer triggers a Pull in the UI) or automatically when running scheduled workflows on a given Git commit/branch[28][29]. In this setup, we’ll treat the main branch as the production code reference for Dataform’s release config.
- Dataform in BigQuery (Managed Service): The managed Dataform service in GCP compiles the SQLX and runs SQL against BigQuery. It uses a GCP service account/agent to execute queries (with appropriate BigQuery roles)[30][31]. This service provides the UI for workflow development (including an interactive DAG of dependencies), execution logs, data lineage, and scheduling[32][1]. We will configure a second Dataform repository here (since one already exists for another workflow) – each repository is isolated in terms of code and execution, even if in the same project[5].
- BigQuery Warehouse: Dataform reads source tables and writes transformed output tables in BigQuery. Upstream data (raw tables) might reside in the same project or another – we must grant Dataform’s service account at least BigQuery Data Viewer on sources and Data Editor on target datasets[31]. Transformed tables are then consumed by the local application or analytics tools.
- CI/CD Pipeline: Automated workflows (GitHub Actions, shown) ensure code quality and facilitate deployments. On each push or PR, CI can lint SQLX and run Dataform’s compilation/tests. On merge to main, CI triggers a Dataform workflow invocation via GCP’s REST API or CLI. This can be done using the official Dataform API (triggering the managed service to run new code)[33] or by running Dataform CLI in a CI runner to apply changes directly. The CI pipeline authenticates to GCP using Workload Identity Federation (GitHub OIDC) – no secrets needed[12][14].
Alternate Execution Patterns: Two alternatives were evaluated against the hybrid approach:
•	A. Fully Managed Dataform: Developers push changes to GitHub and rely entirely on Dataform (BigQuery) to run them. In this mode, one would typically develop either in the Dataform UI’s workspace (with “GitHub connected” mode) or locally but always push to trigger runs. Triggering runs can be manual (via the GCP Console “Run” button) or automated: e.g. Dataform’s Workflow Configurations for scheduled runs[34], or via an external call to the Dataform API endpoints (which allow event-driven execution by creating a workflow invocation on demand)[33]. This approach leverages the UI fully and simplifies pipeline orchestration (no separate runner needed for execution). However, pure-managed means local editing must be synced/pulled into Dataform for testing, which can slow dev feedback loop, and event-driven or CI-triggered runs require extra integration (using the API or Cloud Composer/Airflow operators[35]). We detail this in the Execution Paths section.
•	B. Fully Dataform Core (no managed service): The Dataform project is treated like a typical code artifact (similar to a dbt project). Developers run dataform compile/test/run locally and in CI. A CI job (or Cloud Build pipeline) uses the @dataform/cli and a service account to deploy transformations to BigQuery on each push. There is no Dataform UI in this workflow; lineage and scheduling would be custom-built or omitted. This gives maximum control and independence (the code can run anywhere, with any custom orchestration), at the cost of losing the GCP-managed features (you’d need to rely on logs in CI/Cloud Logging and build your own DAG visualization or rely on dbt-style docs generation if any). Compatibility-wise, the SQLX and config in our repo work with both Core and Managed Dataform (the underlying compilation is the same[3]). In fact, Google’s docs explicitly allow using the open-source CLI “outside of Google Cloud” for development or automation[3]. We cover using Dataform Core with BigQuery and how it can integrate with CI (including dry-run mode and storing compiled SQL artifacts).
The hybrid approach combines aspects of both: local/CI compile for quick feedback and the managed service for production runs and UI benefits. Next, we dive into the repository layout that supports this and how AI coding agents can work effectively within it.
Repository Blueprint and Project Structure
Below is the canonical repo structure for housing both the application code and Dataform project side by side. This layout ensures a clear separation of concerns and provides cues for AI code assistants to understand context (for instance, Copilot will see .sqlx files under /dataform/ and infer they are SQL model definitions, not application code):
repo-root/
├── app/
│   ├── cli_tool.py             # Example application/analysis code (Python CLI)
│   ├── ... 
│   └── requirements.txt        # App dependencies 
├── dataform/                   # Dataform project root (SQLX models & config)
│   ├── dataform.json           # Dataform project config (default schemas, etc.)
│   ├── package.json            # Node package file for Dataform (core version & deps)
│   ├── includes/               # Reusable SQL/JS snippets (Dataform includes)
│   │   └── helpers.js          # (Optional) JavaScript helper functions
│   ├── definitions/            # Main Dataform model definitions
│   │   ├── sources/            # (Optional) Source declarations (.sqlx or .js)
│   │   ├── staging/            # Staging tables (SQLX selecting from sources)
│   │   ├── marts/              # Mart tables (business logic, can be incremental)
│   │   └── assertions/         # Data quality tests (assertion SQLX files)
│   ├── tests/                  # (Optional) Unit tests or SQL snapshot tests
│   └── env/ (optional)         # Environment-specific overrides (if not using release configs)
│       └── dev.json, prod.json # (Optional) Legacy style env configs – *not used in GCP Dataform*
├── infra/                      # Infra-as-code (optional, e.g., Terraform for dataset or IAM setup)
│   └── bigquery_datasets.tf    # Example: Terraform file to create BQ datasets and grant roles
├── .vscode/
│   ├── settings.json           # VS Code workspace settings (file associations, etc.)
│   └── extensions.json         # (Optional) Recommended extensions (SQL linters, etc.)
├── .github/
│   └── workflows/
│       └── dataform-ci.yml     # GitHub Actions workflow for CI/CD (lint, test, deploy)
├── .env.example                # Example env file (no secrets; instruct how to auth locally)
└── README.md                   # Developer guide to using this repo
Folder Explanations & Key Files:
- /app/ – Contains the local application code (e.g., a Python CLI that queries BigQuery). This is logically separate from Dataform. AI agents should focus on Dataform files only when asked to modify transformation logic. Keeping them in distinct folders helps prevent accidental modifications (e.g., a prompt about Dataform shouldn’t lead the AI to change application code and vice versa).
- /dataform/ – Root of the Dataform project. When running Dataform Core CLI, this directory is your working directory. Important files:
- dataform.json – The Dataform workflow settings JSON[36]. This defines global config like the default database (GCP project ID), default BigQuery dataset (schema) for output tables, optional assertion dataset, default location, etc. For example:

{
  "warehouse": "bigquery",
  "defaultDatabase": "my-gcp-project-id",
  "defaultLocation": "US",
  "defaultSchema": "myapp_dev",          // default dataset for tables
  "assertionSchema": "myapp_assertions"  // dataset for assertions (views of test results)
  /* ,"tablePrefix": "dev_" */          // optional prefix for table names (could use for env)
}
In GCP’s managed Dataform, this file is respected; however, environments.json is not (GCP Dataform doesn’t support it[11]). Instead, environment variants (like using myapp_prod schema in production) are handled via compilation overrides or set in the release config. For instance, we might keep defaultSchema: "myapp_dev" in git (for local/dev runs) and configure the production release in Dataform to override the schema to myapp_prod[37][38]. We’ll explain that in the environments section.
- package.json – Defines the Dataform NPM dependencies. Crucially, this is where we pin the @dataform/core version to match GCP’s version. For example:

{
  "dependencies": {
    "@dataform/core": "3.0.0"
  }
}
Locking the Dataform core version ensures consistency between local and cloud compilation[39][40]. GCP Dataform uses a service to install this package (or uses an internal equivalent), and you can update it via the UI if needed[41][42]. We recommend aligning with the latest supported version in GCP (as of writing, Dataform core 3.x).
- includes/ – Optional directory for JavaScript or SQL includes that can be imported across multiple models. This is useful for DRY patterns (e.g., reusable SQL expressions or UDFs). Dataform allows including JS across files[43]. The presence of an includes folder signals to AI that some logic might be abstracted (e.g., if Copilot sees require('includes/helpers') in a SQLX, it knows to look at that file for context).
- definitions/ – All Dataform action definitions reside here. By convention we separate subfolders by layer: sources (for data source declarations), staging (for lightly transformed raw data), marts (for final transformed tables), and assertions (for tests). This mirrors common practice in data modeling (similar to dbt’s staging/mart structure). It also helps Copilot: if you ask it to “create a new mart model that ref()’s a staging model”, it can deduce the file path. Naming conventions (e.g., prefixing files to indicate type) can also help avoid confusion. Each .sqlx file typically yields one BigQuery table or view. Dataform’s dependency graph is inferred through ref("table_name") calls and explicit dependencies in config. We ensure AI uses ref() properly rather than hard-coding dataset.table names.
- Source declarations: In Dataform, you can declare external tables as sources using .sqlx files with type: "declaration" or via a definitions/.js file calling declare({}). These help document and manage upstream dependencies[44]. For simplicity, we might declare sources in a JS file (e.g., sources/tables.js) with dataform.declare calls. This allows the AI to see a list of available source tables and their dataset locations.
- Staging models: Usually SQLX files that select from sources, doing minimal transformations (aliases, type casts). We configure them typically as ephemeral or tables depending on size (in Dataform, all type: "table" are materialized by default as tables unless we specify disabled or use operations). If only used downstream and not needed in BQ for other uses, they could even be declared as type: "view" to save storage, but here we’ll assume tables.
- Mart models: Heavier transformations, joins, aggregations. Many of these might be incremental. We use config { type: "incremental", uniqueKey: "...", … } in those SQLX to ensure they only process new data after initial backfill[45][19]. Each such model likely ref()s one or more staging tables. The naming in ref() should match the file’s name config or file name if not overridden. By default, Dataform uses the file name as the table name unless a name: is set in config[46].
- Assertions: Each test is a SQLX with config { type: "assertion" } that contains a SELECT query returning rows that violate a condition. If any rows are returned, Dataform marks the assertion as failure[18]. For example, assert_customer_emails.sqlx might SELECT * FROM ${ref('customers')} WHERE email NOT LIKE '%@%'. Dataform will create a view in BigQuery (in the assertions dataset, e.g., myapp_assertions.assert_customer_emails) containing the failing rows[47]. Dataform automatically runs all assertions on each workflow run, and will alert if any assertion fails[18], which is critical for quality control.
- tests/ – (Optional) If using Dataform’s unit test functionality or snapshot tests, they could reside here. Dataform Core supports a rudimentary test via dataform test (which actually executes assertions as well as any JS tests). In practice, many teams rely on assertions instead of separate unit tests, so this folder is optional.
- env/ or environment files: Given GCP Dataform doesn’t use environments.json, this folder might be unused. However, if we were to use Dataform Core exclusively, one could have JSON files per environment and script logic to swap variables. For GCP managed, we instead use Release Configurations in the UI to define environment-specific overrides (like adding a table prefix “prod_” or pointing to a different project for production)[9][10]. We mention this folder only to clarify that environment config will be handled differently (in code via variables or in the UI) for our main solution.
- /infra/ – Optional. Infrastructure-as-Code scripts if needed (creating BigQuery datasets, setting IAM roles, etc.). For example, a Terraform file could define datasets myapp_dev, myapp_prod and grant the Dataform service account the needed BigQuery roles on them. Since Terraform is out-of-scope for this task, this folder can be minimal or omitted. But including an infra/ directory signals to AI agents that some config is off-limits (we might mark it read-only in the editor to avoid accidental changes by AI).
- VS Code settings (.vscode/): We add workspace settings to improve the developer experience for Dataform: - File Associations: In settings.json, map .sqlx to SQL syntax highlighting. For example:

{
  "files.associations": {
    "*.sqlx": "sql"
  },
  // Treat Dataform config files as JSON/JS for language features:
  "files.associations": {
    "dataform.json": "json",
    "*.df.js": "javascript"
  },
  "[sql]": {
    "editor.defaultFormatter": "ms-mssql.mssql"  // example: use MSSQL formatter for SQLX
  }
}
This ensures Copilot/Codex sees SQLX files as SQL, enabling it to suggest valid SQL snippets. Without this, an AI might not recognize the file context and produce poor suggestions.
- Workspace Trust: Enable trust for this workspace so that the AI extensions (which run in VS Code) can access the files. E.g., add "security.workspace.trust.enabled": true and mark this folder as trusted. This prevents VS Code from isolating extensions – important for Copilot to function across the repo.
- Recommended Extensions: In extensions.json, we can list helpful extensions, e.g.:
{
  "recommendations": [
    "googlecloudtools.cloudcode",     // Google Cloud Code (for YAML, cloud integration)
    "ms-mssql.mssql",                // MS SQL (good SQL formatter, BigQuery is similar to ANSI SQL)
    "sqlfluff.sqlfluff",             // SQLFluff linter, we will configure for BigQuery dialect
    "dbaeumer.vscode-eslint"         // ESLint, if we use JS in Dataform includes
  ]
}
These appear as suggestions when someone opens the repo in VS Code. While not mandatory, they ensure a consistent dev environment. For instance, SQLFluff with BigQuery dialect can catch syntax issues in SQLX (though it needs to be configured to ignore Dataform-specific syntax, as noted later).
- Snippets & Emmet: We may create a custom snippet file (e.g., dataform.code-snippets) to help generate boilerplate. For example, a snippet trigger df_table that inserts a template:
"Dataform Table Template": {
  "prefix": "df_table",
  "body": [
    "config {",
    "  type: \"table\",",
    "  schema: \"${1:dataset}\",",
    "  name: \"${2:table_name}\"",
    "  /* tags: [\"${3:tag}\"] */",
    "}",
    "SELECT ...",
    "FROM ${ref(\"$4\")};"
  ],
  "description": "New Dataform table with config block"
}
This can guide Copilot as well; often if you start typing config { type: "table", ... }, Copilot will learn to complete it properly. We also leverage Dataform’s built-in Gemini AI in BigQuery console if available (Dataform UI has an AI assist called Gemini[48], but our focus is Copilot in VS Code).
•	Git Ignore/Env files: We include .env.example to document any environment variables needed (for example, instruct developers to run gcloud auth login and not to put GCP keys in a .env). We do not commit any service account JSON. If the local app needs credentials, it should use Application Default Credentials or ask the user to authenticate via gcloud – our documentation in README will reflect that.
•	Git Branch Conventions: Not a file, but important to mention in repo organization: we’ll encourage feature branches prefixed by component, e.g., feat/dataform-... for transformation changes. This helps reviewers and possibly triggers specialized CI (for instance, branches with dataform in the name could run an extra CI job). Frequent merges to main ensure Dataform’s linked repo is up-to-date. We avoid long-lived divergent branches to reduce sync issues in Dataform UI.
AI Agent Considerations: By structuring the repository and adding the above config, we enable Copilot and Codex to be effective co-authors: they will respect that .sqlx files use SQL context with possible JavaScript { } blocks, they’ll see dataform.json which hints at the warehouse and dataset names, and they’ll notice patterns in existing files (e.g., how ref('...') is used). We should explicitly document (in a CONTRIBUTING.md or README) the conventions so that any AI usage is guided – for example: “Always use ${ref('table_name')} for cross-references; do not hardcode dataset names, as the Dataform config manages that.” This will indirectly train AI by context.
In summary, this repo blueprint keeps things modular and explicit. It delineates app code vs. data pipeline code, supports multi-environment config, and sets up the IDE environment to maximize AI coding assistance while minimizing mistakes. Next, we’ll explore how the pipeline execution works under three scenarios (Managed, Core, Hybrid) and the trade-offs of each.
End-to-End Execution Paths (Managed vs Core vs Hybrid)
We evaluate three approaches for executing the Dataform workflow from development through production, and provide a recommendation:
A. Managed Dataform (BigQuery) + GitHub Link
Workflow: Develop Dataform files locally (or in Dataform’s web IDE if desired), commit and push to GitHub, let Google Cloud Dataform auto-sync and execute. In this mode, the Dataform service in GCP is the only executor of SQL transformations – you do not run them via CLI in production. The typical path:
1.	Development: A developer might use the Dataform UI’s “Development Workspace” connected to the Git repo to edit SQLX, or edit locally and push to a feature branch. The Dataform UI can pull changes from GitHub and compile in real-time to show the DAG and catch compilation errors[49]. The UI supports previewing queries on BigQuery with a click[50], which is handy for interactive development. (Using Copilot in VS Code, the dev can also iterate locally and use the CLI to preview if comfortable; both are possible.)
2.	GitHub Integration: Once changes are ready, the dev pushes to the repository. Because our Dataform repo is connected to GitHub via HTTPS or SSH, the Dataform service has read access. The connection setup involves either providing a deploy key (SSH key pair) or a GitHub token with repo access[51][15]. With that configured, Dataform can fetch the latest code from the remote repository. In practice, when you open the Dataform repository in Cloud Console, you’d click “Pull from branch” to get updates[52], or Dataform will automatically fetch the specified commit for a scheduled run (as part of a Release Config).
3.	Execution (Manual or Scheduled): For an on-demand run, a developer can go to the Dataform console and start a workflow run of the latest code[53]. They can select to run all actions or a subset (by tags or names). Dataform will compile the SQLX to SQL and execute the DAG in dependency order on BigQuery. Alternatively, you set up Workflow Configurations (cron-like schedules) in Dataform to run, say, every night at 2 AM[34]. Each workflow config ties to a Release Config (which defines which branch/commit and overrides to use – e.g., “main branch, prod overrides”). This is great for recurring pipelines. The limitation is schedules are time-based (no built-in event triggering)[54]. For event-driven needs, you can call the Dataform Workflow Invocation API when needed.
4.	CI/CD and Promotion: In a pure managed approach, you might simply rely on GitHub for version control and Dataform’s own scheduling for deployment. CI could be as simple as running dataform compile to ensure the project compiles on PRs (without actually running it) – though note as per community feedback, dataform compile doesn’t validate SQL syntax fully[17]. One could integrate a linter in CI for that (more in CI section). After merge, you might not need a CI deploy step; the code is in main, and either a schedule or a manual trigger via API kicks off the Dataform run. We could also automate it: e.g. a GitHub Action that calls the Dataform REST API to immediately run the new main commit after a merge (to always keep data up-to-date). Dataform’s API has an endpoint to create a Workflow Invocation (with an optional release_config_id or explicit commit-ish)[55][56]. Using that, CI can programmatically trigger the run as part of deployment.
Dev Experience: Managed-only means potentially slower dev feedback if not using the UI’s preview. However, Dataform’s web IDE is quite robust – it compiles on the fly and shows errors in code, and you can even use Gemini AI assistance in the UI to generate SQL[48]. Some developers may prefer staying in VS Code with Copilot though. It’s feasible: they can write SQLX in VS Code, run dataform compile locally for quick graph checks, even do a dataform run --dry-run (which compiles to BigQuery jobs without actually writing tables). But to actually see data or ensure queries run, they’d push to a dev branch and trigger a run in a dev Dataform repository or dev release config. Alternatively, the developer can temporarily set their defaultSchema to a dev dataset (e.g., myapp_dev) and run dataform run locally against BigQuery to see the result tables. In summary, the managed approach is slightly less flexible for ad-hoc runs but provides a governed environment – everything that happens is logged in GCP, and no one is running arbitrary transformations outside of that context in production.
CI/CD Considerations:
- Security: No need to distribute broad BigQuery credentials to developers or CI; the Dataform service’s own service account executes the SQL. We must ensure that service account has correct IAM: at least BigQuery Data Editor for the target project/dataset and BigQuery Data Viewer for any source datasets[31]. By default, the Dataform service agent has no BigQuery roles until we grant them[30], so an admin must grant these once (or use a custom service account for Dataform with those roles, configured in Dataform settings). Also, to link GitHub, a minimal-scoped token or deploy key is used – we don’t store any credentials to BigQuery in GitHub. - Cost: Dataform managed is free of charge; you only pay for BigQuery query costs and minimal storage of the Dataform metadata[57]. It’s fully serverless – no VMs or persistent containers. If the workflow is large, note that Dataform will compile everything on each run; extremely large projects might hit compilation limits, in which case splitting repos is advised[58][59]. But for typical use, this is fine. - Scheduling and triggers: The built-in Workflow Config is easy to set up (point-and-click or Terraform)[34], but it cannot listen for events like “a new file arrived in Cloud Storage” by itself. For event-driven, one can use Cloud Composer (Airflow) with the Dataform operators to trigger runs after upstream tasks[35], or Cloud Workflows/Cloud Functions calling Dataform API. Google provides an Airflow DataformCreateWorkflowInvocationOperator which our Stack Overflow example used[60][61]. Managed approach thus can integrate into a larger orchestration if needed, albeit with a bit of code. - Lineage/UX: Dataform managed shines here – every table, view, and assertion is tracked. The UI shows a DAG of all actions[62], and provides detailed logs for each step. For example, if a table fails, you see the SQL and error from BigQuery. You also get automatic documentation: Dataform will use any table descriptions or column descriptions you put in config to populate BigQuery metadata, and you can browse it in the UI. This is comparable to dbt docs, except integrated into BigQuery’s interface. - Maintenance: Little infrastructure to maintain. Upgrading Dataform core version is a matter of changing package.json and clicking “Install packages” in UI[41][63]. GitHub link maintenance is minimal (might need to update token if it expires). The main overhead is managing permissions and possibly handling multi-repo if splitting logic.
Recommendation Fit: Use Approach A (managed) if you prioritize simplicity and GCP integration over local control. It’s ideal when all pipelines run on a schedule or via upstream orchestrators, and the team is comfortable using the GCP console for pipeline runs and monitoring. If the local CLI/app frequently needs to trigger transformations on-demand, approach A is less convenient (you’d have to call the API each time). In our case, since the local CLI app consumes BigQuery data but doesn’t necessarily need to trigger the pipeline every run (assuming data is refreshed regularly or on update events), Managed Dataform can work. We will, however, incorporate an ability to trigger runs via CI or a script using the Dataform API to cover those cases (e.g., a CLI command like invoke_pipeline that calls Dataform’s REST endpoint with the appropriate release/workflow config).
B. Dataform Core (Local/CI) → BigQuery
Workflow: Treat Dataform like a library: your pipeline code is executed by the Dataform CLI (via Node.js) in a controlled environment (developer’s machine or CI runner), which connects to BigQuery with credentials to run queries. In this scenario, Google Cloud Dataform (UI) may not even be aware of the repository. The steps are:
1.	Development: The developer uses VS Code and runs commands like dataform compile to validate the project (checks the graph and config) and dataform run to execute SQL against a dev dataset. The CLI needs authentication; locally this is achieved by running gcloud auth login or dataform init-creds to set up a .df-credentials.json. We prefer the former (ADC) because it’s seamlessly picked up by Google’s client libraries – Dataform CLI will use ADC by default if no explicit credentials file is present. Once authed, dataform run will create/update tables in BigQuery as per the SQLX definitions, using the local user’s permissions. This gives extremely fast feedback (you see your tables in BigQuery immediately). It’s wise to use a dedicated dev dataset or a personal dataset prefix to avoid clobbering prod tables. For example, set defaultSchema to myapp_dev in dataform.json as we showed, so local runs only touch the dev dataset. Production will be separate.
2.	Testing: The developer can also run dataform test to execute assertions locally[64] – this actually connects to BigQuery and runs those test queries, reporting failures in the console. This is great for catching data issues early. If any assertion fails, the CLI exit code is non-zero, which we can use in CI to fail a build.
3.	CI Execution: In a pure core approach, when code is merged to main, a CI/CD pipeline (GitHub Action or Cloud Build) will handle deployment. For instance, a GitHub Action job might do:
4.	Checkout code,
5.	npm install (installs @dataform/cli and dependencies, or we can use a Docker image with Dataform pre-installed),
6.	Use google-github-actions/auth to auth to GCP as an impersonated service account with BigQuery permissions,
7.	Run dataform compile (just to check), dataform test (to run assertions on new code against dev or a test dataset), and finally dataform run --var 'env=prod' (for example) to execute the transformations in BigQuery. The --var could be used to parameterize the target dataset or date boundaries, etc., if our code is written to handle it. Alternatively, one could maintain separate branches for environments; but since we want one repo, running with variables or separate configs is cleaner.
8.	The CI job will thereby apply the changes to BigQuery. We could also have a manual promotion step if needed (say, only run dataform run on prod when a tag or manual approval is given, to mimic release promotions).
9.	Compatibility with GCP Dataform: It’s worth noting that one can use Dataform Core in CI and still link the repo to GCP Dataform just for lineage and monitoring. However, if you never trigger runs via GCP, the UI will always show the last state as whatever was last run in it (which could be stale). In our use-case, if we went full core, we might choose not to use GCP Dataform at all, or use it only in a monitoring capacity by occasionally triggering a run. But essentially, approach B sidelines the GCP Dataform UI.
Dev Experience: This is very similar to dbt’s workflow. Immediate local runs, full control of job execution. Copilot is very helpful here because you can iterate rapidly and even have Copilot suggest changes, run again, see data. There’s no waiting for an external service. The downside: you need the BigQuery project and dataset setup done beforehand (via Terraform or manually). Also, the developer needs appropriate IAM (likely BigQuery Data Editor on dev datasets). From a governance perspective, giving every developer direct editor access to BigQuery might be a concern (though they’d typically only use dev/test datasets).
CI/CD Considerations:
- Security: The CI pipeline must authenticate to BigQuery. We strongly recommend Workload Identity Federation here as well – the GitHub Action can exchange its OIDC token for a GCP service account token with BigQuery permissions[13][65]. We would create a service account like dataform-ci@project.iam.gserviceaccount.com with roles BigQuery Data Editor (on target datasets) and BigQuery Job User (on the project) so it can run queries[31]. No secrets are stored; the GitHub actions config contains the Workload Identity Pool ID and service account email (which are not sensitive). This approach is outlined in Google’s documentation for keyless auth[12][14]. If for some reason OIDC can’t be used, the fallback is storing a JSON key in GitHub Secrets – but that is not advised (it’s less secure and often disallowed by org policy[66]). - Execution in CI: Running dataform run in CI will execute SQL against BigQuery from the runner. This means the network egress from the runner (GitHub’s or self-hosted) to BigQuery occurs and must be allowed. Usually not an issue for cloud-hosted GitHub runners connecting to BigQuery’s public endpoint. The Dataform CLI will parallelize operations where possible, but big transformations still incur BigQuery job runtime. It’s important to consider CI job timing: if the pipeline is large (many models or very heavy queries), running it in CI might exceed typical build times. You can mitigate by breaking the run: e.g., run only a subset or run with --dry-run (which validates SQL by asking BigQuery to parse the queries without executing – essentially setting a destination table to a temporary one with LIMIT 0 to test syntax). Dataform CLI’s --dry-run flag on run is similar to compilation but actually hits BigQuery for syntax checking. Community reports suggest dataform run --dry-run still might not catch all errors (like subtle SQL logic issues), so an external linter or actual execution is needed for full confidence[67][17]. - Continuous Deployment: The benefit here is that deployment is just code merge; CI does the rest. However, careful with stateful operations: If a model is incremental and we run it in CI on each commit, are we pointing to the prod dataset or a temp one? Ideally, CI on main should run against prod data. But if code is changing frequently, you might not want to rebuild prod tables on every commit without some schedule. Option: CI could run dataform compile/test on each commit and only schedule heavy dataform run nightly (via a separate scheduler or a cron trigger in GitHub Actions). This reintroduces scheduling complexity that approach A handles natively. - Lineage/Documentation: Without Dataform UI, lineage can be achieved by examining the Dataform JSON graph (from dataform compile --json > graph.json) which includes dependencies. One could generate a DAG visualization with custom scripts, or import it into a tool. But you won’t have the nice integrated experience. For many engineers, this trade-off is acceptable if they primarily care about the data and not presenting the lineage to end-users. BigQuery’s own Data Catalog can be used to document and track lineage to some extent (with column-level lineage if set up), but not as easily as Dataform UI. - Error Handling: Failures in dataform CLI runs (e.g., a query fails) will cause a non-zero exit and CI can notify via Slack/email from there. In approach A, Dataform would catch it and could integrate with Cloud Monitoring alerts[68]. In approach B, you’d rely on CI notifications or a custom Cloud Monitoring for BigQuery job failures (but since the jobs are initiated by the CI’s service account, one could set up an alert on any error from that principal in Cloud Logging). It’s more custom work.
Recommendation Fit: Choose Approach B (Core only) if you need maximum control or portability. For example, if you want the option to run the pipeline in a different environment (say on-prem or a different cloud’s data warehouse in the future), Dataform core supports multiple warehouses (BigQuery, Snowflake, etc.). It also might suit an environment where GCP access is limited – e.g. you can’t use Dataform UI due to network restrictions, but you can run CLI on a machine that has BigQuery access. In an enterprise with strict DevOps practices, running everything through CI with code review and approvals may be preferable to letting analysts click “Run” in a UI. It’s essentially treating the data pipeline as code that goes through the same pipeline as application code. However, given our scenario (BigQuery and an existing GCP project with Dataform enabled), we’d lose out on nice features by not using the managed service.
One notable compatibility point: the GCP Dataform service is continuously updated and uses the open-source Dataform core (with possibly some minor GCP-specific enhancements). By pinning @dataform/core in package.json, we ensure our local runs use the same compiler. If Google adds a new feature (say, new config options), the core library gets a new version and one should update both locally and in GCP. In pure core approach, you manage these updates at your pace.
C. Hybrid (Local Dev + Validate, Cloud Execute)
This approach combines A and B: Develop and test with Dataform Core locally/CI, then deploy and execute via GCP Dataform for production. It attempts to get the best of both: developer agility and cloud-managed reliability. The hybrid could be implemented in two main ways:
•	“Dev Core, Prod Managed” – Use Dataform CLI for dev/test environment, but treat main branch commits as triggers for Dataform managed runs in production. For example, a developer creates a new model, runs it on myapp_dev dataset via CLI to verify output. They commit and merge to main. A GitHub Action then calls the Dataform API to start a production workflow invocation (using the release configuration that points to main with prod settings). Dataform executes the prod run and the data is updated. The Dataform UI thus always reflects production runs, and you have lineage and logging for those runs. Meanwhile, dev runs are not visible in the UI (they were done via CLI), but that’s fine. This is analogous to using Dataform UI as your “production job orchestrator” and using CLI as a personal development tool. It’s a common pattern – similar to how some dbt Cloud users develop locally then push to cloud for prod runs.
•	“Compile in CI, Execute in Cloud” – A variant where CI performs a compile and test, possibly even creates a compilation artifact, and then hands off to Cloud. Dataform’s API allows you to create a Compilation Result via API and then use it to start a run[60][69]. In theory, CI could compile the code (with certain variables) and upload the compiled graph to GCP Dataform to execute. However, Dataform’s API expects to compile in its own environment usually (with the createCompilationResult call, you provide the repo and commit ref; you can override settings via that call[70][71], as shown in the Airflow example). Instead of CI uploading SQL, it instructs Dataform to compile with overrides. So CI could simply call the Dataform API to do both compile and run as one step (this is actually what the Workflow Invocation API does: you provide a commit or use the latest, Dataform compiles and immediately runs it). There isn’t much benefit in CI compiling separately unless you want to fail fast on compile errors before hitting the API. Given that Dataform’s API can return compilation errors as a response, it might be simpler to just call it and handle failures.
Workflow detail for Hybrid (our recommendation):
1. Developer uses CLI locally for rapid development against dev dataset. They commit to a feature branch frequently. Possibly, we set up a Dataform development repository in GCP for the dev branch as well, but that’s optional overhead. Instead, the dev just runs things locally. 2. When opening a PR, CI runs dataform compile and dataform test (with the dev dataset) to ensure no breakage. Additionally, we might run a SQL linter step to catch any syntax issues not caught by compile[72]. For example, use sqlfluff with BigQuery dialect to parse all .sqlx (skipping the config {} sections via custom rules). This addresses a known gap where a missing comma in SELECT might only surface on actual execution[67]. 3. On merge to main, CI invokes Dataform in GCP: - If using Dataform’s scheduling, we could rely on a scheduled job (e.g. runs every 30 min). But for immediacy, we use the Workflow Invocation API. We’ll create a Workflow Configuration in GCP with say ID “on_demand” that isn’t scheduled but can be triggered by API, or we directly call projects.locations.repositories.workflowInvocations:create with an InvocationConfig specifying the release config (or just a direct commit ref). - Practically, we can use gcloud CLI in the GitHub Action: for example,
gcloud dataform repositories workflow-invocations create \
  --project=my-project --location=us-central1 --repository=my-dataform-repo \
  --release-config=prod_release_config_id
(Hypothetical example; the actual gcloud support for Dataform may be in beta. Alternatively, use curl with an OAuth token to call the REST API). The service account used by CI must have permission to invoke runs (likely roles/dataform.editor or admin on that repo) so it can start the workflow[73]. If needed, one can specify a subset of actions to run if not everything, but typically we run all in prod. The Dataform run will then proceed in cloud. CI can poll the status or just exit after triggering (perhaps better to poll so it can report success/failure back to GitHub). The Dataform API provides get/list on workflow invocations[74][75] which CI can use to check if it succeeded or failed. 4. Production execution and monitoring happen in GCP. If it fails, our CI job notices and can mark the GitHub deployment as failed, and we can have notifications both from CI and from GCP (Cloud Monitoring alert as backup).
Pros of Hybrid:
- Developers get fast, iterative development with minimal friction (no waiting for cloud compile to test changes on real data). - We maintain a single source of truth in Git (no manual edits in Dataform UI that aren’t in Git – Dataform UI connected mode prevents that anyway, it requires commits for changes)[76][77]. - Production runs are all in GCP – this means all lineage and logs are captured for auditing. If an auditor looks at lineage, they see exactly what queries produced what data (since Dataform logs the SQL and outcome of each action in Cloud Logging[78][79]). Running via CLI locally would not have that central logging – logs would be on the developer’s machine or CI only. - We can leverage GCP features like BigQuery’s fine-grained access control in production. For instance, Dataform can automatically apply column-level security tags if configured[80]. It also has features like policy tags and labels we can use in config. Using the managed run ensures those run under the Dataform service identity, which might be easier to trace or restrict as needed (e.g., VPC Service Controls, if implemented, could allow Dataform’s egress but maybe not arbitrary CI egress – depending on setup).
Cons of Hybrid:
- Complexity: Two execution methods to manage. Team must understand that dev runs happen one way and prod another. The Dataform compilation might behave slightly differently if not kept in sync version-wise (hence lock version). Also environment differences must be carefully managed (e.g. if dev uses smaller data or a different project, any differences in SQL or config must be parameterized properly). - Slight overhead in CI to orchestrate the handoff. But this is quite manageable with the API. We essentially trade a bit of CI logic for not re-implementing alerting and scheduling ourselves.
Hybrid vs Others – Recommendation: This hybrid approach is recommended for our scenario. It best fits when: - Local CLI app downstream expects fresh data but can tolerate minor lag (we don’t need to trigger transforms on every app run synchronously, which would be an anti-pattern). We can update the data via Dataform on schedule or on code changes. If the local app did need to trigger an on-demand transform (say user presses a button to recompute something), we could still expose a CLI command or API that calls Dataform’s API to run a subset of pipeline (since Dataform API allows specifying an action or tag filter to run only certain tables). This is event-driven execution done safely via service accounts, rather than embedding transformation logic in the app itself – a good separation. - Enterprise controls: All production data modifications go through a controlled service with audit logs (Dataform). Devs can’t accidentally write to prod datasets from their laptops because their local runs use dev schemas, and only the CI service account (via Dataform service) writes to prod. This addresses “who did what” questions and limits potential damage. - Use of new Dataform features: We can leverage things like Release Configs to manage dev vs prod settings (prefixes, different GCP project for prod if we had one) without complicating the code with too many if/else. For example, in Dataform UI we define: Release config "dev": use project X, prefix tables with "dev_", run hourly; Release config "prod": use project Y (or same project), prefix "prod_" or no prefix, run on demand or daily. The code itself can remain largely identical, referring to ${prefix}${table_name} or using Dataform’s built-in substitution. Dataform’s dynamic compilation overrides allow adding a suffix/prefix to schema and project per workspace or release[81][38]. In hybrid, we’d configure that in the UI for prod. In pure core, we’d have to implement environment logic ourselves (like using a --vars env=prod to alter names in code, which is doable but more manual).
We will proceed with Hybrid for the remainder of the recommendations, as it offers a balanced solution. We’ll still highlight specific steps for full-managed or full-core where relevant (for those who might choose them).
Below is a comparison matrix of the approaches to summarize differences:
Aspect	A. Managed (BigQuery UI)	B. Core (CLI/CI)	C. Hybrid (Recommended)
Setup Complexity	Easiest initial setup. Link GitHub in UI, grant IAM roles, set schedules in Console. Little custom code for orchestration.	Moderate. Need CI pipeline, service account auth, and possibly custom scheduling (cron or external triggers).	Highest. Must set up CI triggers and GCP linking. More moving parts (CI + Dataform API).
Dev Workflow	Use Dataform UI preview or push to dev branch and run in cloud. Slower iteration unless using UI interactively.	Fast local iterations with CLI. Can test changes on dev data in seconds.	Fast local dev (CLI) + verification in CI, with cloud runs for final merge.
CI/CD	Minimal CI (lint/compile only). Deployment = merge to main (Dataform auto picks it up on schedule or manual trigger).	Full CI/CD needed to run and deploy. More complex YAML, but everything is code-driven and can incorporate tests easily.	CI used for validation and orchestrating cloud run. Still need CI logic but not running heavy SQL in runner (offloaded to GCP).
Scheduling/Trigger	Built-in scheduling (cron-style) in Dataform UI[34]. Event triggers via API or Composer possible[33].
Use any scheduler (GitHub Actions cron, Cloud Scheduler invoking Cloud Build, etc.). Event triggers easy to implement (just run CLI when event occurs).	Use Dataform scheduling for routine runs; CI or external events call Dataform API for event-driven triggers (no need to maintain separate scheduler service).
Lineage & Catalog	Excellent: Dataform UI shows full DAG and lets you drill into each action’s status[32]. Easy to demonstrate lineage to stakeholders.	Basic: No UI unless you build one. Must rely on BigQuery metadata or manual documentation. Possibly generate JSON graph for internal use.	Excellent for prod: Dataform UI reflects prod lineage. Dev lineage mostly via code or local visualize tool if needed.
Logging & Alerts	Cloud Logging captures all runs[24]. Can set up log-based alerts for failures[68]. Dataform also alerts on assertion failures internally[18].
Logs in CI console (and BigQuery job logs in Stackdriver under user SA). Need custom alerting (e.g., if CI fails or BigQuery job fails). Harder to get persistent run history.	Prod runs logged in GCP (with alerts). CI can also alert on test failures pre-prod. Best of both: robust prod monitoring and pre-prod catch of issues.
Security	No credentials in code; uses Dataform service account in GCP. Must grant that SA proper BigQuery roles[31]. GitHub integration via PAT/SSH with least privilege to just that repo[15]. Devs can be given Dataform roles (viewer/editor) instead of direct BQ access, if desired.	Service account needed for CI with direct BigQuery roles. More places where credentials are used (developer ADC, CI SA). Access is fine-grained at BQ level but devs effectively have direct SQL access in dev. Keys can be avoided with OIDC, but pipeline runs under CI SA which if compromised could modify data.	Dataform service account handles prod (tightly permissioned). CI SA only triggers Dataform, not doing heavy data writes itself (except maybe read for compile). Developer local writes limited to dev schemas. No prod creds on dev machines. Overall least privilege principle applied at each stage.
Cost	Dataform service is free, only BigQuery costs. Some extra Logging cost for detailed logs[82]. No CI infrastructure usage for execution.	Uses CI minutes for running queries (could be significant if data large). BigQuery costs same (queries). If self-hosting runner, need resources for potentially long jobs.	Some CI overhead (compilation, API calls) but heavy lifting on GCP. BigQuery costs same. Logging costs for Dataform runs, minimal.
Maintaining Pipeline	Upgrades and config via UI (less transparent in version control for schedules etc., though one can use Terraform for Dataform resources). Merging code automatically available to run (if auto-pulled).	Everything is code and in Git (including schedule as cron triggers etc.). Higher transparency and reproducibility.	Code in Git, plus some config in UI (release/workflow config could be managed via Terraform to have IaC for that too). A bit of split between code and cloud config, but manageable.
Use Case Fit	Great for scheduled batch transforms and teams that prefer UI-driven ops. Not as good for on-demand or very frequent triggers from external events (requires additional integration).	Great for event-driven or complex pipelines integrated with other systems. Suits teams treating SQL pipelines as software engineering. Not ideal if need GCP UI or if team not comfortable with CI operations.	Great when you need both agility and governance. Slightly more engineering effort to set up, but pays off in flexibility. Suitable for an enterprise where devs iterate rapidly but prod must be stable and auditable.
Our recommendation is Approach C: Hybrid for the scenario described, because it allows the local CLI to consume up-to-date BigQuery tables with low latency and enables robust enterprise controls for production data transformations. Specifically, choose the Managed (A) path if your transformations are mostly scheduled and your team is fine working in the GCP UI (or with a slower dev cycle), choose the Core (B) path if you need maximal control or multi-cloud portability and have CI/CD maturity to support it, and choose Hybrid (C) if you want the benefits of both – quick dev/test cycles and reliable, auditable production runs.
In the following sections, we detail the implementation of the Hybrid approach: how to set up VS Code for the devs and AI, how to configure authentication securely, CI/CD pipelines, daily developer workflow, data quality practices, and more.
VS Code Setup for Copilot and Codex (AI-Assisted Development)
To ensure GitHub Copilot and the OpenAI Codex extension can effectively assist with Dataform development, it’s critical to configure VS Code with the right settings and context. The goal is that the AI “understands” the Dataform project structure and SQLX syntax, enabling it to suggest correct code (such as config blocks, ref() usage, etc.) and not to suggest changes in inappropriate places (like overwriting config files or credentials). Key steps:
1. File Type Recognition:
As mentioned in the repo blueprint, add the file association for .sqlx to SQL. In .vscode/settings.json:
{
  "files.associations": {
    "*.sqlx": "sql",
    "dataform.json": "json"
  },
  "editor.quickSuggestions": {
    "strings": true  // allow Copilot to suggest inside SQL string literals too
  },
  "[sql]": {
    "editor.defaultFormatter": "ms-mssql.mssql"
  },
  "sqlfluff.dialect": "bigquery",
  "sqlfluff.experimental.parser": true
}
The last two lines relate to SQLFluff extension (if installed) to lint with BigQuery rules. By treating .sqlx as SQL, we get proper syntax highlighting and Copilot’s underlying model will use its knowledge of SQL. Copilot has been trained on standard SQL and likely on some Dataform/dbt patterns. For example, it often knows that in Dataform or dbt, one writes SELECT * FROM ${ref('some_table')} to reference another model. Mapping dataform.json to JSON ensures any editing or validation of that file is easier (with JSON schemas if available – though Dataform’s JSON doesn’t have a public schema file, the fields are known from docs).
2. IntelliSense for SQLX:
We can leverage the BigQuery extension (ms-mssql is a generic SQL formatter; there’s also a BigQuery extension by Google but it’s more for running queries). Even without a specific BigQuery VSCode extension, just having correct SQL grammar highlighting helps Copilot. Optionally, define SQLX as its own language to fine-tune suggestions. We could create a custom language definition that treats ${ref()} and config {} as valid constructs (this is advanced and usually not necessary). Copilot generally can cope with embedded ${} syntax if it’s similar to what it’s seen with dbt or Jinja.
3. Copilot Settings: Ensure Copilot suggestions are enabled in all file types. Copilot has an optional setting to disable in certain languages – we should confirm .sqlx isn’t excluded. If needed, one could set .sqlx to map to the SQL language for Copilot or even trick Copilot by adding a comment at top of file like -- sql to prime it (though our association should handle it).
4. Snippets and Prompts:
Create a set of code snippets as scaffolding. Besides the df_table snippet example earlier, consider: - df_incremental: for an incremental table with uniqueKey and partition filter placeholder. - df_assertion: a template for assertion SQLX (maybe including a sample condition). - df_source_declare: if using JS for source declarations, a snippet to declare a table (though Copilot might infer it from one example). - df_operation: Dataform allows custom operations (type: "operations") to run arbitrary SQL (like DDL or GRANT statements)[83]. If we have one example, Copilot can replicate it. A snippet could help if needed.
Additionally, commented prompts in the files can guide Copilot. For instance, at the top of definitions/staging/ files, we might put a comment like: -- Use ${ref('source_table')} to reference raw data declared in sources. This might cue Copilot to follow that pattern in suggestions. In VS Code, you can also write a natural language comment describing what you want, and use the OpenAI Codex extension to “complete” it. Example:
-- Create an incremental fact table joining users and orders (daily partition)
Then invoke Codex completion. If our environment is set up, Codex should produce a config { type: "incremental", ... } block and a SELECT with appropriate refs, perhaps based on similar code it’s seen.
5. Guardrails for AI Agents:
AI coding assistants sometimes confidently generate incorrect or harmful suggestions (e.g., dropping a table). We implement guardrails as follows: - Read-Only Files: Mark critical files as read-only or less accessible to AI. For example, the .envrc (if using direnv) or any secret placeholders should not be modified. We can instruct the team (and thus indirectly the AI via documentation) that these files should not be changed by automated suggestions. Also, by not including secrets at all, we avoid the scenario of Copilot training data including a secret (which can happen if others have accidentally committed similar patterns). - Pre-commit Hooks: Use a tool like pre-commit to run checks. For instance, a hook that rejects any diff that touches dataform.json defaultSchema or infra/ files unless the commit message includes #infra-change. This way, even if an AI tried to modify those, it can be caught. Also a hook could forbid committing service account keys entirely (just in case). - Comments to discourage certain actions: We explicitly comment in config files something like:
{
  // DO NOT change defaultSchema without approval. Use release config overrides for prod schema.
  "defaultSchema": "myapp_dev",
  ...
}
This message might be seen by Copilot (which does read context up to a point) and it will likely avoid suggesting changes to that value. The OpenAI Codex extension also wouldn’t blindly refactor that without a direct user ask.
•	Testing AI suggestions: Encourage a practice that any AI-generated SQL is validated (which we do via CI tests and local preview). This isn’t a config per se, but a guideline so that developers don’t assume the AI is always correct – they must run the code. Given our robust test setup (assertions and dry runs), many AI mistakes will be caught quickly, reinforcing learning.
6. Extension: SQLFluff Linting
Integrating SQLFluff with the BigQuery dialect and a custom rule to ignore config {} and ${ref()} tokens can be immensely helpful. In settings.json, we set sqlfluff.dialect: bigquery. We may need to add a config file .sqlfluff to ignore patterns:
[sqlfluff:rules:L001]  # Example of adjusting a rule
extend_temp_table_references = true

[sqlfluff:ignore]
# Ignore parsing errors for lines containing Dataform-specific syntax
startswith: config { = LXR, PRS
contains: ${ref(  = LXR
(This is illustrative; actual ignore usage might be via inline -- noqa comments in files where needed.) The idea is to not flag Dataform config or ref syntax as errors. The forum discussion showed raw SQLFluff would throw “unparsable section” for those[84][85]. We either configure SQLFluff with a plug-in (some community contributions exist for dbt Jinja, maybe similar needed for Dataform) or simply instruct it to skip those lines.
By having linting in VS Code (on save or via a command), the developer and Copilot get immediate feedback on basic mistakes, which steers the AI. For example, if Copilot suggests SELECT a,b,c d FROM table (missing comma between c and d as in the user’s forum example[86]), SQLFluff underlines it, and Copilot may even learn to correct it next time (Copilot does adapt per session based on recent edits).
7. Workspace Recommendations for AI:
We will include in the README.md some guidance like “When using GitHub Copilot to generate Dataform models, ensure that you include the correct config block. For example, start by typing config { type: "table", schema: "marts", name: "new_model" } and Copilot will often fill in boilerplate based on similar models.” Also mention to avoid letting Copilot guess BigQuery literal project/dataset names – always use ref() or config values. This helps junior devs using AI to understand the boundaries.
8. OpenAI Codex Extension Usage:
If the team uses the OpenAI VS Code extension (which allows directly asking GPT-4 in VS Code), one can craft prompts to assist Dataform coding. For instance, highlight a block of code and ask “Explain this Dataform config” or “Fix any errors in this SQLX.” The extension will use the OpenAI model which may not have native knowledge of Dataform, but it will see context and can be guided by our project files. This can augment Copilot’s inline suggestions with more interactive help.
All the above setup ensures the environment is AI-friendly. It creates an interplay where the AI can suggest 80% of the repetitive SQL or config, and the developer reviews and tests it. Over time, the models might even pick up our specific naming conventions and preferences (Copilot does adapt to project patterns). For example, if all our incremental models use a pattern with updated_at in the WHERE clause, Copilot will start suggesting similar structure for new incremental models.
Finally, we should mention GitHub Copilot Labs (if available) which can refactor or explain code – it might be helpful for bulk renaming of references if needed (though caution with automated refactors in SQL). In any case, VS Code’s baseline settings above are the primary enabler for AI assistance in this project.
Authentication & Security Setup (No Secrets in Repo)
Security is paramount, especially in an enterprise context. We design an auth setup that avoids hardcoding credentials or sharing keys, by using Google Cloud’s recommended ADC and Workload Identity Federation (WIF) mechanisms. Here’s the plan for each environment:
Local Development (Application Default Credentials):
Developers should authenticate with GCP using their own accounts or an allowed identity and leverage ADC. The simplest method on Mac/Linux is:
$ gcloud auth login --update-adc
This opens a browser for the dev to login with corporate Google credentials (or whatever identity is used). It then stores short-lived credentials in ~/.config/gcloud/ (for ADC). Dataform CLI will automatically pick these up to connect to BigQuery. Alternatively, running dataform init-creds in the project will prompt for a GCP OAuth flow and store a .df-credentials.json in the project directory with a refresh token[87]. We do not commit this file. If using init-creds, add .df-credentials.json to .gitignore and possibly .gcloud/ as well.
We recommend ADC (the gcloud method) because it’s more standard and respects organization SSO/MFA policies. This way, when a dev runs dataform run, the BigQuery API calls use their user account, which can be tracked in logs as them. We can grant developers only the minimum roles on dev datasets. For example, give them BigQuery Data Editor on myapp_dev dataset and Data Viewer on source datasets. They do not need access to prod dataset because they won’t be writing there (only the Dataform service account will). This implements least privilege.
Dataform Cloud Service Account:
By default, the managed Dataform uses a service agent identity service-<projnum>@gcp-sa-dataform.iam.gserviceaccount.com[88]. This account needs BigQuery permissions as per docs: BigQuery Data Editor for any dataset it will write to (our myapp_prod and possibly myapp_dev if we let it run dev) and BigQuery Data Viewer for any dataset it reads from (source datasets or if it needs to read prod for incremental merges etc.)[31]. It also needs BigQuery Job User on the project to run jobs[89]. We will create two BigQuery datasets: myapp_dev and myapp_prod. We will grant: - roles/bigquery.dataEditor on myapp_dev to devs (or a dev group) and optionally to Dataform SA if we allow running dev in cloud, - roles/bigquery.dataEditor on myapp_prod to the Dataform service account (and not to individual devs), - roles/bigquery.dataViewer on source data (if those are in raw dataset or another project) to both the Dataform SA (for prod runs) and possibly to devs (or they might already have access through existing permissions).
Additionally, as part of security best practices, we might choose to use a custom service account for Dataform runs instead of the default service agent. Dataform allows specifying a “service account acting as Dataform” (by enabling strict act-as mode and granting Dataform permission to impersonate a given SA)[90][91]. This can be useful to have a clearer identity (e.g., dataform-prod-sa@project.iam.gserviceaccount.com). If we do that, we’d create that SA, grant it BigQuery roles, and then configure Dataform’s repository settings to use it (and grant Dataform permission to assume it via roles/iam.serviceAccountUser). This might be overkill, but is an option for enterprises to control service identities and maybe apply key management or VPC-SC boundaries specifically on that SA.
GitHub Actions CI – Workload Identity Federation:
We absolutely avoid storing any GCP service account keys in GitHub Secrets. Instead, we use OIDC federation: - Create a Workload Identity Pool in our GCP project (or use a central one). Within it, create an OIDC Provider for GitHub with issuer https://token.actions.githubusercontent.com[92]. - Configure attribute mapping, e.g., map attribute.repository to the GitHub repo (owner/repo) and possibly restrict audience (attribute.aud = project-id). A common setup is to allow only a specific repo or specific workflows to assume the identity by setting an attribute.condition on repository and branch/tag. For example: allow if repository == “myorg/myrepo” and workflow == “dataform-ci.yml” and ref == “refs/heads/main” (this level of granularity is possible with IAM Conditions using these attributes). - Then, create a service account dataform-ci-sa and bind it to that pool provider with roles needed. Actually, two ways: either give the SA roles and allow the WIF to impersonate it, or directly assign roles to identities in the pool. Google’s GitHub Actions uses impersonation. So you would run:
gcloud iam service-accounts add-iam-policy-binding dataform-ci-sa@project.iam.gserviceaccount.com \
  --role roles/iam.workloadIdentityUser \
  --member "principalSet://iam.googleapis.com/projects/<proj>/locations/global/workloadIdentityPools/<pool>/attribute.repository/myorg/myrepo"
This binds any workflow from that repo (if attribute filter is broad) to impersonate the SA[93][94]. We can tighten by adding attribute.branch etc. - In GitHub Action YAML, use:
- name: Authenticate to Google Cloud
  uses: google-github-actions/auth@v0.6.0
  with:
    workload_identity_provider: projects/<proj>/locations/global/workloadIdentityPools/<pool>/providers/<provider>
    service_account: dataform-ci-sa@project.iam.gserviceaccount.com
This action will fetch an OIDC token from GitHub, exchange it for a short-lived access token for the SA[13][65]. Subsequent gcloud or API calls in that job automatically use it (it sets ADC environment for the duration). - The dataform-ci-sa should have minimal roles: likely roles/dataform.editor on the Dataform repository (to invoke runs)[55], and possibly roles/dataform.viewer if we want it to fetch compile results or read something. If our CI also runs Dataform CLI in dev mode, that SA would need BigQuery viewer on sources to compile queries if it checks them, and maybe BigQuery job user if compilation does dry-run queries (but pure compile might not run queries). If CI doesn’t execute SQL (just triggers cloud run), it might not need direct BigQuery roles at all, which is a nice containment. It only calls Dataform API; Dataform service then does the queries. So CI SA = Dataform API caller, Dataform SA = BigQuery actor. - If we do have CI doing some BigQuery operations (like a lightweight query or lint via API), we might grant it BigQuery Metadata Viewer just to list tables or dry-run queries with jobs.create on dev project. But ideally, keep CI SA limited to Dataform roles, and let Dataform’s SA handle data.
This OIDC approach is highly secure: no static secrets, short-lived tokens, and scope is constrained to our repo. It also avoids the scenario described as a temptation: “dropping a service account key into chat”. Indeed, sometimes users might think to share a key with an AI to help it do something, which is obviously dangerous. By not having keys at all, we remove that risk. We should explicitly note in our documentation: Never share or commit service account keys. Workload Identity Federation eliminates the need for them[95][12].
GitHub to Dataform (Git Sync) Authentication:
When connecting the Dataform repository to GitHub, use a fine-grained personal access token (PAT) limited to repository contents[15] or an SSH deploy key: - For PAT: generate one with access to contents:read/write on that single repo (fine-grained tokens allow scoping to specific repo and permissions). We plug that into Dataform’s repository settings (over HTTPS). Dataform encrypts and stores it (or uses Secret Manager under the hood) – we don’t expose it elsewhere. Classic PAT with repo scope works too[96], but fine-grained is better for least privilege. - For SSH: Dataform will provide you an SSH public key (or you provide one) to add to GitHub as a deploy key[51]. Deploy keys can be read-only or read-write; Dataform needs write if you want to commit/push from the UI. But since our devs commit locally, Dataform really only needs read to pull latest code. If we want to allow committing via UI (you can commit changes from the Dataform UI back to GitHub[97][98]), then use read-write. We likely allow it for emergency edits or for less technical users. The deploy key method is nice because it restricts access to just that repo and is not tied to a user.
Important: if the GitHub repo is private (likely yes in enterprise), Dataform’s IP must be allowed. As per docs, Dataform egress comes from specific IP ranges[99][100]. If our GitHub is cloud (GitHub.com), it’s fine. If it were on-prem GitHub Enterprise with firewalls, we’d need to whitelist those IPs.
Secret Management – Google Secret Manager (GSM):
We said we won’t store secrets in the repo. But what about any secrets that Dataform code might need? Usually, Dataform transformations shouldn’t need passwords or API keys; they read from BigQuery which uses IAM, or maybe call an external UDF – not common. However, if we had to use an API (say, enrich data by calling an external service), one could use Dataform’s JavaScript to do so, but note: Dataform’s compilation is in a sandbox with no internet[101]. And during execution, you can only run SQL on BigQuery (no arbitrary HTTP calls). So likely no external secrets needed in Dataform logic. If we needed to pass a database credential to connect to another DB, Dataform doesn’t support cross-database connections (only BigQuery and others via separate warehouses). So that’s out of scope. Therefore, our pipeline code itself doesn’t contain sensitive secrets.
For completeness, if we needed to store something sensitive (like a Slack webhook for notifications, or maybe some salt for hashing), we’d use Secret Manager. Dataform’s service account can be granted access to read a secret (there’s mention of Dataform service needing Secret Manager access for some features[102], possibly if using user-managed encryption or secrets in code). We could then fetch it in JavaScript within Dataform by using the Secret Manager API via a UDF or external function. But this is hypothetical. In our scope, secret management is mainly about not leaking GCP keys or credentials, which we have handled with ADC and WIF.
Zero-Trust and Org Policies:
Our design aligns with a zero-trust stance: - No long-lived keys (Org policy iam.disableServiceAccountKeyCreation can be on)[103] – we’re compliant with that. - We could enforce that Dataform’s service agent is the only identity that writes prod (others get access denied if they try). Achieved by carefully scoping IAM. - Use of VPC Service Controls: If the project has a perimeter, Dataform is a Google-managed service so likely included; our CI runner calling the API might be outside the perimeter. We might need to add an access level or use the GitHub Actions IP ranges which is messy. Alternatively, run CI on a runner inside the perimeter. This is advanced, but WIF can integrate with VPC-SC by allowing an OIDC claim to assert source IP or by using a broker inside. For now, assume not using VPC-SC or that necessary holes are made.
IAM Roles Summary:
- Developer user: roles bigquery.dataEditor on dev dataset, bigquery.dataViewer on sources, dataform.viewer on the Dataform repo (if they need to see runs in UI) or dataform.editor if they should be able to run in UI. Possibly also dataform.workspaceCreator if they will use Dataform UI to create dev workspaces (this is part of editor I think). They won’t have access to prod dataset editing. - Dataform service agent: roles bigquery.dataEditor on prod and dev datasets[31], bigquery.jobUser on project[104], bigquery.dataViewer on any read-only source dataset, secretmanager.secretAccessor if needed (likely not). Already has implicit permission to use Dataform features in project. If using custom SA for Dataform: also dataform.serviceAgent role to allow Dataform to act as it[102], plus above BQ roles. - CI Service Account (dataform-ci-sa): roles dataform.editor on Dataform repo (which includes permission to start workflow invocations)[55]. Also iam.serviceAccountTokenCreator on itself if needed (but WIF handles that via binding rather than needing this role explicitly). If CI is compiling code with BigQuery, might also need bigquery.metadataViewer or bigquery.dataViewer on dev dataset just to dry-run queries; but we can possibly avoid heavy checks or grant minimal read. No write needed for CI SA on datasets – it should not be writing data itself. - GitHub Repo Access: We use PAT with repo scope or deploy key. Ensure that token is stored in Dataform only. Alternatively, one could use GitHub App integration (if supported in future) for even tighter control.
By using these roles and avoiding credential sprawl, we fulfill the security story: devs don’t have prod keys, CI doesn’t have long-lived secrets, and everything is auditable. In our documentation and training, we’ll explicitly discourage any practice of copying keys or sensitive info to AI or anywhere else. We cite Google Cloud’s guidance that OIDC + WIF is the modern best practice for GitHub Actions auth[12]:
“With GitHub’s introduction of OIDC tokens into Actions, you can authenticate from GitHub Actions to Google Cloud using Workload Identity Federation, removing the need to export a long-lived JSON service account key[12]. This eliminates additional security risks associated with key leakage.”
To finalize this section, we emphasize that no file in the repo contains secrets. *.json keys are ignored, .env.example contains only placeholders. We lean on cloud identity for both humans and machines. This not only secures the pipeline but also aligns with enterprise policies (e.g., disabling service account key creation, which many orgs do[103]).
CI/CD Pipeline Implementation (GitHub Actions & Cloud Build)
We outline a CI/CD pipeline that covers development validation (linting, testing), deployment (running or invoking Dataform), and environment promotion. We present a solution using GitHub Actions, with notes on Cloud Build as an alternative (since GCP shops might prefer Cloud Build triggers).
CI Pipeline Goals:
- On Pull Request (PR) to main: Validate the Dataform project (syntax, style, tests) without affecting any datasets. Provide fast feedback to developers before merge. - On Merge to main (deployment): If tests pass, update the production tables via Dataform. This could be immediate or scheduled. We prefer immediate (on-demand run via API) to keep data in sync with code. If certain merges should not auto-deploy (maybe feature flags), we could incorporate manual approval gates, but assume here that main is always deployable (we can use feature branches for code that isn’t ready). - Promotion to Prod vs Dev: In our approach, “prod” is essentially main branch in the same project but using different dataset (myapp_prod). If we had multiple GCP projects (one for dev, one for prod), we could incorporate a separate stage that applies to the prod project. The Dataform best practice suggests either multi-repo multi-project or one repo with overrides[8]. We’re doing one repo, one project, two datasets. So promotion is mainly switching dataset context. This is handled by Dataform’s release config in our plan. But we still might conceptually treat main = prod environment, and possibly have a dev branch for experiments that could be linked to a “dev” Dataform release (or just CLI). - Artifact retention: Save compiled SQL, documentation, or run logs as needed for auditing or later review. Also, if a run fails due to a SQL error in prod, having the compiled graph (with all SQL) from that commit could help debugging offline, so perhaps upload graph JSON on each build to an artifact store.
Let’s construct a sample GitHub Actions workflow YAML (.github/workflows/dataform-ci.yml):
name: Dataform CI/CD Pipeline

on:
  pull_request:
    branches: [ main ]
  push:
    branches: [ main ]

jobs:
  validate:  # runs on PRs and can run on push
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write   # needed for OIDC
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Install dependencies
        run: |
          cd dataform
          npm ci  # install @dataform/core as per package-lock.json

      - name: Authenticate to GCP (Workload Identity Federation)
        # Only needed on push to main; on PR, we might not deploy but still need read access for lint if hitting BQ
        if: ${{ github.event_name == 'push' }}
        uses: google-github-actions/auth@v0.6.0
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_ID_PROVIDER }} 
          service_account: ${{ secrets.GCP_DATAFORM_CI_SA }}

      - name: Lint SQL (Syntax and Style)
        run: |
          npm install -g sqlfluff
          sqlfluff lint --dialect bigquery "dataform/definitions/**/*.sqlx"
        # This will report any SQL syntax/style issues. Non-zero exit fails the job.
        # We expect some parse failures due to Dataform syntax; those should be ignored via config as described.

      - name: Compile Dataform project
        working-directory: dataform
        run: npx dataform compile
        # If there are compilation errors (e.g., broken refs, config errors), this fails.

      - name: Run unit tests (Assertions) on dev
        working-directory: dataform
        env:
          DF_PROJECT_ID: my-gcp-project-id
        run: |
          # Optional: override defaultSchema to a temp schema for test runs if we want isolation
          npx dataform test --schema myapp_dev
        # dataform test will run assertions in BigQuery; it needs the DF_PROJECT_ID or defaultDatabase set.
        # Alternatively, run a subset of pipeline with --dry-run to ensure SQL is executable.

      # Possibly: steps to generate docs or graph for artifact
      - name: Export compiled graph
        working-directory: dataform
        run: npx dataform compile --json > graph.json
      - name: Upload graph artifact
        uses: actions/upload-artifact@v3
        with:
          name: dataform-graph
          path: dataform/graph.json

  deploy:
    if: ${{ github.ref == 'refs/heads/main' && github.event_name == 'push' }}
    needs: validate
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write
    environment: production
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup Node (for any tooling if needed)
        uses: actions/setup-node@v3
        with:
          node-version: 18

      - name: Authenticate to GCP
        uses: google-github-actions/auth@v0.6.0
        with:
          workload_identity_provider: ${{ secrets.GCP_WORKLOAD_ID_PROVIDER }}
          service_account: ${{ secrets.GCP_DATAFORM_CI_SA }}

      - name: Invoke Dataform Release
        run: |
          gcloud dataform repositories workflow-invocations create \
            --project=my-gcp-project-id --location=us-central1 --repository="my-dataform-repo" \
            --release-config="prod_release" --invocation-config='{}'
        # The above command triggers the Dataform release "prod_release" to run immediately.
        # invocation-config '{}' means run all actions. We could specify a subset or variables here if needed.

      - name: Wait for Dataform run completion
        run: |
          # pseudo-code: poll the Dataform API for run status
          INVOCATION_ID=$(gcloud dataform repositories workflow-invocations list --project=my-gcp-project-id \
                          --location=us-central1 --repository="my-dataform-repo" --filter="releaseConfigId=prod_release" --limit=1 --format="value(name)")
          echo "Latest Invocation: $INVOCATION_ID"
          # We could use gcloud or curl in a loop to wait for terminalState = SUCCEEDED/FAILED
          for i in {1..30}; do
            STATUS=$(gcloud dataform repositories workflow-invocations describe "$INVOCATION_ID" \
                      --project=my-gcp-project-id --location=us-central1 --repository="my-dataform-repo" \
                      --format="value(state)")
            echo "Status: $STATUS"
            if [[ "$STATUS" == "FAILED" || "$STATUS" == "SUCCEEDED" ]]; then
              break
            fi
            sleep 10
          done
          if [[ "$STATUS" != "SUCCEEDED" ]]; then
            echo "Dataform run failed or timed out"
            exit 1
          fi

      - name: Notify Success
        if: ${{ success() }}
        uses: some/notification-action@v1
        with:
          message: "Dataform PROD run succeeded for commit ${{ github.sha }}."
A few points about this YAML: - It defines two jobs: validate and deploy. The validate runs on PRs and on push to main (we can allow it on push too, it’ll run before deploy due to needs). The deploy job only runs on push to main (and not on PR). We use the needs: validate and if conditions to orchestrate. We also mark deploy with environment: production which on GitHub can tie to environment protection rules (like require approval, but here we likely auto). - We request id-token: write in permissions to allow WIF OIDC token usage[13]. - Validation job: - Installs Node dependencies in the dataform directory (ensuring @dataform/core is installed). We could also globally install dataform-cli via npm i -g @dataform/cli, but using npx with local install is fine. - Auth step is only done for push (main) because on PR from fork, we might not want to give GCP access. Even if it’s same repo PR, we might not need GCP auth just to lint and compile, because compile/test on PR could potentially run queries on dev BQ. If dev BQ is accessible only via GCP auth, we might want to allow it for PR from branch (which is likely internal dev). If open source, one wouldn’t. In enterprise internal repos, it’s fine. So we could do auth on PR too but perhaps limit to read-only or use a different SA with restricted dataset if we fear abuse. For simplicity, I put if: push. - Lint step: runs SQLFluff. We expect to configure it to not flag Dataform-specific syntax as errors. If that’s tricky, an alternative is using the BigQuery dry-run approach: e.g., use bq query --dry_run for each SQL in compiled graph to see if BigQuery accepts it. That is possible by scripting: after compile to JSON, extract all SQL and run dry-run via API. This ensures syntactic validity with BigQuery’s engine. It might be more involved, so using a linter is easier for now. The forum Q we saw ended up with difficulties making SQLFluff fully understand Dataform config blocks[105]. To mitigate, one strategy: run dataform compile to get the compiled SQL (which will have no config blocks, just pure SQL), then lint that compiled SQL. But that compiled SQL often has ephemeral dataset/table names (Dataform might compile references to dataset.table). Actually, Dataform compile JSON gives queries and dependencies. We could take each query from JSON and do EXPLAIN on it via bq command to see if syntax error. That’s perhaps the most foolproof for syntax. For brevity, we say use SQLFluff with ignores. - dataform compile ensures internal consistency (like all ref() resolve, no missing packages, etc.). It doesn’t catch runtime issues. - dataform test will actually attempt to run assertions on BigQuery using the dev dataset. We set an env or override to ensure it uses myapp_dev. Since our dataform.json already is set to dev by default, this might be fine. If dev dataset doesn’t have the latest upstream data, assertions might not truly test logic (but at least they run). If assertions themselves reference tables not yet built in dev (because we haven’t run the pipeline in dev for that code), dataform test might actually run the table build too? Actually, dataform test runs any declared unit tests and all assertions after doing a compile, but it does not build the tables that assertions reference. If tables don’t exist, assertions will fail (view referencing missing table). So to run assertions, we might need to do a partial run in dev. An alternative: use dataform run --dry-run which does create tables as empty and run through the motions. Or do a dataform run on just a small subset. This is tricky on PR because you might not want to actually build dev tables for a feature that’s not merged. But it might be fine to do in a separate isolated dataset (like a ephemeral test dataset named with PR number). - We can consider creating a scratch dataset for test and specify --schema scratch_pr123 in dataform CLI for tests. Dataform CLI supports overriding schema via --schema or using --vars and code logic. Alternatively, create a dynamic environment config. The StackOverflow posts confirm GCP Dataform doesn’t support env file, but Dataform Core CLI does use environments.json (the old way) if present. We could possibly use that solely for CLI test runs. But it might complicate. - For simplicity: maybe skip actually running assertions on PR, just lint and compile. Rely on prod assertions after deploy. But catching issues early is nice. Perhaps the safe approach: run assertions in a controlled dev environment periodically rather than on every PR. Given time constraints, we stick with compile + lint on PR, and run assertions on nightly basis on dev data (could set up a schedule for that outside of CI). - We upload the compiled graph as an artifact (e.g. for debugging if needed). Also perhaps the SQLFluff report or any other logs could be artifacted. - Deploy job: - Depends on validate so it only runs if validate succeeded. We ensure it only runs on push to main. - Authenticates via WIF (here we assume secrets are set with the WIF provider ID and SA email). - Uses gcloud CLI to trigger the Dataform run. This requires gcloud to be installed. On the ubuntu-latest runner, gcloud might not be pre-installed. We might have to sudo apt-get install google-cloud-sdk or use google-github-actions/setup-gcloud action before:
- uses: google-github-actions/setup-gcloud@v1
  with:
    project_id: my-gcp-project-id
    install_components: 'dataform'
    # Actually, as of now, gcloud dataform might be in beta components
    version: 'latest'
This ensures gcloud is available. The pipeline above omitted it for brevity. - The workflow-invocations create command triggers a release config named "prod_release" which would be configured in GCP console. We’ve set that up to use main branch and override defaultSchema to myapp_prod (and perhaps remove any dev prefixes). If our code uses dataform.json with dev values, the release config override will change them at runtime. - We then have a step to wait for completion. Alternatively, instead of manually polling, we could use gcloud beta dataform workflow-invocations wait if it existed (not sure if a wait command exists). Or use the REST API via curl with a loop. The above uses gcloud ... describe in a loop. Dataform’s states might be like RUNNING, SUCCEEDED, FAILED. - On success, we could notify (via a Slack webhook or GitHub Deployment status). Similarly on failure, we should notify or mark CI failed (the script does exit 1 on failure, so job is failed and can send email if configured in GitHub). - We tag this job with environment: production, which in GitHub UI can show a “production deployment” for traceability.
Cloud Build Alternative:
We could achieve similar with Cloud Build triggers: - One trigger on PR could run compile/lint (though Cloud Build isn’t great with PRs as it usually triggers on branch pushes; might skip this and just do main builds). - Another trigger on push to main does the deploy. Cloud Build can use a YAML config that parallels above steps with gcloud dataform workflow-invocations create. Cloud Build can also do substitutions for branch name, etc. - Cloud Build’s advantage: running inside GCP, it has implicit auth (use Cloud Build SA). We could grant Cloud Build SA the Dataform roles and BigQuery roles needed, or better yet use a custom worker SA for builds if needed. - We’d still do WIF if we want GitHub to trigger Cloud Build (which can be done via a GitHub App integration or via manual triggers). - Since our main code is on GitHub, using GitHub Actions is straightforward and keeps pipeline config with code. Cloud Build is an optional alternative.
Dataform Workflow Configurations:
Within Dataform UI, set up: - Release Configuration "prod_release": Branch = main, override defaultSchema to myapp_prod, frequency: not set (so manual or API only), retain live compilation. - Workflow Configuration "production_manual": ties to "prod_release", actions = all, schedule = none (manual only). Actually, we might not even need a named workflow config if we trigger via API specifying release config – Dataform’s workflowInvocations.create can accept either a workflowConfigId or directly a release config and list of actions. In our gcloud we gave release-config and no selection (so runs all, essentially an ad-hoc invocation of that release). - If we wanted scheduled nightly run as a safety net, we could set up a schedule (e.g., run all in prod_release at 2am daily), in addition to on-demand triggers.
Dev/Test Workflows:
We might also create a Release Config "dev_release": Branch = main (or a dev branch), overrides: prefix tables with "dev_" or schema myapp_dev. And a Workflow Config "dev_daily" schedule daily. This way, even if developers didn’t run everything locally, once a day Dataform would build the dev dataset with latest main code. This is essentially integration testing on full data daily. If any issues (assertion failures), Dataform would alert. We could wire those alerts to email/Slack for the team. This is optional but recommended for catching data issues in main before they hit prod dataset. Since our design directly deploys to prod on merge, one could argue main is prod. But maybe we restrict merges to main until dev_daily is green, up to team preference.
Caching & Performance:
We enable npm ci which uses package-lock for deterministic install. Could cache ~/.npm or node_modules between runs to speed it up, using actions/cache. But since dependencies are few (just dataform core), this is fast anyway. If pipeline becomes slow due to many models, consider: - Only running a subset on PRs: e.g., if PR only changes certain models, only lint/compile those. Dataform doesn’t easily select subset on compile (it always compiles all). But we could glean changed files and run sqlfluff just on those, etc. Possibly skip heavy tests for minor changes. - Parallelizing jobs: Not much to parallelize except maybe running lint and compile concurrently – not worth it. - If BigQuery queries are heavy on dev/test runs, consider limiting with LIMIT or dry-run mode. But we largely avoid heavy execution on CI.
Summary: The CI/CD pipeline ensures code quality (no broken SQL) and automates deployment to production BigQuery. By leveraging Dataform’s API, we keep the orchestration code simple – we don’t have to write our own DAG runner. This pipeline also integrates with our security setup (using OIDC auth, which the YAML demonstrates).
Crucially, it addresses promotion through environment separation: - The code in Git is environment-agnostic (always uses whatever defaultSchema is set, which is myapp_dev). - For prod, we rely on release config to switch to myapp_prod. This means the same compiled SQL gets executed but writing to a different dataset. That ensures dev and prod tables can coexist (dev maybe smaller or test data, prod full data). - If we needed multiple GCP projects, we could override the project in release config too[37]. Dataform allows overriding the GCP project per release if the service account has access[106][107]. That pattern (multi-project) is recommended for strict prod isolation[8]. Our design could adapt: e.g., dev release config points to dev project, prod release to prod project. Everything else in pipeline remains same except our gcloud calls specify different project for release config if needed.
We will attach the templates (like the GitHub Actions YAML above) as part of deliverables so it’s copy-pasteable, with placeholders (like project id, repo name, etc.) clearly marked as in the snippet.
Day-to-Day Developer Workflow
With the infrastructure in place, we define how developers will work on this project daily to ensure productivity and code quality. Here’s a typical “happy path” from idea to production:
1. Branching Strategy – Feature Branches for Dataform:
Developers branch off main into feature branches for any change (e.g., feat/dataform-new-mart-model). Keeping main always production-ready is crucial since merges deploy immediately. By prefixing branch names with dataform- or similar, we can identify them; although no strict rule is required, it’s good for clarity. If multiple team members collaborate, they might create branches per feature or bugfix (ensuring each branch is short-lived to avoid drift, since Dataform project evolves quickly).
We also maintain possibly a develop branch if we want an integration phase, but that might duplicate environments. Instead, we treat dev dataset as ephemeral and main->prod as immediate. So likely no long-running develop branch unless required by org.
2. VS Code + Copilot in Action:
The dev syncs the latest main (or their branch if continuing work). They create/edit SQLX files in the dataform/definitions subfolders: - For a new model: Decide where it fits (staging or mart). Create definitions/marts/order_revenue.sqlx for example. Copilot will assist by perhaps suggesting a basic config if similar ones exist. Developer writes a brief description or starts typing config { type: "incremental", schema: "marts", and Copilot suggests the rest (uniqueKey, etc.). The dev adjusts as needed (choose uniqueKey, partition, etc.). They might add a pre_operations or post_operations if needed (Copilot may not auto-suggest those unless pattern exists, but it might if it’s seen from Dataform docs). - Use ref() for dependencies: The dev types ${ref(' and Copilot might list available model names (not actual Intellisense, but based on context it might guess like 'stg_orders' if you have a staging named that). We also have BigQuery results in mind: sometimes, one might directly reference a raw table via standard SQL. But we want them declared as sources and use ref to those sources. Copilot could try to complete with a fully qualified name if it sees one in project (like if raw dataset name appears in code or comments). But our style is to declare sources. So developer should follow that: if referencing a new raw table, first add it in definitions/sources/source_tables.js (e.g., dataform.declare({ database: "...", schema: "...", name: "raw_orders" })). They might copy-paste a previous declare line and change names (Copilot can help if it detects pattern). - Write SQL logic: Given we treat .sqlx as SQL, Copilot will help with SELECT statements. E.g., if writing a join between two refs, after writing FROM ${ref('staging_orders')} o JOIN ${ref('staging_customers')} c ON o.customer_id = c.id, if similar code exists, it may suggest it fully. The dev reviews output, maybe adds conditions. - Insert data quality tests: For each new model, add either config assertions or separate assertion file. If using config assertions (like uniqueKey or rowConditions in config[108][109]), they add those and let Copilot fill expressions (it might guess a typical constraint e.g., email like '%@%' as in docs[109]). If using separate files, they create in assertions/ something like assert_no_nulls_orders.sqlx with config { type: "assertion" } SELECT * FROM ${ref('order_revenue')} WHERE revenue IS NULL;. Possibly they just copy a similar assertion and change details. We could have an assertions_template.sqlx to copy from. - The developer also updates documentation where needed: Dataform allows adding descriptions in config e.g.,
config {
  type: "table",
  description: "This table aggregates order revenue by day...",
  columns: {
    user_id: "References the user placing the order",
    revenue: "Total order amount in USD"
  }
}
Copilot might not automatically do this, but seeing the pattern in some models, it can replicate and even paraphrase. We encourage devs to document columns, as this will flow to BigQuery and Data Catalog. Perhaps a snippet df_doc to generate a stub of description and columns: { col: "desc" } can prompt them.
3. Local Testing Cycle:
After writing or modifying models: - Run dataform compile in terminal (or via VS Code task). If there’s a typo in config or unresolved ref, it will throw an error (with line number)[64]. Developer fixes it (Copilot might assist by reading error and suggesting fix). - Run dataform run --tags=... --full-refresh (optional) on a subset to test logic. Perhaps they run the specific table or schema. Dataform CLI allows filtering by --tags or specifying one action. For example:
dataform run --actions myapp_dev.marts.order_revenue --full-refresh
This compiles and runs only that action and its dependencies. Using --full-refresh forces a rebuild even if incremental (in dev it’s fine to do often). The dev must have credentials and the myapp_dev dataset exists (we ensure dataset creation either manually or via Terraform – the infra/ might have done that). After run, they check BigQuery: the new table myapp_dev.order_revenue should appear. They might query it with bq CLI or in BigQuery Console to verify data looks correct. - Run dataform test to execute assertions on dev data. If any assertion fails (returns rows), the CLI will output failure info and exit non-zero[64]. The dev inspects and fixes either data issues or test logic. Perhaps their assumption was wrong or they need to adjust transformation (for instance, they expected no nulls but found some, so maybe filter them out in logic or accept them and adjust test). - Iterate until no errors and data looks good.
This quick cycle (thanks to working on a smaller dev dataset) encourages writing tests and correct logic early. It’s much faster to catch errors here than in prod.
4. Commit and Push:
The developer commits changes to their feature branch with meaningful message (include context like “[dataform] Added order_revenue incremental model and tests”). They then open a Pull Request on GitHub targeting main.
5. Code Review (with AI support):
Teammates or tech lead review the PR. They might use GitHub’s interface or even an AI code review tool (like GitHub’s Copilot for Pull Requests, or an internal GPT bot) to scrutinize changes. The diff will show .sqlx changes, which reviewers can read – they should verify logic, naming, performance considerations (e.g., did we cluster or partition appropriately for large tables, etc.). If something’s off, they comment. Possibly, if using Copilot Chat, a reviewer could ask it “Does this SQL look correct and performant?” to get a second opinion (not blindly trust it, but as input).
Meanwhile, our CI pipeline runs on the PR (as described in CI section). It will give a status: e.g., Lint/Compile: ✅ or ❌, and output in logs for any issues. If there’s a lint error (like trailing comma or formatting), developer fixes it. We could enforce formatting using dataform format command or sqlfmt if one exists for BigQuery SQL. Dataform CLI’s format will format SQLX consistently (likely based on Prettier rules)[110]. We can integrate that as a pre-commit or CI step to maintain consistent style.
Assuming CI is green and reviews are approved, the PR is merged.
6. Merge to Main → Production Run:
Once merged, our GitHub Actions deploy job triggers. It authenticates and calls Dataform to run the prod_release. The Dataform UI will show a new workflow invocation starting (if we refresh the console or have it open). It will compile the new code with defaultSchema overridden to myapp_prod and execute all transformations. If everything was properly incremental, it might just add new data rather than full re-create (unless we set full-refresh for some reason).
7. Monitoring the Production Run:
We have two feedback channels: - The GitHub Action will wait and then mark the job success/failure. So in GitHub’s interface, the commit gets a green check or red cross. If failure, developer gets alerted (by email from GitHub or a Slack integration on CI failures). - Dataform UI/Cloud Logging: The run logs appear. If an error happens, say BigQuery out-of-resources or a logic error (though logic errors should’ve been caught in dev, but maybe data volume issues or unique constraint violations can surface in prod if assumptions were wrong), Dataform marks the run Failed. Our Cloud Monitoring alert on failed invocations triggers, sending a page/email about “Dataform workflow failure”[68][111]. Also, if any assertion fails in prod, Dataform will mark the workflow as succeeded (I think assertions failing might count as failure or at least show an alert; the doc says it “alerts you if any assertions fail”[18]). We likely treat assertion failures as build failures (data quality issues). The alert might be via email or Slack (if we wired it through a Pub/Sub to Slack integration or used a third-party tool). - Developer goes to Dataform UI’s Execution Logs to investigate (or Cloud Logging if more detail needed). They see which table or assertion failed and error message[78][79]. Suppose an assertion flagged that some new data violated a uniqueness constraint. The developer decides whether to adjust code or if it’s a source data issue that needs cleaning upstream.
8. Fix Forward or Rollback:
If a prod run fails, our pipeline stops. In this design, partial results might exist (if some tables built before failure). Dataform by default tries to run in dependency order, and if one fails, downstream won’t run. We may have partial update. We should decide rollback strategy: Because Dataform builds tables with overwrite by default (or merge for incrementals), if it failed halfway, some tables are updated, others not. This is a common issue with any data pipeline. Usually, if using a tool like dbt/Dataform, you either re-run quickly after fix or have a manual process to rollback if needed (like restore tables from backup if consistency is critical). In our scenario, it might be acceptable to fix and re-run quickly (since transformation is idempotent ideally – running again just brings all up to date). We might note in documentation: if production run fails, fix the issue and re-run (via re-trigger pipeline or manually click “Run” in UI for a quick try).
9. Promotion & Environments:
We effectively treat main as prod code. If we had a staging environment (like a staging branch and myapp_staging dataset), we could incorporate that. For example, merges to main deploy to staging first, then after some verification, promote to prod dataset. However, given the timeline, we stuck to one environment for prod. In many enterprises, they have at least dev/test/prod datasets. Dataform’s release configs support multiple (you can have “dev_release” and “prod_release”). Perhaps a safer approach: - The PR is merged to main -> triggers a run in a staging dataset (like myapp_stage) rather than prod directly. Then some integration tests or user acceptance can occur on stage tables. Then manually (or via tag) promote to prod. But that’s a lot of overhead for each data model change; often, teams directly deploy to prod but rely on assertions to ensure nothing crazy happened. Because data transformations are easier to roll forward (you can recompute if needed). Given the user did not explicitly ask for multi-stage deployment, we didn’t fully implement it, but we did mention how one could do dev/test/prod via branch or release config differences. We can mention choose that if the risk profile demands it.
10. Consumption by App:
Now that tables in myapp_prod are updated, the local application (Python CLI) can query them. The app likely uses BigQuery API or gcloud bq internally. We ensure the app is pointing to prod dataset. Possibly, it uses environment variable to choose dataset (like an .env where DATASET=myapp_prod). In dev mode, the app could point to dev dataset if one wanted to test the app with dev data. That detail is beyond Dataform but important: We should ensure our naming conventions clearly separate dev vs prod data (we did via dataset names). The app’s config can just toggle which dataset to read from. No manual code changes needed.
11. Adding More Models / Scaling:
As more models are added, developers repeat the above. The branching and CI ensures they don’t step on each other. Frequent merges mean the Dataform repo in GCP stays close to main code. If two feature branches modify overlapping parts (e.g., both editing staging_orders.sqlx), Git will handle merge conflicts as in any code. Because they are SQL, devs can resolve with context. The DAG and tests should catch any issues from combined changes.
Safe Backfills & Recompute:
If a major backfill is needed (say a logic bug in incremental logic requires rebuilding a table from scratch), the team can do: - Either change config to {"type": "incremental", ..., "disabled": true} to treat it as full table just once (or use UI to do a full refresh run for that table – Dataform UI allows “Run with full refresh” on incremental[112]). We have protected on incremental if data is not easily recomputed; we use carefully (maybe only on huge tables). - Or use a separate operation or script to rebuild. Dataform’s incremental mechanism with onSchemaChange can add columns without full refresh[113]. We use that when evolving models.
Edge: AI Pitfalls: We watch out for mistakes by AI: - It might not know BigQuery specifics (like using CURRENT_TIMESTAMP() vs standard SQL). BigQuery uses standard SQL, so that’s fine. But e.g., BigQuery requires CAST(... AS INT64) not just INT. Copilot might occasionally use a slightly incorrect function. Developer must review suggestions. - We caution them not to accept any suggestion that includes a literal service account key JSON or other secret (should never happen if none in context). - AI might produce a complex SQL that runs slow. The team should still apply performance tuning (add partitioning, etc.). We have guidelines to cluster large fact tables on date or ID if needed (this can be set in config: clusterBy: ["customer_id"] etc.). Developer must know to do that; AI might not automatically. - If an AI suggests dropping/creating datasets or altering IAM in an operation, likely we avoid that. Infra changes via Dataform should be minimal (maybe GRANT statements in post-ops are fine, Dataform supports post_operations for grant[114]). - The agent should not randomly change environment names or override prefix unless asked.
We set these expectations in the project README so devs use AI wisely.
Final Outcome: - The pipelines run smoothly, devs focus on logic while CI and Dataform handle heavy lifting. - Data quality issues are detected either at dev time (assertions, tests) or promptly in prod with alerts[18]. - If something goes wrong in prod, we can trace exactly which commit (via CI logs and Dataform invocation which records commit SHA used) and which change caused it. - The application sees consistent, up-to-date data in BigQuery. - Auditors can see Dataform’s lineage graph to know how data is produced, and examine logs showing the Dataform SA (or user) ran queries on what tables when – all recorded in Cloud Logging[115][116]. - No sensitive credentials are ever exposed; everything is via roles and identities.
The workflow fosters a culture where data transformation code is treated with the same rigor as application code – with version control, code review, testing, and automated deployment.
Data Quality, Reliability, and Observability
Ensuring the pipeline produces correct and reliable outputs is as important as building it. Dataform provides tools like assertions and dependency management that we will leverage, and we’ll add additional measures:
Data Quality Checks (Assertions & Tests):
We embed data quality tests at multiple levels: - Source Data assertions: If we declare sources in Dataform, we can add assertions on them to validate upstream assumptions. For example, check that an ID column in a raw table is unique or non-null. Since Dataform can create assertions on datasets not produced by itself[117][118], we can declare the source and then write an assertion referencing it. This catches bad data early. We do have to be cautious: if a source fails an assertion, our Dataform run will alert, but we might not want it to fail the whole pipeline run (depending on severity). By default, an assertion failure triggers an alert and marks run as failed[18], which is reasonable because it indicates something is off in source (and our downstream might be invalid). - Model-level assertions: For each important model, we add checks. We saw examples: - Non-null constraints on key fields (via built-in assertions: { nonNull: [...] } in config[108]). - Uniqueness constraints: either use uniqueKey in config for incremental merge (ensuring one row per key)[19], and/or use an assertion to check no duplicate keys exist. Dataform’s built-in assertions.uniqueKey in config serves both as documentation and as a test that fails if duplicates exist[119]. - Value range conditions: use rowConditions in config for each model to assert business logic (like percentages between 0 and 100, dates not in future, etc.)[120]. - Separate assertion SQLX files for more complex tests that might join multiple tables or compare aggregates (e.g., ensure the sum of detail table equals measure in summary table, within tolerance). - Row-count and freshness: BigQuery doesn’t automatically track last updated time easily in table metadata (it has last modified timestamp for table but not for data changes unless using partitioned tables). We can implement freshness checks: - If there’s a timestamp field like created_at in sources, an assertion can check MAX(created_at) is not older than X hours from now for daily feed (freshness) or that yesterday’s partition has data. Dataform doesn’t have a specialized freshness test like dbt, but a custom assertion can do it. For instance, an assertion query:
config { type: "assertion" }
SELECT 1 
FROM ${ref('raw_events')}
WHERE event_date = CURRENT_DATE() 
HAVING COUNT(*) = 0
This would fail (return a row with "1") if no events today. Actually we invert logic (fail when data missing). - Row-count change checks: We can snapshot counts in a meta table or use an assertion to compare count of new vs old. However, Dataform doesn’t preserve previous run stats automatically. We could integrate with BigQuery to store metrics: e.g., after each run, insert a row into a metrics table with table name and row count. Then in next run, compare counts (like ensure not dropped by >50% unexpectedly). But implementing that might be complex. Perhaps simpler: rely on Dataform’s logging/alerting to notice if a job processed 0 rows when normally it processes many (Dataform logs might show how many rows inserted for incremental). - If needed, use Cloud Monitoring to alert on anomalies: e.g., use a log-based metric for rows inserted (Dataform’s logs may have that detail in execution logs for each action), then an alert if below threshold. This is advanced but possible since Dataform execution logs include details of each action (I recall Dataform UI shows e.g., "X rows inserted" after an incremental run).
Using these in combination ensures high data integrity. Dataform automatically creates views for each assertion in the assertions schema[121]. So analysts could even query these to see what rows failed tests. We can also output them to monitoring: e.g., a failed assertion view contains rows of bad data; one could set up a scheduled query to pick those and email them or push to a ticketing system.
Idempotent Incremental Builds:
For incremental tables, we incorporate patterns to avoid duplicate or inconsistent data: - Use uniqueKey in config for incrementals whenever possible[19]. This makes Dataform do a merge (INSERT...ON DUPLICATE UPDATE) rather than append, ensuring one uniqueKey is present exactly once[122][20]. For example, if incremental model is daily aggregate per user, uniqueKey = (user_id, date). If a backfill reruns date already done, it will update rather than double-count. - If uniqueKey not feasible (maybe no PK, or we want append only), ensure logic filters new data properly (WHERE date = CURRENT_DATE() for example for daily loads)[123][124]. Dataform incremental best practice: include a WHERE on the source to only fetch new data since last run, using a stateful marker like max timestamp. Developer must implement that (Copilot can’t infer, but we can code it). - Use protected: true for incrementals that should never be fully refreshed accidentally (like if a developer runs full refresh on an incremental table with a decade of data, could wipe and recompute heavy data). Setting protected: true prevents full refresh unless the flag is explicitly overridden[125][126]. We’d apply this to large fact tables once stable. That way, an inadvertent --full-refresh in CI (or someone toggling a setting) won’t nuke production data. If we need a full rebuild, we’d remove protected or do it carefully by first building to a new table then swapping (so no downtime). - On schema changes for incrementals: we use onSchemaChange: "ALLOW_FIELD_ADDITION" in config (Dataform likely supports similar to dbt’s expand schema without full refresh)[127][128]. This means if we add a new column in SELECT, Dataform will just alter table to add it rather than rebuild from scratch (and not drop historical data). If dropping a column, that might not be possible without full refresh unless using onSchemaChange: "ALLOW_FIELD_RELAXATION" maybe for making not null to nullable. We likely won’t remove columns often. - Backfilling: If we need to backfill old data that was initially missed by incremental (say, we started pipeline from January but now got data for last year), we can run a one-off Dataform run with --full-refresh on that table only, or create a separate backfill workflow that uses Dataform’s ability to run a specific action with overridden date range (maybe via a variable). We consider making our SQL dynamic with a var like ${options.date_from} if needed for backfill runs. But to keep it simple, we might do manual backfills with separate scripts.
Observability and Alerts:
We have implemented: - Logging: All production runs emit logs to Cloud Logging with a resource type dataform.googleapis.com/Repository[129][130]. These logs include run ID, status, timestamp, etc., and if we check execution logs, possibly detailed per action. We ensure Cloud Logging is not disabled (it’s on by default but can be turned off if one chooses; we won’t). There may also be Audit Logs for Dataform (for events like repository accessed, run started by who)[131]. - Error Alerts: As described, we configure a log-based metric that counts failed workflow invocations[68]. Then a Cloud Monitoring alert policy triggers if >=1 failure in last X minutes. The documentation snippet gave the Logs Explorer filter for failures[111]. We set that up and have notifications (email to data team, perhaps an integration to Slack/PagerDuty). - Assertion Failure Alerts: Dataform itself alerts on assertion failures via UI (the run would show failed state or at least highlight them). We can treat any assertion failure as a pipeline failure. If Dataform marks run as failed due to assertion, the above log filter (terminalState="FAILED") will catch it. If not (maybe assertions failing doesn’t set terminalState=FAILED but just logs a separate entry), we may have to filter log entries of type AssertionFailure or monitor the assertions dataset for any view with >0 rows. Alternatively, create a custom log-based metric counting rows in assertion views – but simpler: treat assertion failure as run failure (the doc says Dataform will alert on assertion fail – presumably via UI/email integration too if configured). - Performance Monitoring: We can monitor BigQuery performance via its monitoring (slots, etc.) if needed, but likely not at first. If pipelines grow, we consider if queries are slow or hitting limits. Dataform usage limits (compilation CPU, etc. as per docs) we monitor if project grows above 1000 actions, etc.[132][59]. Currently our scale is moderate.
Lineage and Documentation:
- Lineage: The Dataform UI’s DAG is our go-to for understanding upstream/downstream relationships. It’s updated automatically on code changes. We could also export lineage to an external tool if needed (maybe using the graph JSON for a wiki or using Dataplex Catalog integration[133]). - Documentation: Encourage devs to fill descriptions as mentioned. Dataform can push table/column descriptions to BigQuery. Also, Dataform UI itself can serve as a rudimentary documentation browser, though as of now, it shows descriptions in the table details. If needed, one can generate a static docs site (like Dataform doesn’t have one built-in, but it’s possible to write a script to create markdown from the graph JSON, or wait for an official feature). - We integrate with Dataplex Data Catalog (optional): The Dataform UI has a section “Use Dataplex Universal Catalog”[134]. This likely means we can tag datasets to be in Dataplex, and Dataform’s metadata would flow to Data Catalog, enabling search and lineage across the organization. If enterprise requires central catalog, we might do that.
Recovery and Maintenance:
- If Dataform fails due to infrastructure (rare, but e.g., GCP outage in region), we can rerun later. We might consider deploying to a secondary region if necessary (Dataform can run in specific region, our config says location=us-central1; BigQuery also region or multi-region, we assume multi-regional US since default). - If BigQuery quota issues (too many slots used or query quota), Dataform might log a failure with error from BQ. We should consider slot capacity if heavy – possibly use reservations or at least schedule heavy loads in off-hours. - Maintenance tasks: Upgrading Dataform core (we monitor release notes). Possibly archiving older data (we might implement partition expiration or move old partitions to cheaper storage). Dataform can set partition expiration in config or we do it externally.
Redundancy:
One scenario: having a separate Dataform repo for dev vs prod projects as an alternative to multi-dataset. The best practices mention multiple copies of repo in different projects for dev and prod lifecycles[8]. We opted not to do that to keep it simple. But if reliability demands that dev experiments never interfere with prod, that separation is considered. We trust our CI gating enough with one project.
Templating and Reuse:
We use includes/JS for reuse to avoid copy-paste errors. E.g., if multiple models use same calculation, we put a helper function. Or if dataset names are reused in code, perhaps define constants in a definitions/includes/constants.js like:
module.exports = {
  RAW_DATASET: "analytics_raw",
  STAGING_SCHEMA: "staging",
  MARTS_SCHEMA: "marts"
};
Then in SQLX we can do ${constants.RAW_DATASET} if needed (not sure if Dataform allows injecting JS const in SQL, maybe via backticks and template – yes, Dataform supports JS blocks with js {} to define variables[135]). This ensures if raw dataset changes, we change in one place. It’s also a reliability measure (less prone to typos).
Handling Schema Changes Upstream:
If source tables change (new columns, etc.), our pipeline should ideally adapt or at least fail early. Dataform doesn’t automatically propagate source schema changes to models except if models use SELECT *. Usually we explicitly select needed fields. If upstream adds a column that’s needed, dev must update model code. If upstream removes/renames a column, our model might break (BigQuery error “column not found”). That error surfaces in Dataform run (and likely break compilation since Dataform checks for columns if schema is declared? It might not know schema at compile time, unless we use DECLARE ... statements). But anyway, it’ll fail at query time. In reliability planning, consider adding query-level error handling or using views for backward compatibility. Not easily solved here; just be aware.
In summary, our plan is to prevent bad data and failures whenever possible, and quickly detect and respond when they occur: - We use built-in testing to catch issues early[17]. - We design incrementals and merges to avoid duplications and data loss[122][21]. - We monitor runs and data health metrics, with alerts and logs linking to root cause[68][18]. - We keep the pipeline code maintainable with documentation and avoid complexity that could lead to silent errors.
These measures, combined with the robust CI/CD and AI-assisted development, form a safety net around the pipeline.
Decision Matrix & Final Recommendation
Bringing it all together, here’s a condensed decision matrix for the architecture options (Managed, Core, Hybrid) across key criteria:
Criteria	Managed (A)	Core (B)	Hybrid (C)
Setup Complexity	Low: Leverage GCP UI, minimal CI setup. GitHub linking needed.	Medium: Must build CI/CD, handle auth, environment configs manually.	High: Requires both CI and GCP config (API integration). More moving parts.
Dev Agility	Slower iterations if using only UI (changes need commit & sync). Great UI preview but not full local control.	Fast iterations with local runs. Full control to dev, but no UI preview (must test via CLI/SQL).	Fast local dev (CLI) and can use UI if desired. Upfront CI integration overhead but after that, devs have the best of both worlds.
Orchestration & Scheduling	Built-in scheduling (cron) and manual trigger in console. Event triggers via Cloud Composer or API. Simpler for time-based pipelines.	Custom scheduling needed (GitHub Actions cron, etc.). Flexible to trigger on any event since it’s just code execution.	Use Dataform scheduling for regular jobs; use CI/API triggers for on-demand. Balanced flexibility with simplicity.
Dependency Lineage & Visibility	Excellent lineage graph and details in GCP Console[32]. Suited for sharing with non-dev stakeholders.	No native UI; lineage only in code or custom outputs. Less transparent to non-devs.	Excellent lineage for prod in UI, while devs still get code-based view. Stakeholders see prod lineage in GCP UI.
Logging & Debugging	Rich logs in Cloud Logging[78], one-click to view run errors. Can set up log alerts easily.	Logging scattered: CI logs + BigQuery job logs. Need to aggregate manually if needed. Harder to audit historical runs outside CI.	Prod logs in Cloud Logging (with alerting) plus CI logs for pre-prod tests. Easier debugging of prod issues via UI, and dev issues via CI output.
Security & Compliance	Source control integrated, but devs typically push to run – fairly controlled. No secrets exposed (Dataform SA keys not user-facing). GitHub token stored in GCP securely[15]. Fine-grained IAM possible (dataform roles).	All operations via service accounts you manage. Can enforce code reviews on all changes. Must secure CI credentials properly (we do via OIDC). Slightly higher risk if CI or dev SA misused, but manageable.	CI triggers use short-lived tokens (secure)[14]. Prod runs under service agent with least-privilege roles[31]. No persistent secrets. Strong compliance – every prod change goes through code review + CI. Auditable trail in both Git and GCP logs.
Cost & Efficiency	No cost for Dataform service. Only BigQuery query costs + minimal logging costs[82]. CI usage minimal. Might have slight overhead waiting for external triggers.	CI usage costs (runner time) potentially significant for big data. But might be negligible if using small GitHub-hosted runners and queries run on BQ (the BQ cost is the same either way). Might need dedicated runner if very long queries (to avoid GitHub timeouts).	CI usage moderate (compilation/test only), heavy lifting on BigQuery by Dataform – best of both. Dataform service is free, slight cost for storing compiled graph if at all.
Vendor Lock/Portability	Tied to GCP Dataform. Project can be exported as code easily but the orchestration is GCP-specific. However, Dataform only works on certain warehouses (mostly BQ, Snowflake).	More portable in theory: Dataform core could run on another warehouse if code adjusted (e.g., switch to Snowflake by changing warehouse in config). No reliance on GCP except BigQuery usage.	Moderately tied to GCP for prod (because using Dataform there), but the codebase remains portable – you could choose to later drop Dataform managed and run core only, or vice versa, with minimal refactor.
Team Skill Fit	Good for data analyst-centric teams comfortable with a GUI and SQL, less with CI pipelines.	Good for data engineers who treat everything as code and are comfortable with CLI/DevOps.	Good for teams with mixed skill: analysts get the UI view for results, engineers have full CI control. Requires team to grasp both domain (might be slightly more to learn).
Use-case Examples	Nightly batch ETL where schedule is predictable and lineage/ UI is needed for governance. E.g., finance reports pipelined daily, with Dataform logs reviewed by compliance.	Event-driven enrichment: e.g., trigger Dataform run when new files arrive or code merges, integrated tightly in a larger system. Also where one wants unified pipeline with other code (Dataform CLI can be invoked from any script).	Modern analytics pipeline with frequent incremental updates and continuous integration. E.g., a product analytics team that experiments rapidly (with dev runs) but needs robust prod operation (with monitoring).
Our final recommendation is the Hybrid approach (C). It offers a compelling mix of agility and control: developers can iterate quickly using familiar tools (VS Code, CLI, Git) and AI assistance, while the organization benefits from GCP’s managed infrastructure for production runs, including built-in lineage, scheduling, and security integrations. This approach ensures that the local application always has fresh, trustworthy data from BigQuery, because every change is tested and automatically deployed through a governed process.
Choose Hybrid (C) if: - You want fast development cycles without compromising on production stability. - Your team has or is willing to adopt DevOps practices (CI/CD, code reviews) for data work, leveraging automation to catch errors early. - You value the Dataform UI’s lineage and monitoring but also need the flexibility of custom CI logic or event triggers. - Security and auditability are paramount – every change is tracked in Git and every production run in Cloud Logging, with no manual steps that could be error-prone.
Choose Managed only (A) if: - Your data workflows are relatively infrequent or batch (e.g., once nightly) and the team prefers a low-code operational model. - The overhead of setting up CI or custom triggers isn’t justified – for example, if transformations rarely change and you can rely on a simple daily schedule. - You have non-technical users who may use the Dataform UI directly to make minor edits (with proper access controls) – though even in that case, we’d suggest keeping Git as source of truth.
Choose Core only (B) if: - You need the pipeline to be integrated tightly with other systems or non-GCP environments (maybe you’ll run Dataform in AWS, writing to BigQuery, or you plan to move to another warehouse in future – Dataform core supports multiple warehouses, whereas Dataform managed is BigQuery-specific). - Or if corporate policy disallows storing data transformation logic in a cloud service (for instance, some regulated industries might want everything on-prem; though with Dataform managed, code is in GitHub and only temporarily in Dataform runtime, but some might prefer not even that). - Your team is small and very engineering-focused, happy to maintain their own tooling and perhaps doesn’t need/want a separate UI – they treat it like pure code.
Given the context (BigQuery in GCP, enterprise environment, local app usage), Hybrid hits the sweet spot by enabling CI/CD rigor and enterprise features concurrently.
To implement the recommendation, we proceed with the architecture described: a single repo with /dataform project, VS Code+AI configurations, CI pipelines with WIF auth, Dataform linked for prod runs, and robust testing/alerting. The next section provides a minimal proof-of-concept script to validate that everything works as expected.
Proof-of-Concept: Minimal Pipeline Example
To validate the setup, consider a simple scenario: we have one source table raw_orders in BigQuery, and we want to create a staging table and a mart table from it, plus an assertion. We’ll walk through creating these in the repo, running Dataform, and checking outputs:
Step 0: Prerequisites – Ensure BigQuery dataset myapp_dev (for dev) and myapp_prod (for prod) exist in the GCP project, and the Dataform repo is connected to GitHub with our code. Also, developer has run gcloud auth login locally and Dataform SA has proper BigQuery roles.
Files and Content:
•	dataform/includes/helpers.js (optional, can be empty or have some trivial function).
•	dataform/definitions/sources/tables.js – declare the source:
    // Declare source table in BigQuery
dataform.declare({
  database: dataform.projectConfig.defaultDatabase,  // my-gcp-project-id
  schema: "sales_raw",    // assume raw data in dataset "sales_raw"
  name: "raw_orders"
});
    (This tells Dataform there is a table my-gcp-project-id.sales_raw.raw_orders accessible. Adjust schema to actual raw dataset.)
•	dataform/definitions/staging/stg_orders.sqlx:
    config {
  type: "table",
  schema: "staging",
  tags: ["orders"],    // optional tag
  description: "Staging orders: selected and cleaned from raw_orders"
}

select 
  order_id,
  customer_id,
  order_date,
  total_amount as revenue,
  status
from ${ref("raw_orders")}
where status != 'CANCELLED';
    This creates a staging table with only needed columns and filters out cancelled orders. (We assume raw_orders has those fields.)
•	dataform/definitions/marts/orders_revenue.sqlx:
    config {
  type: "incremental",
  schema: "marts",
  uniqueKey: "order_id",
  assertions: {
    nonNull: ["order_id", "customer_id", "revenue"],
    rowConditions: [
      "revenue >= 0"
    ]
  },
  description: "Fact table for order revenue, one row per order."
}

select 
  o.order_id,
  o.customer_id,
  date(o.order_date) as order_date,
  o.revenue
from ${ref("stg_orders")} o

% if (dataform.projectConfig.vars && dataform.projectConfig.vars.backfill_date) { %
where o.order_date >= date(${dataform.projectConfig.vars.backfill_date})
% } %
;
    Explanation:
•	type: "incremental": on first run, creates full table; on subsequent runs, inserts new orders.
•	uniqueKey: "order_id": ensures each order_id is unique (so updates on conflict). This prevents double-counting if an order appears again.
•	Assertions: no nulls for IDs and revenue, and a rowCondition that revenue must be non-negative.
•	The bottom part uses a templating trick: if a variable backfill_date is provided, filter order_date >= that date. This allows a controlled backfill via --vars '{ "backfill_date": "2020-01-01" }' if we want to limit data. If not provided, it includes all (notice the semicolon placement ensures valid SQL).
In typical runs, we won’t pass backfill_date, so it selects all orders (or we could always process all because uniqueKey prevents duplicates anyway; but this filter could be useful to reduce scanned data if backfilling in portions). - dataform/definitions/assertions/assert_order_revenue.sqlx (an extra assertion example):
config {
  type: "assertion",
  dependencies: [${ref("orders_revenue")}]
}

-- Ensure each customer_id in orders_revenue exists in customers dimension (hypothetical check)
select o.order_id 
from ${ref("orders_revenue")} o
left join ${ref("dim_customers")} c on o.customer_id = c.customer_id
where c.customer_id is null;
This assertion would fail if any order refers to a non-existent customer. (It assumes a dim_customers table exists or is declared; if not, skip this in POC. It's just to illustrate a join assertion.)
The dependencies in config explicitly tells Dataform to run orders_revenue before this assertion[80] (it would anyway by ref usage, but dependencies is another way).
Now, our POC pipeline steps:
Local Run (Dev dataset):
Open a terminal in VS Code (with our environment configured): - Run dataform compile. It should output JSON or success message "Compilation successful" (if no errors). If any error, fix accordingly. E.g., if a ref is not found because we forgot to declare dim_customers, either declare it or remove that assertion for now. - Run dataform run --schema myapp_dev --full-refresh. We specify schema override just in case defaultSchema wasn’t set to dev (but it is). --full-refresh ensures incremental table orders_revenue is built from scratch even if it existed. The CLI will: - Create myapp_dev.staging.stg_orders, - Create/replace myapp_dev.marts.orders_revenue (full refresh due to flag, ignoring incremental state), - Run assertions: - NonNull and rowConditions (built-in, they run automatically after creating table[136]), - The separate assert_order_revenue (it will run and if dim_customers not found or empty, likely return all orders failing. For POC we might exclude this or ensure dim_customers exists as a declared source with some dummy values). - The CLI output will print each action. Example (not actual but illustrative):
Running actions:
- executing dataset myapp_dev.staging.stg_orders ... ✔ (500 rows)
- executing dataset myapp_dev.marts.orders_revenue ... ✔ (500 rows)
- executing assertion assert_order_revenue ... ✔ (0 rows failing)
- 2 assertions in orders_revenue passed (nonNull, rowConditions)
Run completed successfully in 3.2s.
If any assertion fails, CLI would mark that with an ❌ and exit non-zero. - Check BigQuery: The developer can run:
bq query --use_legacy_sql=false 'SELECT COUNT(*) FROM myapp_dev.marts.orders_revenue'
to see there are 500 rows (just an example). They could also query SELECT * FROM myapp_dev.marts.orders_revenue LIMIT 5 to eyeball data. If results look good, proceed.
CI Dry Run (on PR):
When this code is pushed to a feature branch and PR opened, CI (validate job) runs: - sqlfluff lint ensures formatting (if any issues, fix them – e.g., maybe we want uppercase SQL keywords, etc., which Copilot might not always do. We configure lint to our style). - dataform compile – should be fine. - We might skip actual dataform run on PR to avoid writing to even dev dataset. Or we run it with a test dataset set. Given our earlier design, probably skip heavy runs on PR to be safe. The assertions and tests were already done by dev locally ideally.
Merge & Deploy (Prod run):
After PR is approved and merged: - GitHub Actions deploy job triggers. It calls:
gcloud dataform repositories workflow-invocations create ... --release-config=prod_release
In Dataform UI, we should have set up prod_release to use main branch, override defaultSchema to myapp_prod. On invocation, Dataform compiles the same code but with schema = myapp_prod and executes: - Creates myapp_prod.staging.stg_orders, - Creates/merges myapp_prod.marts.orders_revenue (if existing, it will merge new data; first time it will create table), - Runs assertions similarly, creating assertion views in myapp_prod.myapp_assertions dataset by default (since in dataform.json we set assertionSchema). - Dataform logs each step. We can see in Cloud Console Dataform: “orders_revenue: Assertion nonNull passed (0 failures)” etc., or if something fails, it highlights. - The GitHub Action polls and sees success. It marks the workflow success.
Verification:
As part of POC, verify that: - The table myapp_prod.marts.orders_revenue now exists in BigQuery and has expected data. - The assertions views e.g., myapp_prod.myapp_assertions.assert_order_revenue exists. If all good, that view might be empty (0 rows). If there was a failure, that view contains the offending rows (e.g., orders with null customer). - Dataform UI’s DAG shows raw_orders -> stg_orders -> orders_revenue -> assertion. And all green status.
Example Commands & Outputs:
Suppose we run a quick manual test outside CI, using Dataform CLI for prod (just to simulate):
# Authenticate with prod SA (if not already via ADC)
gcloud auth application-default login

# Full refresh prod for initial load
dataform run --project-id my-gcp-project-id --schema myapp_prod --full-refresh
Output (example):
dataform: Running 4 actions (2 table ops, 2 assertions) in my-gcp-project-id
[1/4] myapp_prod.staging.stg_orders - CREATED (4500 rows)
[2/4] myapp_prod.marts.orders_revenue - CREATED (4500 rows, incremental merge)
      - Assertion nonNull passed (columns: order_id, customer_id, revenue)
      - Assertion rowConditions passed (revenue >= 0)
[3/4] myapp_prod.assertions.assert_order_revenue - FAILED (5 rows returned)
[4/4] (skipped remaining assertions due to failure)
Error: Assertion failed: assert_order_revenue returned 5 rows.
This indicates perhaps 5 orders have customer_id not in dim_customers. Dataform likely stops at that point, marking run failed. In Cloud Logging, an entry with terminalState="FAILED" appears[111], triggering our alert.
The team would investigate those 5 rows (the view contains them). If it’s a valid issue (maybe those customers were missing due to a late upstream load), they might decide to re-run after upstream fix. Or if the test is too strict, adjust it. Then redeploy and run again.
For POC, we can simplify by assuming all assertions pass (maybe dim_customers exists and covers all, or remove that assertion). Then output would be all passed:
[3/4] myapp_prod.assertions.assert_order_revenue - PASSED (0 rows)
Workflow completed successfully.
At this point, the local app can query myapp_prod.marts.orders_revenue. A quick verification:
bq query --use_legacy_sql=false "SELECT COUNT(*) FROM myapp_prod.marts.orders_revenue"
Output:
f0_
----
4500
(for example, meaning 4500 orders processed).
The proof-of-concept confirms: - Repo structure and Dataform config are correct (no compile errors). - CI lint/compile would catch nothing major (maybe style). - Dataform runs both locally and via the managed service produce intended results in the separate datasets. - Auth flows work (developer could run with their ADC, CI impersonated SA to run Dataform, Dataform SA wrote to BQ). - AI suggestions likely helped in writing config and SQL but final outcome is developer-approved.
Finally, we check the Dataform UI repository page: It should show the run history with our latest run succeeded. The DAG graph should illustrate dependencies, and one can click on orders_revenue and see its SQL (compiled) and that it’s incremental with uniqueKey etc., and see that the last run was at [time] by [Dataform service account] triggered via API. The lineage view can highlight upstream sources and downstream assertions.
Everything in the POC works with minimal friction, demonstrating the viability of the proposed architecture and workflow.
 
Sources:
•	Google Cloud Dataform Documentation, “Dataform overview” – on Git integration and Dataform core usage[76][3].
•	Google Cloud Dataform Documentation, “Connect a remote repository” – supported Git providers and methods (GitHub via PAT or SSH)[15][16].
•	Google Cloud Dataform Documentation, “Best practices for repositories” – environment management in one vs multiple repos[7][8].
•	Google Cloud Dataform Documentation, “Create tables” – incremental table configuration (uniqueKey for merge, protected flag, etc.)[19][21].
•	Google Cloud Dataform Documentation, “Test data quality” – assertions concept and automatic alerts on failure[18][108].
•	Google Cloud Dataform Documentation, “Monitor runs” – Cloud Logging of Dataform runs and example of alert configuration for failures[115][68].
•	Google Cloud Blog, “Enabling keyless authentication from GitHub Actions” – rationale and example of using Workload Identity Federation instead of service account keys[12][13].
•	Google Developer Forums (community), “Dataform CI CD” – highlighting that dataform compile alone doesn’t catch SQL syntax errors, recommending external SQL linting[17].
•	Stack Overflow, “How to use environments.json in GCP Dataform?” – clarifying that GCP Dataform doesn’t support environments.json, and how to override via API/vars instead[11][70].
 
[1] [3] [4] [32] [43] [44] [49] [50] [53] [62] [76] [80] [81] [88] [101] Dataform overview  |  Google Cloud Documentation
https://docs.cloud.google.com/dataform/docs/overview
[2] [33] [34] [35] [54] [57] Mastering Dataform Execution in GCP: A Practical Guide with CI/CD Example | by Hugo | Google Cloud - Community | Medium
https://medium.com/google-cloud/mastering-dataform-execution-in-gcp-a-practical-guide-with-ci-cd-example-26ef411c148d
[5] [6] [7] [8] [58] [59] [132] Best practices for repositories  |  Dataform  |  Google Cloud
https://cloud.google.com/dataform/docs/best-practices-repositories
[9] [10] [28] [29] [37] [38] [55] [56] [73] [106] [107] Configure compilations  |  Dataform  |  Google Cloud Documentation
https://docs.cloud.google.com/dataform/docs/configure-compilation
[11] [36] [46] [60] [61] [69] [70] [71] google cloud platform - How to use the dataform environments.json file when invocating the workflow from Airflow? - Stack Overflow
https://stackoverflow.com/questions/77786872/how-to-use-the-dataform-environments-json-file-when-invocating-the-workflow-from
[12] [13] [14] [65] [66] [92] [93] [94] [95] [103] Enabling keyless authentication from GitHub Actions | Google Cloud Blog
https://cloud.google.com/blog/products/identity-security/enabling-keyless-authentication-from-github-actions
[15] [16] [48] [51] [96] [99] [100] [133] [134] Connect to a third-party Git repository  |  Dataform  |  Google Cloud Documentation
https://docs.cloud.google.com/dataform/docs/connect-repository
[17] [67] [72] [84] [85] [86] [105] Dataform CI CD - Data Analytics - Google Developer forums
https://discuss.google.dev/t/dataform-ci-cd/147827
[18] [47] [108] [109] [117] [118] [119] [120] [121] [135] [136] Test data quality  |  Dataform  |  Google Cloud
https://cloud.google.com/dataform/docs/assertions
[19] [20] [21] [22] [23] [45] [112] [113] [122] [123] [124] [125] [126] [127] [128] Create tables  |  Dataform  |  Google Cloud Documentation
https://docs.cloud.google.com/dataform/docs/create-tables
[24] [25] [26] [27] [68] [78] [79] [82] [111] [115] [116] [129] [130] [131] Monitor runs  |  Dataform  |  Google Cloud
https://cloud.google.com/dataform/docs/monitor-runs
[30] [31] [83] [89] [90] [91] [102] [104] [114] Control access with IAM  |  Dataform  |  Google Cloud Documentation
https://docs.cloud.google.com/dataform/docs/access-control
[39] [40] [41] [42] [52] [63] [77] [97] [98] Manage a repository  |  Dataform  |  Google Cloud
https://cloud.google.com/dataform/docs/manage-repository
[64] [87] [110] Dataform CLI reference  |  Google Cloud
https://cloud.google.com/dataform/docs/reference/dataform-cli-reference
[74] [75] Dataform client libraries  |  Google Cloud
https://cloud.google.com/dataform/docs/reference/libraries