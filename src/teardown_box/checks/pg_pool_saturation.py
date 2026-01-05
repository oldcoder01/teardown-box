from __future__ import annotations

from typing import List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class PostgresPoolSaturationCheck:
    name = "postgres.pool_saturation"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("postgres/pg_pool_stats.json")

    def run(self, fx: Fixtures) -> List[Finding]:
        d = fx.read_json("postgres/pg_pool_stats.json")
        if d is None:
            return []

        max_client = int(d.get("max_client_conn", 0) or 0)
        current = int(d.get("current_clients", 0) or 0)
        waiting = int(d.get("current_waiting", 0) or 0)
        avg_wait = float(d.get("avg_wait_ms", 0) or 0)

        if max_client <= 0:
            return []

        usage = current / max_client if max_client else 0.0
        saturated = usage >= 0.90 or waiting > 0 or avg_wait >= 150
        if not saturated:
            return []

        severity = "high" if waiting >= 100 or avg_wait >= 200 else "medium"

        return [
            Finding(
                category="Reliability",
                severity=severity,
                title="Connection pool appears saturated (high client usage / waiting queue)",
                impact=(
                    "When the pool saturates, requests queue and tail latency spikes. This often presents as "
                    "timeouts and cascading retries, which further increases load."
                ),
                confidence="Medium",
                evidence=[
                    EvidenceRef(
                        path="fixtures/postgres/pg_pool_stats.json",
                        note=f"clients={current}/{max_client}, waiting={waiting}, avg_wait_ms={avg_wait}",
                    )
                ],
                fix_now=FixNow(
                    title="Reduce pool pressure and protect the DB from connection storms",
                    commands=[
                        "# Align app pool sizes to DB capacity and reduce per-instance pools if needed.",
                        "# Consider transaction pooling for short-lived queries (if compatible).",
                        'psql -c "SHOW max_connections;"',
                        'psql -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"',
                    ],
                ),
                plan_7d=[
                    "Inventory all services connecting to Postgres and their pool sizes.",
                    "Set sane timeouts/backoff to prevent retry storms when DB is slow.",
                    "Correlate pool wait spikes with deploy windows, traffic, and slow queries.",
                ],
                plan_30d=[
                    "Introduce admission control (rate limiting/load shedding) for hot endpoints.",
                    "Reduce transaction time via query/index fixes so connections return faster.",
                    "Automate capacity planning based on concurrency and transaction duration.",
                ],
                questions=[
                    "How many app instances connect to the pooler at peak?",
                    "Are there deploy events that align with wait spikes (connection churn)?",
                    "Are long-running queries holding connections open?",
                ],
            )
        ]
