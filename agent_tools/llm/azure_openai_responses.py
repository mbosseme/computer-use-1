from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Literal, Optional

import requests

ReasoningEffort = Literal["minimal", "low", "medium", "high"]


@dataclass(frozen=True)
class AzureResponsesClientConfig:
    api_key: str
    responses_api_url: str
    deployment_name: str

    # Defaults are conservative; callers can override.
    max_output_tokens: int = 2048
    reasoning_effort: ReasoningEffort = "medium"


class AzureOpenAIResponsesClient:
    """Minimal Azure OpenAI Responses API client.

    Designed as a starter building block for computer-use agent runs.
    """

    def __init__(self, config: AzureResponsesClientConfig):
        self._config = config

    def create_response(
        self,
        *,
        input_text: str,
        instructions: Optional[str] = None,
        max_output_tokens: Optional[int] = None,
        reasoning_effort: Optional[ReasoningEffort] = None,
        timeout_s: float = 90,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": self._config.deployment_name,
            "input": input_text,
            "max_output_tokens": int(max_output_tokens or self._config.max_output_tokens),
            "stream": False,
        }

        if instructions:
            payload["instructions"] = instructions

        effort = reasoning_effort or self._config.reasoning_effort
        payload["reasoning"] = {"effort": self._map_reasoning_effort(effort)}

        headers = {
            "api-key": self._config.api_key,
            "Content-Type": "application/json",
        }

        started = time.time()
        resp = requests.post(
            self._config.responses_api_url,
            headers=headers,
            data=json.dumps(payload),
            timeout=timeout_s,
        )

        duration_s = time.time() - started
        if resp.status_code >= 400:
            raise RuntimeError(
                "Azure OpenAI request failed "
                f"({resp.status_code}) after {duration_s:.2f}s: {resp.text}"
            )

        return resp.json()

    @staticmethod
    def extract_output_text(result: dict[str, Any]) -> str:
        """Extract assistant text from a Responses API result."""

        if isinstance(result.get("output_text"), str):
            return result["output_text"]

        # Fallback: parse output[] array shapes.
        output = result.get("output")
        if not isinstance(output, list):
            return ""

        parts: list[str] = []
        for item in output:
            if not isinstance(item, dict):
                continue

            # Common shape: {"type": "message", "content": [{"type": "output_text", "text": "..."}]}
            content = item.get("content")
            if isinstance(content, list):
                for c in content:
                    if not isinstance(c, dict):
                        continue
                    if c.get("type") in {"output_text", "text"} and isinstance(c.get("text"), str):
                        parts.append(c["text"])

        return "".join(parts).strip()

    @staticmethod
    def conversation_to_responses_input(messages: list[dict[str, Any]]) -> tuple[Optional[str], str]:
        """Convert chat-style messages to (instructions, input transcript).

        - First system message becomes instructions
        - The rest become a plain text transcript:
            User: ...\nAssistant: ...
        """

        instructions: Optional[str] = None
        transcript_lines: list[str] = []

        for msg in messages:
            role = msg.get("role")
            content = msg.get("content")
            if role not in {"system", "user", "assistant"}:
                continue

            if role == "system" and instructions is None:
                if isinstance(content, str):
                    instructions = content
                continue

            if not isinstance(content, str):
                continue

            prefix = "User" if role == "user" else "Assistant"
            transcript_lines.append(f"{prefix}: {content}")

        return instructions, "\n".join(transcript_lines).strip()

    @staticmethod
    def _map_reasoning_effort(effort: ReasoningEffort) -> Literal["low", "medium", "high"]:
        # Azure Responses API effort does not accept "minimal"; map it down.
        if effort == "minimal":
            return "low"
        if effort == "low":
            return "low"
        if effort == "high":
            return "high"
        return "medium"
