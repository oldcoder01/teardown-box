from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class EvidenceRef:
    path: str
    note: str
    line_start: Optional[int] = None
    line_end: Optional[int] = None

    def format(self) -> str:
        if self.line_start is not None and self.line_end is not None:
            return f"{self.path}:L{self.line_start}-L{self.line_end} ({self.note})"
        return f"{self.path} ({self.note})"


@dataclass(frozen=True)
class FixNow:
    title: str
    commands: List[str] = field(default_factory=list)
    snippet: Optional[str] = None


@dataclass(frozen=True)
class Finding:
    category: str  # Security / Reliability / Performance / Cost
    severity: str  # critical/high/medium/low
    title: str
    impact: str
    confidence: str  # High/Medium/Low
    evidence: List[EvidenceRef] = field(default_factory=list)
    fix_now: Optional[FixNow] = None
    plan_7d: List[str] = field(default_factory=list)
    plan_30d: List[str] = field(default_factory=list)
    questions: List[str] = field(default_factory=list)


def finding_sort_key(f: Finding) -> tuple:
    from teardown_box.severity import SEVERITIES
    sev = SEVERITIES.get(f.severity)
    sev_sort = sev.sort if sev is not None else 99
    return (f.category, sev_sort, f.title.lower())
