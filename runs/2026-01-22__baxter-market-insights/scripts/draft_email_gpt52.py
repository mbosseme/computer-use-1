import os
import glob
from pathlib import Path
from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient, AzureResponsesClientConfig
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config

def main():
    print("Initializing...")
    # Setup
    repo_root = Path.cwd()
    load_repo_dotenv(repo_root)
    
    # Load Config
    env = read_azure_openai_env()
    models = load_models_config(repo_root)
    model_name = "azure-gpt-5.2"
    model_config = models.get(model_name)
    
    if not model_config:
        print(f"Model {model_name} not found in config. Using env defaults.")
        client_config = AzureResponsesClientConfig(
            api_key=env.api_key,
            responses_api_url=env.responses_api_url,
            deployment_name=env.deployment_name,
            max_output_tokens=4096,
            reasoning_effort="high"
        )
    else:
        # Prefer env vars for secrets/URLs if set, else model config placeholders might be used (which is bad if they are <placeholders>)
        # The pattern usually is: model config defines characteristics/deployment name, env defines endpoint/key.
        # But here model config has URL placeholder. 
        # Safer to prioritize env.responses_api_url if present.
        
        deployment = model_config.deployment_name
        if not deployment or "your-" in deployment:
             deployment = env.deployment_name

        url = model_config.api_url
        if not url or "your-" in url:
             url = env.responses_api_url

        client_config = AzureResponsesClientConfig(
            api_key=env.api_key,
            responses_api_url=url,
            deployment_name=deployment,
            max_output_tokens=model_config.max_output_tokens or 4096,
            reasoning_effort="high"
        )

    print(f"Using deployment: {client_config.deployment_name}")
    client = AzureOpenAIResponsesClient(client_config)

    # Gather Context
    synthesis_dir = Path("runs/2026-01-22__baxter-market-insights/exports/baxter_per_doc")
    context_text = ""
    # Only pick the synthesis MD files
    files = sorted(glob.glob(str(synthesis_dir / "*_synthesis.md")))
    
    print(f"Reading {len(files)} synthesis files from {synthesis_dir}...")
    
    for f_path in files:
        f = Path(f_path)
        content = f.read_text(encoding="utf-8")
        context_text += f"\n\n--- DOCUMENT: {f.name} ---\n{content}"

    if not context_text:
        print("No synthesis files found!")
        return

    # Prompt
    user_request_template = """
    After JPM, Myla is planning to send email to CFO at Baxter, and wants to include blurb on Market Insights. Can you send me paragraph. Something like.

    Over the last year, we conducted a demonstration project with ____ to quantify the impact of conservation efforts on IV sales. This confirmed XYZ, and has helped ___ to do ..... We recommend expanding this pilot to do XYZ.

    We also have worked closely with ____, ____, and ___ in the Advanced wound care team to do _____.
    """

    user_message = f"""
    You are an expert assistant drafting a high-stakes email for a senior executive.
    
    TASK:
    Fill in the blanks in the requested email draft below.
    Use the provided "CONTEXT DOCUMENTS" to find the specific names, project details, findings, and teams.
    If multiple options exist, choose the most evidenced ones and explain your choice in a "reasoning" section after the draft.
    
    REQUESTED DRAFT (Template):
    {user_request_template}

    CONTEXT DOCUMENTS:
    {context_text}
    """

    # Call
    print("Calling GPT-5.2 (this may take 30-60s)...")
    try:
        response = client.create_response(
            input_text=user_message,
            reasoning_effort="high",
            timeout_s=120
        )
        
        output_text = AzureOpenAIResponsesClient.extract_output_text(response)
        
        print("\n" + "="*40)
        print("GPT-5.2 GENERATED RESPONSE")
        print("="*40 + "\n")
        print(output_text)
        
    except Exception as e:
        print(f"Error calling LLM: {e}")

if __name__ == "__main__":
    main()
