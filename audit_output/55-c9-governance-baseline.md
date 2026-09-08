# C9 governance baseline

Date (UTC): 2026-09-08

## Gate C9-G0

| Check | Expected | Observed | Result |
|---|---|---|---|
| Repository | `MHX-Digital/cold-wallets` | matched | PASS |
| Active branch | `audit/cold-wallet-security-architecture-20260907` | matched | PASS |
| Initial HEAD | `f39b529d448cb3eff21148a49bf91d4f738b87ed` | matched locally, remotely and in PR #1 | PASS |
| Local/remote `main` | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | matched | PASS |
| Worktree | clean, including untracked | clean | PASS |
| Registered worktrees | one | one | PASS |
| Remote branches | exactly `main` and audit branch | matched | PASS |
| PR #1 | open, draft, unmerged, correct base/head | matched and mergeable | PASS |
| Checkpoint chain | manifests 50, 52 and 54 | manifest files 50/52 authenticated by 54; all current targets in 54 matched | PASS |
| Git integrity | diff check and fsck | passed | PASS |

There is one additional local-only historical branch,
`audit/cold-wallet-security-architecture`. It has no worktree and is not
published. It is retained until the authorized post-merge branch cleanup.

## GitHub identity and authority

- Authenticated GitHub login: `neomaike`.
- Organization membership: active owner (`admin`) of `MHX-Digital`.
- Repository permission: `admin` (also push/maintain/triage/pull).
- Direct collaborators: only `neomaike`, with admin permission.
- Resolved CODEOWNER for this cycle: `@neomaike`.

No credential value was recorded. Authentication output displayed only a
masked token.

## Initial GitHub configuration

| Control | Initial state |
|---|---|
| Default branch | `main` |
| Branch protection / rulesets | none; `main` unprotected |
| GitHub Actions | enabled; all actions allowed; SHA pinning not required |
| Workflows | none |
| Environments | none |
| Actions/Dependabot/Codespaces secrets | zero names returned |
| Dependabot security updates | disabled |
| Vulnerability alerts endpoint | unavailable/disabled (404) |
| Private vulnerability reporting | disabled |
| Secret scanning / push protection | disabled |
| Releases / tags | none |
| Deploy keys / webhooks | none |
| Issues | enabled |
| Wiki | enabled |
| Auto-merge | disabled |
| About description / homepage / topics | empty |

Organization GitHub Apps visible to the authenticated owner were Railway,
Atlassian, ChatGPT Codex Connector, Claude, Claude Design Import, and Vercel.
Most report organization-wide repository selection; this inventory does not
prove which permissions each App exercises on this repository. None was
removed because obsolescence and authorization to revoke were not established.

## Safety baseline

The product remains **EXPERIMENTAL — NO-GO FOR REAL FUNDS**. This cycle does not
authorize deployment, blockchain network execution, wallets, signing with real
secrets, Tor, Helios, Bitcoin Core, or broadcast.
