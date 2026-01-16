"""Document extraction and LLM call utilities for synthesis workflows.

This module provides reusable functions for:
- Extracting text from PDF and EML files
- Sanitizing text to remove potential secrets
- Calling LLM endpoints with retry/backoff logic

Usage:
    from agent_tools.llm.document_extraction import (
        extract_pdf_text,
        extract_eml_text,
        sanitize_text,
        call_with_retry,
    )
"""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Any, Optional

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None  # type: ignore


@dataclass(frozen=True)
class PdfPageExtraction:
    page_number: int  # 1-based
    text: str
    error: Optional[str] = None


def extract_pdf_text(file_path: Path, max_pages: Optional[int] = None) -> str:
    """Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file.
        max_pages: Optional limit on pages to extract (useful for large/redundant PDFs).

    Returns:
        Extracted text as a single string.
    """
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is required for PDF extraction. Install with: pip install PyPDF2")

    text_parts = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            pages_to_read = reader.pages[:max_pages] if max_pages else reader.pages
            for page in pages_to_read:
                text_parts.append(page.extract_text() or "")
    except Exception as e:
        raise RuntimeError(f"Error extracting PDF {file_path}: {e}") from e

    return "\n".join(text_parts)


def extract_pdf_pages(
    file_path: Path,
    *,
    max_pages: Optional[int] = None,
    page_timeout_s: Optional[int] = None,
) -> list[PdfPageExtraction]:
    """Extract text from a PDF file as page-level records.

    This is more robust for long documents where we want to chunk/summarize without
    dropping late-document content.

    Args:
        file_path: Path to the PDF file.
        max_pages: Optional limit on number of pages to extract.
        page_timeout_s: Optional per-page timeout (seconds). On timeout, the page is
            recorded with error and empty text.

    Returns:
        A list of PdfPageExtraction in page order (1-based page_number).
    """

    if PyPDF2 is None:
        raise ImportError("PyPDF2 is required for PDF extraction. Install with: pip install PyPDF2")

    def _extract_one_page(page) -> str:
        if page_timeout_s is None:
            return page.extract_text() or ""

        # Best-effort per-page timeout for macOS/Linux.
        try:
            import signal

            if not hasattr(signal, "SIGALRM"):
                return page.extract_text() or ""

            class _Timeout(Exception):
                pass

            def _handler(_signum, _frame):
                raise _Timeout("page extraction timed out")

            previous_handler = signal.getsignal(signal.SIGALRM)
            signal.signal(signal.SIGALRM, _handler)
            signal.alarm(int(page_timeout_s))
            try:
                return page.extract_text() or ""
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, previous_handler)
        except Exception:
            return page.extract_text() or ""

    results: list[PdfPageExtraction] = []
    try:
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            pages = reader.pages[:max_pages] if max_pages else reader.pages
            for idx, page in enumerate(pages, start=1):
                try:
                    page_text = _extract_one_page(page)
                    results.append(PdfPageExtraction(page_number=idx, text=page_text, error=None))
                except Exception as e:
                    results.append(PdfPageExtraction(page_number=idx, text="", error=str(e)))
    except Exception as e:
        raise RuntimeError(f"Error extracting PDF pages {file_path}: {e}") from e

    return results


def extract_eml_text(file_path: Path) -> str:
    """Extract text from an EML (email) file.

    Args:
        file_path: Path to the EML file.

    Returns:
        Extracted email content including headers and body.
    """
    try:
        with open(file_path, "rb") as f:
            msg = BytesParser(policy=policy.default).parse(f)

        text = (
            f"Subject: {msg['subject']}\n"
            f"From: {msg['from']}\n"
            f"To: {msg['to']}\n"
            f"Date: {msg['date']}\n\n"
        )
        body = msg.get_body(preferencelist=("plain", "html"))
        if body:
            text += body.get_content()
        return text
    except Exception as e:
        raise RuntimeError(f"Error extracting EML {file_path}: {e}") from e


def sanitize_text(text: str) -> str:
    """Remove potential secrets and sensitive patterns from text.

    Redacts:
    - API keys, secrets, tokens, passwords, credentials
    - Bearer tokens

    Args:
        text: Raw text to sanitize.

    Returns:
        Sanitized text with sensitive values replaced by [REDACTED].
    """
    # Redact common secret patterns
    text = re.sub(
        r"(?i)(api[-_]?key|secret|token|password|credential|pwd)\s*[:=]\s*[a-zA-Z0-9_\-\.~]+",
        r"\1: [REDACTED]",
        text,
    )
    # Redact Bearer tokens
    text = re.sub(r"Bearer\s+[a-zA-Z0-9\-\._]+", "Bearer [REDACTED]", text)
    return text


def call_with_retry(
    client: Any,
    input_text: str,
    instructions: Optional[str] = None,
    *,
    max_retries: int = 5,
    initial_delay: float = 2.0,
    timeout_s: float = 300.0,
) -> dict[str, Any]:
    """Call an LLM client with exponential backoff retry logic.

    Handles:
    - 429 Too Many Requests (rate limits)
    - Read timeouts (increases timeout on retry)

    Args:
        client: An AzureOpenAIResponsesClient (or compatible) with create_response method.
        input_text: The input text to send.
        instructions: Optional system instructions.
        max_retries: Maximum retry attempts.
        initial_delay: Initial delay in seconds before first retry.
        timeout_s: Initial timeout for the request.

    Returns:
        The API response dict.

    Raises:
        RuntimeError: If max retries exceeded or non-retriable error occurs.
    """
    current_timeout = timeout_s

    for attempt in range(max_retries):
        try:
            result = client.create_response(
                input_text=input_text,
                instructions=instructions,
                timeout_s=current_timeout,
            )
            return result
        except Exception as e:
            error_str = str(e)

            # Rate limit handling
            if "429" in error_str or "Too Many Requests" in error_str:
                delay = initial_delay * (2**attempt)
                print(f"Rate limited (attempt {attempt + 1}/{max_retries}). Retrying in {delay:.1f}s...")
                time.sleep(delay)
                continue

            # Timeout handling
            if "Read timed out" in error_str or "timed out" in error_str.lower():
                current_timeout += 120
                print(f"Timeout (attempt {attempt + 1}/{max_retries}). Retrying with {current_timeout:.0f}s timeout...")
                continue

            # Non-retriable error
            raise

    raise RuntimeError(f"Max retries ({max_retries}) exceeded for LLM API call")


def check_pdf_redundancy(file_path: Path, threshold_chars_per_page: int = 50000) -> bool:
    """Check if a PDF has suspiciously redundant content (e.g., transcript repeated per page).

    Args:
        file_path: Path to the PDF file.
        threshold_chars_per_page: If avg chars per page exceeds this, likely redundant.

    Returns:
        True if the PDF appears to have redundant content per page.
    """
    if PyPDF2 is None:
        raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")

    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        num_pages = len(reader.pages)
        if num_pages == 0:
            return False

        total_chars = sum(len(page.extract_text() or "") for page in reader.pages)
        avg_chars_per_page = total_chars / num_pages

    return avg_chars_per_page > threshold_chars_per_page
