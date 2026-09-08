# C8 test evidence

## Result boundary

No native Windows test was executed. No Windows version, Python, launcher, ACL,
Tor, Bitcoin Core regtest, Helios, Docker Desktop, backup-media, or interruption
result is claimed.

## Local independent checks

| Check | Result | Duration / limitation |
|---|---|---|
| C8 environment and Git preflight | Git matched expected branch/HEAD/main and was clean; host is Ubuntu Linux | native Windows gate blocked |
| C7.2 checksum verification | all four entries matched | read-only |
| `tests.test_architecture` + `tests.test_windows_validation` | 14/14 pass | 0.182 s; pure/static checks only |
| `git diff --check` | pass | formatting only |
| `__pycache__` scan | zero | bytecode disabled |

An initial development invocation also selected the Dashboard HTTP tests. The
sandbox denied socket creation at fixture setup (`PermissionError`) before a
listener was created, so this is neither a product failure nor test evidence.
The first static run correctly rejected the newly added offline install harness
under the older blanket policy; the policy was narrowed to one explicit,
native-only `--no-index --require-hashes` harness and the final 14 tests passed.

The complete 79-test source suite was not run and must not be reported as a
Windows pass. The prior 74/74 result remains evidence only for the Linux 3.12
hash-locked environment.

## Hygiene

| Resource | Preexisting | Created | Ended/removed | Residue |
|---|---:|---:|---:|---:|
| processes / threads | relevant process scan found none | 0 | 0 | 0 |
| test listeners / ports | Linux netlink inventory blocked by sandbox | 0 | 0 | 0 |
| temporary files/directories | 0 C8 run roots found | 0 | 0 | 0 |
| virtualenvs / wheelhouses / caches | 0 created | 0 | 0 | 0 |
| Tor / Bitcoin Core / regtest wallets/datadirs | 0 | 0 | 0 | 0 |
| Helios / containers / networks / volumes | not queried because execution is prohibited here | 0 | 0 | 0 |
| operational logs / synthetic backups | 0 | 0 | 0 | 0 |
| `__pycache__` | 0 | 0 | 0 | 0 |

Repository code, tests, validation scripts and audit reports are deliberate
versioned deliverables, not temporary residue.
