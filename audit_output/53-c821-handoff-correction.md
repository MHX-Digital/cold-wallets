# C8.2.1 Windows handoff correction

Date (UTC): 2026-09-08
Product classification: **NO-GO FOR REAL FUNDS**

## Gate C8.2.1-G0

The gate was completed before editing. The repository root was
`/home/mhx/projects/cold-wallets`, the active branch was
`audit/cold-wallet-security-architecture-20260907`, and the initial HEAD was
`e2d60c8839002890fb2a4b1168d7e761c16df729`. Local `main` remained
`5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f`. The worktree, including untracked
files, was clean; the configured upstream was the same audit branch on
`origin`; one worktree was registered; and both checkpoint manifests 50 and 52
validated in full. Git diff checking and `git fsck --no-dangling` passed.

PR #1 was open, draft, unmerged, based on `main`, and pointed to the initial
HEAD. No token-bearing remote URL was recorded.

## Corrections

- `ExpectedTestCount` is now mandatory in `c8-python-matrix.ps1`; it has no
  stale or inferred default.
- The matrix requires exactly one `Ran N tests` conclusion, requires the
  external expectation to match, and rejects skips, failures and errors.
- The Windows runbook supplies all matrix parameters explicitly for CPython
  3.10, 3.12 and 3.14, including `-ExpectedTestCount 83`.
- The runbook supplies `ExpectedHead` externally and the immutable expected
  `main`; the preflight contains no self-referential final HEAD.
- The preflight validates the new non-recursive manifest 54, which authenticates
  immutable historical manifests 50 and 52 plus the current handoff files. It
  retains its existing branch, HEAD, main, cleanliness, single-worktree and
  path-confinement checks. Historical manifests are not incorrectly applied to
  superseding file versions.
- Existing regression tests were strengthened without adding a new test case,
  so the declared suite count remains exactly 83.

## Reproducible Linux evidence

The authoritative final run was `cold-wallets-c821-IJ4DQ9Fi` on CPython 3.12.3,
Linux x86-64. A preparation virtualenv populated a 32-artifact wheelhouse from
the committed hash locks. Build tools were installed from their lock before
processing the PSBT sdist. A second virtualenv installed with `--no-index`,
`--require-hashes`, `--no-cache-dir`, and `--no-build-isolation` where required.

Command under test:

```text
PYTHONDONTWRITEBYTECODE=1 <isolated-venv>/bin/python -m unittest discover -s tests -v
```

Result: **83 tests run; 83 passed; 0 skipped; 0 failures; 0 errors** in 3.624
seconds (4 seconds at the harness wall-clock granularity).

An earlier setup attempt, `cold-wallets-c821-UsPPLWlm`, was deliberately
interrupted after detecting an incorrect build-isolation order and cleaned with
zero run-root residue. A subsequent successful diagnostic run,
`cold-wallets-c821-ctwClF4g`, exposed two run-created files in the global pip
wheel cache because `--isolated` ignored the cache environment variable. Those
two exact files and their now-empty leaf directory were identified, removed,
and verified absent before the authoritative run. The authoritative run used
explicit `--cache-dir` for download and `--no-cache-dir` for installation.
One diagnostic invocation against the unprovisioned host interpreter was
rejected as evidence because its optional crypto dependencies were absent and
the restricted sandbox denied its test listener. It created no bytecode or
run-root residue; the final result above comes exclusively from the complete
hash-locked environment after all source changes.

## Resource hygiene

| Resource | Before | Created | Removed/ended | Residue |
|---|---:|---:|---:|---:|
| Test processes/subprocesses | 0 owned by run | transient | all | 0 |
| Test threads | 0 | transient in suite | all | 0 |
| Listening ports owned by run | 0 | 1 ephemeral test listener | 1 | 0 |
| Host listeners (inventory) | 34 | 0 persistent | n/a; untouched | 34 |
| Virtualenvs | 0 | 2 | 2 | 0 |
| Wheelhouse | 0 | 1 (32 files) | 1 | 0 |
| Run-local pip cache | 0 | 1 | 1 | 0 |
| Global pip cache created by authoritative run | 0 | 0 | 0 | 0 |
| Temporary run roots | 0 | 1 authoritative | 1 | 0 |
| Repository `__pycache__` / bytecode | 0 | 0 | 0 | 0 |
| Containers, networks, volumes | 0 | 0 | 0 | 0 |
| Tor, Helios, Bitcoin Core, blockchain RPC | 0 | 0 | 0 | 0 |

The suite's own resource summary reported run ID
`731546ca2a084971bf102afc0eba4215`, ephemeral port `42735`, and zero process,
container, network, volume, or file residue.

## Limitations

PowerShell and the matrix harness have not been executed on native Windows.
Windows locks and wheelhouse manifests remain intentionally absent until they
are generated and independently reviewed on each exact Windows/CPython target.
Tor, Helios, Bitcoin Core regtest, and any blockchain broadcast were not run.
This checkpoint does not change the product classification.
