from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agent_tools.llm.azure_openai_responses import (
    AzureOpenAIResponsesClient,
    AzureResponsesClientConfig,
)
from agent_tools.llm.env import load_repo_dotenv, read_azure_openai_env
from agent_tools.llm.model_registry import load_models_config


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _resolve_azure_config(*, model_name: str) -> AzureResponsesClientConfig:
    repo_root = _repo_root()
    load_repo_dotenv(repo_root)

    env = read_azure_openai_env()
    models = load_models_config(repo_root)
    model = models.get(model_name)

    api_key = env.api_key
    if not api_key:
        raise RuntimeError("Missing AZURE_OPENAI_KEY. Add it to your local .env (do not commit).")

    deployment_name = (model.deployment_name if model else None) or env.deployment_name
    if not deployment_name:
        raise RuntimeError(
            "Missing deployment name. Set AZURE_OPENAI_DEPLOYMENT or configure config/models.json."
        )

    # Prefer explicit Responses URL.
    candidate_url = (model.api_url if model else None) or env.responses_api_url or env.api_url
    if not candidate_url:
        raise RuntimeError(
            "Missing Azure Responses API URL. Set AZURE_OPENAI_RESPONSES_URL or configure config/models.json."
        )

    if "/openai/responses" not in candidate_url:
        raise RuntimeError(
            "Azure URL does not look like a Responses API endpoint (expected path contains /openai/responses). "
            "Set AZURE_OPENAI_RESPONSES_URL to a Responses API URL."
        )

    max_output_tokens = (model.max_output_tokens if model else None) or 2048
    reasoning_effort = (model.reasoning_effort if model else None) or "medium"

    return AzureResponsesClientConfig(
        api_key=api_key,
        responses_api_url=candidate_url,
        deployment_name=deployment_name,
        max_output_tokens=int(max_output_tokens),
        reasoning_effort=reasoning_effort,  # type: ignore[arg-type]
    )


def _write_run_artifact(*, run_id: str, record: dict[str, Any]) -> Path:
    repo_root = _repo_root()
    out_dir = repo_root / "runs" / run_id / "exports" / "llm"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / "azure_gpt52_smoketest.jsonl"
    with out_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Azure OpenAI GPT-5.2 smoke test (Responses API)")
    parser.add_argument("--model", default="azure-gpt-5.2", help="Model key in config/models.json")
    parser.add_argument("--prompt", help="User prompt. If omitted, reads from stdin.")
    parser.add_argument("--instructions", help="Optional system instructions")
    parser.add_argument(
        "--run-id",
        help="If set, writes a JSONL record under runs/<RUN_ID>/exports/llm/.",
    )
    args = parser.parse_args()

    prompt = args.prompt
    if prompt is None:
        # Avoid hanging when invoked interactively with no stdin.
        # If stdin is piped, read it; otherwise use a default prompt.
        if sys.stdin is not None and sys.stdin.isatty():
            prompt = "ping"
        else:
            prompt = sys.stdin.read()
            if not prompt.strip():
                prompt = "ping"

    cfg = _resolve_azure_config(model_name=args.model)
    client = AzureOpenAIResponsesClient(cfg)

    messages = []
    if args.instructions:
        messages.append({"role": "system", "content": args.instructions})
    messages.append({"role": "user", "content": prompt})

    instructions, input_text = client.conversation_to_responses_input(messages)

    result = client.create_response(
        input_text=input_text,
        instructions=instructions,
        max_output_tokens=cfg.max_output_tokens,
        reasoning_effort=cfg.reasoning_effort,
    )
    output_text = client.extract_output_text(result)

    print(output_text)

    if args.run_id:
        record = {
            "model": args.model,
            "config": {**asdict(cfg), "api_key": "<redacted>"},
            "messages": messages,
            "output_text": output_text,
            "raw_result": result,
        }
        out_path = _write_run_artifact(run_id=args.run_id, record=record)
        print(f"\nWrote: {out_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
