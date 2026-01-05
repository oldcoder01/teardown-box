from __future__ import annotations

import re
from typing import List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class LinuxSystemdFlapCheck:
    name = "linux.systemd.flap"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("linux/systemctl_status.txt")

    def run(self, fx: Fixtures) -> List[Finding]:
        txt = fx.read_text("linux/systemctl_status.txt")
        if txt is None:
            return []

        lines = txt.splitlines()
        restart_counter = None
        counter_line_no = None

        for idx, line in enumerate(lines, start=1):
            m = re.search(r"restart counter is at (\d+)", line, re.IGNORECASE)
            if m is not None:
                restart_counter = int(m.group(1))
                counter_line_no = idx
                break

        auto_restart = any("auto-restart" in l.lower() for l in lines)
        if not auto_restart and restart_counter is None:
            return []

        sev = "high" if (restart_counter is not None and restart_counter >= 10) else "medium"
        counter_note = "Service is in auto-restart state" if restart_counter is None else f"Restart counter is {restart_counter}"

        return [
            Finding(
                category="Reliability",
                severity=sev,
                title="systemd service appears to be flapping (restart loop)",
                impact=(
                    "Restart loops create intermittent downtime, amplify load (retry storms), and usually mask a real dependency "
                    "issue (DB, DNS, config, or secrets). They also consume CPU and can trigger cascading failures."
                ),
                confidence="High",
                evidence=[
                    EvidenceRef(
                        path="fixtures/linux/systemctl_status.txt",
                        note=counter_note,
                        line_start=counter_line_no,
                        line_end=counter_line_no,
                    )
                ] if counter_line_no is not None else [
                    EvidenceRef(
                        path="fixtures/linux/systemctl_status.txt",
                        note="Detected auto-restart state in service status output",
                    )
                ],
                fix_now=FixNow(
                    title="Pull recent logs and verify dependencies; add backoff while fixing root cause",
                    commands=[
                        "sudo journalctl -u api.service --since '2 hours ago' | tail -200",
                        "sudo systemctl show api.service -p Restart -p RestartUSec -p StartLimitBurst -p StartLimitIntervalUSec",
                        "sudo systemctl status api.service",
                    ],
                ),
                plan_7d=[
                    "Identify the failing dependency (DB connectivity, DNS, secrets, config) and fix root cause.",
                    "Add health checks and a reasonable restart policy (backoff + limits) to avoid retry storms.",
                    "Add alerting on restart rate and error budget burn.",
                ],
                plan_30d=[
                    "Add graceful degradation (circuit breaker/backoff) in the app for dependency failures.",
                    "Add dependency SLOs (DB latency, DNS) and correlate with deploy events.",
                    "Standardize systemd unit templates and logging across services.",
                ],
                questions=[
                    "Is this happening constantly or only during deploy windows?",
                    "What database/network path does the service use (VPC, SG, local socket)?",
                    "Do you have an incident timeline for when this started?",
                ],
            )
        ]
