from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha1
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from teardown_box.findings import EvidenceRef, Finding, finding_sort_key
from teardown_box.report.boilerplate import ACCESS_MD, ASSUMPTIONS_MD, VERIFY_PLAN_MD
from teardown_box.severity import SEVERITIES


@dataclass(frozen=True)
class EvidenceBlock:
    evidence_id: str
    ref: EvidenceRef
    snippet: Optional[str]


def _sev_label(key: str) -> str:
    sev = SEVERITIES.get(key)
    return sev.label if sev is not None else key


def _sev_rank(key: str) -> int:
    sev = SEVERITIES.get(key)
    return sev.sort if sev is not None else 99


def _first_sentence(text: str, max_len: int = 140) -> str:
    t = " ".join(text.strip().split())
    if not t:
        return ""
    parts = t.split(".")
    head = parts[0].strip()
    if not head:
        head = t
    if len(head) > max_len:
        return head[: max_len - 1].rstrip() + "…"
    return head


def _finding_anchor(idx: int) -> str:
    return f"finding-{idx:04d}"


def _evidence_id(ref: EvidenceRef) -> str:
    key = f"{ref.path}|{ref.line_start}|{ref.line_end}|{ref.note}"
    h = sha1(key.encode("utf-8")).hexdigest()[:10]
    return f"ev-{h}"


def _read_evidence_snippet(fixtures_root: str, ref: EvidenceRef, max_lines_no_range: int = 40) -> Optional[str]:
    root = Path(fixtures_root)
    rel = ref.path.replace("\\", "/")
    if rel.startswith("fixtures/"):
        rel = rel[len("fixtures/") :]
    p = root / rel
    if not p.exists() or not p.is_file():
        return None

    try:
        raw = p.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return None

    lines = raw.splitlines()
    if not lines:
        return ""

    if ref.line_start is not None and ref.line_end is not None:
        start = max(ref.line_start, 1)
        end = max(ref.line_end, start)
        # Evidence line numbers in this repo are 1-based.
        slice_lines = lines[start - 1 : min(end, len(lines))]
        out: List[str] = []
        for i, l in enumerate(slice_lines, start=start):
            out.append(f"{i:>5}: {l}")
        return "\n".join(out)

    # No line range: show a small header excerpt.
    slice_lines = lines[: min(max_lines_no_range, len(lines))]
    out2: List[str] = []
    for i, l in enumerate(slice_lines, start=1):
        out2.append(f"{i:>5}: {l}")
    return "\n".join(out2)


def render_markdown(
    findings: List[Finding],
    title: str,
    generated_at_iso: str,
    inputs_reviewed: List[str],
    fixtures_root: Optional[str] = None,
    cta_label: str = "Book 15 minutes",
    cta_url: str = "#",
    contact_line: str = "Replace this with your email / Calendly link",
) -> str:
    findings_sorted = sorted(findings, key=finding_sort_key)

    counts: Dict[str, int] = defaultdict(int)
    for f in findings_sorted:
        counts[f.severity] += 1

    # Top wins: highest severity first; prefer items with Fix Now
    fixables = [f for f in findings_sorted if f.fix_now is not None]
    fixables = sorted(fixables, key=lambda f: (_sev_rank(f.severity), f.category, f.title.lower()))
    top_wins = fixables[:3]

    # Build stable anchors for findings in sorted order
    finding_ids: Dict[int, str] = {}
    for i, _ in enumerate(findings_sorted, start=1):
        finding_ids[i] = _finding_anchor(i)

    # Group by category for main body rendering
    by_cat: Dict[str, List[Tuple[int, Finding]]] = defaultdict(list)
    for idx, f in enumerate(findings_sorted, start=1):
        by_cat[f.category].append((idx, f))

    # Collect evidence blocks (dedupe by evidence id)
    evidence_blocks: Dict[str, EvidenceBlock] = {}
    if fixtures_root is not None:
        for _, f in by_cat.items():
            for idx, finding in f:
                for ev in finding.evidence:
                    ev_id = _evidence_id(ev)
                    if ev_id not in evidence_blocks:
                        snippet = _read_evidence_snippet(fixtures_root, ev)
                        evidence_blocks[ev_id] = EvidenceBlock(evidence_id=ev_id, ref=ev, snippet=snippet)

    lines: List[str] = []
    lines.append(f"# {title}")
    lines.append("")

    # ---- Front door: one-screen intro + CTA ----
    lines.append("## Teardown in a Box (48-hour non-invasive teardown)")
    lines.append("")
    lines.append("**What this is:** A fast, non-invasive teardown that turns a messy system into a prioritized fix list.")
    lines.append("**What you get:** A report like this + a short call to confirm priorities + a fix-now shortlist.")
    lines.append("**Who it's for:** Small SaaS / agencies / teams with recurring incidents, slow Postgres, and unclear next steps.")
    lines.append("")
    lines.append(f"**Next step:** [{cta_label}]({cta_url}) — {contact_line}")
    lines.append("")

    lines.append(f"_Generated: {generated_at_iso}_")
    lines.append("")

    # ---- Executive summary ----
    lines.append("## Executive summary")
    lines.append("")
    lines.append(f"- Findings: {len(findings_sorted)} total")
    for key in ["critical", "high", "medium", "low"]:
        if counts.get(key, 0) > 0:
            lines.append(f"- {_sev_label(key)}: {counts[key]}")
    lines.append("")

    if inputs_reviewed:
        lines.append("## Inputs reviewed (scope)")
        lines.append("")
        lines.append("This report is generated from the following snapshot artifacts (synthetic fixtures in this demo).")

        lines.append("")
        for p in inputs_reviewed:
            lines.append(f"- `{p}`")
        lines.append("")

    if top_wins:
        lines.append("## Top 3 fix-now wins (highest ROI)")
        lines.append("")
        for f in top_wins:
            effort = getattr(f, "effort", "Medium")
            blast = getattr(f, "blast_radius", "Medium")
            lines.append(
                f"- **[{_sev_label(f.severity)}] {f.title}** "
                f"(Effort: {effort}, Blast radius: {blast}) — Fix now: *{f.fix_now.title}*"
            )
        lines.append("")

    # ---- Triage table ----
    lines.append("## Triage table (skim-friendly)")
    lines.append("")
    lines.append("| Sev | Area | Finding | Why it matters | Fix-now | Effort | Risk |") 
    lines.append("|---|---|---|---|---|---|---|")
    for idx, f in enumerate(findings_sorted, start=1):
        anchor = finding_ids[idx]
        why = _first_sentence(f.impact)
        fix = f.fix_now.title if f.fix_now is not None else "—"
        effort = getattr(f, "effort", "Medium")
        risk = getattr(f, "blast_radius", "Medium")
        lines.append(
            f"| {_sev_label(f.severity)} | {f.category} | [**{f.title}**](#{anchor}) | {why} | {fix} | {effort} | {risk} |"
        )
    lines.append("")

    # ---- Process + access clarity ----
    lines.append(ASSUMPTIONS_MD.strip())
    lines.append("")
    lines.append(ACCESS_MD.strip())
    lines.append("")
    lines.append(VERIFY_PLAN_MD.strip())
    lines.append("")
    lines.append("## Findings")
    lines.append("")
    for cat in ["Security", "Reliability", "Performance", "Cost"]:
        items = by_cat.get(cat, [])
        if not items:
            continue
        lines.append(f"### {cat}")
        lines.append("")
        for idx, f in items:
            anchor = finding_ids[idx]
            effort = getattr(f, "effort", "Medium")
            blast = getattr(f, "blast_radius", "Medium")
            validate = getattr(f, "validate_safely", None)
            success = getattr(f, "success_metric", None)
            rollback = getattr(f, "rollback", None)

            lines.append(f"<a id=\"{anchor}\"></a>")
            lines.append(f"#### [{_sev_label(f.severity)}] {f.title}")
            lines.append("")
            lines.append(f"**Impact:** {f.impact}")
            lines.append("")
            lines.append(f"**Confidence:** {f.confidence}")
            lines.append("")
            lines.append(f"**Effort / Blast radius:** {effort} / {blast}")
            lines.append("")

            if f.evidence:
                lines.append("**Evidence:**")
                for ev in f.evidence:
                    label = ev.format()
                    ev_id = _evidence_id(ev)
                    if fixtures_root is not None and ev_id in evidence_blocks:
                        lines.append(f"- [{label}](#{ev_id})")
                    else:
                        lines.append(f"- {label}")
                lines.append("")

            if f.fix_now is not None:
                lines.append(f"**Fix now:** {f.fix_now.title}")
                lines.append("")
                if f.fix_now.commands:
                    lines.append("```bash")
                    lines.extend(f.fix_now.commands)
                    lines.append("```")
                    lines.append("")
                if f.fix_now.snippet:
                    lines.append("```")
                    lines.append(f.fix_now.snippet)
                    lines.append("```")
                    lines.append("")
            if validate or success or rollback:
                lines.append("**Validation / success / rollback:**")
                if validate:
                    lines.append(f"- Validate safely: {validate}")
                if success:
                    lines.append(f"- Success metric: {success}")
                if rollback:
                    lines.append(f"- Rollback: {rollback}")
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
    # ---- Raw evidence appendix ----
    if evidence_blocks:
        lines.append("## Raw evidence")
        lines.append("")
        lines.append("Evidence links above jump here. Snippets are extracted from the fixture bundle used to generate this report.")
        lines.append("")
        for ev_id, blk in sorted(evidence_blocks.items(), key=lambda kv: kv[0]):
            label = blk.ref.format()
            lines.append(f"<a id=\"{ev_id}\"></a>")
            lines.append(f"### {label}")
            lines.append("")
            if blk.snippet is None:
                lines.append("_Unable to load snippet from fixtures._")
                lines.append("")
                continue
            lines.append("<details>")
            lines.append("<summary>Show snippet</summary>")
            lines.append("")
            lines.append("```text")
            lines.append(blk.snippet)
            lines.append("```")
            lines.append("")
            lines.append("</details>")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"
