"""
Read the macOS clipboard HTML content and save it to a file for analysis.
Also extract any embedded images.
"""
import subprocess
import re
import os
from pathlib import Path

def get_html_clipboard():
    """Get HTML content from macOS clipboard via osascript."""
    r = subprocess.run(
        ['osascript', '-e', 'the clipboard as «class HTML»'],
        capture_output=True
    )
    if r.returncode != 0:
        print(f"Error: {r.stderr.decode()}")
        return None
    
    raw = r.stdout.decode('utf-8', errors='replace').strip()
    
    # osascript returns hex-encoded data like: «data HTML3C6D657461...»
    # Strip the «data HTML...» wrapper
    if raw.startswith('«data HTML') and raw.endswith('»'):
        hex_str = raw[10:-1]  # strip «data HTML and »
    else:
        hex_str = raw
    
    # Decode hex to bytes then to UTF-8
    try:
        html_bytes = bytes.fromhex(hex_str)
        return html_bytes.decode('utf-8', errors='replace')
    except ValueError:
        print("Failed to decode hex")
        return None


def main():
    html = get_html_clipboard()
    if not html:
        print("No HTML clipboard content")
        return
    
    out_dir = Path("runs/2026-03-02__onenote-org/tmp")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    # Save raw HTML
    html_path = out_dir / "clipboard_html.html"
    html_path.write_text(html, encoding='utf-8')
    print(f"Saved HTML ({len(html)} chars) to {html_path}")
    
    # Find image tags
    img_pattern = re.compile(r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
    images = img_pattern.findall(html)
    print(f"Found {len(images)} <img> tags")
    
    for i, src in enumerate(images):
        if src.startswith('data:'):
            print(f"  Image {i}: data URI ({len(src)} chars)")
        else:
            print(f"  Image {i}: {src[:100]}")


if __name__ == "__main__":
    main()
