"""Auth & Environment Diagnostics for BigQuery.

Run: python -m tests.test_auth_diagnostics

Checks:
1. CA bundle environment variables (REQUESTS_CA_BUNDLE / SSL_CERT_FILE) present & readable
2. ADC credentials file existence & readable JSON
3. google.auth.default() loads credentials & project id
4. Optional BigQuery client init + 1-row test query (skips if bigquery import missing)

Exit code is non-zero if any required step fails.
"""
from __future__ import annotations

import json
import os
import sys
import textwrap
from pathlib import Path
from typing import List


def fail(msg: str) -> None:
    print(f"[FAIL] {msg}")
    sys.exit(1)


def warn(msg: str) -> None:
    print(f"[WARN] {msg}")


def ok(msg: str) -> None:
    print(f"[ OK ] {msg}")


def check_ca_bundle() -> None:
    paths: List[str] = []
    for var in ("REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        val = os.getenv(var)
        if val:
            paths.append(val)
            if Path(val).is_file():
                ok(f"{var} -> {val}")
            else:
                fail(f"{var} set but file missing: {val}")
        else:
            warn(f"{var} not set (may be fine if corporate TLS interception not in use)")
    # If one is set ensure they point to same file (consistency)
    if len(paths) == 2 and paths[0] != paths[1]:
        warn("REQUESTS_CA_BUNDLE and SSL_CERT_FILE differ; consider unifying")


def check_adc_file() -> Path | None:
    adc_path = Path.home() / ".config/gcloud/application_default_credentials.json"
    if not adc_path.exists():
        fail("ADC credentials file not found. Run: gcloud auth application-default login")
    data = {}
    try:
        data = json.loads(adc_path.read_text())
    except Exception as e:  # pragma: no cover (corruption edge)
        fail(f"ADC file unreadable JSON: {e}")
    required = ["client_id", "client_secret"]
    missing = [k for k in required if k not in data]
    if missing:
        warn(f"ADC file missing expected keys: {missing}")
    ok(f"ADC file present ({adc_path}) size={adc_path.stat().st_size} bytes")
    return adc_path


def check_google_auth() -> str | None:
    try:
        import google.auth  # type: ignore
    except Exception as e:  # pragma: no cover - dependency edge
        fail(f"google-auth import failed: {e}")
    creds, project_id = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])  # type: ignore
    if not project_id:
        warn("google.auth.default() returned no project_id; ensure BIGQUERY_PROJECT_ID set or gcloud config project set")
    else:
        ok(f"google.auth.default() project={project_id}")
    # Refresh token quickly to surface issues
    try:
        creds.refresh(request=__import__("google.auth.transport.requests").auth.transport.requests.Request())  # type: ignore
        ok("Credential refresh succeeded")
    except Exception as e:  # pragma: no cover
        fail(f"Credential refresh failed: {e}")
    return project_id


def check_bigquery(project_id: str | None) -> None:
    try:
        from google.cloud import bigquery  # type: ignore
    except Exception:
        warn("google-cloud-bigquery not installed; skipping BQ test")
        return
    client = None
    try:
        client = bigquery.Client(project=project_id or None)  # type: ignore
        ok("BigQuery client initialized")
    except Exception as e:  # pragma: no cover
        fail(f"BigQuery client init failed: {e}")
    try:
        assert client is not None
        rows = list(client.query("SELECT 1 AS ok").result())
        if len(rows) == 1 and getattr(rows[0], "ok", None) == 1:
            ok("Test query returned 1 row")
        else:
            fail("Unexpected test query result shape")
    except Exception as e:  # pragma: no cover
        fail(f"Test query failed: {e}")


def main() -> None:
    print("== Auth Diagnostics ==")
    check_ca_bundle()
    check_adc_file()
    project_id = check_google_auth()
    check_bigquery(project_id)
    print("All diagnostics passed.")


if __name__ == "__main__":  # pragma: no cover
    main()
