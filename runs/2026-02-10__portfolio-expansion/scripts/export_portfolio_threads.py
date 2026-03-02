from pathlib import Path

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import export_thread_markdown


def safe_name(subject: str) -> str:
    name = subject.lower()
    for old, new in [("/", "_"), (":", ""), (" ", "_")]:
        name = name.replace(old, new)
    while "__" in name:
        name = name.replace("__", "_")
    return f"{name}.md"


def main() -> None:
    repo = Path(__file__).resolve().parents[3]
    out_dir = repo / "runs" / "2026-02-10__portfolio-expansion" / "exports" / "m365_threads"
    out_dir.mkdir(parents=True, exist_ok=True)

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

    subjects = [
        "Portfolio Expansion Update",
        "On/Off/Non-Contract Analysis",
        "Fusion Team Weekly Check-in",
        "Data to support Portfolio Expansion",
        "Extrapolating from Core HS Set",
        "Data and Analytics to support strategic initiatives",
    ]

    for subject in subjects:
        out_path = out_dir / safe_name(subject)
        try:
            export_thread_markdown(
                client,
                subject=subject,
                out_path=out_path,
                max_messages=80,
                timeout_s=120,
            )
            print(f"OK {subject} -> {out_path}")
        except Exception as exc:
            print(f"ERR {subject}: {exc}")


if __name__ == "__main__":
    main()
