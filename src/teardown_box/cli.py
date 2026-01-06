from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from teardown_box.report.render_html import render_html_from_markdown
from teardown_box.report.render_md import render_markdown
from teardown_box.runner import run_all_checks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="teardown-box",
        description="Teardown-in-a-Box: generate a client-ready teardown report from fixtures.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run all checks against a fixtures folder and emit a report.")
    run_p.add_argument("--fixtures", required=True, help="Path to fixtures root (e.g., ./fixtures)")
    run_p.add_argument("--out", required=True, help="Output directory for docs (e.g., ./docs)")
    run_p.add_argument("--title", default="Teardown Report (Sample)", help="Report title")
    run_p.add_argument("--html", action="store_true", help="Also generate HTML output")
    run_p.add_argument("--cta-label", default="Book 15 minutes", help="CTA label shown near the top of the report")
    run_p.add_argument("--cta-url", default="#", help="CTA URL (Calendly, mailto, website contact page, etc.)")
    run_p.add_argument(
        "--contact-line",
        default="Replace this with your email / Calendly link",
        help="Short contact note shown next to the CTA",
    )

    run_p.add_argument(
        "--contact-url",
        default="#",
        help="Optional URL for a contact page (shown next to contact line).",
    )

    args = parser.parse_args(argv)

    if args.cmd == "run":
        res = run_all_checks(args.fixtures)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        md = render_markdown(
            res.findings,
            title=args.title,
            generated_at_iso=generated_at,
            inputs_reviewed=res.inputs_reviewed,
            fixtures_root=args.fixtures,
            cta_label=args.cta_label,
            cta_url=args.cta_url,
            contact_line=args.contact_line,
            contact_url=args.contact_url,
        )

        md_path = out_dir / "sample-report.md"
        md_path.write_text(md, encoding="utf-8")

        if args.html:
            html_doc = render_html_from_markdown(md, title=args.title)
            html_path = out_dir / "sample-report.html"
            html_path.write_text(html_doc, encoding="utf-8")

            # Convenience for GitHub Pages: publish docs/index.html by default.
            index_path = out_dir / "index.html"
            index_path.write_text(html_doc, encoding="utf-8")

            nojekyll = out_dir / ".nojekyll"
            if not nojekyll.exists():
                nojekyll.write_text("", encoding="utf-8")

        print(f"Wrote: {md_path}")
        if args.html:
            print(f"Wrote: {out_dir / 'sample-report.html'}")
            print(f"Wrote: {out_dir / 'index.html'}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
