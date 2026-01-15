# Skill: Document Synthesis via LLM

## Purpose
Synthesize a folder of documents (PDF, EML, etc.) into a structured summary using an LLM endpoint (Azure OpenAI GPT-5.2 Responses API or similar).

## When to use this skill
- User asks to "summarize," "synthesize," or "extract key themes" from a set of documents.
- Input is a folder of files (PDFs, emails, transcripts).
- Output is a consolidated markdown summary with themes, action items, or strategic takeaways.

## Core workflow

### Phase 1: Inventory & Extract
1. **Inventory the folder**: List all files, noting extensions (`.pdf`, `.eml`, `.docx`, etc.).
2. **Extract text locally** (do NOT send binaries to the LLM):
   - **PDF**: Use `PyPDF2` (see `agent_tools/llm/document_extraction.py`).
   - **EML**: Use Python's `email` module with `BytesParser`.
   - **Other**: Extend as needed (e.g., `python-docx` for Word).
3. **Sanitize**: Remove potential secrets (API keys, tokens, passwords) before sending to LLM.
4. **Character-limit check**: Truncate individual documents to ~20k chars to avoid context limits.

### Phase 2: Per-Document Summarization Loop
**Why loop?** Sending all documents in one payload often exceeds context limits or triggers rate limits. A per-document loop is more robust.

1. For each extracted document:
   - Build a prompt: "Summarize this document, highlighting key business intelligence..."
   - Call the LLM with `call_with_retry` (handles 429s and timeouts).
   - Collect the summary.
   - Add a small delay (1–2s) between calls to reduce rate-limit risk.

### Phase 3: Final Aggregation
1. Combine all per-document summaries into a single input.
2. Call the LLM with a "meta-synthesis" prompt: "Given these summaries, identify recurring themes, strategic takeaways, and action items."
3. Save the final output to `runs/<RUN_ID>/exports/<output_name>.md`.

## Key code patterns

### Resolving Azure config
```python
from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient, AzureResponsesClientConfig
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config

def _resolve_azure_config(*, model_name: str = "azure-gpt-5.2") -> AzureResponsesClientConfig:
    repo_root = Path(__file__).resolve().parents[3]
    load_repo_dotenv(repo_root)
    env = read_azure_openai_env()
    models = load_models_config(repo_root)
    model = models.get(model_name)
    return AzureResponsesClientConfig(
        api_key=env.api_key,
        responses_api_url=model.api_url or env.responses_api_url,
        deployment_name=model.deployment_name or env.deployment_name,
        max_output_tokens=model.max_output_tokens or 16384,
        reasoning_effort=model.reasoning_effort or "medium",
    )
```

### Retry with exponential backoff
```python
from agent_tools.llm.document_extraction import call_with_retry

result = call_with_retry(client, input_text, instructions, max_retries=5, initial_delay=2)
```

### Text extraction
```python
from agent_tools.llm.document_extraction import extract_pdf_text, extract_eml_text, sanitize_text

pdf_content = extract_pdf_text(Path("/path/to/file.pdf"))
eml_content = extract_eml_text(Path("/path/to/file.eml"))
safe_content = sanitize_text(pdf_content)
```

## Recovery rules

### Rate limits (429 Too Many Requests)
- **Detection**: Exception message contains "429" or "Too Many Requests".
- **Recovery**: Exponential backoff (2s → 4s → 8s → 16s → 32s). Max 5 retries.
- **Prevention**: Add 1–2s delay between per-document calls.

### Context length exceeded (400 Bad Request)
- **Detection**: Exception message contains "context_length_exceeded" or similar.
- **Recovery**:
  1. Check if the file has redundant content (e.g., transcript repeated on every page).
  2. Truncate to first N pages or first 20k characters.
  3. Re-run the single-document summarization.
- **Prevention**: Always truncate individual docs before sending.

### Read timeout
- **Detection**: "Read timed out" in exception.
- **Recovery**: Increase `timeout_s` (e.g., +60–120s) and retry.
- **Prevention**: Use generous initial timeout (180–300s) for large payloads.

### PDF quirks (repeated content per page)
- **Detection**: `len(full_text) / num_pages > 50000` (suspiciously large per-page average).
- **Recovery**: Extract only page 1 for transcript-style PDFs.
- **Lesson**: Always inspect file properties (page count, char count) before full extraction.

## Outputs
- **Primary**: `runs/<RUN_ID>/exports/<synthesis_name>.md`
- **Intermediate** (optional): Per-document summaries can be saved for debugging.

## Dependencies
- `PyPDF2` (Tier A base)
- `python-dotenv` (Tier A base)
- `requests` (Tier A base)
- Azure OpenAI Responses API access (configured in `.env` + `config/models.json`)

## Related utilities
- [agent_tools/llm/azure_openai_responses.py](../../../agent_tools/llm/azure_openai_responses.py): Core Responses API client.
- [agent_tools/llm/document_extraction.py](../../../agent_tools/llm/document_extraction.py): PDF/EML extraction + retry logic.
- [agent_tools/llm/env.py](../../../agent_tools/llm/env.py): Environment variable loading.
- [agent_tools/llm/model_registry.py](../../../agent_tools/llm/model_registry.py): Model config from `config/models.json`.

## Example run script
See `runs/2026-01-15__b-braun-pdf-synthesis/scripts/extract_and_synthesize.py` as a reference implementation.
