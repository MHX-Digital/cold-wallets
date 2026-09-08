# C6 script reachability matrix

Forty `.bat`/`.ps1` files were inventoried. No script was executed.

| Group | Classification | Reachability / action |
|---|---|---|
| `start.bat` | safe and necessary | rewritten: unprivileged, foreground, Dashboard only; no curl/install/Tor/signing |
| `requirements/generate-windows-lock.ps1` | safe manual build tool | validates actual Windows/Python target; refuses overwrite; output remains unverified |
| `cold_wallets/*.bat`, `cold_wallets/hot_disposable/*.bat` | legacy, removal required | not called by primary launcher; still directly invocable and tree is read-only to auditor |
| `cold_wallets/install.bat` | prohibited installer | contains unpinned runtime pip install; not called by primary launcher; removal blocked by permissions |
| `tools/start_*`, `tools/status.bat` | legacy network/process control | direct curl and process orchestration; not called by primary launcher; removal blocked by permissions |
| `tools/enable_*`, `tools/disable_*`, `tools/stop_*` | administrative | may change services/network; requires explicit future authorization; not executed |
| `rpc/*.bat`, `rpc/scripts/*.ps1` | legacy RPC/Docker/admin | direct localhost/Tor curl, PowerShell RPC, Docker and/or elevation; not part of new reachable path |
| `rpc/hardening/*` | administrative security tooling | firewall/UPnP changes require separate Windows review and explicit authorization |
| `hardware/*.ps1` | administrative/destructive/download tooling | disk changes or unverified downloads; excluded from normal flow and never executed |

Three writable Python entrypoints (`fetch_tx_data.py`, `broadcast_tor.py`, and
`eth_rpc_proxy.py`) now raise a migration error before their legacy imports. The
primary launcher cannot invoke any script above. This is containment, not physical
removal: manual direct invocation of remaining legacy scripts is an open P0.
