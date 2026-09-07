# C8.1 Linux checkpoint

Date: 2026-09-07 UTC  
Gate C8.1-G0: **APPROVED WITH RESERVATIONS**

## Git baseline

| Check | Observed | Result |
|---|---|---|
| Root | `/home/mhx/projects/cold-wallets` | pass |
| Branch | `audit/cold-wallet-security-architecture-20260907` | pass |
| Audited HEAD before checkpoint | `57e35f33c8acc78801a33b7ab5bcb0609ce125c4` | pass |
| main/base | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | pass |
| Worktree | clean | pass |
| Upstream | none | expected before first publication |
| Remote | `origin`, sanitized identity `MHX-Digital/cold-wallets` | pass |
| Remote main | equals base | pass |
| Remote audit branch | absent | safe for first non-force push |
| Worktrees / tags | one / zero | pass |
| Commits since base | 64 | pass |
| Git objects | 460 loose; 104 packed; zero garbage | pass |
| C8 checksums | 4/4 match | pass |
| `git fsck --no-dangling` | pass | pass |
| Interference | none observed | pass |

## Integral reproducible suite

The run `cold-wallets-c81-sx1dX3sb` used CPython 3.12.3 on Linux x86-64.
A preparation virtualenv downloaded exactly the artifacts selected by the three
committed locks into a private wheelhouse. A second virtualenv installed build,
runtime and PSBT dependencies offline with `--no-index --require-hashes`; embit
used `--no-build-isolation`. All 79 tests passed, with zero skip, failure or
error. Both virtualenvs, the 32-artifact wheelhouse and private pip cache were
removed. Blockchain/RPC/Tor/Helios/broadcast access did not occur.

## Complete diff review

Range: base through audited HEAD. Total: 176 paths, 4,378 additions and 10,517
deletions. Statuses: 103 added, 6 modified, 67 removed. There are zero binary
entries, zero blobs over 2 MB, and the largest tracked file is 22,186 bytes.

| Area | Paths | Purpose | Change risk | Evidence |
|---|---:|---|---|---|
| audit reports | 50 | threat model, findings, gates and reproducible evidence | low; documentary | checksums and Git history |
| legacy `cold_wallets`, tools, hardware and RPC | 71 | physically remove combined signing/network/admin infrastructure | medium/high compatibility; security-positive | filesystem/AST negative tests |
| Dashboard | 2 | watch-only UI/API boundary | medium | API, Host/Origin/token/routes and UI tests |
| coordinator | 8 | proposals, PSBT review, lifecycle and RPC identity | medium | contract/integration tests |
| signer/backend | 4 | offline ETH and fail-closed BTC signing | high | real ETH recovery; BTC backend gate |
| broadcaster | 4 | persistent idempotency and recovery | high | concurrency/state/restart tests |
| transport/storage | 8 | Tor-only adapter, atomic artifacts and authenticated fixtures | high | negative, tamper and recovery tests |
| requirements | 7 | exact Linux locks and Windows lock workflow | medium supply chain | hash-locked clean-room install |
| tests | 16 | 79 security/functional invariants | low | integral suite |
| Windows launcher/harness | 4 | explicit venv/port, native preflight and offline matrix | medium; Windows unvalidated | static tests only |
| root documentation/config | 3 | truthful capability and ignore policy | low | review/tests |

No unrelated functional change was identified. Deletions are the reviewed
legacy implementations and unsupported infrastructure retained by Git history.

## Secret and artifact review

A redacted scanner inspected 64 commit trees and 284 unique text blobs, including
intermediate branch history. It found zero private key, WIF, mnemonic, seed,
credential, API token, authenticated connection string, private certificate or
fixed raw-transaction match. It found 29 personal-path patterns: 28 in audit
report revisions and one in a removed historical RPC configuration. They are
repository-location metadata explicitly supplied for this audit, not secrets;
no credential component was present.

Tracked-name and size inspection found no `.env`, wallet, SQLite execution DB,
wheel, virtualenv, log, PID, dump, Tor/Bitcoin datadir, synthetic backup or
secret-key artifact. No untracked file exists. Reports and declared lockfiles are
intentional deliverables.

## Ownership debt

The root, `.git`, `.git/objects` and `.git/refs` remain `nobody:nogroup` mode
0775. Git operations and integrity checks work through current group membership,
so publication is not blocked, but ownership remains operational debt.

The exact empty paths `rpc/l2-templates/arbitrum` and
`rpc/l2-templates/optimism` are owned by `mhx`, but their parent
`rpc/l2-templates` is `nobody:nogroup` mode 0755. A specific `rmdir` attempt was
denied and changed nothing. Future correction requires only:

```text
sudo chown mhx:mhx /home/mhx/projects/cold-wallets/rpc/l2-templates
rmdir /home/mhx/projects/cold-wallets/rpc/l2-templates/arbitrum
rmdir /home/mhx/projects/cold-wallets/rpc/l2-templates/optimism
```

These commands were not executed. No recursive ownership or deletion operation
is authorized.
