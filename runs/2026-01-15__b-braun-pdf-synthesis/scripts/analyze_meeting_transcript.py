from __future__ import annotations

import os
import re
import json
import time
import PyPDF2
from pathlib import Path
from typing import Any, Optional

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]

def _resolve_azure_config(*, model_name: str = "azure-gpt-5.2") -> AzureResponsesClientConfig:
    repo_root = _repo_root()
    load_repo_dotenv(repo_root)

    env = read_azure_openai_env()
    models = load_models_config(repo_root)
    model = models.get(model_name)

    api_key = env.api_key
    deployment_name = (model.deployment_name if model else None) or env.deployment_name
    candidate_url = (model.api_url if model else None) or env.responses_api_url or env.api_url
    
    max_output_tokens = 16384
    reasoning_effort = (model.reasoning_effort if model else None) or "medium"

    return AzureResponsesClientConfig(
        api_key=api_key,
        responses_api_url=candidate_url,
        deployment_name=deployment_name,
        max_output_tokens=int(max_output_tokens),
        reasoning_effort=reasoning_effort,  # type: ignore[arg-type]
    )

def extract_pdf_text(file_path: Path) -> str:
    text = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text.append(page.extract_text() or "")
    except Exception as e:
        print(f"Error extracting PDF {file_path}: {e}")
    return "\n".join(text)

def call_with_retry(client, input_text, instructions=None, max_retries=5, initial_delay=2, timeout_s=300):
    for i in range(max_retries):
        try:
            result = client.create_response(input_text=input_text, instructions=instructions, timeout_s=timeout_s)
            return result
        except Exception as e:
            if "429" in str(e) or "Too Many Requests" in str(e):
                delay = initial_delay * (2 ** i)
                print(f"Rate limited. Retrying in {delay}s...")
                time.sleep(delay)
            elif "Read timed out" in str(e):
                print(f"Read timed out. Retrying with longer timeout...")
                timeout_s += 120
            else:
                raise e
    raise RuntimeError("Max retries exceeded for API call")

def main():
    file_path = Path("/Users/matt_bossemeyer/Library/CloudStorage/OneDrive-Premier,Inc/Notebook LM Documents/B Braun/Confirmed-BBraun MI Demo - virtual.pdf")
    run_id = "2026-01-15__b-braun-pdf-synthesis"
    repo_root = _repo_root()
    export_path = repo_root / "runs" / run_id / "exports" / "meeting_analysis_confirmed_demo.md"
    
    print(f"Extracting text from: {file_path.name}")
    # Optimization: We found the PDF repeats the full transcript on every page.
    # We will extract only the first page and verify it has the content.
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            # The transcript resides in the first page (and repeats on others)
            content = reader.pages[0].extract_text() or ""
    except Exception as e:
        print(f"Error extracting PDF: {e}")
        return
    
    if not content or len(content) < 100:
        print("No meaningful content extracted.")
        return

    print(f"Extracted {len(content)} characters. Sending to GPT-5.2 for single-pass synthesis (Actions Focus)...")
    
    cfg = _resolve_azure_config()
    client = AzureOpenAIResponsesClient(cfg)
    
    prompt = f"""
Analyze the following meeting transcript from a B Braun Market Insights Demo.
The transcript is complete. Please provide:
1. **Executive Summary**: A high-level overview of what transpired.
2. **Key Follow-up Actions**: A rigorous list of all assignments, deliverables, and next steps mentioned. Identify the owner and any mentioned timelines.
3. **Strategic Pain Points**: Any specific challenges or feature requests expressed by B Braun.

TRANSCRIPT:
{content}
"""

    try:
        messages = [
            {"role": "system", "content": "You are a professional business analyst specializing in strategic implementation and project management."},
            {"role": "user", "content": prompt}
        ]
        
        instructions, input_text = client.conversation_to_responses_input(messages)
        # Using a longer timeout as the full transcript synthesis might take time for the model to reason through.
        result = call_with_retry(client, input_text, instructions, timeout_s=400)
        final_analysis = client.extract_output_text(result)
        
        print(f"Writing analysis to {export_path}")
        export_path.parent.mkdir(parents=True, exist_ok=True)
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(f"# Meeting Analysis & Action Items: B Braun MI Demo\n\nSource: {file_path.name}\nGenerated on: 2026-01-15\n\n{final_analysis}")
            
        print("Success!")
        
    except Exception as e:
        print(f"Error during analysis: {e}")

if __name__ == "__main__":
    main()
