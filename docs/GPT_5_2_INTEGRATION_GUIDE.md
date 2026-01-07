# GPT-5.2 Integration Implementation Guide (Azure OpenAI Responses API)

This document describes **exactly how this repository currently integrates Azure OpenAI GPT‑5.2** (via the Azure OpenAI **Responses API**) including:

- Where GPT‑5.2 is configured
- How the backend decides to use the Responses API vs Chat Completions
- The precise request payload and headers we send to Azure
- Where credentials come from (and which files/vars you must provide)

This is intended as a “copy/paste to another repo” guide.

---

## Table of Contents

1. Model configuration (`config/models.json`)
2. Credential & auth wiring (`.env` + `agent_tools/llm/env.py`)
3. Azure client implementation (`agent_tools/llm/azure_openai_responses.py`)
4. Smoke test entrypoint (`python -m agent_tools.llm.smoketest`)
5. Output parsing (Responses payload → text)
6. Setup checklist (what to provide)
7. Troubleshooting

---

## 1. Model Configuration (`config/models.json`)

**Source of truth:** `config/models.json`

GPT‑5.2 is configured under the model key:

- `azure-gpt-5.2`

Current shape (representative — keep values accurate for your Azure resource):

```json
{
  "azure-gpt-5.2": {
    "provider": "azure_openai",
    "model": "gpt-5.2",
    "deployment_name": "<your-gpt-5.2-deployment>",
    "api_url": "https://<your-resource>.openai.azure.com/openai/responses?api-version=2025-04-01-preview",
    "display_name": "Azure GPT-5.2",
    "max_output_tokens": 16384,
    "reasoning_effort": "medium",
    "supports_temperature": false,
    "supports_reasoning_effort": true
  }
}
```

Key points:

- `api_url` is a **Responses API** URL. The backend uses a simple detection rule:
  - If the URL contains `/openai/responses`, it uses the Responses API request format.
- `deployment_name` is used as the `model` field in the Responses API payload.
  - In Azure OpenAI, the request `model` is typically your **deployment name**, not a public model ID.
- GPT‑5.2 uses `max_output_tokens` (not `max_completion_tokens`).

---

## 2. Credentials & Authentication (`.env` + `agent_tools/llm/env.py`)

### Where secrets come from

This repo loads Azure credentials from environment variables. The code that loads them is:

- `agent_tools/llm/env.py`

It calls `load_dotenv()` (from `python-dotenv`), which will load variables from a repo-root `.env` file if present.

Starter template:

- [.env.example](../.env.example)

### Required Azure variables

Required:

- `AZURE_OPENAI_KEY`
  - Used as the `api-key` request header for Azure OpenAI.

Recommended / still validated in this repo:

- `AZURE_OPENAI_RESPONSES_URL`
  - Preferred explicit Responses API URL.
- `AZURE_OPENAI_DEPLOYMENT`
  - Required if you do not set `deployment_name` in `config/models.json`.
- `AZURE_OPENAI_URL`
  - Optional legacy/fallback variable name (only used if it contains `/openai/responses`).

Example `.env` (DO NOT commit real secrets):

```bash
AZURE_OPENAI_KEY=<your-azure-openai-key>
AZURE_OPENAI_RESPONSES_URL=https://<your-resource>.openai.azure.com/openai/responses?api-version=2025-04-01-preview
AZURE_OPENAI_DEPLOYMENT=<your-gpt-5.2-deployment-name>
```

### Exactly how we authenticate to Azure

The Azure client sends:

```http
api-key: <AZURE_OPENAI_KEY>
Content-Type: application/json
```

Important:

- This repo does **not** use `Authorization: Bearer ...` for Azure.
- Earlier documentation referenced macOS Keychain; the runtime path in this repo is **environment variables via `.env`**.

### “Credential files”

For Azure OpenAI GPT‑5.2 specifically:

- There is **no** JSON credential file.
- The only required secret is the value of `AZURE_OPENAI_KEY`.

(Separately, Google Vertex uses `GOOGLE_APPLICATION_CREDENTIALS`, which points at a JSON file. That’s unrelated to Azure GPT‑5.2 but is supported by the app.)

---

## 3. Azure OpenAI Client Implementation (`agent_tools/llm/azure_openai_responses.py`)

### Where GPT‑5.2 is detected

The Azure Responses client is:

- `AzureOpenAIResponsesClient` in `agent_tools/llm/azure_openai_responses.py`

Configuration is typically loaded from:

- `config/models.json` via `agent_tools/llm/model_registry.py`

The smoke test (and most starter usage) requires the URL to contain `/openai/responses`.

### Request payload for GPT‑5.2 (Responses API)

We send a payload shaped like:

```python
payload = {
    "model": self.deployment_name,
    "input": input_text,
    "max_output_tokens": effective_max_output_tokens,
    "stream": False,
}
```

Additional fields:

- `instructions`: included if a system message exists
- `temperature`: included only if the model supports it
- `reasoning`: included when `supports_reasoning_effort` is true

Reasoning effort mapping:

- UI/backend accepts: `minimal`, `low`, `medium`, `high`
- For the Responses API payload, the client maps:
  - `minimal` → `low`
  - `low|medium|high` pass through

Responses API reasoning field:

```python
payload["reasoning"] = {"effort": "low" | "medium" | "high"}
```

### How the code converts chat messages to Responses input

The repo’s prompt builder produces chat-style messages (`[{role, content}, ...]`) for all providers.

For Responses API, the Azure client converts:

- First `system` message → `instructions`
- Remaining conversation → a plain text transcript (`input`), formatted as:
  - `User: ...`
  - `Assistant: ...`

This logic is implemented in:

- `conversation_to_responses_input(...)`

### How the response is parsed

The client extracts assistant text using:

- `output_text` if present, otherwise
- parses the `output[]` array and concatenates `message` content parts of type `output_text`/`text`.

This logic is implemented in:

- `extract_output_text(...)`

---

## 4. Smoke Test Entrypoint (`python -m agent_tools.llm.smoketest`)

This repo provides a simple smoke test to validate credentials + connectivity:

```bash
python -m agent_tools.llm.smoketest --model azure-gpt-5.2 --prompt "hello"
```

Optionally write a run artifact (append-only JSONL) under `runs/<RUN_ID>/exports/llm/`:

```bash
python -m agent_tools.llm.smoketest --run-id "YYYY-MM-DD__short-slug" --prompt "hello"
```

---

## 5. Output Parsing (Responses payload → text)

The client currently sets `"stream": False` and extracts assistant text via:

- `output_text` when present, otherwise
- parsing the `output[]` array and concatenating `output_text`/`text` parts

---

## 6. Setup Checklist (What to Provide)

If you want another repo/environment to reproduce this integration, you need:

### Files

Minimum (Azure GPT‑5.2 only):

- `config/models.json`
- `agent_tools/llm/azure_openai_responses.py`
- `agent_tools/llm/env.py`
- `agent_tools/llm/smoketest.py`
- `requirements.txt`

Optional (recommended):

- `.env.example`

### Secrets / credentials

- `AZURE_OPENAI_KEY` (required)
- `AZURE_OPENAI_RESPONSES_URL` (recommended)
- `AZURE_OPENAI_DEPLOYMENT` (required if not set in `config/models.json`)

### Non-secret but required config details

- The Azure OpenAI resource hostname (for your `api_url`)
- Your GPT‑5.2 deployment name (for `deployment_name`)
- The correct API version (embedded in `api_url`)

---

## 7. Troubleshooting

### 401 Authentication failed

- `AZURE_OPENAI_KEY` missing or incorrect
- Azure resource rejects the key

### 404 Not found / deployment missing

- `deployment_name` does not match an Azure deployment
- `api_url` points at the wrong resource or region

### Empty response text

- The deployment returned a Responses payload without `output_text`; this repo has a fallback parser, but if Azure returns a different shape, update `_extract_text_from_responses_api_result` accordingly.

### “Missing environment variables” warning on startup

- If you see missing vars at runtime, ensure `AZURE_OPENAI_KEY` is set.
- For a clean Azure-only setup, set `AZURE_OPENAI_KEY`, `AZURE_OPENAI_RESPONSES_URL`, and `AZURE_OPENAI_DEPLOYMENT` (or configure `config/models.json`).
