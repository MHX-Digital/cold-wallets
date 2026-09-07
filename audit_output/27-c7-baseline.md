# C7 baseline and ownership gate

Date: 2026-09-07 UTC  
Gate C7-G0: **APPROVED WITH RESERVATIONS**

| Check | Expected | Observed | Result |
|---|---|---|---|
| Root | `/home/mhx/projects/cold-wallets` | same | approved |
| User/groups | non-admin | `mhx` uid/gid 1000; groups `mhx,nogroup` | approved |
| Branch | audit branch | `audit/cold-wallet-security-architecture-20260907` | approved |
| HEAD | `51dec97a...` | same | approved |
| main/base | `5374c1c0...` | same | approved |
| Worktree | clean | clean before this report | approved |
| C6 chain | 10 commits | intact through `51dec97` | approved |
| Worktrees | one | only this worktree | approved |
| Tracked files | stable | 150 | approved |
| Symlinks | inventory | none reported inside repository | approved |
| Temporary roots/bytecode | none | none | approved |
| Regression suite | prior 59/59 in locked venv | system Python: 48 run, four dependency-gated skips, pass in 1.00 s | reservation |
| Test residue | zero | runner: processes/containers/networks/volumes/residue all zero; port 43141 released | approved |
| Port inventory | read-only | sandbox denied netlink; no service changed | reservation |
| Ownership | consistent | mixed `mhx:mhx` and `nobody:nogroup` | reservation |

## Ownership inventory

| Path/group | Owner | Group | Mode | Tracked | Needs edit | Action |
|---|---|---|---:|---:|---:|---|
| new architecture (`coordinator`, `signer`, `broadcaster`, `transport`, tests) | mostly `mhx` | `mhx` | 664/775 | yes | yes | editable; continue |
| `README.md`, Dashboard | `mhx` | `mhx` | 664 | yes | yes | editable; continue |
| repository root and `.git` | `nobody` | `nogroup` | 775 | yes/internal | Git only | do not change ownership automatically |
| `cold_wallets/` directory | `nobody` | `nogroup` | 755 | yes | yes | cannot delete/add entries as current user |
| legacy key/sign/send files | `nobody` | `nogroup` | 644 or 664 | yes | yes | 664 files may be replaced; 644 files require owner action |
| `tools/`, `rpc/`, `hardware/` directories | `nobody` | `nogroup` | 755 | yes | yes | direct removal/addition blocked; individual 664 files may be replaced |
| 39 legacy Windows scripts | `nobody` | `nogroup` | mostly 644 | yes | yes | quarantine and deliver exact ownership command |
| generated/untracked wallet directories | not inspected | not inspected | not inspected | no | no | excluded by secret-safety rule |

The likely cause is a shared/container-created checkout: old trees and Git metadata
are owned by uid `nobody`, while audit-created files are owned by `mhx`. Ownership
does not indicate content integrity; Git/content checks remain separate.

No `chown`, recursive `chmod`, ACL change, administrative operation, external
network, Tor, Helios, Docker, Bitcoin Core, or wallet directory access occurred.

The first attempt to index this report was rejected because its Git object prefix
resolved to a non-writable object bucket owned by the shared checkout. No index,
object, permission, or content was overwritten.
