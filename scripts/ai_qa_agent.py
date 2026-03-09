import json
import sys
from pathlib import Path

# Add project root to path
repo_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(repo_root))

from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient
from agent_tools.llm.smoketest import _resolve_azure_config

def main():
    # 1. Load the semantic evidence bundle we generated earlier
    bundle_path = Path("scripts/sniff_test_bundle.json")
    if not bundle_path.exists():
        print(f"Error: Could not find evidence bundle at {bundle_path}")
        return 1
        
    with open(bundle_path, "r") as f:
        evidence_bundle = json.load(f)
        
    # 2. Define the exact persona from the research and briefing
    system_prompt = """You are "The Skeptical Contract Director," a cynical healthcare supply-chain data QA expert.

Mission:
- Determine whether the output table is business-plausible for contract/catalog/spend analytics, answering Bruce's prompt of 'Where do our Premier contracts land vs Healthcare IQ'.
- Find relationship anomalies that would mislead an executive dashboard or savings model.

Operating rules (non-negotiable):
1) Never assume: every claim must be backed by a computed metric or a query result in the provided JSON Evidence Bundle.
2) Focus on semantic failures required by the executive briefing:
   - extreme price vs benchmark ratios identifying UOM explosions
   - missing benchmarks leading to $0 baseline inflation
   - rollup/reconciliation disconnects between Item-level and Contract-level data
   - Does our top-tier pricing accurately yield savings versus median benchmarks.
3) Every issue you report must include:
   - severity (blocker / investigate / FYI)
   - confidence (high/med/low)
   - evidence (key numbers from the JSON)
   - suspected cause / recommendation

Output a formal Markdown formatted QA report:"""

    # 3. Submit to Azure OpenAI GPT-5.4
    print("Initiating connection to Azure GPT-5.4...")
    try:
        cfg = _resolve_azure_config(model_name="azure-gpt-5.4")
        client = AzureOpenAIResponsesClient(cfg)
    except Exception as e:
        print(f"Failed to load Azure OpenAI Config: {e}")
        return 1

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": json.dumps(evidence_bundle, indent=2)}
    ]

    instructions, input_data = client.conversation_to_responses_input(messages)

    print("Generating Skeptical Contract Director QA Report... (This may take 30-45 seconds depending on reasoning effort)")
    
    try:
        result = client.create_response(
            input_data=input_data,
            instructions=instructions,
            max_output_tokens=3000,
            reasoning_effort="high"
        )
    except Exception as e:
        print(f"Azure API Call Failed: {e}")
        return 1
    
    # 4. Extract and save the output
    output_text = client.extract_output_text(result)
    
    out_file = Path("runs/2026-03-04__portfolio-competitiveness/notes/agent-runs/2026-03-08_GPT_5_4_Skeptical_QA_Report.md")
    with open(out_file, "w") as f:
        f.write(output_text)
        
    print(f"\nSuccess! Placed automated AI QA review in: {out_file}")

if __name__ == "__main__":
    sys.exit(main())