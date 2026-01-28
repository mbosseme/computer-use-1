# BigQuery Cross-Project Access Guide

This document explains how to query BigQuery tables across different GCP projects from this workspace.

## Overview

Many Premier data assets live in projects other than your personal GCP project (e.g., `abi-inbound-prod`). To query these tables, you need proper authentication and project configuration.

## Authentication: ADC (Application Default Credentials)

**Always use ADC for interactive work.** Never use service account JSON files.

### Setup (One-Time)

```bash
# Authenticate with your Google account
gcloud auth application-default login

# Set your default project (for quota/billing)
gcloud config set project matthew-bossemeyer
```

### Verify ADC

```bash
cat ~/.config/gcloud/application_default_credentials.json | grep -E '"type"|"quota_project_id"'
```

Expected output:
```json
"quota_project_id": "matthew-bossemeyer",
"type": "authorized_user",
```

## Critical Rule: No GOOGLE_APPLICATION_CREDENTIALS

**Do NOT set `GOOGLE_APPLICATION_CREDENTIALS` in your environment** when doing cross-project queries.

### Why This Matters

| Auth Method | How It Works | Cross-Project Access |
|-------------|--------------|----------------------|
| ADC (user) | Uses your Google account (`matt_bossemeyer@premierinc.com`) | ✅ Works if you have IAM access |
| Service Account JSON | Uses a service account identity | ❌ Often lacks cross-project permissions |

When `GOOGLE_APPLICATION_CREDENTIALS` is set, the BigQuery client uses the service account instead of your user identity — even if your user has the correct permissions.

### Fix: Unset in Python

If you're running code that might inherit a problematic environment:

```python
import os

# Remove any service account override before importing BigQuery
for key in ["GOOGLE_APPLICATION_CREDENTIALS", "BIGQUERY_PROJECT"]:
    os.environ.pop(key, None)

from google.cloud import bigquery
client = bigquery.Client()  # Now uses ADC
```

### Fix: Local .env Override

If your code uses `python-dotenv` and a parent `.env` sets problematic values, create a local `.env` in your working directory that **doesn't** set those variables. `load_dotenv()` finds the closest `.env` first.

```bash
# In your project directory
echo "# Local override - use ADC, no service account" > .env
```

## Project Configuration

### Job Project vs Data Project

- **Job Project:** Where the query runs and is billed (your project)
- **Data Project:** Where the data lives (e.g., `abi-inbound-prod`)

You query cross-project by specifying the full table path:

```sql
SELECT * 
FROM `abi-inbound-prod.dataset_name.table_name`
LIMIT 10
```

The job runs in your project (`matthew-bossemeyer`) and reads from `abi-inbound-prod`.

### Python Client Setup

```python
from google.cloud import bigquery

# Default client - uses ADC quota_project_id
client = bigquery.Client()

# Or explicitly set project for jobs
client = bigquery.Client(project="matthew-bossemeyer")

# Query cross-project table
sql = """
SELECT COUNT(*) 
FROM `abi-inbound-prod.abi_inbound_bq_stg_purchasing_provider_transaction.transaction_analysis_expanded`
"""
df = client.query(sql).to_dataframe()
```

## Common Errors and Fixes

### Error: "Access Denied: User does not have permission to query table"

**Cause:** Your identity lacks read access to the target project.

**Fix:**
1. Verify you're using ADC (not a service account)
2. Check IAM permissions in the target project
3. Request `roles/bigquery.dataViewer` on the dataset

### Error: "User does not have bigquery.jobs.create permission in project"

**Cause:** Trying to run jobs in a project where you lack job-creation rights.

**Fix:** Ensure your client uses your personal project for jobs:
```python
client = bigquery.Client(project="matthew-bossemeyer")
```

### Error: "403 GET ... Permission bigquery.tables.get denied"

**Cause:** Service account being used instead of your user identity.

**Fix:** Unset `GOOGLE_APPLICATION_CREDENTIALS`:
```python
import os
os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)
```

## Dataform Configuration

For Dataform, use a minimal credentials file that specifies ADC:

**`.df-credentials.json`:**
```json
{
  "projectId": "matthew-bossemeyer",
  "location": "US"
}
```

This tells Dataform to use ADC authentication with your project as the job project.

## Subprocess Isolation

When spawning subprocesses that need ADC, ensure they don't inherit problematic env vars:

```python
import os
import subprocess

# Build clean environment
clean_env = {k: v for k, v in os.environ.items() 
             if k not in ("GOOGLE_APPLICATION_CREDENTIALS", "BIGQUERY_PROJECT")}
clean_env["PYTHONPATH"] = "."

subprocess.run(
    ["python", "my_script.py"],
    env=clean_env,
    check=True
)
```

## Reference

- [BigQuery Data Exploration Skill](.github/skills/bigquery-data-exploration/SKILL.md)
- [ge-pipeline ADC client](runs/2026-01-16__ge-market-insights/ge-pipeline/src/bigquery_client.py)
