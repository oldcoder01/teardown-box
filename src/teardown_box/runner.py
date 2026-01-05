from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List

from teardown_box.checks import all_checks
from teardown_box.fixtures import Fixtures
from teardown_box.findings import Finding


@dataclass(frozen=True)
class RunResult:
    findings: List[Finding]
    inputs_reviewed: List[str]


def _list_fixture_files(fixtures_root: Path) -> List[str]:
    if not fixtures_root.exists():
        return []
    paths: List[str] = []
    for p in fixtures_root.rglob("*"):
        if p.is_file():
            paths.append(str(p.relative_to(fixtures_root)).replace("\\", "/"))
    return sorted(paths)


def run_all_checks(fixtures_root: str) -> RunResult:
    root = Path(fixtures_root)
    fx = Fixtures(root=root)

    inputs = _list_fixture_files(root)

    findings: List[Finding] = []
    for chk in all_checks():
        try:
            if chk.applies(fx):
                findings.extend(chk.run(fx))
        except Exception as e:
            findings.append(
                Finding(
                    category="Reliability",
                    severity="low",
                    title=f"Check failed: {getattr(chk, 'name', chk.__class__.__name__)}",
                    impact=f"A check raised an exception and was skipped: {e}",
                    confidence="Low",
                    effort="Low",
                    blast_radius="Low",
                    evidence=[],
                    fix_now=None,
                    plan_7d=["Review fixture format and check implementation for robustness."],
                    plan_30d=["Add tests/fixtures variants to harden parsers against real-world noise."],
                    questions=["Are fixture formats consistent with your target environments?"],
                )
            )

    return RunResult(findings=findings, inputs_reviewed=inputs)
