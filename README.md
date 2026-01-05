# Teardown-in-a-Box

A small CLI that ingests sample data (fixtures) and produces a client-ready report (Markdown + optional HTML) with:

- Findings grouped by category (Security / Reliability / Performance / Cost)
- Severity + impact + evidence references
- "Fix now" commands/snippets
- A 7-day plan + 30-day plan
- A "Questions I need answered" section

## Quickstart

From the project root:

```bash
python -m teardown_box.cli run --fixtures fixtures --out docs --html --cta-url "https://<your-link>" --contact-line "you@domain.com"
```

Outputs:
- `docs/sample-report.md`
- `docs/sample-report.html` (rendered HTML)
- `docs/index.html` (GitHub Pages entrypoint)

## Notes
- Fixtures are fake but realistic-ish.
- HTML rendering uses `markdown2` to produce a styled report (with TOC, tables, and clickable evidence).
- The generated HTML is committed to `docs/` so GitHub Pages is purely static (no build step).
