from __future__ import annotations

from typing import Dict, List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class PostgresAutovacuumCheck:
    name = "postgres.autovacuum"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("postgres/pg_stat_user_tables.csv")

    def run(self, fx: Fixtures) -> List[Finding]:
        rows = fx.read_csv_dicts("postgres/pg_stat_user_tables.csv")
        if rows is None:
            return []

        bad: List[Dict[str, str]] = []
        for r in rows:
            try:
                live = int(float(r.get("n_live_tup", "0") or "0"))
                dead = int(float(r.get("n_dead_tup", "0") or "0"))
            except ValueError:
                continue

            if live <= 0:
                continue

            ratio = dead / max(live, 1)
            last_av = (r.get("last_autovacuum") or "").strip()

            # Heuristic: dead tuples >= 10% of live and autovac is running (so pressure exists).
            if ratio >= 0.10 and last_av != "":
                bad.append(r)

        if not bad:
            return []

        names = ", ".join([f"{r.get('schemaname')}.{r.get('relname')}" for r in bad[:3]])

        return [
            Finding(
                category="Reliability",
                severity="medium",
                title=f"Autovacuum pressure likely on ({names}) with high dead tuple ratios",
                impact=(
                    "High dead tuples increase bloat and slow queries (more pages to scan, worse cache locality). "
                    "If vacuum can't keep up, performance degrades and storage costs rise."
                ),
                confidence="Medium",
                evidence=[
                    EvidenceRef(
                        path="fixtures/postgres/pg_stat_user_tables.csv",
                        note="Tables with high n_dead_tup relative to n_live_tup",
                    )
                ],
                fix_now=FixNow(
                    title="Inspect worst tables and tune vacuum/analyze thresholds where needed",
                    commands=[
                        'psql -c "SELECT relname, n_live_tup, n_dead_tup, last_autovacuum '
                        'FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 20;"',
                        "# Consider per-table tuning on hot churn tables:",
                        "# autovacuum_vacuum_scale_factor, autovacuum_vacuum_threshold, "
                        "# autovacuum_analyze_scale_factor, autovacuum_analyze_threshold",
                        "# Also check for long-running transactions preventing cleanup.",
                    ],
                ),
                plan_7d=[
                    "Identify top bloat contributors and confirm vacuum is running as expected.",
                    "Adjust autovac settings for the highest-churn tables (sessions/events/orders).",
                    "Add alerting for dead tuple ratio and vacuum lag.",
                ],
                plan_30d=[
                    "Schedule periodic bloat checks and reindex strategy where appropriate.",
                    "Review retention policies (e.g., session cleanup) to reduce churn.",
                    "Add runbooks for vacuum/reindex and long-transaction mitigation.",
                ],
                questions=[
                    "Any long-running transactions or idle-in-transaction sessions during peaks?",
                    "Are you using managed defaults (RDS/Aurora) or custom autovac settings?",
                    "Do you have strict maintenance window constraints?",
                ],
            )
        ]
