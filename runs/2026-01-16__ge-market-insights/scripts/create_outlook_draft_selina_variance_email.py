from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running this script directly while still importing the repo package.
REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))

from agent_tools.graph.auth import GraphAuthenticator  # noqa: E402
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig  # noqa: E402
from agent_tools.graph.env import load_graph_env  # noqa: E402


def _build_html_body(*, recipient_first_name: str) -> str:
    # Keep this as a true draft email body: placeholders for your paste + chart.
    return """<p>Hi {recipient_first_name},</p>

<p>Wanted to follow up and let you know we’ve completed the variance analysis across the three priority categories (MRI, CT, and Physiological/Patient Monitoring). I’m going to paste the results directly in the body of this email below.</p>

<p><strong>[INSERT VARIANCE ANALYSIS CONTENT HERE]</strong></p>

<p>As a quick visual companion, here’s the seasonality comparison (indexed) between GE supplier-reported spend and the spend we extract from provider ERP transactions:</p>

<p><strong>[INSERT CHART IMAGE HERE — “Seasonality comparison (indexed): Supplier vs Provider-reported spend”]</strong></p>

<p><strong>Key takeaways (at the combined bucket level):</strong></p>
<ul>
  <li>The supplier-reported spend shows the pattern you expected: Q4 is higher volume relative to adjacent quarters.</li>
  <li>Overall, the supplier feed and provider ERP-extracted feed are well aligned directionally and show broadly consistent seasonality.</li>
  <li>The main divergence is a timing shift around the Q4→Q1 boundary (most visible from 2024 Q4 into 2025 Q1): the provider ERP-extracted spend peaks later (Q1 2025 appears higher than Q4 2024), while the supplier-reported view reflects more of that volume in Q4.</li>
  <li>Our working interpretation is that both can be “right,” but based on different timing conventions—for example, supplier spend is often invoice-aligned, while the provider ERP extraction can vary depending on how transactions are represented (e.g., invoice date vs payment/posting date).</li>
  <li>In Q4 2023, the two feeds aligned almost exactly.</li>
</ul>

<p>Mainly sharing this timing analysis to help build confidence in the dataset and to get your quick feedback on whether this interpretation lines up with what you’re seeing on your side.</p>

<p>Separately, we’re still working on the draft statement of work and should have that over to you shortly.</p>

<p>Best,<br/>Matt</p>
""".format(recipient_first_name=recipient_first_name)


def _graph_client(repo_root: Path) -> GraphAPIClient:
    env = load_graph_env(repo_root)
    authenticator = GraphAuthenticator(repo_root=repo_root, env=env)
    config = GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone)
    return GraphAPIClient(authenticator=authenticator, config=config)


def create_draft(*, to_address: str, to_name: str | None, subject: str, html_body: str) -> dict:
    client = _graph_client(REPO_ROOT)

    payload: dict = {
        "subject": subject,
        "body": {"contentType": "HTML", "content": html_body},
        "toRecipients": [
            {
                "emailAddress": {
                    "address": to_address,
                    **({"name": to_name} if to_name else {}),
                }
            }
        ],
    }

    # Creating a message under Drafts ensures it lands in the Drafts folder.
    return client.post("me/mailFolders('Drafts')/messages", json=payload)


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a draft email to Selina with variance analysis summary.")
    parser.add_argument("--to", default="Selina.Singh@gehealthcare.com")
    parser.add_argument("--to-name", default="Selina Singh")
    parser.add_argument(
        "--subject",
        default="Variance Analysis Complete — Supplier vs Provider-Reported Spend (MRI/CT/Monitoring)",
    )
    parser.add_argument("--recipient-first-name", default="Selina")

    args = parser.parse_args()

    html_body = _build_html_body(recipient_first_name=args.recipient_first_name)
    draft = create_draft(to_address=args.to, to_name=args.to_name, subject=args.subject, html_body=html_body)

    # Avoid printing deep links; confirm via metadata only.
    draft_id = draft.get("id")
    created = draft.get("createdDateTime")

    print("Draft created in Outlook Drafts.")
    print(f"- Subject: {args.subject}")
    if created:
        print(f"- Created: {created}")
    if draft_id:
        print(f"- Draft ID: {draft_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
