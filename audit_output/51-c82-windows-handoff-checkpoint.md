# C8.2 corrected Windows handoff checkpoint

Date: 2026-09-07 UTC

## Baseline

- Branch: `audit/cold-wallet-security-architecture-20260907`
- Parent HEAD: `5fdb89b362641931a67e41dc6a78d3c573d6edb1`
- Base/main: `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f`
- PR: `https://github.com/MHX-Digital/cold-wallets/pull/1`, draft
- Worktree before changes: clean
- Product: **NO-GO**

## Corrected preflight contract

`c8-preflight.ps1` now requires `ExpectedHead`, accepts an optional pinned
`ExpectedMain`, requires the exact audit branch, clean worktree and exactly one
worktree, and validates every entry in both the immutable C8.1 manifest
`audit_output/50-c81-checksums.txt` and this cycle's
`audit_output/52-c82-checksums.txt`.

The expected HEAD is external input. It is not embedded in the script, avoiding
a circular self-reference. Absolute paths, traversal, missing targets,
duplicates and reparse-point checksum targets fail closed. A checksum mismatch
throws before host inventory is accepted.

## Matrix harness hardening

- all three lock paths resolve inside repository `requirements/`;
- the wheelhouse root is explicit and may not be a reparse point;
- a mandatory JSON manifest stored under `requirements/` enumerates the exact
  wheelhouse filenames and SHA-256 hashes;
- extra, missing, duplicate, nested, malformed and reparse-point entries fail;
- `pip --isolated --no-index --require-hashes` prevents dynamic resolution;
- proxy/index environment variables are removed during execution and every
  modified process variable is restored to its prior value in `finally`;
- test count must equal the explicit expectation and any skipped result fails;
- cleanup is permitted only for a direct child of the system temp directory
  matching `^cold-wallets-c8-[0-9a-f]{32}$`.

No Windows wheelhouse manifest is fabricated here. It must be generated from
the officially sourced, hash-reviewed artifacts for the exact Windows/Python
target before the matrix harness can run.

## Tests

Run ID: `cold-wallets-c82-M3K81gB5`. CPython 3.12.3, Linux x86-64. Two temporary
virtualenvs and a 32-artifact wheelhouse were reconstructed from the committed
locks; the second install was offline and hash-locked.

- complete suite: **83/83 pass**;
- skips, failures, errors: **0/0/0**;
- unittest duration: 4.486 seconds;
- final static handoff selection: 18/18 pass;
- test resource summary: ephemeral port 35311, residue zero;
- virtualenv, wheelhouse, cache, processes, ports and bytecode residue: zero.

These Linux tests validate contracts and regression only. Native PowerShell and
Windows behavior remain unexecuted.

## Transfer rule

After the checkpoint commit is pushed, the caller must pass the exact remote/PR
head SHA to `-ExpectedHead`. The SHA cannot be predicted inside its own commit;
the authoritative value is the equality-confirmed Git remote ref and PR head.
No merge, main push, force push or product status change is authorized.
