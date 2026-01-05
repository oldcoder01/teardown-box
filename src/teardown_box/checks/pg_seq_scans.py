from __future__ import annotations

from typing import Dict, List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class PostgresSeqScansCheck:
    name = "postgres.seq_scans"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("postgres/pg_stat_user_tables.csv")

    def run(self, fx: Fixtures) -> List[Finding]:
        rows = fx.read_csv_dicts("postgres/pg_stat_user_tables.csv")
        if rows is None:
            return []

        offenders: List[Dict[str, str]] = []
        for r in rows:
            try:
                reltuples = int(float(r.get("reltuples", "0") or "0"))
                seq_scan = int(r.get("seq_scan", "0") or "0")
            except ValueError:
                continue

            if reltuples >= 100000 and seq_scan >= 5000:
                offenders.append(r)

        if not offenders:
            return []

        names = ", ".join([f"{r.get('schemaname')}.{r.get('relname')}" for r in offenders[:3]])

        return [
            Finding(
                category="Performance",
                severity="high",
                title=f"High sequential scan activity on large tables ({names})",
                impact=(
                    "Repeated sequential scans on large tables inflate latency and CPU, especially under concurrency. "
                    "This is a common root cause of 'DB is slow' incidents."
                ),
                confidence="Medium",
                evidence=[
                    EvidenceRef(
                        path="fixtures/postgres/pg_stat_user_tables.csv",
                        note="Tables with high reltuples and high seq_scan",
                    )
                ],
                fix_now=FixNow(
                    title="Identify query patterns causing seq_scans and add targeted indexes",
                    commands=[
                        "# Map top seq_scans to query patterns (pg_stat_statements + logs)",
                        "# Run EXPLAIN (ANALYZE, BUFFERS) to confirm scan type and cost",
                        "# Add the smallest viable index to support the common filter/order",
                        'psql -c "SELECT relname, seq_scan, idx_scan, n_live_tup, n_dead_tup '
                        'FROM pg_stat_user_tables ORDER BY seq_scan DESC LIMIT 20;"',
                    ],
                ),
                plan_7d=[
                    "Map top seq_scanned tables to specific endpoints/jobs.",
                    "Implement 1–2 high-ROI fixes (index or query rewrite) and measure p95 before/after.",
                    "Ensure stats are current (ANALYZE) for affected tables.",
                ],
                plan_30d=[
                    "Add performance dashboards/alerts (DB CPU, buffer hit rate, slow query spikes).",
                    "Review ORM/query patterns (wide SELECT *, missing filters) driving scans.",
                    "Consider partitioning for large time-series tables if growth continues.",
                ],
                questions=[
                    "Are these tables expected to be scan-heavy (analytics), or OLTP hot paths?",
                    "Do you have read replicas or a separate analytics store?",
                    "Any existing indexes that are unused or misaligned with query patterns?",
                ],
            )
        ]
