# C9.1 Windows main handoff correction

Date (UTC): 2026-09-08

## Baseline

The workspace was refreshed from
`https://github.com/MHX-Digital/cold-wallets.git`. The required initial main
commit was confirmed locally and remotely:

`12ed2fa968d341fcbd12601ff156de884ca3a101`

Gate C9.1-G0 confirmed GitHub authentication for `neomaike`, Git identity
`MaikeH <neomaike@gmail.com>`, default branch `main`, one registered worktree,
clean tracked and untracked state, exactly one remote branch (`origin/main`),
merged PR #1, passing `git diff --check`, passing `git fsck --no-dangling`, and
manifest 57 matching the published Git blobs from the baseline commit. The
Windows checkout had `core.autocrlf=true`, so direct working-tree
`sha256sum -c` was not used as the baseline authority.

## Root cause

The C8 Windows preflight still required the deleted audit branch and the
pre-merge `main` base. After PR #1 was squash-merged, a fresh clone of `main`
could not satisfy those branch and base checks. The CI integrity job also still
validated manifest 57, which is a historical checkpoint covering files modified
by this correction.

## Corrections

- `validation/windows/c8-preflight.ps1` now requires `ExpectedHead` externally,
  defaults `ExpectedBranch` to `main`, rejects detached HEAD, validates the
  official origin remote, and requires `HEAD`, `refs/heads/main`, and
  `refs/remotes/origin/main` to equal the supplied SHA.
- The preflight does not fetch, pull, clone, reset, clean, deploy, or call web
  endpoints. The operator must fetch references before running it.
- The worktree inventory is coerced to an array before counting, so a valid
  single-worktree clone does not become a PowerShell scalar without `.Count`.
- The preflight validates only manifest 59 as the operational checksum manifest.
  Manifest 57 is historical evidence authenticated by manifest 59.
- `.github/workflows/ci.yml` validates
  `audit_output/59-c91-checksums.txt`, keeps read-only contents permission,
  keeps SHA-pinned actions, and keeps the explicit zero-skip test gate.
- `validation/windows/C8-RUNBOOK.md` now starts from a fresh clone of `main`,
  fetches and checks out `main`, requires `main == origin/main`, and passes the
  post-C9.1 merge SHA through `-ExpectedHead`.
- `CHANGELOG.md` records the unreleased handoff correction while preserving the
  existing pre-release tag.
- The SQLite-backed stores now close short-lived connections explicitly so
  Windows cleanup can remove run-owned temporary database files.

## Checksum chain

Manifest 59 is the operational checksum manifest for C9.1. It authenticates:

- historical manifest `audit_output/57-c9-checksums.txt`;
- this report;
- the corrected preflight;
- the Windows runbook;
- modified tests;
- modified CI workflow;
- modified changelog.
- SQLite-backed store modules touched for Windows cleanup hygiene.

Manifest 59 intentionally does not include itself.

## Local validation

Authoritative local run ID:
`cold-wallets-c91-872e9b10a8a443a5b4e24d07ab0cd4ec`.

The run used an isolated CPython 3.12 virtualenv under a literal temporary
directory, installed the runtime and PSBT dependencies needed to avoid skips,
validated `.github/workflows/ci.yml` with PyYAML 6.0.3, and executed:

```text
env PYTHONDONTWRITEBYTECODE=1 <python-isolado> -m unittest discover -s tests -v
```

Result: 89 tests, 89 passed, 0 skipped, 0 failures, 0 errors, 13.719 seconds.
The suite resource summary reported run ID
`1e8cf48721644eb0b96341b6dedd5841`, ephemeral port 52792, zero processes,
containers, networks, volumes, and residue. The isolated run-root was removed
after the run and confirmed with `CLEANUP_RESIDUE=0`. Repository bytecode
residue was separately checked after cleanup and was zero.

## GitHub Apps inventory

The inventory was read-only. No token or credential value was printed or
recorded.

| App | Installation ID | Owner | Scope | Effective access to cold-wallets | Key permissions | Write/deploy/config capability | C9.1 action |
|---|---:|---|---|---|---|---|---|
| railway-app | 94129474 | MHX-Digital | all repositories | yes, by scope | contents write, actions write, deployments write, administration write, pull requests write, workflows write, metadata read | yes | Pending manual organization-level restriction |
| atlassian | 110053661 | MHX-Digital | all repositories | yes, by scope | contents write, deployments write, administration read, actions read, pull requests write, metadata read | yes | Pending manual organization-level restriction |
| chatgpt-codex-connector | 110062815 | MHX-Digital | all repositories | yes, by scope | contents write, actions write, workflows write, pull requests write, metadata read | yes | Retained for this cycle; pending manual post-cycle restriction decision |
| claude | 130735282 | MHX-Digital | all repositories | yes, by scope | contents write, workflows write, repository hooks write, checks write, pull requests write, metadata read | yes | Pending manual organization-level restriction |
| claude-design-import | 146595031 | MHX-Digital | all repositories | yes, by scope | contents read, issues read, pull requests read, metadata read | no repository write/deploy permission observed | No restriction required for publication exclusivity |
| vercel | 146890589 | MHX-Digital | selected repositories | not proven by available API; repository list endpoint returned 403/404 | contents write, deployments write, administration write, workflows write, repository hooks write, metadata read | yes if cold-wallets is selected | Pending manual verification of selected repository list |

No repository deployments, environments, webhooks, Actions secrets, or Dependabot
secrets were present at inventory time. The existing
`v0.1.0-alpha.1` release is a pre-release targeting the baseline merge commit;
no stable release was created.

## Safety

No Tor, Helios, Bitcoin Core, mainnet, broadcast, deploy, wallet, seed, WIF, or
real key operation was executed. The product remains:

**EXPERIMENTAL - NO-GO FOR REAL FUNDS**.
