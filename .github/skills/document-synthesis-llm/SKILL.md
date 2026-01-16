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
4. **Avoid naive truncation**: Do **not** default to `text[:N]` for long documents. Instead use chunking (map-reduce) so late-document content is not silently dropped.

### Phase 2: Per-Document Summarization Loop
**Why loop?** Long documents can exceed practical prompt sizes. A chunked per-document loop is more robust and provides explicit coverage accounting.

1. For each extracted document:
  - Chunk the extracted text (prefer page-aware chunking for PDFs).
  - **Map step**: summarize each chunk.
  - **Reduce step**: synthesize chunk summaries into a single document-level synthesis.
  - Add a small delay (0.5–2s) between calls to reduce rate-limit risk.

User-visible contract:
- The output MUST include a **Coverage / Limit Warnings** section.
- If any content is omitted due to configured limits (max chunks/pages/timeouts), the warning must explicitly say so (pages omitted, extraction failures, truncation events).

### Phase 3: Final Aggregation
1. Combine all per-document summaries into a single input.
2. Call the LLM with a "meta-synthesis" prompt: "Given these summaries, identify recurring themes, strategic takeaways, and action items."
3. Save the final output to `runs/<RUN_ID>/exports/<output_name>.md`.

## Recommended implementation
- Use `agent_tools/llm/summarize_file.py` for chunked PDF synthesis (map-reduce) with coverage warnings and an optional JSON manifest.

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
  1. Prefer chunking/map-reduce over truncation so late-document content is not silently dropped.
  2. If a PDF extractor produces duplicated page text (same content repeated), emit a coverage warning and consider switching extractor/OCR.
  3. If you must bound inputs, do so with explicit user-visible warnings/manifests (max chunks/pages/timeouts), not silent `text[:N]`.

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
- [agent_tools/llm/summarize_file.py](../../../agent_tools/llm/summarize_file.py): Chunked map-reduce synthesis for PDFs and text, with coverage warnings.
- [agent_tools/llm/summarize_folder.py](../../../agent_tools/llm/summarize_folder.py): One-command folder synthesis (PDF/EML/text).
- [agent_tools/llm/env.py](../../../agent_tools/llm/env.py): Environment variable loading.
- [agent_tools/llm/model_registry.py](../../../agent_tools/llm/model_registry.py): Model config from `config/models.json`.

## Example run script
See `runs/2026-01-15__b-braun-pdf-synthesis/scripts/extract_and_synthesize.py` as a reference implementation.
