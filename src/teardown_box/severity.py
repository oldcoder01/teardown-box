from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Severity:
    key: str
    sort: int
    label: str


SEVERITIES = {
    "critical": Severity(key="critical", sort=0, label="Critical"),
    "high": Severity(key="high", sort=1, label="High"),
    "medium": Severity(key="medium", sort=2, label="Medium"),
    "low": Severity(key="low", sort=3, label="Low"),
}
