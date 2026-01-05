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

    runp = sub.add_parser("run", help="Run checks against fixtures and generate reports")
    runp.add_argument("--fixtures", default="fixtures", help="Path to fixtures folder")
    runp.add_argument("--out", default="docs", help="Output folder for reports")
    runp.add_argument("--title", default="Teardown Report (Sample)", help="Report title")
    runp.add_argument("--html", action="store_true", help="Also write an HTML report (fallback wrapper)")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        res = run_all_checks(args.fixtures)
        out_dir = Path(args.out)
        out_dir.mkdir(parents=True, exist_ok=True)

        generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
        md = render_markdown(res.findings, title=args.title, generated_at_iso=generated_at)

        md_path = out_dir / "sample-report.md"
        md_path.write_text(md, encoding="utf-8")

        if args.html:
            html_doc = render_html_from_markdown(md, title=args.title)
            html_path = out_dir / "sample-report.html"
            html_path.write_text(html_doc, encoding="utf-8")

        print(f"Wrote: {md_path}")
        if args.html:
            print(f"Wrote: {out_dir / 'sample-report.html'}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
