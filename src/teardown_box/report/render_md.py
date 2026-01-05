from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Tuple

from teardown_box.findings import Finding, finding_sort_key
from teardown_box.severity import SEVERITIES


def _sev_label(key: str) -> str:
    sev = SEVERITIES.get(key)
    if sev is None:
        return key
    return sev.label


def render_markdown(findings: List[Finding], title: str, generated_at_iso: str) -> str:
    findings_sorted = sorted(findings, key=finding_sort_key)

    # Summary counts
    counts: Dict[str, int] = defaultdict(int)
    for f in findings_sorted:
        counts[f.severity] += 1

    # Group by category
    by_cat: Dict[str, List[Finding]] = defaultdict(list)
    for f in findings_sorted:
        by_cat[f.category].append(f)

    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"_Generated: {generated_at_iso}_")
    lines.append("")
    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Findings: {len(findings_sorted)} total")
    for key in ["critical", "high", "medium", "low"]:
        if counts.get(key, 0) > 0:
            lines.append(f"- {_sev_label(key)}: {counts[key]}")
    lines.append("")
    lines.append("## Findings")
    lines.append("")

    for cat in ["Security", "Reliability", "Performance", "Cost"]:
        items = by_cat.get(cat, [])
        if not items:
            continue
        lines.append(f"### {cat}")
        lines.append("")
        for f in items:
            lines.append(f"#### [{_sev_label(f.severity)}] {f.title}")
            lines.append("")
            lines.append(f"**Impact:** {f.impact}")
            lines.append("")
            lines.append(f"**Confidence:** {f.confidence}")
            lines.append("")
            if f.evidence:
                lines.append("**Evidence:**")
                for ev in f.evidence:
                    lines.append(f"- {ev.format()}")
                lines.append("")
            if f.fix_now is not None:
                lines.append(f"**Fix now:** {f.fix_now.title}")
                lines.append("")
                if f.fix_now.commands:
                    lines.append("```bash")
                    for c in f.fix_now.commands:
                        lines.append(c)
                    lines.append("```")
                    lines.append("")
                if f.fix_now.snippet:
                    lines.append("```")
                    lines.append(f.fix_now.snippet)
                    lines.append("```")
                    lines.append("")
            if f.plan_7d:
                lines.append("**7-day plan:**")
                for p in f.plan_7d:
                    lines.append(f"- {p}")
                lines.append("")
            if f.plan_30d:
                lines.append("**30-day plan:**")
                for p in f.plan_30d:
                    lines.append(f"- {p}")
                lines.append("")
            if f.questions:
                lines.append("**Questions I need answered:**")
                for q in f.questions:
                    lines.append(f"- {q}")
                lines.append("")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"
