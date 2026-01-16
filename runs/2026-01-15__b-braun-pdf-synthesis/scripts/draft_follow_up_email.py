from __future__ import annotations

import os
import json
import time
from pathlib import Path

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config

def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]

def _resolve_azure_config() -> AzureResponsesClientConfig:
    repo_root = _repo_root()
    load_repo_dotenv(repo_root)
    env = read_azure_openai_env()
    models = load_models_config(repo_root)
    model = models.get("azure-gpt-5.2")
    return AzureResponsesClientConfig(
        api_key=env.api_key,
        responses_api_url=model.api_url if model else env.responses_api_url,
        deployment_name=model.deployment_name if model else env.deployment_name,
        max_output_tokens=4096,
        reasoning_effort="medium",
    )

def main():
    run_id = "2026-01-15__b-braun-pdf-synthesis"
    repo_root = _repo_root()
    
    # Load synthesis and meeting analysis context
    synthesis_path = repo_root / "runs" / run_id / "exports" / "b-braun_synthesis.md"
    meeting_path = repo_root / "runs" / run_id / "exports" / "meeting_analysis_confirmed_demo.md"
    
    synthesis_text = synthesis_path.read_text() if synthesis_path.exists() else "No global synthesis found."
    meeting_text = meeting_path.read_text() if meeting_path.exists() else "No meeting analysis found."

    prompt = f"""
Draft a professional follow-up email from Matt Bossemeyer to Tracy Butryn and Jennifer Gotto at B. Braun.

CONTEXT:
- Meeting Date: Last Friday (Jan 9, 2026)
- Current Date: Thursday (Jan 15, 2026)
- Goal: Check in after their internal debrief to move toward a more detailed proposal.
- Primary Interest: Custom Analytics Services for the 6 Category IV Ecosystem (Infusion Devices, Sets, Safety IV Catheters, IV Fluids & TPN, Needleless Connectors, Pharmacy & Admixture).
- Key Action Items (from meeting):
    1. B. Braun internal debrief to select engagement approach.
    2. Requesting the specific SKU list from Claire Concowich for the CAPS/compounding sample data cut.
    3. Offering to provide more detail/validation on "what's informing the outputs" (Data Dictionary).

IMAGE CONTEXT (RECAP OF CURRENT PROPOSAL ATTACHED IN CHAT):
- Continue Compliance ($175k/yr)
- Expand Compliance (+$165k/yr)
- IV Categories (6) Custom Analytics Services: $250,000 for 6-month engagement (Goal: National market share map, ERP + Rx Wholesaler data).
- Optional Add-ons: Capital Refresh Recency, DEHP/PVC-Free Targets.

TONE: 
Polite, professional, persistent but helpful. Focus on narrowing down specifics to provide a more detailed proposal.

INCORPORATE STRATEGIC CONTEXT:
{synthesis_text[:2000]} 

DRAFT THE EMAIL:
"""

    try:
        cfg = _resolve_azure_config()
        client = AzureOpenAIResponsesClient(cfg)
        
        messages = [
            {"role": "system", "content": "You are a strategic business development professional at Premier drafting a high-stakes follow-up email to B. Braun executives."},
            {"role": "user", "content": prompt}
        ]
        
        instructions, input_text = client.conversation_to_responses_input(messages)
        # Using a timeout for reasoning
        headers = {"api-key": cfg.api_key, "Content-Type": "application/json"}
        payload = {
            "model": cfg.deployment_name,
            "input": input_text,
            "instructions": instructions,
            "max_output_tokens": 2048,
            "reasoning": {"effort": "medium"},
            "stream": False
        }
        import requests
        resp = requests.post(cfg.responses_api_url, headers=headers, json=payload, timeout=300)
        result = resp.json()
        draft = client.extract_output_text(result)
        
        print("\n--- DRAFT EMAIL RECOMMENDATION ---\n")
        print(draft)
        
        # Save draft as record
        draft_path = repo_root / "runs" / run_id / "exports" / "follow_up_email_draft.md"
        draft_path.write_text(draft)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
