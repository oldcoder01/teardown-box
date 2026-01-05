from __future__ import annotations

from typing import List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class NginxProxyTimeoutsCheck:
    name = "edge.nginx.proxy_timeouts"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("edge/nginx.conf")

    def run(self, fx: Fixtures) -> List[Finding]:
        txt = fx.read_text("edge/nginx.conf")
        if txt is None:
            return []

        has_proxy_pass = "proxy_pass" in txt
        has_read_timeout = "proxy_read_timeout" in txt
        if not has_proxy_pass or has_read_timeout:
            return []

        return [
            Finding(
                category="Reliability",
                severity="medium",
                title="Nginx proxy_read_timeout not set (may cause upstream timeouts under load)",
                impact=(
                    "Default proxy timeouts can be too short for slow upstreams or cold starts, causing 504s and client retries. "
                    "This inflates load and worsens tail latency."
                ),
                confidence="High",
                evidence=[
                    EvidenceRef(
                        path="fixtures/edge/nginx.conf",
                        note="proxy_pass present but proxy_read_timeout not found",
                    )
                ],
                fix_now=FixNow(
                    title="Set baseline proxy timeouts for upstream behavior",
                    commands=[
                        "# Example baseline (tune per service):",
                        "proxy_connect_timeout 5s;",
                        "proxy_send_timeout 60s;",
                        "proxy_read_timeout 60s;",
                    ],
                ),
                plan_7d=[
                    "Set reasonable defaults for proxy_*_timeout and document per-service overrides.",
                    "Correlate 5xx spikes with upstream latency; tune timeouts to reality.",
                    "Add request timeouts in the app to avoid hung requests.",
                ],
                plan_30d=[
                    "Add structured edge logging (upstream_response_time, status) and dashboards.",
                    "Introduce circuit breakers/backoff for slow downstream dependencies.",
                    "Standardize Nginx templates and test configs in CI.",
                ],
                questions=[
                    "What are the upstream p95/p99 response times during peak?",
                    "Do you run long-lived requests (exports, reports) that need higher timeouts?",
                    "Any CDN in front that imposes its own timeouts?",
                ],
            )
        ]
