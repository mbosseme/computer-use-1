**API SKILL** — Interact with the Microsoft Graph API using the local agent wrappers. USE FOR: sending emails, searching mailbox history, downloading attachments. DO NOT USE FOR: standard web retrieval.

### Strict Instantiation Rules
The `GraphAuthenticator` and `GraphAPIClient` wrappers require strict explicit keyword arguments. You **must** pass `repo_root` and `env`. Positional arguments will cause Python `TypeErrors` and crash.

```python
from pathlib import Path
from agent_tools.graph.client import GraphAPIClient, GraphClientConfig
from agent_tools.graph.auth import GraphAuthenticator
from agent_tools.graph.env import load_graph_env

repo_root = Path('.')
env = load_graph_env(repo_root)
client_config = GraphClientConfig(base_url=env.base_url, scopes=env.scopes, planner_timezone=env.planner_timezone)
auth = GraphAuthenticator(repo_root=repo_root, env=env)
client = GraphAPIClient(authenticator=auth, config=client_config)
```

### KQL Escaping (400 BadRequest Prevention)
The Graph API uses Keyword Query Language (KQL) for the `$search` parameter. If you search for strings containing special characters (`-`, `&`, `:`, etc.) without enclosing them in double-quotes, the API will fail with a `400 BadRequest (Syntax error)`. 
* **Safe:** `search_messages(client, query='"Healthcare IQ - Beta"')`
* **Unsafe:** `search_messages(client, query='Healthcare IQ - Beta')`
*(Note: Recent updates to `search_messages` include an `auto_escape=True` parameter which attempts to fix this automatically, but being aware of KQL rules remains important).*

### Email Body Extraction
Do not rely on `bodyPreview` as it truncates text. Extract the raw HTML from `msg['body']['content']` and use `bs4.BeautifulSoup` or the local wrapper `html_to_text(html_str)` to strip it down to plain text. Always write giant payloads to a temporary file via `.txt` and read it rather than printing to stdout.

You can also use the helper function `get_clean_body(msg)` available in `agent_tools.graph.mail_search` which safely extracts and cleans the text natively without boilerplate.