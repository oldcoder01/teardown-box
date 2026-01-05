# How I work (48-hour teardown)

This is the same playbook I use on real systems. The CLI demo is a portable version of the workflow.

## Day 0 (intake + scope)
- Clarify goals: cost reduction, stability, security posture, performance, or all of the above.
- Identify constraints: maintenance windows, compliance requirements, risk tolerance.
- Collect artifacts:
  - OS/service snapshots, logs, network listeners/ports
  - Database stats: pg_stat_statements, pg_stat_user_tables, config basics
  - Edge config: nginx/ingress, TLS posture, headers
  - Infra/IaC diffs: terraform plan, security group changes
  - Cost/utilization: p95 CPU/memory, storage types

## Day 1 (triage + quick wins)
- Normalize evidence and establish a baseline.
- Identify top risks by severity + impact.
- Deliver "Fix now" items that are safe and reversible.
- Draft a 7-day stabilization plan.

## Day 2 (report + plan)
- Produce a client-ready report:
  - Findings grouped by category with evidence references
  - Severity + impact explained in plain English
  - Safe "Fix now" commands/snippets
  - 7-day plan (stabilize) + 30-day plan (hardening)
  - Questions I need answered to validate assumptions
- Walk the report live and agree on an implementation plan.

## What you get
- A tangible artifact you can share internally (Markdown and optional HTML)
- Clear next steps (7-day / 30-day)
- A short list of questions that unblock deeper remediation work
