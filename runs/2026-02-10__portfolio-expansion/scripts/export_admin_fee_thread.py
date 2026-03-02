from pathlib import Path
import json

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import export_thread_markdown, search_messages


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    run_id = "2026-02-10__portfolio-expansion"

    out_dir = repo / "runs" / run_id / "exports" / "m365_threads"
    out_dir.mkdir(parents=True, exist_ok=True)

    subject = "Re: Admin Fee Data Discovery"
    out_md = out_dir / "re_admin_fee_data_discovery.md"

    env = load_graph_env(repo)
    auth = GraphAuthenticator(repo_root=repo, env=env)
    client = GraphAPIClient(
        authenticator=auth,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )

    export_thread_markdown(
        client,
        subject=subject,
        out_path=out_md,
        max_messages=120,
        timeout_s=120,
    )

    query = '"Admin Fee Data Discovery" OR "admin fee rate" OR "raw data collection"'
    msgs = search_messages(client, query=query, top=50, max_messages=200, timeout_s=120)

    keep = []
    for message in msgs:
        message_subject = message.get("subject") or ""
        body_preview = message.get("bodyPreview") or ""
        text = f"{message_subject} {body_preview}".lower()
        if "admin fee" in text or "data discovery" in text:
            from_info = (message.get("from") or {}).get("emailAddress") or {}
            keep.append(
                {
                    "subject": message_subject,
                    "from": from_info.get("address"),
                    "from_name": from_info.get("name"),
                    "receivedDateTime": message.get("receivedDateTime"),
                    "sentDateTime": message.get("sentDateTime"),
                    "conversationId": message.get("conversationId"),
                    "bodyPreview": body_preview,
                }
            )

    keep = keep[:80]
    meta_path = repo / "runs" / run_id / "exports" / "admin_fee_discovery_graph_hits.json"
    meta_path.write_text(json.dumps(keep, indent=2), encoding="utf-8")

    print(out_md)
    print(meta_path)
    print(f"kept={len(keep)}")


if __name__ == "__main__":
    main()
