from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from msal import PublicClientApplication, SerializableTokenCache

from agent_tools.graph.env import GraphEnv


def _jwt_claims_without_verify(access_token: str) -> dict[str, Any]:
    """Best-effort decode of JWT payload for diagnostics (no signature verification)."""

    try:
        import base64

        parts = access_token.split(".")
        if len(parts) < 2:
            return {}
        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload.encode("utf-8"))
        return json.loads(decoded.decode("utf-8"))
    except Exception:
        return {}


@dataclass
class TokenResult:
    access_token: str
    scp: Optional[str]


class GraphAuthenticator:
    def __init__(self, *, repo_root: Path, env: GraphEnv):
        self._repo_root = repo_root
        self._env = env

        self._cache_path = self._resolve_cache_path(env.token_cache_file)
        self._cache = SerializableTokenCache()
        if self._cache_path.exists():
            self._cache.deserialize(self._cache_path.read_text(encoding="utf-8"))

        self._app = PublicClientApplication(
            client_id=env.client_id,
            authority=env.authority_url,
            token_cache=self._cache,
        )

    def _resolve_cache_path(self, cache_file: str) -> Path:
        p = Path(cache_file)
        return p if p.is_absolute() else (self._repo_root / p)

    def _save_cache(self) -> None:
        if self._cache.has_state_changed:
            self._cache_path.write_text(self._cache.serialize(), encoding="utf-8")

    def acquire_access_token(self, *, scopes: list[str], timeout_s: int = 600) -> TokenResult:
        """Acquire token silently if possible, else via interactive loopback."""

        accounts = self._app.get_accounts()
        if accounts:
            result = self._app.acquire_token_silent(scopes, account=accounts[0])
            token = self._extract_token(result)
            if token:
                claims = _jwt_claims_without_verify(token)
                return TokenResult(access_token=token, scp=claims.get("scp"))

        result = self._app.acquire_token_interactive(
            scopes=scopes,
            prompt="select_account",
            timeout=timeout_s,
        )
        token = self._extract_token(result)
        if not token:
            raise RuntimeError(f"Failed to obtain Graph access token: {result}")

        self._save_cache()
        claims = _jwt_claims_without_verify(token)
        return TokenResult(access_token=token, scp=claims.get("scp"))

    @staticmethod
    def _extract_token(result: Any) -> Optional[str]:
        if isinstance(result, dict) and isinstance(result.get("access_token"), str):
            return result["access_token"]
        return None
