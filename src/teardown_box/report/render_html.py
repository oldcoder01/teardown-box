from __future__ import annotations

import html


def render_html_from_markdown(md: str, title: str) -> str:
    # Inject a TOC marker for HTML only.
    md_input = "[TOC]\n\n" + md

    body: str
    try:
        import markdown2

        body = markdown2.markdown(
            md_input,
            extras=[
                "fenced-code-blocks",
                "tables",
                "toc",
                "cuddled-lists",
                "strike",
                "task_list",
            ],
        )
    except Exception:
        try:
            import markdown as mdlib  # type: ignore

            body = mdlib.markdown(
                md_input,
                extensions=[
                    "fenced_code",
                    "tables",
                    "toc",
                    "sane_lists",
                ],
                output_format="html5",
            )
        except Exception:
            body = f"<pre>{html.escape(md)}</pre>"

    safe_title = html.escape(title)

    return f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{safe_title}</title>
  <style>
    :root {{
      --bg: #ffffff;
      --fg: #111827;
      --muted: #6b7280;
      --border: #e5e7eb;
      --codebg: #f6f8fa;
      --link: #2563eb;
    }}
    body {{
      font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
      margin: 0;
      background: var(--bg);
      color: var(--fg);
      line-height: 1.55;
    }}
    .wrap {{
      max-width: 1000px;
      margin: 0 auto;
      padding: 2rem 1rem;
    }}
    h1, h2, h3, h4 {{
      line-height: 1.25;
      margin-top: 1.6em;
    }}
    h1 {{ margin-top: 0; }}
    a {{ color: var(--link); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    code, pre {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \"Liberation Mono\", \"Courier New\", monospace;
    }}
    pre {{
      background: var(--codebg);
      padding: 0.9rem;
      border-radius: 10px;
      overflow-x: auto;
      border: 1px solid var(--border);
    }}
    code {{
      background: var(--codebg);
      padding: 0.15rem 0.3rem;
      border-radius: 6px;
      border: 1px solid var(--border);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 1rem 0;
      border: 1px solid var(--border);
      border-radius: 12px;
      overflow: hidden;
      display: block;
    }}
    th, td {{
      padding: 0.55rem 0.6rem;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    th {{
      text-align: left;
      background: #f9fafb;
      font-weight: 600;
    }}
    tr:last-child td {{ border-bottom: none; }}
    blockquote {{
      margin: 1rem 0;
      padding: 0.75rem 1rem;
      border-left: 4px solid var(--border);
      background: #fafafa;
      color: var(--muted);
    }}
    .toc {{
      padding: 1rem;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: #fcfcfc;
    }}
    details {{
      margin: 0.4rem 0 1.0rem;
      padding: 0.65rem 0.8rem;
      border: 1px solid var(--border);
      border-radius: 12px;
      background: #fcfcfc;
    }}
    summary {{
      cursor: pointer;
      font-weight: 600;
    }}
    hr {{
      border: none;
      border-top: 1px solid var(--border);
      margin: 1.8rem 0;
    }}
  </style>
</head>
<body>
  <div class=\"wrap\">
    {body}
  </div>
</body>
</html>
"""
