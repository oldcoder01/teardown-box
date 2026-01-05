from __future__ import annotations

import re
from typing import List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class LinuxDiskCheck:
    name = "linux.disk"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("linux/df_h.txt")

    def run(self, fx: Fixtures) -> List[Finding]:
        txt = fx.read_text("linux/df_h.txt")
        if txt is None:
            return []

        hot = []
        lines = txt.strip().splitlines()
        for idx, line in enumerate(lines[1:], start=2):
            m = re.search(r"\s(\d+)%\s", line)
            if m is None:
                continue
            pct = int(m.group(1))
            if pct >= 80:
                hot.append((idx, line, pct))

        if not hot:
            return []

        line_no, line_text, pct = max(hot, key=lambda t: t[2])

        return [
            Finding(
                category="Reliability",
                severity="high" if pct >= 90 else "medium",
                title=f"Disk usage is high ({pct}%) on at least one filesystem",
                impact=(
                    "High disk usage is a common outage trigger (writes fail, services crash, databases stall). "
                    "It also hides other problems (logs grow until the host falls over)."
                ),
                confidence="High",
                evidence=[
                    EvidenceRef(
                        path="fixtures/linux/df_h.txt",
                        note=f"Filesystem above threshold: {line_text.strip()}",
                        line_start=line_no,
                        line_end=line_no,
                    )
                ],
                fix_now=FixNow(
                    title="Identify top disk consumers and cap runaway logs safely",
                    commands=[
                        "sudo du -xh /var/log | sort -h | tail -50",
                        "sudo journalctl --disk-usage",
                        "sudo sed -i 's/^#SystemMaxUse=.*/SystemMaxUse=1G/' /etc/systemd/journald.conf || true",
                        "sudo systemctl restart systemd-journald || true",
                    ],
                ),
                plan_7d=[
                    "Confirm alerting on disk % and inode usage (thresholds + paging policy).",
                    "Implement log rotation policy for app logs and set journald caps.",
                    "Add a runbook: safe cleanup + where growth typically comes from.",
                ],
                plan_30d=[
                    "Add SLO-driven alerting and capacity planning (trend disk growth).",
                    "Standardize log retention per environment (dev/stage/prod).",
                    "Automate checks in CI or daily cron to catch regressions.",
                ],
                questions=[
                    "Is this host stateful (DB) or stateless (app)? Cleanup approach differs.",
                    "Any known log bursts (deploys, retries, noisy errors) causing growth?",
                    "What is your on-call policy for disk alerts (page vs ticket)?",
                ],
            )
        ]
