# C8 native Windows baseline

Date: 2026-09-07 UTC  
Gate C8-G0: **BLOCKED**

The current execution host is native Ubuntu Linux on x86-64. It is neither
native Windows nor WSL. Under the C8 gate rules, Linux is not an acceptable
substitute and no Windows, Tor, Helios, Docker, Bitcoin Core, RPC, launcher, or
network claim can be validated from this host.

## Repository reference

| Check | Expected | Observed | Result |
|---|---|---|---|
| Repository root | `/home/mhx/projects/cold-wallets` | same | pass |
| Branch | `audit/cold-wallet-security-architecture-20260907` | same | pass |
| HEAD | `2bca54ef982933c8485fa468ef386580f3304753` | same | pass |
| main/base | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | same | pass |
| Worktree | clean | clean | pass |
| Worktrees | one | one | pass |
| C7.2 checksums | all match | all match | pass |
| `git diff --check` | clean | clean | pass |
| Concurrent interference | none | none observed | pass |

## Host condition

| Required C8 evidence | Observed | Result |
|---|---|---|
| Native Windows 10/11 version and build | Linux kernel 6.8; Ubuntu; hostname masked as `mhx-***` | **blocked** |
| Windows architecture/filesystem/ACL | not available | NOT TESTED |
| Windows privileges and Defender | not available | NOT TESTED |
| Windows PowerShell and Python matrix | not available | NOT TESTED |
| Docker Desktop, Bitcoin Core and Tor inventory | not inspected on a Windows host | NOT TESTED |
| Windows interfaces, listeners and processes | not available | NOT TESTED |
| Windows disk space and filesystem | not available | NOT TESTED |

The current Unix user is unprivileged (`uid=1000`) and no administrative
operation was attempted. No wallet, secret-bearing directory, external service,
container, blockchain network, or real transaction was accessed.

## Gate decision

**C8-G0 BLOCKED.** Operational testing must resume on the intended native
Windows 10/11 host. Safe Windows-only preflight and clean-room test harnesses are
prepared under `validation/windows/`; both reject non-Windows execution and do
not constitute evidence until their output is reviewed on that host.
