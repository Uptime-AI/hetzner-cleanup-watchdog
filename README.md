# Generic free firewall cleanup proof — NOT activated

Publication candidate only. This directory contains no product code, repository history, credentials, project identifiers or customer data. Export ONLY watchdog.py, test_watchdog.py, this README, and delete-firewall.yml (the latter to .github/workflows/delete-firewall.yml) into a separately approved new public repository. Never export the surrounding repository or its history. No external Actions, packages, cache, artifacts or self-hosted runners are needed.

## Decision

GO for a reviewed public minimal repository model and offline preparation. NO-GO for publication, credential upload, dispatch or paid infrastructure until explicit approval and verified controls. This is a bounded FREE FIREWALL proof, not a server-deletion watchdog. It cannot authorize a paid build. Server/primary-IP/key cleanup, partial-creation recovery, the long-lived READY/heartbeat timer and cancellation handling remain unimplemented and must be reviewed/tested before any paid resource.

## Required repository controls BEFORE any secret

- New public generic-only repository, default branch main; no imported private history, credentials or product workflows. Keep all other repositories private and unchanged.
- Protect main against direct/force push/deletion; require reviewed changes to every executable file/workflow. Apply protections to administrators too. Verify an actual allowed reviewer exists; do not claim a two-person review if there is only one maintainer. If policy requires an independent reviewer and none exists, STOP.
- Create exactly the cleanup-proof Environment. Select branch main explicitly (branch, not tag); do not use the broad 'protected branches only' setting, which permits all branches when no protection exists. Require human approval, disable administrator bypass. Prevent self-review only when a distinct authorized approver exists; otherwise disclose and resolve that limitation before activation.
- HCLOUD_TOKEN must exist ONLY as that Environment's encrypted secret, never repository/organization-wide, input, file, command argument, output or artifact. The secret-bearing step alone receives it. No debug tracing or raw exception/header/body logs. Remove the secret and revoke the temporary token after verified cleanup and watcher exit.
- Environment restrictions are NOT workflow-exclusive. Any reviewed workflow on allowed main could request the same Environment. Repository administrators and workflow/code editors remain trusted. Hetzner read-write token grants broad project rights despite this code allowing GET/DELETE firewalls only. Use a dedicated otherwise empty diagnostic project; verify its isolation privately before accepting this residual risk. Do not claim a delete-only token.
- workflow_dispatch only; no push/PR/pull_request_target/workflow_run/cron, reusable-workflow entry or external Actions. Job additionally requires dispatch+refs/heads/main. Public forks receive neither Environment configuration nor this secret. Never approve a different ref or unreviewed commit.
- Standard ubuntu-24.04 hosted runner only, 10-minute timeout, serialized proof, no cache/artifact/larger runner. Verify Actions permitted and runner availability before creating the free firewall. Public standard hosted minutes are free; no paid runner or storage path is included. Queued/approved does not mean RUNNING.

## One future FREE live proof (requires approval; NOT performed)

1. Verify actual repository protections, environment branch rule, reviewers/bypass, exact reviewed commit and cost path. Inspect code and run offline tests before token delegation. Token stays off all public surfaces.
2. From the authorized local controller create exactly one explicitly approved unattached Cloud Firewall, with fresh random 32-character lowercase hexadecimal run identifier. Name cleanup-proof-<run>; labels exactly cleanup-run=<run>. No selector, server association, paid IP/VM or other resources. Confirm ID/creation timestamp and all ownership fields privately. Hetzner documents Cloud Firewalls as free.
3. Dispatch exactly once with that non-secret firewall ID/run label. Review exact main SHA before Environment approval. Start within 14 minutes of firewall creation. Inputs are data env vars, never shell expressions. No credential in dispatch inputs. Runner fetches its exact public commit without credentials before the secret step.
4. On BOUND_READY, observe the remote job still RUNNING, then suspend the LOCAL OBSERVER for the bounded 60-second delay (leave Mac fallback available). The hosted process must perform one DELETE, require known-ID404 and paginated list absence. Never attach the firewall meanwhile. A 202 alone is not success; initial404 is not proof; wrong ownership/freshness => zero DELETE. API errors => STOP, not absence.
5. Independently GET the known ID and all list pages from the local API or Console. Record sanitized workflow/run/SHA/timestamps, exact resource binding, DELETE result, confirmed absence and costs. Public logs show fixed status messages only. Offline tests do not establish real API compatibility or independent execution. No live success is asserted now.
6. On failure/cancellation, use the independent Mac fallback to delete ONLY the same verified unattached resource. No blind redispatch. Free firewall remaining is a failed proof, not a billing-ended claim. Remove secret and revoke token after both controllers exit and absence is verified.

## Later paid-resource gate (separate, unresolved)

Only after the free proof succeeds, review the additional generic server/IP/key ownership and orphan-recovery implementation and tests. Run a hosted watchdog BEFORE provisioning; require fresh READY/heartbeat and sufficient deadline. Planned remote deletion begins READY+195min, Mac fallback at210min, VM creation within5min; timeout240min leaves cleanup margin below the four-hour VM cap. Neither simultaneous controller failure nor Hetzner API outage can be guaranteed away. STOP if an absolute failure-independent four-hour guarantee is required. Prices/capacity/VAT and cumulative budget must be freshly checked before any paid creation. This proof template has no server deletion capability and MUST NOT be reused as that safeguard.

## Offline tests

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -v

Tests use fake transport/time only. No cloud/API requests, credentials or resource creation. The executable supports only the fixed HTTPS Hetzner API, disables redirects and environment proxies, limits response size and pagination, and never prints raw API errors. A platform admin or compromised trusted runner remains outside these code guards.

## Primary references

- https://docs.github.com/en/actions/reference/workflows-and-actions/deployments-and-environments
- https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow
- https://docs.github.com/en/actions/reference/runners/github-hosted-runners
- https://docs.hetzner.com/cloud/firewalls/overview/
