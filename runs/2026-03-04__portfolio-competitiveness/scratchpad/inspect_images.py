import base64
import sys
from pathlib import Path
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.azure_openai_responses import AzureOpenAIResponsesClient, AzureResponsesClientConfig

repo_root = Path(__file__).resolve().parent
load_repo_dotenv(repo_root)
env = read_azure_openai_env()

config = AzureResponsesClientConfig(
    api_key=env.api_key,
    responses_api_url=env.responses_api_url,
    deployment_name=env.deployment_name,
    reasoning_effort="high"
)

client = AzureOpenAIResponsesClient(config)

def describe_image(img_path):
    print(f"--- Analyzing {img_path} ---", file=sys.stderr)
    
    with open(img_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        
    mime_type = "image/png" if img_path.endswith(".png") else "image/jpeg"
    data_uri = f"data:{mime_type};base64,{encoded_string}"

    msg = {
        "role": "user",
        "content": [
            {
                "type": "input_text",
                "text": "Please analyze this image, focusing on any charts, data tables, or visualizations.\n"
                        "Describe the:\n"
                        "1. Overall structure of the chart (e.g. axis, labels, legends)\n"
                        "2. Data presented, highlighting any key trends or anomalies\n"
                        "3. Formatting, particularly any color coding, bubble sizes, or annotations\n"
                        "4. Output specific text or labels you see."
            },
            {
                "type": "input_image",
                "image_url": data_uri
            }
        ]
    }
    
    instructions, input_data = AzureOpenAIResponsesClient.conversation_to_responses_input([msg])
    
    try:
        result = client.create_response(
            input_data=input_data,
            instructions=instructions,
            max_output_tokens=2048,
            reasoning_effort="high"
        )
        print(AzureOpenAIResponsesClient.extract_output_text(result))
    except Exception as e:
        print(f"Failed to analyze {img_path}: {e}")
    print("\n")

describe_image('inline_img_0.png')
describe_image('inline_img_1.png')
describe_image('inline_img_2.png')

