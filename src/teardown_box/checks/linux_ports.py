from __future__ import annotations

import re
from typing import List, Set

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class LinuxPortsCheck:
    name = "linux.ports"

    def __init__(self) -> None:
        self.allowed_public_ports: Set[int] = {22, 80, 443}

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("linux/ss_lntp.txt")

    def run(self, fx: Fixtures) -> List[Finding]:
        txt = fx.read_text("linux/ss_lntp.txt")
        if txt is None:
            return []

        lines = txt.strip().splitlines()
        findings: List[Finding] = []

        for idx, line in enumerate(lines[1:], start=2):
            m = re.search(r"LISTEN\s+\d+\s+\d+\s+([0-9\.]+):(\d+)", line)
            if m is None:
                continue
            addr = m.group(1).strip()
            port = int(m.group(2))
            is_public_bind = addr == "0.0.0.0"
            if is_public_bind and port not in self.allowed_public_ports:
                findings.append(
                    Finding(
                        category="Security",
                        severity="high" if port in {5432, 6379, 9200, 27017} else "medium",
                        title=f"Unexpected public listener detected on port {port}",
                        impact=(
                            "Public listeners expand the attack surface. Databases and caches should not be exposed to the internet "
                            "without strong justification, network controls, and monitoring."
                        ),
                        confidence="High",
                        evidence=[
                            EvidenceRef(
                                path="fixtures/linux/ss_lntp.txt",
                                note=f"Bound to 0.0.0.0:{port}",
                                line_start=idx,
                                line_end=idx,
                            )
                        ],
                        fix_now=FixNow(
                            title="Restrict bind address and enforce network controls",
                            commands=[
                                f"# If this is Postgres, prefer listen_addresses='localhost' (or private subnet only)",
                                f"# Verify cloud SG/firewall: deny inbound {port} from 0.0.0.0/0",
                                "sudo ufw status || true",
                                "sudo ss -lntp | head -50",
                            ],
                        ),
                        plan_7d=[
                            "Confirm which services should be public and document an explicit allowlist.",
                            "Restrict binds to localhost/private interfaces and enforce SG/firewall rules.",
                            "Add monitoring/alerting for new public listeners.",
                        ],
                        plan_30d=[
                            "Standardize hardening baselines (CIS-ish) for hosts and containers.",
                            "Add continuous drift detection (ports, firewall, SGs) as a scheduled check.",
                            "Adopt least-privilege network segmentation between app and data tiers.",
                        ],
                        questions=[
                            f"Is port {port} intentionally public (e.g., temporary debug, migration)?",
                            "What enforces network policy today (security groups, nftables, kubernetes, etc.)?",
                            "Do you have a documented threat model / compliance constraints?",
                        ],
                    )
                )

        return findings
