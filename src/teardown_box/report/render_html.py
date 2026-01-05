from __future__ import annotations

import html
from typing import List

from teardown_box.findings import Finding


def render_html_from_markdown(md: str, title: str) -> str:
    # Dependency-free fallback: embed markdown as preformatted text.
    # If you want a nicer HTML conversion, add a markdown library later.
    escaped = html.escape(md)
    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 2rem; line-height: 1.5; }}
    pre {{ background: #f6f8fa; padding: 1rem; overflow: auto; border-radius: 8px; }}
    h1,h2,h3,h4 {{ margin-top: 1.25rem; }}
    .note {{ color: #555; }}
  </style>
</head>
<body>
  <p class="note">HTML mode is a dependency-free fallback that embeds the markdown output. For richer HTML, add a markdown renderer.</p>
  <pre>{escaped}</pre>
</body>
</html>
"""
