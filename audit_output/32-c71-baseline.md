# C7.1 ownership and integrity baseline

Date: 2026-09-07 UTC  
Gate C7.1-G0: **APPROVED WITH RESERVATIONS**

| Check | Expected | Observed | Result |
|---|---|---|---|
| Root | `/home/mhx/projects/cold-wallets` | same | approved |
| User/groups | `mhx` with required group access | uid/gid 1000; groups `mhx,nogroup` | approved |
| Branch | audit branch | `audit/cold-wallet-security-architecture-20260907` | approved |
| HEAD | `2ef5be3b...` | same | approved |
| main/base | `5374c1c0...` | same | approved |
| Worktree | clean | clean | approved |
| Worktrees | one | only this checkout | approved |
| Corrected directories | owned/writable by `mhx` | all eight are `mhx:mhx`, mode 0755, writable | approved |
| Root / `.git` | consistent ownership | `nobody:nogroup`, mode 0775; current user is in `nogroup` | reservation |
| Prior report checksums | intact | all entries in `31-c7-checksums.txt` pass | approved |
| Git object integrity | intact | `git fsck --no-dangling` passes | approved |
| Git locks/temporary objects | absent | none found | approved |
| Symlinks | absent outside excluded wallet paths | none found | approved |
| ACL inventory | available | `getfacl` is unavailable; effective mode/write checks were used | reservation |
| Sticky bit | absent | repository, corrected directories, and `.git` show no sticky bit | approved |

The ownership operation changed directory metadata but did not change tracked
content: Git is clean, report checksums pass, and object integrity passes. Wallet,
generated, address-pool, and backup directories were not opened.

## Read-only `.git` ownership inventory

Non-`mhx` object buckets are `.git/objects/53`, `5d`, `73`, `7d`, `b4`, and
`fe`; each is `nobody:nogroup` mode 0775 and writable through the current user's
`nogroup` membership. Existing objects inside them are read-only data and do not
need mutation. `.git/objects`, `refs`, and `logs` are also group-writable 0775.
The index is `nobody:nogroup` 0644 but can be atomically replaced through the
group-writable `.git` directory. No residual lockfile or temporary object exists.

No `.git` ownership change is proposed before a real commit proves whether these
effective permissions are sufficient.
