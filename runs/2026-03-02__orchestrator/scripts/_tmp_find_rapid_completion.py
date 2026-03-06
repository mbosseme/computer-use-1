from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import html_to_text, search_messages, search_sent_messages


QUERIES = [
    '"AI" (completed OR delivered OR build OR analysis) (days OR hours OR week OR weeks OR months)',
    '"Copilot" (days OR hours OR overnight OR turnaround OR timeline)',
    '"automation" (saved OR faster OR accelerated OR quick OR rapidly)',
    '"record time" OR "ahead of schedule" OR "in under"',
    '"weeks" "now" "days" (analysis OR deliverable OR project)',
    '"months" "now" "weeks" (build OR migration OR implementation)',
    '"script" (saved OR turnaround OR completed) (hours OR days)',
    '"LLM" OR "GPT" (prototype OR build OR delivered)',
]

def first_nonempty(*vals: str | None) -> str:
    for v in vals:
        if v and v.strip():
            return v.strip()
    return ''


def build_client(repo_root: Path) -> GraphAPIClient:
    env = load_graph_env(repo_root)
    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    return GraphAPIClient(
        authenticator=authenticator,
        config=GraphClientConfig(
            base_url=env.base_url,
            scopes=env.scopes,
            planner_timezone=env.planner_timezone,
        ),
    )


def main() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    client = build_client(repo_root)

    by_id: OrderedDict[str, dict] = OrderedDict()

    for q in QUERIES:
        print(f"\n=== QUERY: {q} ===")
        try:
            msgs = search_messages(client, query=q, folder='inbox', top=25, max_messages=60, timeout_s=90)
            msgs += search_sent_messages(client, query=q, top=25, max_messages=60, timeout_s=90)
        except Exception as exc:
            print(f"ERROR: {exc}")
            continue

        print(f"returned={len(msgs)}")
        for m in msgs[:8]:
            msg_id = m.get('id', '')
            if not msg_id:
                continue
            if msg_id not in by_id:
                body_text = html_to_text((m.get('body') or {}).get('content') or '')
                snippet = first_nonempty(m.get('bodyPreview'), body_text)
                by_id[msg_id] = {
                    'id': msg_id,
                    'subject': m.get('subject', ''),
                    'from': ((m.get('from') or {}).get('emailAddress') or {}).get('address', ''),
                    'receivedDateTime': m.get('receivedDateTime', ''),
                    'sentDateTime': m.get('sentDateTime', ''),
                    'conversationId': m.get('conversationId', ''),
                    'webLink': m.get('webLink', ''),
                    'snippet': (snippet or '').replace('\n', ' ')[:360],
                }

    print(f"\nTOTAL_UNIQUE={len(by_id)}")
    for i, item in enumerate(list(by_id.values())[:120], start=1):
        print(f"\n[{i}] {item['receivedDateTime']} | {item['subject']}")
        print(f"from={item['from']}")
        print(f"conversationId={item['conversationId']}")
        print(f"snippet={item['snippet']}")
        print(f"id={item['id']}")


if __name__ == '__main__':
    main()
