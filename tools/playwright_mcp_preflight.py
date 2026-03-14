from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


DEFAULT_CONFIG = Path(".vscode/mcp.json")
KNOWN_PLAYWRIGHT_BINS = {"playwright-mcp", "mcp-server-playwright"}


def _strip_jsonc(raw: str) -> str:
    raw = re.sub(r"/\*.*?\*/", "", raw, flags=re.DOTALL)
    raw = re.sub(r"(^|\s)//.*$", "", raw, flags=re.MULTILINE)
    return raw


def _load_jsonc(path: Path) -> Dict[str, Any]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return json.loads(_strip_jsonc(text))


def _discover_package_bins(timeout_s: int = 12) -> Optional[List[str]]:
    try:
        proc = subprocess.run(
            ["npm", "view", "@playwright/mcp", "bin", "--json"],
            capture_output=True,
            text=True,
            timeout=timeout_s,
            check=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None

    if proc.returncode != 0:
        return None

    stdout = (proc.stdout or "").strip()
    if not stdout:
        return None

    try:
        parsed = json.loads(stdout)
    except json.JSONDecodeError:
        return None

    if isinstance(parsed, dict):
        # npm returns { "bin-name": "path/to/cli.js" }; we care about bin names.
        return sorted(str(k) for k in parsed.keys())
    if isinstance(parsed, list):
        return sorted(str(v) for v in parsed)
    if isinstance(parsed, str):
        return [parsed]
    return None


def _find_playwright_server(cfg: Dict[str, Any]) -> Optional[Tuple[str, Dict[str, Any]]]:
    servers = cfg.get("servers")
    if not isinstance(servers, dict):
        return None

    if "playwright" in servers and isinstance(servers["playwright"], dict):
        return "playwright", servers["playwright"]

    for server_id, server in servers.items():
        if not isinstance(server, dict):
            continue
        args = server.get("args")
        if not isinstance(args, list):
            continue
        args_text = " ".join(str(a) for a in args)
        if "@playwright/mcp" in args_text or any(str(a) in KNOWN_PLAYWRIGHT_BINS for a in args):
            return str(server_id), server

    return None


def _check(server_id: str, server: Dict[str, Any], package_bins: Optional[List[str]]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    command = str(server.get("command") or "").strip()
    args = server.get("args")
    if not isinstance(args, list):
        errors.append(f"Server '{server_id}' is missing a valid args array.")
        return errors, warnings

    args_str = [str(a) for a in args]

    if command != "npx":
        warnings.append(
            f"Server '{server_id}' command is '{command}' (expected 'npx' for @playwright/mcp package workflow)."
        )

    package_declared = any("@playwright/mcp" in a for a in args_str)
    if not package_declared:
        warnings.append(f"Server '{server_id}' args do not reference @playwright/mcp package.")

    found_bin = next((a for a in args_str if a in KNOWN_PLAYWRIGHT_BINS), None)
    if not found_bin:
        errors.append(
            f"Server '{server_id}' args do not include a known Playwright MCP binary ({sorted(KNOWN_PLAYWRIGHT_BINS)})."
        )

    if package_bins and found_bin and found_bin not in package_bins:
        errors.append(
            f"Configured binary '{found_bin}' is not currently published for @playwright/mcp. "
            f"Published bins: {package_bins}."
        )

    if package_bins and "playwright-mcp" in package_bins and found_bin == "mcp-server-playwright":
        warnings.append(
            "Legacy binary 'mcp-server-playwright' detected; published package supports 'playwright-mcp'. "
            "Consider switching to reduce startup failures."
        )

    if "--user-data-dir" not in args_str:
        warnings.append("Missing '--user-data-dir' (recommended for per-run browser-state isolation).")
    if "--output-dir" not in args_str:
        warnings.append("Missing '--output-dir' (recommended for per-run artifact isolation).")

    return errors, warnings


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preflight-check Playwright MCP config for binary compatibility and run isolation flags."
    )
    parser.add_argument(
        "--file",
        default=str(DEFAULT_CONFIG),
        help="Path to MCP config JSON/JSONC file (default: .vscode/mcp.json)",
    )
    parser.add_argument(
        "--skip-npm-bin-check",
        action="store_true",
        help="Skip npm package bin discovery (offline mode).",
    )
    args = parser.parse_args(argv)

    cfg_path = Path(args.file).expanduser().resolve()
    if not cfg_path.exists():
        print(f"ERROR: Config file not found: {cfg_path}")
        return 2

    try:
        cfg = _load_jsonc(cfg_path)
    except Exception as exc:
        print(f"ERROR: Failed to parse config as JSON/JSONC: {cfg_path}\n{exc}")
        return 2

    match = _find_playwright_server(cfg)
    if not match:
        print("ERROR: Could not find a Playwright server entry in MCP config.")
        return 2

    server_id, server = match
    package_bins = None if args.skip_npm_bin_check else _discover_package_bins()

    errors, warnings = _check(server_id, server, package_bins)

    print(f"Playwright MCP preflight: {cfg_path}")
    print(f"Server: {server_id}")
    if package_bins:
        print(f"Published bins (@playwright/mcp): {', '.join(package_bins)}")
    elif not args.skip_npm_bin_check:
        print("Published bins (@playwright/mcp): unavailable (npm/network not reachable)")

    if warnings:
        print("\nWarnings:")
        for w in warnings:
            print(f"- {w}")

    if errors:
        print("\nErrors:")
        for e in errors:
            print(f"- {e}")
        return 1

    print("\nOK: Playwright MCP config passed preflight checks.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
