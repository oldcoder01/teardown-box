# Teardown Report (Sample)

## Teardown in a Box (48-hour non-invasive teardown)

**What this is:** A fast, non-invasive teardown that turns a messy system into a prioritized fix list.
**What you get:** A report like this + a short call to confirm priorities + a fix-now shortlist.
**Who it's for:** Small SaaS / agencies / teams with recurring incidents, slow Postgres, and unclear next steps.

**Next step:** [Book 15 minutes](https://calendly.com/jason-kelly-001/introcall) — info@buzzyplanet.com

_Generated: 2026-01-05T12:56:44-08:00_

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

## Triage table (skim-friendly)

| Sev | Area | Finding | Why it matters | Fix-now | Effort | Risk |
|---|---|---|---|---|---|---|
| Medium | Cost | [**Possible overprovisioning signal: m5.2xlarge at low p95 utilization**](#finding-0001) | If sustained utilization is low, you may be paying for capacity you don't need | Create a rightsizing candidate and validate against peak/burst patterns | Medium | High |
| Low | Cost | [**EBS gp2 volumes detected; consider gp3 for cost/performance control**](#finding-0002) | gp3 often provides better baseline performance and more predictable tuning | Evaluate gp3 migration plan (low-risk, validate per workload) | Low | Medium |
| High | Performance | [**High sequential scan activity on large tables (public.orders, public.events)**](#finding-0003) | Repeated sequential scans on large tables inflate latency and CPU, especially under concurrency | Identify query patterns causing seq_scans and add targeted indexes | Medium | Medium |
| High | Performance | [**Postgres shows heavy time spent in a small set of queries (pg_stat_statements)**](#finding-0004) | A handful of queries often dominate database load | Validate query plans and implement the highest-impact index/query changes | Medium | Medium |
| High | Reliability | [**Connection pool appears saturated (high client usage / waiting queue)**](#finding-0005) | When the pool saturates, requests queue and tail latency spikes | Reduce pool pressure and protect the DB from connection storms | Medium | Medium |
| High | Reliability | [**systemd service appears to be flapping (restart loop)**](#finding-0006) | Restart loops create intermittent downtime, amplify load (retry storms), and usually mask a real dependency issue (DB, DNS, config, or secr… | Pull recent logs and verify dependencies; add backoff while fixing root cause | Medium | Medium |
| Medium | Reliability | [**Autovacuum pressure likely on (public.orders, public.events, public.sessions) with high dead tuple ratios**](#finding-0007) | High dead tuples increase bloat and slow queries (more pages to scan, worse cache locality) | Inspect worst tables and tune vacuum/analyze thresholds where needed | Medium | Medium |
| Medium | Reliability | [**Disk usage is high (87%) on at least one filesystem**](#finding-0008) | High disk usage is a common outage trigger (writes fail, services crash, databases stall) | Identify top disk consumers and cap runaway logs safely | Medium | Medium |
| High | Security | [**Unexpected public listener detected on port 5432**](#finding-0009) | Public listeners expand the attack surface | Restrict bind address and enforce network controls | Medium | Medium |
| Medium | Security | [**Legacy TLS versions appear enabled (TLS 1.0/1.1)**](#finding-0010) | Older TLS versions weaken security posture and may violate compliance expectations | Disable TLS 1.0/1.1 and standardize a modern policy | Medium | Medium |
| Low | Security | [**HSTS is missing**](#finding-0011) | Without HSTS, clients can be tricked into initial HTTP connections in some downgrade scenarios | Add an HSTS header after validating HTTPS-only readiness | Medium | Medium |

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

## Findings

### Security

<a id="finding-0009"></a>
#### [High] Unexpected public listener detected on port 5432

**Impact:** Public listeners expand the attack surface. Databases and caches should not be exposed to the internet without strong justification, network controls, and monitoring.

**Confidence:** High

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/linux/ss_lntp.txt:L5-L5 (Bound to 0.0.0.0:5432)](#ev-38959d52f8)

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

<a id="finding-0010"></a>
#### [Medium] Legacy TLS versions appear enabled (TLS 1.0/1.1)

**Impact:** Older TLS versions weaken security posture and may violate compliance expectations. Most modern clients support TLS 1.2+.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/edge/tls_scan.txt (TLSv1.0/TLSv1.1 enabled in scan summary)](#ev-8eba99682e)

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

<a id="finding-0011"></a>
#### [Low] HSTS is missing

**Impact:** Without HSTS, clients can be tricked into initial HTTP connections in some downgrade scenarios. HSTS is usually a low-risk hardening win for public HTTPS sites.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/edge/tls_scan.txt (HSTS marked missing in scan summary)](#ev-23fd6b3517)

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

<a id="finding-0005"></a>
#### [High] Connection pool appears saturated (high client usage / waiting queue)

**Impact:** When the pool saturates, requests queue and tail latency spikes. This often presents as timeouts and cascading retries, which further increases load.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/postgres/pg_pool_stats.json (clients=4860/5000, waiting=322, avg_wait_ms=185.0)](#ev-5ee8609c2c)

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

<a id="finding-0006"></a>
#### [High] systemd service appears to be flapping (restart loop)

**Impact:** Restart loops create intermittent downtime, amplify load (retry storms), and usually mask a real dependency issue (DB, DNS, config, or secrets). They also consume CPU and can trigger cascading failures.

**Confidence:** High

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/linux/systemctl_status.txt:L8-L8 (Restart counter is 27)](#ev-b723445da9)

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

<a id="finding-0007"></a>
#### [Medium] Autovacuum pressure likely on (public.orders, public.events, public.sessions) with high dead tuple ratios

**Impact:** High dead tuples increase bloat and slow queries (more pages to scan, worse cache locality). If vacuum can't keep up, performance degrades and storage costs rise.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/postgres/pg_stat_user_tables.csv (Tables with high n_dead_tup relative to n_live_tup)](#ev-14ed22c00e)

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

<a id="finding-0008"></a>
#### [Medium] Disk usage is high (87%) on at least one filesystem

**Impact:** High disk usage is a common outage trigger (writes fail, services crash, databases stall). It also hides other problems (logs grow until the host falls over).

**Confidence:** High

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/linux/df_h.txt:L2-L2 (Filesystem above threshold: /dev/nvme0n1p2  100G   87G   13G  87% /)](#ev-981e1d7f5a)

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

<a id="finding-0003"></a>
#### [High] High sequential scan activity on large tables (public.orders, public.events)

**Impact:** Repeated sequential scans on large tables inflate latency and CPU, especially under concurrency. This is a common root cause of 'DB is slow' incidents.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/postgres/pg_stat_user_tables.csv (Tables with high reltuples and high seq_scan)](#ev-909b017bb4)

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

<a id="finding-0004"></a>
#### [High] Postgres shows heavy time spent in a small set of queries (pg_stat_statements)

**Impact:** A handful of queries often dominate database load. Improving them typically reduces p95 latency, stabilizes CPU, and lowers infra cost by delaying scale-up.

**Confidence:** Medium

**Effort / Blast radius:** Medium / Medium

**Evidence:**
- [fixtures/postgres/pg_stat_statements.csv:L1-L4 (Top queries by total_time_ms (sample))](#ev-473008823f)

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

<a id="finding-0001"></a>
#### [Medium] Possible overprovisioning signal: m5.2xlarge at low p95 utilization

**Impact:** If sustained utilization is low, you may be paying for capacity you don't need. Rightsizing can reduce spend without reducing reliability (when validated carefully).

**Confidence:** Low

**Effort / Blast radius:** Medium / High

**Evidence:**
- [fixtures/cost/utilization_summary.json (instance=i-0123456789abcdef0, cpu_p95=12.4%, mem_p95=28.1% over 30 days)](#ev-87d6e8aded)

**Fix now:** Create a rightsizing candidate and validate against peak/burst patterns

```bash
# Validate with a larger window and include disk + network + burst behavior
# If safe, test downsize one step in a canary environment first
aws cloudwatch get-metric-statistics ...  # (example: CPUUtilization p95/p99)
```

**Validation / success / rollback:**
- Validate safely: Validate with 30–90d metrics and test one-step downsize on a canary; ensure p95/p99 latency and error rate do not regress.
- Success metric: Monthly spend reduced without SLO regression (p95 latency, error rate, saturation).
- Rollback: Scale back to prior instance type/size immediately; revert autoscaling/schedule changes if applied.

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

<a id="finding-0002"></a>
#### [Low] EBS gp2 volumes detected; consider gp3 for cost/performance control

**Impact:** gp3 often provides better baseline performance and more predictable tuning. Switching from gp2 to gp3 can reduce cost and decouple size from performance.

**Confidence:** Medium

**Effort / Blast radius:** Low / Medium

**Evidence:**
- [fixtures/cost/ebs_volumes.csv (gp2 volumes: vol-0aaa111)](#ev-4b5c109bc2)

**Fix now:** Evaluate gp3 migration plan (low-risk, validate per workload)

```bash
# In AWS: modify volume type to gp3 and set IOPS/throughput as needed
# Validate latency/IOPS requirements before and after
aws ec2 modify-volume --volume-id <vol-id> --volume-type gp3 --iops 3000 --throughput 125
```

**Validation / success / rollback:**
- Validate safely: Migrate a non-critical volume first; compare I/O latency and throughput before/after under normal and peak load.
- Success metric: Lower storage cost and/or improved baseline IOPS/throughput with no latency regressions.
- Rollback: Switch volume type back (or increase gp3 IOPS/throughput) if latency regresses.

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


## Raw evidence

Evidence links above jump here. Snippets are extracted from the fixture bundle used to generate this report.

<a id="ev-14ed22c00e"></a>
### fixtures/postgres/pg_stat_user_tables.csv (Tables with high n_dead_tup relative to n_live_tup)

<details>
<summary>Show snippet</summary>

```text
    1: schemaname,relname,seq_scan,seq_tup_read,idx_scan,n_tup_ins,n_tup_upd,n_tup_del,n_live_tup,n_dead_tup,last_vacuum,last_autovacuum,last_analyze,last_autoanalyze,reltuples
    2: public,orders,18250,92384012,1200,250000,12000,800,2150000,420000,,2025-12-29 03:10:00,2025-12-30 04:10:00,2025-12-31 04:10:00,2300000
    3: public,events,9050,55120000,500,1100000,5000,1000,9100000,1250000,,2025-12-15 02:00:00,2025-12-20 02:00:00,2025-12-20 02:00:00,10300000
    4: public,users,120,8200,55000,5000,2000,10,84000,1200,2025-12-28 01:00:00,2025-12-31 01:00:00,2025-12-31 01:05:00,2025-12-31 01:05:00,84000
    5: public,sessions,240,56000,2200,800000,900000,200000,1200000,950000,,2025-12-10 01:00:00,2025-12-10 01:05:00,2025-12-10 01:05:00,1250000
```

</details>

<a id="ev-23fd6b3517"></a>
### fixtures/edge/tls_scan.txt (HSTS marked missing in scan summary)

<details>
<summary>Show snippet</summary>

```text
    1: # Fake TLS scan summary
    2: TLSv1.0: enabled
    3: TLSv1.1: enabled
    4: TLSv1.2: enabled
    5: TLSv1.3: enabled
    6: HSTS: missing
    7: Cipher suites: includes some legacy CBC suites
```

</details>

<a id="ev-38959d52f8"></a>
### fixtures/linux/ss_lntp.txt:L5-L5 (Bound to 0.0.0.0:5432)

<details>
<summary>Show snippet</summary>

```text
    5: LISTEN 0      244    0.0.0.0:5432         0.0.0.0:*          users:(("postgres",pid=1201,fd=7))
```

</details>

<a id="ev-473008823f"></a>
### fixtures/postgres/pg_stat_statements.csv:L1-L4 (Top queries by total_time_ms (sample))

<details>
<summary>Show snippet</summary>

```text
    1: queryid,calls,total_time_ms,mean_time_ms,rows,query
    2: 1001,8421,912345.5,108.3,8421,"SELECT id,email,last_login FROM users WHERE email = $1"
    3: 1002,421,602110.2,1430.4,421,"SELECT * FROM orders WHERE created_at >= $1 AND created_at < $2 ORDER BY created_at DESC LIMIT 200"
    4: 1003,11021,401221.9,36.4,11021,"UPDATE sessions SET expires_at = $1 WHERE session_token = $2"
```

</details>

<a id="ev-4b5c109bc2"></a>
### fixtures/cost/ebs_volumes.csv (gp2 volumes: vol-0aaa111)

<details>
<summary>Show snippet</summary>

```text
    1: volume_id,type,size_gb,iops,throughput_mbps,attached_instance_id
    2: vol-0aaa111,gp2,500,1500,,i-0123456789abcdef0
    3: vol-0bbb222,gp3,200,3000,125,i-0123456789abcdef0
```

</details>

<a id="ev-5ee8609c2c"></a>
### fixtures/postgres/pg_pool_stats.json (clients=4860/5000, waiting=322, avg_wait_ms=185.0)

<details>
<summary>Show snippet</summary>

```text
    1: {
    2:   "pooler": "pgbouncer",
    3:   "db": "app",
    4:   "max_client_conn": 5000,
    5:   "default_pool_size": 50,
    6:   "current_clients": 4860,
    7:   "current_waiting": 322,
    8:   "avg_wait_ms": 185,
    9:   "peak_wait_ms": 2400,
   10:   "notes": "Spikes observed during deploy window"
   11: }
```

</details>

<a id="ev-87d6e8aded"></a>
### fixtures/cost/utilization_summary.json (instance=i-0123456789abcdef0, cpu_p95=12.4%, mem_p95=28.1% over 30 days)

<details>
<summary>Show snippet</summary>

```text
    1: {
    2:   "instance_id": "i-0123456789abcdef0",
    3:   "instance_type": "m5.2xlarge",
    4:   "cpu_p95_percent": 12.4,
    5:   "cpu_p50_percent": 4.8,
    6:   "memory_p95_percent": 28.1,
    7:   "network_p95_mbps": 42.0,
    8:   "period_days": 30,
    9:   "notes": "Workload steady; no batch peaks detected"
   10: }
```

</details>

<a id="ev-8eba99682e"></a>
### fixtures/edge/tls_scan.txt (TLSv1.0/TLSv1.1 enabled in scan summary)

<details>
<summary>Show snippet</summary>

```text
    1: # Fake TLS scan summary
    2: TLSv1.0: enabled
    3: TLSv1.1: enabled
    4: TLSv1.2: enabled
    5: TLSv1.3: enabled
    6: HSTS: missing
    7: Cipher suites: includes some legacy CBC suites
```

</details>

<a id="ev-909b017bb4"></a>
### fixtures/postgres/pg_stat_user_tables.csv (Tables with high reltuples and high seq_scan)

<details>
<summary>Show snippet</summary>

```text
    1: schemaname,relname,seq_scan,seq_tup_read,idx_scan,n_tup_ins,n_tup_upd,n_tup_del,n_live_tup,n_dead_tup,last_vacuum,last_autovacuum,last_analyze,last_autoanalyze,reltuples
    2: public,orders,18250,92384012,1200,250000,12000,800,2150000,420000,,2025-12-29 03:10:00,2025-12-30 04:10:00,2025-12-31 04:10:00,2300000
    3: public,events,9050,55120000,500,1100000,5000,1000,9100000,1250000,,2025-12-15 02:00:00,2025-12-20 02:00:00,2025-12-20 02:00:00,10300000
    4: public,users,120,8200,55000,5000,2000,10,84000,1200,2025-12-28 01:00:00,2025-12-31 01:00:00,2025-12-31 01:05:00,2025-12-31 01:05:00,84000
    5: public,sessions,240,56000,2200,800000,900000,200000,1200000,950000,,2025-12-10 01:00:00,2025-12-10 01:05:00,2025-12-10 01:05:00,1250000
```

</details>

<a id="ev-981e1d7f5a"></a>
### fixtures/linux/df_h.txt:L2-L2 (Filesystem above threshold: /dev/nvme0n1p2  100G   87G   13G  87% /)

<details>
<summary>Show snippet</summary>

```text
    2: /dev/nvme0n1p2  100G   87G   13G  87% /
```

</details>

<a id="ev-b723445da9"></a>
### fixtures/linux/systemctl_status.txt:L8-L8 (Restart counter is 27)

<details>
<summary>Show snippet</summary>

```text
    8: Jan 05 07:41:22 host systemd[1]: api.service: Scheduled restart job, restart counter is at 27.
```

</details>
