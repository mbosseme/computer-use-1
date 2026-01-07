import os
import requests
import json
from dotenv import load_dotenv

# Load env variables from a repo-root .env file if present
load_dotenv()

class AzureOpenAIResponsesClient:
    """
    Minimal run-local client for Azure OpenAI Responses API (GPT-5.2).
    Follows the specification in docs/GPT_5_2_INTEGRATION_GUIDE.md.
    """
    def __init__(self, api_key=None, api_url=None, deployment_name=None):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_KEY")
        self.api_url = api_url or os.getenv("AZURE_OPENAI_RESPONSES_URL")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT")

        # Validate configuration
        if not self.api_key:
            raise ValueError("AZURE_OPENAI_KEY is required.")
        if not self.api_url:
            raise ValueError("AZURE_OPENAI_RESPONSES_URL is required.")
        if not self.deployment_name:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is required.")
            
        # Ensure URL is correct for Responses API
        if "/openai/responses" not in self.api_url:
            print(f"WARNING: The provided URL '{self.api_url}' does not look like a Responses API URL.")

    def chat(
        self,
        messages,
        max_output_tokens=16384,
        reasoning_effort="medium",
        additional_payload=None,
        timeout_s: int = 180,
    ):
        """
        Sends a chat conversion to the Azure Responses API.
        
        Args:
            messages: List of dicts [{"role": "user", "content": ...}]
            max_output_tokens: Max tokens for the response.
            reasoning_effort: "low", "medium", or "high".
            additional_payload: Dict of extra fields to merge into payload (e.g. temperature).
            
        Returns:
            The extracted text content of the assistant's response.
        """
        
        # 1. Convert messages to Responses API input format
        # First system message became "instructions", the rest is a text transcript.
        instructions = ""
        input_text = ""
        
        start_idx = 0
        if messages and messages[0]["role"] == "system":
            instructions = messages[0]["content"]
            start_idx = 1
            
        # Transcript builder
        # For the Responses API, if we have multimodal content (images),
        # we try to pass the user content list directly to "input".
        
        last_msg = messages[-1]
        payload_input = ""
        
        # Check if we can do the simple System + User pattern
        if len(messages) >= 1 and last_msg["role"] == "user" and isinstance(last_msg["content"], list):
            # Pass the list of messages directly (Multimodal support).
            # The Responses API uses specific content types: 'input_text', 'input_image'.
            # We must map standard OpenAI types ('text', 'image_url') to these values.
            
            transformed_content = []
            for part in last_msg["content"]:
                new_part = part.copy()
                if part.get("type") == "text":
                    new_part["type"] = "input_text"
                elif part.get("type") == "image_url":
                    new_part["type"] = "input_image"
                    # Flatten the image_url object to a string if it's a dict
                    if isinstance(part.get("image_url"), dict):
                         new_part["image_url"] = part["image_url"].get("url")
                transformed_content.append(new_part)
                
            # Construct the message object with transformed content
            payload_input = [{"role": "user", "content": transformed_content}]
        else:
            # Fallback for text-only transcript construction
            for msg in messages[start_idx:]:
                content = msg["content"]
                if isinstance(content, list):
                    text_parts = []
                    for part in content:
                        if isinstance(part, str):
                            text_parts.append(part)
                        elif part.get("type") == "text":
                            text_parts.append(part["text"])
                        elif part.get("type") == "image_url":
                            text_parts.append("[IMAGE]")
                    payload_input += f"{msg['role'].capitalize()}: {' '.join(text_parts)}\n"
                else:
                    payload_input += f"{msg['role'].capitalize()}: {content}\n"

        # 2. Build Payload
        payload = {
            "model": self.deployment_name,
            "input": payload_input, # Trying text-only first based on guide
            "max_output_tokens": max_output_tokens,
            "stream": False,
            "reasoning": {"effort": reasoning_effort}
        }
        
        if instructions:
            payload["instructions"] = instructions

        if additional_payload:
            payload.update(additional_payload)

        # 3. Send Request
        headers = {
            "api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=timeout_s)
            response.raise_for_status()
            result = response.json()
            print(f"DEBUG: Raw API Response: {json.dumps(result, indent=2)}") 
            return self._extract_output(result)
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            print(f"API Request Failed: {e}")
            raise

    def _extract_output(self, result):
        """
        Parses the Responses API result.
        """
        if "output_text" in result:
            return result["output_text"]
        
        # Fallback: parse output array
        output_content = ""
        if "output" in result and isinstance(result["output"], list):
            for item in result["output"]:
                # The item itself is the message object in recent versions
                # Check for content directly on item
                content_list = item.get("content", [])
                
                # Also check if it's nested under "message" (older format?)
                if "message" in item:
                    content_list = item["message"].get("content", [])

                for part in content_list:
                    if part.get("type") == "text":
                        output_content += part.get("text", "")
                    elif part.get("type") == "output_text":
                        output_content += part.get("text", "")
        
        return output_content
