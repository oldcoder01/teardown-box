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
python -m teardown_box.cli run --fixtures fixtures --out docs --html
```

Outputs:
- `docs/sample-report.md`
- `docs/sample-report.html` (fallback HTML wrapper)

## Notes
- Fixtures are fake but realistic-ish.
- HTML rendering is dependency-free and embeds the markdown as preformatted text. If you want nicer HTML, we can add a markdown renderer later.
