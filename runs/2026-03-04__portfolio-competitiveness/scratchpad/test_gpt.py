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

with open('runs/2026-03-04__portfolio-competitiveness/Opportunity_Timing_Bubble_Chart.png', 'rb') as f:
    b64_image = base64.b64encode(f.read()).decode('utf-8')

messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": "We are generating an 'Opportunity Timing Bubble Chart' to show top expiring contracts from a portfolio. X-axis is time until expiration, Y-axis is the % gap to a target benchmark price, and bubble size is annualized savings opportunity. Please act as a data visualization expert and give us some design feedback on this chart to make it more impactful, readable, and professional for an executive audience. We're about to refine the legend, the overlapping bubbles, and shorten the text labels further, but anything else you can point out would be great. Specifically call out grid lines, color scales, label placements, and formatting."
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
res = client.create_response(input_data=input_data, instructions=instructions, reasoning_effort="high", timeout_s=120)
print("\n" + "="*80 + "\n")
print(client.extract_output_text(res))
