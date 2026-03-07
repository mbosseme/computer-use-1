"""Find all messages in the HCIQ Beta Workbook thread."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import search_messages

env = load_graph_env(ROOT)
auth = GraphAuthenticator(repo_root=ROOT, env=env)
client = GraphAPIClient(
    authenticator=auth,
    config=GraphClientConfig(
        base_url=env.base_url,
        scopes=env.scopes,
        planner_timezone=env.planner_timezone,
    ),
)

results = search_messages(
    client,
    query='"Healthcare IQ Benchmark Analysis"',
    top=20,
)

thread = [r for r in results if "Healthcare IQ Benchmark Analysis" in r.get("subject", "")]
for r in thread:
    subj = r.get("subject", "")
    dt = r.get("receivedDateTime") or r.get("sentDateTime")
    frm = (r.get("from") or {}).get("emailAddress", {}).get("address", "")
    msg_id = r.get("id", "")
    print(f"Subject: {subj}")
    print(f"Date: {dt}")
    print(f"From: {frm}")
    print(f"ID: {msg_id}")
    print()
