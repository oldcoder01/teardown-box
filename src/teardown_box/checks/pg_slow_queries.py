from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class PostgresSlowQueriesCheck:
    name = "postgres.slow_queries"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("postgres/pg_stat_statements.csv")

    def _top_queries(self, rows: List[Dict[str, str]], n: int) -> List[Dict[str, str]]:
        def total_ms(r: Dict[str, str]) -> float:
            try:
                return float(r.get("total_time_ms", "0") or "0")
            except ValueError:
                return 0.0
        return sorted(rows, key=total_ms, reverse=True)[:n]

    def _index_hint(self, query: str) -> Optional[str]:
        q = query.lower()
        if "from users" in q and "where email" in q:
            return "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON public.users (email);"
        if "from orders" in q and "where created_at" in q:
            return "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at ON public.orders (created_at DESC);"
        if "from invoices" in q and "where account_id" in q and "status" in q:
            return "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_invoices_account_status_due ON public.invoices (account_id, status, due_date);"
        if "update sessions" in q and "where session_token" in q:
            return "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_token ON public.sessions (session_token);"
        return None

    def run(self, fx: Fixtures) -> List[Finding]:
        rows = fx.read_csv_dicts("postgres/pg_stat_statements.csv")
        if rows is None:
            return []

        top = self._top_queries(rows, 3)
        if not top:
            return []

        evidence_notes: List[EvidenceRef] = [
            EvidenceRef(
                path="fixtures/postgres/pg_stat_statements.csv",
                note="Top queries by total_time_ms (sample)",
                line_start=1,
                line_end=1 + len(top),
            )
        ]

        fix_cmds: List[str] = [
            "# For each top query, run EXPLAIN (ANALYZE, BUFFERS) in a safe environment",
            "# Confirm indexes with \\d+ <table> and actual query patterns (params, ordering)",
        ]

        hints: List[str] = []
        for r in top:
            q = (r.get("query") or "").strip().strip('"')
            hint = self._index_hint(q)
            if hint is not None:
                hints.append(hint)

        if hints:
            fix_cmds.append("# Candidate index statements (validate with EXPLAIN + production constraints):")
            fix_cmds.extend(hints)

        return [
            Finding(
                category="Performance",
                severity="high",
                title="Postgres shows heavy time spent in a small set of queries (pg_stat_statements)",
                impact=(
                    "A handful of queries often dominate database load. Improving them typically reduces p95 latency, "
                    "stabilizes CPU, and lowers infra cost by delaying scale-up."
                ),
                confidence="Medium",
                evidence=evidence_notes,
                fix_now=FixNow(
                    title="Validate query plans and implement the highest-impact index/query changes",
                    commands=fix_cmds,
                ),
                plan_7d=[
                    "Confirm pg_stat_statements is enabled and capturing representative traffic.",
                    "Run EXPLAIN (ANALYZE, BUFFERS) for top queries and identify scans/sorts/hot joins.",
                    "Implement 1-2 highest-ROI fixes (index or query rewrite) with safe rollout.",
                ],
                plan_30d=[
                    "Add performance regression tests (key endpoints) and track DB p95 + CPU.",
                    "Introduce SLO/alerts for slow query spikes and lock contention.",
                    "Consider connection pooling tuning to reduce per-query overhead.",
                ],
                questions=[
                    "Are these queries representative of peak traffic (same workload + time window)?",
                    "Any hard constraints on index build time / lock tolerance?",
                    "Is read/write split or partitioning on the roadmap?",
                ],
            )
        ]
