from __future__ import annotations

from teardown_box.checks.linux_disk import LinuxDiskCheck
from teardown_box.checks.linux_ports import LinuxPortsCheck
from teardown_box.checks.linux_systemd import LinuxSystemdFlapCheck
from teardown_box.checks.nginx_proxy_timeouts import NginxProxyTimeoutsCheck
from teardown_box.checks.pg_autovacuum import PostgresAutovacuumCheck
from teardown_box.checks.pg_pool_saturation import PostgresPoolSaturationCheck
from teardown_box.checks.pg_seq_scans import PostgresSeqScansCheck
from teardown_box.checks.pg_slow_queries import PostgresSlowQueriesCheck
from teardown_box.checks.tls_policy import TlsPolicyCheck
from teardown_box.checks.cost_signals import CostSignalsCheck


def all_checks() -> list:
    return [
        LinuxDiskCheck(),
        LinuxSystemdFlapCheck(),
        LinuxPortsCheck(),
        PostgresSlowQueriesCheck(),
        PostgresSeqScansCheck(),
        PostgresAutovacuumCheck(),
        PostgresPoolSaturationCheck(),
        NginxProxyTimeoutsCheck(),
        TlsPolicyCheck(),
        CostSignalsCheck(),
    ]
