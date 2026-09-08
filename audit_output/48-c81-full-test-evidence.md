# C8.1 full Linux test evidence

## Reproducible environment

| Item | Observed |
|---|---|
| Run ID | `cold-wallets-c81-sx1dX3sb` |
| OS / architecture | Ubuntu Linux, x86-64, kernel 6.8.0-138 |
| Python | CPython 3.12.3 |
| Locks | `build-py312.lock`, `runtime-py312-linux.lock`, `psbt-py312-linux.lock` |
| Wheelhouse | 32 locked artifacts, temporary |
| Runtime install | second virtualenv; `--no-index --require-hashes` |
| eth-account | 0.14.0 |
| requests / PySocks | 2.34.2 / 1.7.1 |
| embit | 0.8.0 sdist, locally built with locked build tools |

## Commands and results

The preparation virtualenv used `pip download --require-hashes` for each lock.
The test virtualenv installed build and runtime locks from the wheelhouse with
`--no-index --require-hashes`, then installed embit with the additional
`--no-build-isolation` restriction. `PYTHONDONTWRITEBYTECODE=1` and a run-local
`PIP_CACHE_DIR` were active.

| Check | Result | Duration / invariant |
|---|---|---|
| `python -m unittest discover -s tests -v` | 79/79 pass; 0 skip/failure/error | 3.161 s unittest; 4 s measured wall |
| resource harness | pass | ephemeral port 46151; process/container/network/volume/residue 0 |
| `git diff --check` | pass | no whitespace error |
| `git fsck --no-dangling` | pass | object integrity |
| post-run temp scan | pass | no `cold-wallets-c81-*` root |
| post-run bytecode scan | pass | no `__pycache__` |

Coverage includes all 74 C7.2 tests plus the five C8 architecture/Windows-harness
tests. The Windows tests in this Linux suite validate script contracts only and
do not claim Windows runtime compatibility.

## Hygiene

| Resource | Preexisting | Created | Removed | Residue |
|---|---:|---:|---:|---:|
| preparation/test virtualenvs | 0 | 2 | 2 | 0 |
| wheelhouse artifacts | 0 | 32 | 32 | 0 |
| private pip cache | 0 | 1 | 1 | 0 |
| test processes/threads | 0 owned | test-owned only | all | 0 |
| test ports | relevant preflight none recorded | 1 ephemeral | 1 | 0 |
| temporary files/databases/fixtures | 0 | test-owned | all | 0 |
| containers/networks/volumes | 0 | 0 | 0 | 0 |
| Tor/Helios/Bitcoin Core/RPC/broadcast | 0 | 0 | 0 | 0 |
| wallets/backups/logs/`__pycache__` | 0 | synthetic/test-only | all | 0 |

The package-index connection was limited to downloading artifacts named and
hashed by committed locks. The actual installation and test execution were
offline. No global cache or Python environment was modified.
