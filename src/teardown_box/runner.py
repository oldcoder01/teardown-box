from __future__ import annotations

from dataclasses import dataclass
from typing import List

from teardown_box.checks import all_checks
from teardown_box.fixtures import Fixtures
from teardown_box.findings import Finding


@dataclass(frozen=True)
class RunResult:
    findings: List[Finding]


def run_all_checks(fixtures_root: str) -> RunResult:
    fx = Fixtures(root=__import__("pathlib").Path(fixtures_root))
    findings: List[Finding] = []
    for chk in all_checks():
        try:
            if chk.applies(fx):
                findings.extend(chk.run(fx))
        except Exception as e:
            # In client-facing mode, prefer a non-fatal failure with a clear note.
            findings.append(
                Finding(
                    category="Reliability",
                    severity="low",
                    title=f"Check failed: {getattr(chk, 'name', chk.__class__.__name__)}",
                    impact=f"A check raised an exception and was skipped: {e}",
                    confidence="Low",
                    evidence=[],
                    fix_now=None,
                    plan_7d=["Review fixture format and check implementation for robustness."],
                    plan_30d=["Add tests/fixtures variants to harden parsers against real-world noise."],
                    questions=["Are fixture formats consistent with your target environments?"],
                )
            )
    return RunResult(findings=findings)
