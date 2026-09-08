# C7 ownership inventory and minimum operator action

The checkout is shared/mixed: legacy trees are `nobody:nogroup`, while new audit
files are `mhx:mhx`. The current user belongs to `nogroup`, but legacy directories
are mode 0755, so group membership does not permit deleting their entries.

| Path | Owner | Group | Mode | Tracked | Needs edit | Action |
|---|---|---|---:|---:|---:|---|
| `/home/mhx/projects/cold-wallets/cold_wallets` | nobody | nogroup | 755 | yes | yes | owner must transfer this directory only |
| `.../cold_wallets/hot_disposable` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `.../cold_wallets/tools` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `/home/mhx/projects/cold-wallets/tools` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `/home/mhx/projects/cold-wallets/rpc` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `.../rpc/hardening` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `.../rpc/scripts` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `/home/mhx/projects/cold-wallets/hardware` | nobody | nogroup | 755 | yes | yes | transfer directory only |
| `.git` and some object buckets | mixed | mixed | 775 | internal | no current change | do not change; identify a bucket only if a future write collides |

Probable cause: checkout populated by a container/shared user and later edited by
the local user. This is an inference from uid/group distribution, not proof.

Minimum command for the repository owner, not executed by the audit:

```text
sudo chown mhx:mhx \
  /home/mhx/projects/cold-wallets/cold_wallets \
  /home/mhx/projects/cold-wallets/cold_wallets/hot_disposable \
  /home/mhx/projects/cold-wallets/cold_wallets/tools \
  /home/mhx/projects/cold-wallets/tools \
  /home/mhx/projects/cold-wallets/rpc \
  /home/mhx/projects/cold-wallets/rpc/hardening \
  /home/mhx/projects/cold-wallets/rpc/scripts \
  /home/mhx/projects/cold-wallets/hardware
```

This intentionally does not use `-R`, a glob, home shorthand, or repository-root
ownership change. Afterward, compare Git content before removing only reviewed,
tracked legacy files.
