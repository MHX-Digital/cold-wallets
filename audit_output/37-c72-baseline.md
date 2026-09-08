# C7.2 ownership and integrity baseline

Date: 2026-09-07 UTC  
Gate C7.2-G0: **APPROVED WITH RESERVATIONS**

| Check | Expected | Observed | Result |
|---|---|---|---|
| User/groups | `mhx`, required group access | uid/gid 1000; groups `mhx,nogroup` | approved |
| Branch | audit branch | `audit/cold-wallet-security-architecture-20260907` | approved |
| HEAD | `88fadf9...` | same | approved |
| main/base | `5374c1c0...` | same | approved |
| Worktree | clean | clean | approved |
| C7.1 chain | intact | eight expected commits present | approved |
| Worktrees | one | only this checkout | approved |
| Seven RPC directories | corrected and writable | all `mhx:mhx` 0755; effective write succeeds | approved |
| Internal file owners | may remain old owner | files remain `nobody:nogroup` 0644; parent write permits reviewed deletion | approved for deletion |
| Prior checksums | intact | all C7.1 report checksums pass | approved |
| Symlinks / Git locks | absent | none found | approved |
| ACL tool | optional inventory | `getfacl` unavailable; modes/effective access recorded | reservation |
| Root / `.git` | consistent | `nobody:nogroup` 0775 and operational through group membership | operational debt |

No tracked content divergence or concurrent interference was observed. No wallet,
generated, address-pool, or backup directory was opened.
