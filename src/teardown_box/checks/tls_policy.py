from __future__ import annotations

from typing import List

from teardown_box.findings import EvidenceRef, Finding, FixNow
from teardown_box.fixtures import Fixtures


class TlsPolicyCheck:
    name = "edge.tls_policy"

    def applies(self, fx: Fixtures) -> bool:
        return fx.exists("edge/tls_scan.txt")

    def run(self, fx: Fixtures) -> List[Finding]:
        txt = fx.read_text("edge/tls_scan.txt")
        if txt is None:
            return []

        lower = txt.lower()
        legacy_enabled = ("tlsv1.0: enabled" in lower) or ("tlsv1.1: enabled" in lower)
        hsts_missing = "hsts: missing" in lower

        findings: List[Finding] = []

        if legacy_enabled:
            findings.append(
                Finding(
                    category="Security",
                    severity="medium",
                    title="Legacy TLS versions appear enabled (TLS 1.0/1.1)",
                    impact=(
                        "Older TLS versions weaken security posture and may violate compliance expectations. "
                        "Most modern clients support TLS 1.2+."
                    ),
                    confidence="Medium",
                    evidence=[
                        EvidenceRef(
                            path="fixtures/edge/tls_scan.txt",
                            note="TLSv1.0/TLSv1.1 enabled in scan summary",
                        )
                    ],
                    fix_now=FixNow(
                        title="Disable TLS 1.0/1.1 and standardize a modern policy",
                        commands=[
                            "# Target: TLS 1.2 and 1.3 only (exact config depends on your edge stack).",
                            "ssl_protocols TLSv1.2 TLSv1.3;",
                            "# Use a modern cipher suite policy appropriate to your environment.",
                        ],
                    ),
                    plan_7d=[
                        "Confirm client compatibility requirements (legacy devices/browsers).",
                        "Disable TLS 1.0/1.1 and redeploy edge config.",
                        "Run a follow-up scan to confirm posture.",
                    ],
                    plan_30d=[
                        "Automate TLS posture scans (scheduled) and alert on regressions.",
                        "Adopt managed TLS policies via CDN/WAF where feasible.",
                        "Track certificate renewal and config drift.",
                    ],
                    questions=[
                        "Do you terminate TLS at a CDN/WAF or on the origin?",
                        "Any compliance requirements (PCI/HIPAA/SOC2) driving a specific policy?",
                        "Any legacy clients that truly require TLS 1.0/1.1?",
                    ],
                )
            )

        if hsts_missing:
            findings.append(
                Finding(
                    category="Security",
                    severity="low",
                    title="HSTS is missing",
                    impact=(
                        "Without HSTS, clients can be tricked into initial HTTP connections in some downgrade scenarios. "
                        "HSTS is usually a low-risk hardening win for public HTTPS sites."
                    ),
                    confidence="Medium",
                    evidence=[
                        EvidenceRef(
                            path="fixtures/edge/tls_scan.txt",
                            note="HSTS marked missing in scan summary",
                        )
                    ],
                    fix_now=FixNow(
                        title="Add an HSTS header after validating HTTPS-only readiness",
                        commands=[
                            'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
                            "# Consider preload only after careful validation.",
                        ],
                    ),
                    plan_7d=[
                        "Confirm all subdomains are HTTPS and redirects are correct.",
                        "Deploy HSTS and validate no mixed-content regressions.",
                    ],
                    plan_30d=[
                        "Add a baseline set of security headers (CSP, X-Content-Type-Options, etc.).",
                        "Automate header checks in CI.",
                    ],
                    questions=[
                        "Are there any HTTP-only subdomains/endpoints still in use?",
                        "Do you already use a CDN/WAF that can set headers globally?",
                    ],
                )
            )

        return findings
