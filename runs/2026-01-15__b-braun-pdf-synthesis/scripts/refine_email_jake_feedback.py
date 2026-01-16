import os
import requests
import json
from dotenv import load_dotenv
from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient, AzureResponsesClientConfig

# Load environment variables from the root .env file
load_dotenv("/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis/.env")

def call_gpt5_refinement():
    # Load env vars
    api_key = os.getenv("AZURE_OPENAI_KEY")
    url = os.getenv("AZURE_OPENAI_RESPONSES_URL")
    deployment_name = "gpt-5.2-mv-2025-12-11"

    if not api_key or not url:
        print("Error: Missing API credentials.")
        return

    config = AzureResponsesClientConfig(
        api_key=api_key,
        responses_api_url=url,
        deployment_name=deployment_name,
        reasoning_effort="medium"
    )
    client = AzureOpenAIResponsesClient(config)

    # The prompt focus
    instructions = """
    You are assisting Matt Bossemeyer (Premier) in drafting a follow-up email to Tracy Butryn and Jennifer Gotto (B. Braun) following a Market Insights demo.
    """
    
    input_text = """
    CRITICAL CONTEXT FROM JAKE ASTARITA (B. Braun Stakeholder):
    - Jake's primary objective: Identifying "Portfolio Gaps" (where B. Braun is missing items the market is buying).
    - Jake's targeting strategy: Filter the data by "Committed Members" (those with high IV Fluid share) to show them exactly what else they are missing from B. Braun's 'Triple Play' or 'Plus 3' bundles.
    - Jake's need for validation: Seeing if Premier can accurately represent the CAPS (503B) and pharmacy admixture market.
    
    TASK:
    Refine the "Proposed Solution" section of the follow-up email. Instead of generic "analytics," phrase it as a custom-built environment that specifically solves Jake's "Portfolio Gap" challenge using his "Committed Member Filter" strategy.
    
    The email should urge them to provide the SKU list (for CAPS/Pharmacy) so we can build the validation sample Jake specifically requested.
    
    Current Draft Context:
    - We are proposing a Custom Analytics environment for 6 categories (Infusion Devices, Sets/Accessories, Connectors, Fluids, TPN, and Catheters).
    - We discussed a $150k initial engagement (Data + Services).
    
    Desired Tone: Professional, urgent (it's been a few days since the Friday demo), and highly responsive to Jake's specific "Asks".
    
    Please provide ONLY the revised "Proposed Solution" section and a short "Call to Action" that references Jake's input.
    """

    try:
        result = client.create_response(
            input_text=input_text,
            instructions=instructions,
            timeout_s=300
        )
        
        content = client.extract_output_text(result)
        print("--- REFINED EMAIL SECTION ---")
        print(content)
        
        # Save to a temporary file
        output_path = "/Users/matt_bossemeyer/Projects/wt-2026-01-15__b-braun-pdf-synthesis/runs/2026-01-15__b-braun-pdf-synthesis/exports/jake_feedback_refinement.md"
        with open(output_path, "w") as f:
            f.write(content)
        print(f"\nSaved refinement to {output_path}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    call_gpt5_refinement()
