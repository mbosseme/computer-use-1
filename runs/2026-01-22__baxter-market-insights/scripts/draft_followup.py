import os
from pathlib import Path
from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient, AzureResponsesClientConfig
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config

def main():
    repo_root = Path.cwd()
    load_repo_dotenv(repo_root)
    env = read_azure_openai_env()
    
    # Simple config init relying on env vars
    client_config = AzureResponsesClientConfig(
        api_key=env.api_key,
        responses_api_url=env.responses_api_url,
        deployment_name=env.deployment_name,
        max_output_tokens=2048,
        reasoning_effort="medium"
    )
    client = AzureOpenAIResponsesClient(client_config)

    # Context
    slots = """
    - Friday, Jan 23: 9:30 AM, 12:00 PM EST
    - Monday, Jan 26: 9:30 AM, 1:30 PM EST
    - Tuesday, Jan 27: 12:00 PM, 3:00 PM EST
    """
    
    prev_email_context = """
    From: Bossemeyer, Matthew
    To: Gullion, Caroline
    Date: Dec 17, 2025
    Subject: Re: Next Steps After Demand Planning Pilot
    Content: "I look forward to reconnecting in mid-January to explore what opportunities might exist for continuing to work together."
    
    Caroline previously said: "At this time, we dont have any more budget... Im hoping this changes in the new year... Let's touch base in mid-January to re-assess."
    """
    
    prompt = f"""
    Draft a follow-up email to Caroline Gullion.
    
    Context:
    {prev_email_context}
    
    Goal: 
    - Reconnect as planned in mid-January.
    - Warm and friendly tone, but professional (not overly casual).
    - Suggest specific times for a 30-45 min call from the following availability:
    {slots}
    - Topics: Check in on their needs, where they stand with the budgeting process, and discuss potential partnership opportunities going forward.
    
    Output Format:
    Subject: ...
    Body: ...
    """
    
    print("Generating draft...")
    response = client.create_response(input_text=prompt)
    
    # Use the static helper to extract text
    content = client.extract_output_text(response)
    if not content:
        # Debug if empty
        import json
        print("DEBUG: Full response dump:\n" + json.dumps(response, indent=2))
        content = "Error: No content generated."
    
    output_path = repo_root / "runs/2026-01-22__baxter-market-insights/exports/caroline_followup_draft.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    
    print(f"\nDraft saved to {output_path}")
    print("-" * 40)
    print(content)
    print("-" * 40)

if __name__ == "__main__":
    main()
