from __future__ import annotations

from typing import List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class CostSignalsCheck:
    name = "cost.signals"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("cost/utilization_summary.json") or fx.exists("cost/ebs_volumes.csv")

    def run(self, fx: Fixtures) -> List[Finding]:
        findings: List[Finding] = []

        util = fx.read_json("cost/utilization_summary.json")
        if util is not None:
            cpu_p95 = float(util.get("cpu_p95_percent", 0) or 0)
            mem_p95 = float(util.get("memory_p95_percent", 0) or 0)
            itype = str(util.get("instance_type", "unknown"))
            iid = str(util.get("instance_id", "unknown"))

            if cpu_p95 < 20 and mem_p95 < 40:
                findings.append(
                    Finding(
                        category="Cost",
                        severity="medium",
                        title=f"Possible overprovisioning signal: {itype} at low p95 utilization",
                        impact=(
                            "If sustained utilization is low, you may be paying for capacity you don’t need. "
                            "Rightsizing can reduce spend without reducing reliability (when validated carefully)."
                        ),
                        confidence="Low",
                        evidence=[
                            EvidenceRef(
                                path="fixtures/cost/utilization_summary.json",
                                note=f"instance={iid}, cpu_p95={cpu_p95}%, mem_p95={mem_p95}% over {util.get('period_days')} days",
                            )
                        ],
                        fix_now=FixNow(
                            title="Create a rightsizing candidate and validate against peak/burst patterns",
                            commands=[
                                "# Validate with a larger window and include disk + network + burst behavior",
                                "# If safe, test downsize one step in a canary environment first",
                                "aws cloudwatch get-metric-statistics ...  # (example: CPUUtilization p95/p99)",
                            ],
                        ),
                        plan_7d=[
                            "Pull 30–90d utilization including peak events and deploy windows.",
                            "Identify a safe canary target for downsize and test rollback.",
                            "Estimate savings and risk; execute one change with monitoring.",
                        ],
                        plan_30d=[
                            "Adopt scheduled scaling or autoscaling where appropriate.",
                            "Track unit cost per request/job and alert on regressions.",
                            "Automate monthly cost posture checks and recommendations.",
                        ],
                        questions=[
                            "Are there known weekly/monthly peaks not represented in this sample?",
                            "Any CPU credit/burstable instances involved?",
                            "What is your rollback plan if latency increases after downsize?",
                        ],
                    )
                )

        vols = fx.read_csv_dicts("cost/ebs_volumes.csv")
        if vols is not None:
            gp2 = [v for v in vols if (v.get("type") or "").strip().lower() == "gp2"]
            if gp2:
                findings.append(
                    Finding(
                        category="Cost",
                        severity="low",
                        title="EBS gp2 volumes detected; consider gp3 for cost/performance control",
                        impact=(
                            "gp3 often provides better baseline performance and more predictable tuning. "
                            "Switching from gp2 to gp3 can reduce cost and decouple size from performance."
                        ),
                        confidence="Medium",
                        evidence=[
                            EvidenceRef(
                                path="fixtures/cost/ebs_volumes.csv",
                                note=f"gp2 volumes: {', '.join([v.get('volume_id','?') for v in gp2])}",
                            )
                        ],
                        fix_now=FixNow(
                            title="Evaluate gp3 migration plan (low-risk, validate per workload)",
                            commands=[
                                "# In AWS: modify volume type to gp3 and set IOPS/throughput as needed",
                                "# Validate latency/IOPS requirements before and after",
                                "aws ec2 modify-volume --volume-id <vol-id> --volume-type gp3 --iops 3000 --throughput 125",
                            ],
                        ),
                        plan_7d=[
                            "Inventory gp2 volumes and identify those safe to migrate first.",
                            "Migrate a non-critical volume and confirm workload metrics.",
                            "Roll out remaining migrations with a change window + monitoring.",
                        ],
                        plan_30d=[
                            "Standardize volume types/policies in IaC (default to gp3).",
                            "Add cost posture checks for storage, snapshots, and idle resources.",
                        ],
                        questions=[
                            "Are there workloads with unusually high IOPS/throughput requirements?",
                            "Do you have maintenance windows for volume modifications?",
                        ],
                    )
                )

        return findings
