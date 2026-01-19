# Skill: Batch Research & Data Extraction

## Context
Use this skill when tasked with researching information for a long list of entities (e.g., >20 records) using external tools (web search, Tavily, etc.) and saving them to a structured file (CSV/JSON/Database).

## Problem Solved
- **API Limits:** Prevents `400 Bad Request` or timeout errors from search providers like Tavily by enforcing batch constraints.
- **State Loss:** Prevents losing progress or creating duplicates by enforcing a "diff-based" workflow (Master List vs. Done List).
- **Data Corruption:** Prevents malformed files by using Python scripts for updates instead of direct text editing.

## Critical Invariants
1. **Never** attempt to query >10 entities in a single tool call. (Preferred: 5-8).
2. **Never** edit the data file directly with text editor tools (like `replace_string_in_file`) for append operations. Always use a Python script.
3. **Always** calculate "Remaining" at the start of a turn by reading the actual files. Do not trust conversation history for state.

## Workflow Patterns

### 1. The "Diff" State Check
Before running any search, identify exactly what remains to be done.

```python
import pandas as pd

# Load inputs
master_df = pd.read_csv('inputs/master_list.csv')
target_df = pd.read_csv('exports/target_list.csv')

# Identify Primary Key (e.g., 'company_name', 'url', 'id')
key = 'company_name'

# Calculate Diff
master_set = set(master_df[key])
done_set = set(target_df[key])
remaining = sorted(list(master_set - done_set))

print(f"Total Scope: {len(master_set)}")
print(f"Completed:   {len(done_set)}")
print(f"Remaining:   {len(remaining)}")
print(f"Next Batch:  {remaining[:6]}") # Print first 6 for next action
```

### 2. The Chunked Search (Tavily Specific)
When using `mcp_tavily_tavily-search` or similar tools:
- **Batch Size:** 5-6 entities per call.
- **Query Format:** Create a numbered list in the query string.
  - *Good:* "Find email addresses for: 1. Acme Corp, 2. Globex, 3. Soylent Corp"
  - *Bad:* "Find emails for Acme, Globex, Soylent... [20 more]"

### 3. The "Append Script" Pattern
After gathering research data, create a temporary script (e.g., `scripts/update_batch.py`) to safely write to the file.

```python
import pandas as pd
import os

CSV_PATH = 'exports/target_list.csv'

# 1. Define the fresh data (LLM populates this)
new_records = [
    {"company_name": "Acme Corp", "email": "contact@acme.com", "notes": "Verified on footer"},
    {"company_name": "Globex",    "email": "info@globex.com",  "notes": "About page"},
]

# 2. Load Existing
if os.path.exists(CSV_PATH):
    df = pd.read_csv(CSV_PATH)
else:
    df = pd.DataFrame(columns=["company_name", "email", "notes"])

# 3. Concatenate
new_df = pd.DataFrame(new_records)
df = pd.concat([df, new_df], ignore_index=True)

# 4. Deduplicate (Critical Safety Step)
df = df.drop_duplicates(subset=['company_name'], keep='last')

# 5. Write
df.to_csv(CSV_PATH, index=False)
print(f"Success. Total records: {len(df)}")
```

## Recovery Rules
- **If Tavily API errors (400/Timeout):** Immediately stop. Reduce batch size by 50% (e.g., 6 -> 3) and retry.
- **If duplicates appear:** Run a dedicated cleanup script using `pandas.drop_duplicates`.
- **If data is missing:** Do not guess. Log it as empty or "Not Found" in the notes column.
