# C6 baseline and Git stabilization

Date: 2026-09-07 UTC  
Gate: **C6-G0 APPROVED WITH RESERVATIONS**

| Check | Expected | Observed | Result |
|---|---|---|---|
| Repository root | `/home/mhx/projects/cold-wallets` | `/home/mhx/projects/cold-wallets` | Approved |
| Branch | `audit/cold-wallet-security-architecture-20260907` | same | Approved |
| HEAD | `e285c21a853f1f0644d14a5fc7b0211709978884` | same | Approved |
| `main` / original base | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | same | Approved |
| Worktree | clean | clean before this report | Approved |
| Upstream | none required | no upstream configured | Approved |
| C5 commit chain | 10 commits through `e285c21` | chain intact (`f62b6aa` through `e285c21`) | Approved |
| Dependency locks | present and hashed | runtime, PSBT and build locks present; checksums recorded below | Approved |
| Regression suite | 47 discovered tests | 44 executed, 2 dependency-gated skips, exit 0 in 1.27 s | Reservation |
| `git diff --check` | pass | pass | Approved |
| C5/C6 temporary roots | none | none found under `/tmp` | Approved |
| Python bytecode residue | none | none found | Approved |
| Listening-port inventory | read-only | unavailable: sandbox denied netlink; no process was stopped | Reservation |
| Concurrent interference | none | no divergent HEAD, `main`, or unknown worktree files | Approved |

## Lock integrity

- `runtime-py312-linux.lock`: `c0ef4b4c2a22c4c95cafad2638dff0778d244d750d87b5311fca2ddaa6ec37d3`
- `psbt-py312-linux.lock`: `edf784b4b50ec95a80e014ba7462b7d656d6b7fa594f4b8521f4d6eb6235391f`
- `build-py312.lock`: `83f111e093bad00e18d8ee645a55359e4a3b9ea26a1b2d8b91776712a0db30fb`

The baseline reports retained their prior checksums, including `00-baseline.md` at
`f4170979c73aa04ab2238e5eb3b621ad7fba7c4b789891abad995f7e5cec7dea`.

## Test hygiene

The runner reported `processes=0`, `containers=0`, `networks=0`, `volumes=0`,
and `residue=0`. It selected an ephemeral port (`41681`) and released it. No
blockchain network, Tor process, container, wallet directory, or external service
was used. The two skipped cryptographic integration tests require the reviewed,
hash-locked virtual environment and must be executed again in the C6 isolated run.

The repository required an ephemeral Git `safe.directory` command option because
its filesystem owner differs from the runner. No global or repository Git
configuration was changed.
