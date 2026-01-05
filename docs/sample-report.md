# Teardown Report (Sample)

_Generated: 2026-01-05T09:57:32-08:00_

## Executive summary

- Findings: 11 total
- High: 5
- Medium: 4
- Low: 2

## Inputs reviewed (scope)

This report is generated from the following snapshot artifacts (synthetic fixtures in this demo).

- `cost/ebs_volumes.csv`
- `cost/utilization_summary.json`
- `edge/nginx.conf`
- `edge/tls_scan.txt`
- `infra/terraform_plan.txt`
- `linux/df_h.txt`
- `linux/ss_lntp.txt`
- `linux/systemctl_status.txt`
- `postgres/pg_pool_stats.json`
- `postgres/pg_stat_statements.csv`
- `postgres/pg_stat_user_tables.csv`

## Top 3 fix-now wins (highest ROI)

- **[High] High sequential scan activity on large tables (public.orders, public.events)** (Effort: Medium, Blast radius: Medium) — Fix now: *Identify query patterns causing seq_scans and add targeted indexes*
- **[High] Postgres shows heavy time spent in a small set of queries (pg_stat_statements)** (Effort: Medium, Blast radius: Medium) — Fix now: *Validate query plans and implement the highest-impact index/query changes*
- **[High] Connection pool appears saturated (high client usage / waiting queue)** (Effort: Medium, Blast radius: Medium) — Fix now: *Reduce pool pressure and protect the DB from connection storms*

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

**Decision rules used**
- *High severity* = likely to cause outage or material security exposure.
- *High impact* = affects user-facing latency/availability or increases breach surface.
- *Confidence* reflects evidence strength from artifacts (not "gut feel").

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
- Pull 30-90 days utilization and include peak events; validate headroom requirements.
- Confirm storage policy: gp2/gp3 usage, snapshot retention, orphaned volumes.
- Tie spend to workload (unit cost per request/job) to avoid "savings that break SLOs".

**Exit criteria (what "done" looks like)**
- Top risks have owners, rollback plans, and a validated implementation path.
- We agree on SLOs (or at least p95/p99 targets) to define "improvement."
- A 7-day stabilization plan + 30-day hardening plan is accepted by the team.

## Findings

### Security

#### [High] Unexpected public listener detected on port 5432

**Impact:** Public listeners expand the attack surface. Databases and caches should not be exposed to the internet without strong justification, network controls, and monitoring.

**Confidence:** High

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/linux/ss_lntp.txt:L5-L5 (Bound to 0.0.0.0:5432)

**Fix now:** Restrict bind address and enforce network controls

```bash
# If this is Postgres, prefer listen_addresses='localhost' (or private subnet only)
# Verify cloud SG/firewall: deny inbound 5432 from 0.0.0.0/0
sudo ufw status || true
sudo ss -lntp | head -50
```

**7-day plan:**
- Confirm which services should be public and document an explicit allowlist.
- Restrict binds to localhost/private interfaces and enforce SG/firewall rules.
- Add monitoring/alerting for new public listeners.

**30-day plan:**
- Standardize hardening baselines (CIS-ish) for hosts and containers.
- Add continuous drift detection (ports, firewall, SGs) as a scheduled check.
- Adopt least-privilege network segmentation between app and data tiers.

**Questions I need answered:**
- Is port 5432 intentionally public (e.g., temporary debug, migration)?
- What enforces network policy today (security groups, nftables, kubernetes, etc.)?
- Do you have a documented threat model / compliance constraints?

#### [Medium] Legacy TLS versions appear enabled (TLS 1.0/1.1)

**Impact:** Older TLS versions weaken security posture and may violate compliance expectations. Most modern clients support TLS 1.2+.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/edge/tls_scan.txt (TLSv1.0/TLSv1.1 enabled in scan summary)

**Fix now:** Disable TLS 1.0/1.1 and standardize a modern policy

```bash
# Target: TLS 1.2 and 1.3 only (exact config depends on your edge stack).
ssl_protocols TLSv1.2 TLSv1.3;
# Use a modern cipher suite policy appropriate to your environment.
```

**7-day plan:**
- Confirm client compatibility requirements (legacy devices/browsers).
- Disable TLS 1.0/1.1 and redeploy edge config.
- Run a follow-up scan to confirm posture.

**30-day plan:**
- Automate TLS posture scans (scheduled) and alert on regressions.
- Adopt managed TLS policies via CDN/WAF where feasible.
- Track certificate renewal and config drift.

**Questions I need answered:**
- Do you terminate TLS at a CDN/WAF or on the origin?
- Any compliance requirements (PCI/HIPAA/SOC2) driving a specific policy?
- Any legacy clients that truly require TLS 1.0/1.1?

#### [Low] HSTS is missing

**Impact:** Without HSTS, clients can be tricked into initial HTTP connections in some downgrade scenarios. HSTS is usually a low-risk hardening win for public HTTPS sites.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/edge/tls_scan.txt (HSTS marked missing in scan summary)

**Fix now:** Add an HSTS header after validating HTTPS-only readiness

```bash
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
# Consider preload only after careful validation.
```

**7-day plan:**
- Confirm all subdomains are HTTPS and redirects are correct.
- Deploy HSTS and validate no mixed-content regressions.

**30-day plan:**
- Add a baseline set of security headers (CSP, X-Content-Type-Options, etc.).
- Automate header checks in CI.

**Questions I need answered:**
- Are there any HTTP-only subdomains/endpoints still in use?
- Do you already use a CDN/WAF that can set headers globally?


### Reliability

#### [High] Connection pool appears saturated (high client usage / waiting queue)

**Impact:** When the pool saturates, requests queue and tail latency spikes. This often presents as timeouts and cascading retries, which further increases load.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/postgres/pg_pool_stats.json (clients=4860/5000, waiting=322, avg_wait_ms=185.0)

**Fix now:** Reduce pool pressure and protect the DB from connection storms

```bash
# Align app pool sizes to DB capacity and reduce per-instance pools if needed.
# Consider transaction pooling for short-lived queries (if compatible).
psql -c "SHOW max_connections;"
psql -c "SELECT state, count(*) FROM pg_stat_activity GROUP BY state;"
```

**7-day plan:**
- Inventory all services connecting to Postgres and their pool sizes.
- Set sane timeouts/backoff to prevent retry storms when DB is slow.
- Correlate pool wait spikes with deploy windows, traffic, and slow queries.

**30-day plan:**
- Introduce admission control (rate limiting/load shedding) for hot endpoints.
- Reduce transaction time via query/index fixes so connections return faster.
- Automate capacity planning based on concurrency and transaction duration.

**Questions I need answered:**
- How many app instances connect to the pooler at peak?
- Are there deploy events that align with wait spikes (connection churn)?
- Are long-running queries holding connections open?

#### [High] systemd service appears to be flapping (restart loop)

**Impact:** Restart loops create intermittent downtime, amplify load (retry storms), and usually mask a real dependency issue (DB, DNS, config, or secrets). They also consume CPU and can trigger cascading failures.

**Confidence:** High

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/linux/systemctl_status.txt:L8-L8 (Restart counter is 27)

**Fix now:** Pull recent logs and verify dependencies; add backoff while fixing root cause

```bash
sudo journalctl -u api.service --since '2 hours ago' | tail -200
sudo systemctl show api.service -p Restart -p RestartUSec -p StartLimitBurst -p StartLimitIntervalUSec
sudo systemctl status api.service
```

**7-day plan:**
- Identify the failing dependency (DB connectivity, DNS, secrets, config) and fix root cause.
- Add health checks and a reasonable restart policy (backoff + limits) to avoid retry storms.
- Add alerting on restart rate and error budget burn.

**30-day plan:**
- Add graceful degradation (circuit breaker/backoff) in the app for dependency failures.
- Add dependency SLOs (DB latency, DNS) and correlate with deploy events.
- Standardize systemd unit templates and logging across services.

**Questions I need answered:**
- Is this happening constantly or only during deploy windows?
- What database/network path does the service use (VPC, SG, local socket)?
- Do you have an incident timeline for when this started?

#### [Medium] Autovacuum pressure likely on (public.orders, public.events, public.sessions) with high dead tuple ratios

**Impact:** High dead tuples increase bloat and slow queries (more pages to scan, worse cache locality). If vacuum can't keep up, performance degrades and storage costs rise.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/postgres/pg_stat_user_tables.csv (Tables with high n_dead_tup relative to n_live_tup)

**Fix now:** Inspect worst tables and tune vacuum/analyze thresholds where needed

```bash
psql -c "SELECT relname, n_live_tup, n_dead_tup, last_autovacuum FROM pg_stat_user_tables ORDER BY n_dead_tup DESC LIMIT 20;"
# Consider per-table tuning on hot churn tables:
# autovacuum_vacuum_scale_factor, autovacuum_vacuum_threshold, # autovacuum_analyze_scale_factor, autovacuum_analyze_threshold
# Also check for long-running transactions preventing cleanup.
```

**7-day plan:**
- Identify top bloat contributors and confirm vacuum is running as expected.
- Adjust autovac settings for the highest-churn tables (sessions/events/orders).
- Add alerting for dead tuple ratio and vacuum lag.

**30-day plan:**
- Schedule periodic bloat checks and reindex strategy where appropriate.
- Review retention policies (e.g., session cleanup) to reduce churn.
- Add runbooks for vacuum/reindex and long-transaction mitigation.

**Questions I need answered:**
- Any long-running transactions or idle-in-transaction sessions during peaks?
- Are you using managed defaults (RDS/Aurora) or custom autovac settings?
- Do you have strict maintenance window constraints?

#### [Medium] Disk usage is high (87%) on at least one filesystem

**Impact:** High disk usage is a common outage trigger (writes fail, services crash, databases stall). It also hides other problems (logs grow until the host falls over).

**Confidence:** High

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/linux/df_h.txt:L2-L2 (Filesystem above threshold: /dev/nvme0n1p2  100G   87G   13G  87% /)

**Fix now:** Identify top disk consumers and cap runaway logs safely

```bash
sudo du -xh /var/log | sort -h | tail -50
sudo journalctl --disk-usage
sudo sed -i 's/^#SystemMaxUse=.*/SystemMaxUse=1G/' /etc/systemd/journald.conf || true
sudo systemctl restart systemd-journald || true
```

**7-day plan:**
- Confirm alerting on disk % and inode usage (thresholds + paging policy).
- Implement log rotation policy for app logs and set journald caps.
- Add a runbook: safe cleanup + where growth typically comes from.

**30-day plan:**
- Add SLO-driven alerting and capacity planning (trend disk growth).
- Standardize log retention per environment (dev/stage/prod).
- Automate checks in CI or daily cron to catch regressions.

**Questions I need answered:**
- Is this host stateful (DB) or stateless (app)? Cleanup approach differs.
- Any known log bursts (deploys, retries, noisy errors) causing growth?
- What is your on-call policy for disk alerts (page vs ticket)?


### Performance

#### [High] High sequential scan activity on large tables (public.orders, public.events)

**Impact:** Repeated sequential scans on large tables inflate latency and CPU, especially under concurrency. This is a common root cause of 'DB is slow' incidents.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/postgres/pg_stat_user_tables.csv (Tables with high reltuples and high seq_scan)

**Fix now:** Identify query patterns causing seq_scans and add targeted indexes

```bash
# Map top seq_scans to query patterns (pg_stat_statements + logs)
# Run EXPLAIN (ANALYZE, BUFFERS) to confirm scan type and cost
# Add the smallest viable index to support the common filter/order
psql -c "SELECT relname, seq_scan, idx_scan, n_live_tup, n_dead_tup FROM pg_stat_user_tables ORDER BY seq_scan DESC LIMIT 20;"
```

**7-day plan:**
- Map top seq_scanned tables to specific endpoints/jobs.
- Implement 1-2 high-ROI fixes (index or query rewrite) and measure p95 before/after.
- Ensure stats are current (ANALYZE) for affected tables.

**30-day plan:**
- Add performance dashboards/alerts (DB CPU, buffer hit rate, slow query spikes).
- Review ORM/query patterns (wide SELECT *, missing filters) driving scans.
- Consider partitioning for large time-series tables if growth continues.

**Questions I need answered:**
- Are these tables expected to be scan-heavy (analytics), or OLTP hot paths?
- Do you have read replicas or a separate analytics store?
- Any existing indexes that are unused or misaligned with query patterns?

#### [High] Postgres shows heavy time spent in a small set of queries (pg_stat_statements)

**Impact:** A handful of queries often dominate database load. Improving them typically reduces p95 latency, stabilizes CPU, and lowers infra cost by delaying scale-up.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/postgres/pg_stat_statements.csv:L1-L4 (Top queries by total_time_ms (sample))

**Fix now:** Validate query plans and implement the highest-impact index/query changes

```bash
# For each top query, run EXPLAIN (ANALYZE, BUFFERS) in a safe environment
# Confirm indexes with \d+ <table> and actual query patterns (params, ordering)
# Candidate index statements (validate with EXPLAIN + production constraints):
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON public.users (email);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_created_at ON public.orders (created_at DESC);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_token ON public.sessions (session_token);
```

**7-day plan:**
- Confirm pg_stat_statements is enabled and capturing representative traffic.
- Run EXPLAIN (ANALYZE, BUFFERS) for top queries and identify scans/sorts/hot joins.
- Implement 1-2 highest-ROI fixes (index or query rewrite) with safe rollout.

**30-day plan:**
- Add performance regression tests (key endpoints) and track DB p95 + CPU.
- Introduce SLO/alerts for slow query spikes and lock contention.
- Consider connection pooling tuning to reduce per-query overhead.

**Questions I need answered:**
- Are these queries representative of peak traffic (same workload + time window)?
- Any hard constraints on index build time / lock tolerance?
- Is read/write split or partitioning on the roadmap?


### Cost

#### [Medium] Possible overprovisioning signal: m5.2xlarge at low p95 utilization

**Impact:** If sustained utilization is low, you may be paying for capacity you don't need. Rightsizing can reduce spend without reducing reliability (when validated carefully).

**Confidence:** Low

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/cost/utilization_summary.json (instance=i-0123456789abcdef0, cpu_p95=12.4%, mem_p95=28.1% over 30 days)

**Fix now:** Create a rightsizing candidate and validate against peak/burst patterns

```bash
# Validate with a larger window and include disk + network + burst behavior
# If safe, test downsize one step in a canary environment first
aws cloudwatch get-metric-statistics ...  # (example: CPUUtilization p95/p99)
```

**7-day plan:**
- Pull 30-90d utilization including peak events and deploy windows.
- Identify a safe canary target for downsize and test rollback.
- Estimate savings and risk; execute one change with monitoring.

**30-day plan:**
- Adopt scheduled scaling or autoscaling where appropriate.
- Track unit cost per request/job and alert on regressions.
- Automate monthly cost posture checks and recommendations.

**Questions I need answered:**
- Are there known weekly/monthly peaks not represented in this sample?
- Any CPU credit/burstable instances involved?
- What is your rollback plan if latency increases after downsize?

#### [Low] EBS gp2 volumes detected; consider gp3 for cost/performance control

**Impact:** gp3 often provides better baseline performance and more predictable tuning. Switching from gp2 to gp3 can reduce cost and decouple size from performance.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- fixtures/cost/ebs_volumes.csv (gp2 volumes: vol-0aaa111)

**Fix now:** Evaluate gp3 migration plan (low-risk, validate per workload)

```bash
# In AWS: modify volume type to gp3 and set IOPS/throughput as needed
# Validate latency/IOPS requirements before and after
aws ec2 modify-volume --volume-id <vol-id> --volume-type gp3 --iops 3000 --throughput 125
```

**7-day plan:**
- Inventory gp2 volumes and identify those safe to migrate first.
- Migrate a non-critical volume and confirm workload metrics.
- Roll out remaining migrations with a change window + monitoring.

**30-day plan:**
- Standardize volume types/policies in IaC (default to gp3).
- Add cost posture checks for storage, snapshots, and idle resources.

**Questions I need answered:**
- Are there workloads with unusually high IOPS/throughput requirements?
- Do you have maintenance windows for volume modifications?
