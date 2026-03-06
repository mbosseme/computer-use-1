from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List

from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.env import load_graph_env
from agent_tools.graph.mail_search import search_messages_query_api


REPO_ROOT = Path(__file__).resolve().parents[3]
OUT_JSON = REPO_ROOT / "runs" / "2026-03-02__orchestrator" / "exports" / "ai_high_contribution_candidates.json"
OUT_MD = REPO_ROOT / "runs" / "2026-03-02__orchestrator" / "exports" / "ai_high_contribution_candidates.md"


QUERIES = [
    "GitHub Copilot time saved production deployed",
    "AI automation reduced manual effort improved accuracy",
    "Copilot use case accelerated root-cause analysis",
    "AI agent saved team time revenue decision",
    "automated dashboard deployed PROD issue detection",
    "AI workshop business impact productivity",
    "LLM prototype delivered in hours days",
    "automation script reduced cycle time",
]


IMPACT_TERMS = [
    "saved",
    "reduced",
    "accelerated",
    "improved",
    "deployed",
    "production",
    "accuracy",
    "revenue",
    "risk",
    "hours",
    "days",
    "60%",
    "45 mins",
    "20 hours",
]


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


def pick_sender(msg: Dict[str, Any]) -> str:
    f = msg.get("from")
    if isinstance(f, dict):
        ea = f.get("emailAddress")
        if isinstance(ea, dict):
            return str(ea.get("address") or "")
    return ""


def pick_name(msg: Dict[str, Any]) -> str:
    f = msg.get("from")
    if isinstance(f, dict):
        ea = f.get("emailAddress")
        if isinstance(ea, dict):
            return str(ea.get("name") or "")
    return ""


def is_internal(addr: str) -> bool:
    a = (addr or "").lower()
    return a.endswith("@premierinc.com")


def score(msg: Dict[str, Any]) -> int:
    text = f"{msg.get('subject','')} {msg.get('bodyPreview','')}".lower()
    s = 0
    for term in IMPACT_TERMS:
        if term in text:
            s += 1
    return s


def to_row(msg: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": msg.get("id"),
        "subject": msg.get("subject"),
        "receivedDateTime": msg.get("receivedDateTime") or msg.get("sentDateTime"),
        "sender": pick_sender(msg),
        "sender_name": pick_name(msg),
        "bodyPreview": msg.get("bodyPreview", ""),
        "score": score(msg),
    }


def main() -> None:
    client = build_client(REPO_ROOT)

    by_id: Dict[str, Dict[str, Any]] = {}
    for q in QUERIES:
        msgs = search_messages_query_api(client, query=q, size=80)
        for m in msgs:
            mid = str(m.get("id") or "")
            if not mid:
                # Search API may omit id even when requested; use a stable fallback key.
                mid = "|".join(
                    [
                        str(m.get("receivedDateTime") or m.get("sentDateTime") or ""),
                        str(m.get("subject") or ""),
                        pick_sender(m),
                    ]
                )
            row = to_row(m)
            if mid not in by_id or row["score"] > by_id[mid]["score"]:
                by_id[mid] = row

    all_rows = list(by_id.values())
    internal_rows = [r for r in all_rows if is_internal(r["sender"])]
    internal_rows.sort(key=lambda r: (r["score"], str(r.get("receivedDateTime") or "")), reverse=True)

    # Group by employee to identify repeated impact evidence.
    by_sender: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    for r in internal_rows:
        by_sender[r["sender"]].append(r)

    summary = []
    for sender, rows in by_sender.items():
        top_rows = sorted(rows, key=lambda r: r["score"], reverse=True)[:5]
        avg_score = round(sum(r["score"] for r in top_rows) / max(1, len(top_rows)), 2)
        summary.append(
            {
                "sender": sender,
                "sender_name": top_rows[0].get("sender_name", ""),
                "evidence_count": len(rows),
                "avg_top_score": avg_score,
                "top_subjects": [r.get("subject") for r in top_rows],
                "top_samples": [
                    {
                        "subject": r.get("subject"),
                        "receivedDateTime": r.get("receivedDateTime"),
                        "score": r.get("score"),
                        "bodyPreview": (r.get("bodyPreview") or "")[:260],
                    }
                    for r in top_rows
                ],
            }
        )

    summary.sort(key=lambda x: (x["evidence_count"], x["avg_top_score"]), reverse=True)

    OUT_JSON.write_text(
        json.dumps(
            {
                "query_count": len(QUERIES),
                "total_unique_messages": len(all_rows),
                "internal_unique_messages": len(internal_rows),
                "employee_summary": summary[:30],
                "top_internal_messages": internal_rows[:120],
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("# AI High-Contribution Candidate Scan (Internal Employees)")
    lines.append("")
    lines.append(f"Total unique messages: {len(all_rows)}")
    lines.append(f"Internal employee messages: {len(internal_rows)}")
    lines.append("")
    lines.append("## Top Employee Candidates")
    for i, s in enumerate(summary[:15], start=1):
        lines.append(
            f"{i}. {s.get('sender_name') or '(name missing)'} <{s['sender']}> | evidence={s['evidence_count']} | avg_top_score={s['avg_top_score']}"
        )
        for t in s["top_samples"][:3]:
            lines.append(f"   - {t['receivedDateTime']} | score={t['score']} | {t['subject']}")
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT_JSON}")
    print(f"Wrote {OUT_MD}")


if __name__ == "__main__":
    main()
