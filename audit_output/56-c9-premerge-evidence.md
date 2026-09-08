# C9 pre-merge evidence

Date (UTC): 2026-09-08

## Scope and classification

This evidence covers open source governance, deterministic CI, repository
metadata, and the pre-merge promotion gate. The product remains
**EXPERIMENTAL — NO-GO FOR REAL FUNDS**. No wallet, funded key, mainnet,
broadcast, Tor, Helios, Bitcoin Core, Docker, deployment, or production
environment was used.

## Governance delivered

- Standard MIT license, copyright MHX Digital 2026.
- Security policy centered on GitHub Private Vulnerability Reporting.
- Contributor Covenant 2.1, contribution/DCO policy, support policy, changelog,
  CODEOWNERS, pull request template, issue forms, and Dependabot configuration.
- Professional README with explicit trust boundaries, supported/blocked
  functionality, verified platforms, reproducible dependency flow, and
  third-party deployment/trademark disclaimer.
- Verified CODEOWNER `@neomaike`, the only direct repository collaborator and
  an active organization owner at the C9 baseline.

## CI review

`.github/workflows/ci.yml` responds only to pull requests into `main`, pushes to
`main`, and manual dispatch. Default permissions are `contents: read`.
Checkout does not persist credentials; no write permission, OIDC, deploy,
`pull_request_target`, Tor, Helios, Bitcoin Core, or privileged Docker exists.

Actions are pinned to full official commit SHAs:

- `actions/checkout` v4.2.2:
  `11bd71901bbe5b1630ceea73d27597364c9af683`.
- `actions/setup-python` v6.3.0:
  `ece7cb06caefa5fff74198d8649806c4678c61a1`.

The integrity job performs no dependency download after checkout. The test job
uses GitHub's action/Python infrastructure and the configured Python package
index to download only artifacts constrained by the committed hashes. A second
virtualenv installs from the private wheelhouse with `--no-index` and
`--require-hashes`. Its run-root is confined to `RUNNER_TEMP` and removed in a
trap. The expected suite count is explicit: 84.

All five YAML files parsed successfully with PyYAML 6.0.1. Repository tests also
enforce immutable action references, read-only permissions, events, lack of
deploy/OIDC, dependency hashing, exact suite count, and cleanup boundaries.

## Local pre-merge tests

Authoritative run ID: `cold-wallets-c9-tLqf8w02`. Platform: Linux x86-64,
CPython 3.12.3. A preparation virtualenv populated a 32-file wheelhouse using
the committed hashes. A second virtualenv installed offline and ran:

```text
env PYTHONDONTWRITEBYTECODE=1 <test-venv>/bin/python -m unittest discover -s tests -v
```

Result: **84 tests, 84 passed, 0 skipped, 0 failures, 0 errors**, 3.359 seconds
(4 seconds at harness wall-clock granularity).

The suite resource record used run ID
`9b71baa1d32d4edcb1ecdc21a4849268`, ephemeral port `46383`, and reported zero
process, container, network, volume, or file residue. Host listener inventory
was 35 before and after; preexisting listeners were not touched.

## Secret review

Gitleaks 8.30.1 was downloaded from its official GitHub release into an
exclusive temporary root. The release checksum authenticated the Linux x64
archive as:

`551f6fc83ea457d62a0d98237cbad105af8d557003051f41f3e7ca7b3f2470eb`

The current tree and branch history from base to HEAD both completed with zero
unsuppressed findings. One prior `generic-api-key` match was a reviewed
synthetic idempotency fixture, not a credential. The current tree renamed its
ambiguous local variable, and `.gitleaksignore` suppresses only the exact
historical fingerprint. A regression test prevents silently broadening that
allowlist. No possible secret value was printed or recorded.

## Hygiene

| Resource | Preexisting | Created by authoritative run | Removed/ended | Residue |
|---|---:|---:|---:|---:|
| Processes/subprocesses | inventoried | transient test processes | all owned | 0 |
| Threads | 0 owned | transient | all owned | 0 |
| Listening ports | 35 host listeners | one ephemeral listener | released | 0 |
| Virtualenvs | 0 cycle-owned | 2 | 2 | 0 |
| Wheelhouse | 0 cycle-owned | 1 / 32 files | 1 | 0 |
| Pip cache | 0 cycle-owned | 1 confined cache | 1 | 0 |
| Test files/databases/logs | 0 cycle-owned | temporary fixtures | all owned | 0 |
| Repository bytecode | 0 | 0 | 0 | 0 |
| Containers/networks/volumes | 0 cycle-owned | 0 | 0 | 0 |
| External services/deploys | 0 | 0 | 0 | 0 |

Gitleaks run `cold-wallets-c9-scan-i7NgGzqK` also ended with zero temporary
residue. Earlier diagnostic scan roots were each removed after use.

## Promotion constraints

Promotion to `main` requires the remote CI for the exact final PR HEAD, checksum
manifest 57, clean worktree, secret review, and branch protection. Because the
repository has one human owner/collaborator, GitHub cannot count self-approval.
For the first merge, any temporary zero-review PR gate must be documented and
immediately replaced after merge with a definitive one-review CODEOWNER rule.
That definitive rule intentionally blocks future merges until a second trusted
reviewer can provide independent approval.

No deploy workflow will be created. A `production` environment is unnecessary
while official deployment does not exist. Third parties may deploy MIT-licensed
forks, but those deployments are not official or endorsed by MHX Digital.
