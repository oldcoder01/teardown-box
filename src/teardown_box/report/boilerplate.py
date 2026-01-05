from __future__ import annotations


ASSUMPTIONS_MD = """\
## Assumptions & limits (what this report is / isn't)

This report is based on a point-in-time snapshot of the artifacts listed in **Inputs reviewed**.
It intentionally avoids invasive actions. Findings are prioritized by *severity x impact x confidence*.

**Assumptions**
- The snapshot is representative of normal and peak behavior (or at least of a recent incident window).
- The environment is a typical internet-facing web app with a Postgres-backed data tier.
- "Fix now" commands are intended to be safe and reversible, but should be validated in your environment.

**Limits**
- No live access was used for this demo; real environments require verification (config drift, active traffic, dependencies).
- Cost signals are directional (rightsizing recommendations require longer windows and peak analysis).
- Some findings depend on business context (SLOs, traffic patterns, compliance requirements).

## Scoring rubric (how to read this report)

**Severity**
- **Critical**: active or likely outage/security exposure; fix immediately.
- **High**: probable incident, meaningful security risk, or major user impact.
- **Medium**: important hygiene/perf work; schedule into the next sprint.
- **Low**: improvements/opportunities; do when convenient or bundle with other work.

**Confidence**
- **High**: direct evidence in artifacts (clear config/log/metric signal).
- **Medium**: strong indicators, but needs a quick confirm in live systems.
- **Low**: directional signal; must validate before acting (common for cost).

**Effort**
- **Low**: < 1–2 hours to ship a safe change (plus verification).
- **Medium**: 0.5–2 days, coordination or testing required.
- **High**: multi-day work, refactors, migrations, or multiple systems touched.

**Blast radius**
- **Low**: isolated change; easy rollback.
- **Medium**: touches shared components (LB/DB/pooler); requires coordination.
- **High**: broad change surface; run a staged rollout + explicit rollback plan.
"""


ACCESS_MD = """\
## What I need from you (access options)

Prospects often worry that a contractor needs deep access. This teardown can be done in tiers:

**Option A — No access (artifact-only)**
- You send a snapshot bundle (similar to the fixtures in this demo): service status, configs, key metrics exports, database stats.
- Best for fast triage and a prioritized plan.

**Option B — Read-only access (preferred for accuracy)**
- Cloud metrics (CloudWatch/Stackdriver), load balancer stats, DB performance insights, logs (read-only), and IaC state/plan output.
- This turns "likely" into "we're sure" without invasive changes.

**Option C — Timeboxed elevated access (rare)**
- Only if required for a specific fix (e.g., emergency mitigation), with explicit scope and a rollback plan.
"""


VERIFY_PLAN_MD = """\
## What I would verify with real access (48-hour verification plan)

This is the short list of checks I run to turn snapshot findings into "we're sure" conclusions.

**Security**
- Confirm firewall/SG reality vs host listeners (what is actually reachable from the internet).
- Validate TLS termination point (CDN/WAF vs origin) and confirm enforced TLS versions/ciphers.
- Review IAM/service principals for least-privilege (read/write boundaries, credential rotation).

**Reliability**
- Confirm restart-loop root cause via logs + dependency checks (DB reachability, DNS, secrets/config).
- Validate disk growth source (log volume, retention policy, and whether growth is correlated to incidents/deploys).
- Verify alerting: paging thresholds, on-call policy, and whether alerts are actionable.

**Performance**
- Run EXPLAIN (ANALYZE, BUFFERS) on top queries with representative parameters.
- Identify whether seq scans are driven by hot endpoints, background jobs, or analytics queries.
- Check lock contention and connection churn (pg_stat_activity, pooler stats, deploy windows).

**Cost**
- Pull 30–90 days utilization and include peak events; validate headroom requirements.
- Confirm storage policy: gp2/gp3 usage, snapshot retention, orphaned volumes.
- Tie spend to workload (unit cost per request/job) to avoid "savings that break SLOs".

**Exit criteria (what "done" looks like)**
- Top risks have owners, rollback plans, and a validated implementation path.
- We agree on SLOs (or at least p95/p99 targets) to define "improvement."
- A 7-day stabilization plan + 30-day hardening plan is accepted by the team.
"""
