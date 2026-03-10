import pandas as pd
from pathlib import Path
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.azure_openai_responses import AzureResponsesClientConfig, AzureOpenAIResponsesClient
import base64

load_repo_dotenv(Path('.'))
env = read_azure_openai_env()

config = AzureResponsesClientConfig(
    api_key=env.api_key,
    responses_api_url=env.responses_api_url,
    deployment_name=env.deployment_name
)

client = AzureOpenAIResponsesClient(config)

excel_file = "runs/2026-03-04__portfolio-competitiveness/Category_Competitive_Heat_Map.xlsx"
df_categories = pd.read_excel(excel_file, sheet_name="Top Category Opportunities", nrows=20)
df_summary = pd.read_excel(excel_file, sheet_name="Service Line Summary")

context_text = f"""
We have compiled data on expiring categories in a national portfolio to identify cost reduction opportunities. 
Below is the summary data and the top 20 category opportunities. 

# Service Line Summary
{df_summary.to_markdown(index=False)}

# Top 20 Category Opportunities
{df_categories.to_markdown(index=False)}
"""

with open('runs/2026-03-04__portfolio-competitiveness/Opportunity_Timing_Bubble_Chart_Category.png', 'rb') as f:
    b64_image = base64.b64encode(f.read()).decode('utf-8')

prompt = """
You are acting as a skeptical, highly experienced contracting director. This attached chart and data tables will be used to set your performance targets for the upcoming year's supply chain negotiations. You have a vested interest in questioning and evaluating the data for inconsistencies, mathematical impossibilities, or visual misrepresentations that might make your targets unfairly high, unrealistic, or confusing to interpret.

Analyze the provided data (markdown tables) and the visualization (image) and look for:
1. Mathematical anomalies (e.g., Savings > Benchmarked Spend, impossible percentages, inconsistent aggregation).
2. Data consistency between the chart and the tables. (Are the biggest bubbles truly mapping to the highest opportunity in the table? Do the dates and percentages map correctly to what is seen in the visualization labels?)
3. Outliers that might heavily skew the results.
4. Business logic & methodological concerns from your perspective as a sourcing director setting negotiation strategy.

Provide a detailed QA response directly confronting the analyst who produced this. Summarize your findings in a direct, clear list. Be highly critical but constructively analytic, focusing aggressively on data integrity.
"""

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": context_text + "\n\n" + prompt
            },
            {
                "type": "input_image",
                "image_url": "data:image/png;base64," + b64_image
            }
        ]
    }
]

instructions, input_data = client.conversation_to_responses_input(messages)
print("Querying GPT-5.4...")
res = client.create_response(input_data=input_data, instructions=instructions, reasoning_effort="low", timeout_s=300, max_output_tokens=8192)
out_text = client.extract_output_text(res)
print("\n" + "="*80 + "\n")
with open("runs/2026-03-04__portfolio-competitiveness/scratchpad/qa_results.txt", "w") as f:
    f.write(out_text)
print(out_text)