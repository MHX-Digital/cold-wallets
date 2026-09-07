# C7.1 final legacy inventory and removal decision

Historical audit reports remain as evidence. The executable/configuration paths
below have no consumers in the new Dashboard/coordinator/signer/broadcaster flow.

| Path | Former function | Risk | Consumers | Replacement | Action |
|---|---|---|---|---|---|
| `cold_wallets/generate_wallets.py`, `gerar.bat` | online key generation | private-key exposure and fragile network isolation | legacy launcher only | offline signer boundary; no Dashboard key generation | remove |
| `cold_wallets/sign_btc.py`, `assinar_btc.bat` | legacy BTC signing | `bit`, trusted remote prevouts, online-capable process | legacy launcher only | PSBT v0 P2WPKH signer, fail-closed backend | remove |
| `cold_wallets/sign_eth.py`, `assinar_eth.bat` | legacy ETH signing | combined privilege/network controls | legacy launcher only | `signer/ethereum.py` | remove |
| `cold_wallets/enviar_btc.py`, `enviar_btc.bat` | combined BTC prepare/sign/send | online signing and parallel broadcast | none after C6 block | coordinator + PSBT + broadcaster | remove |
| `cold_wallets/enviar_eth.py`, `enviar_eth.bat` | combined ETH prepare/sign/send | online signing and parallel broadcast | none after C6 block | envelope + offline signer + broadcaster | remove |
| `cold_wallets/network_control.py` | adapter/UAC isolation | false air-gap guarantee and administrative effects | legacy signers/generator | physical offline host and documented boundary | remove |
| `cold_wallets/install.bat`, `requirements.txt` | runtime install | unpinned dependency installation including `bit` | legacy users only | hash-locked files under `requirements/` | remove |
| `cold_wallets/hot_disposable/*` | file-based disposable lifecycle/sweep | secret coupling, races, legacy signing | legacy batch wrappers | `coordinator/disposable_store.py` and service | remove all six tracked files |
| `cold_wallets/tools/fetch_tx_data.py`, `broadcast_tor.py` | direct fetch/broadcast | parallel HTTP and broadcast paths | none after C6 block | coordinator adapters and persistent broadcaster | remove |
| `tools/check_tor.py`, `tor_manager.py`, `eth_rpc_proxy.py` | Tor download/process and public RPC proxy | download/execute, direct network, false trust label | legacy scripts only | central fail-closed transport and explicit RPC identity | remove |
| `tools/*.bat` | Tor/Helios/proxy/service control | direct network, process killing, adapter/service changes | manually invocable only | no automatic replacement; controlled future runbook | remove all nine scripts |
| `rpc/**` | Docker/Tor/Helios/reverse-proxy/admin stack | parallel network path, auto-setup, trust ambiguity | manually invocable only | future separately validated deployment package | remove every tracked file |
| `hardware/*.ps1` | disk inspection/install/resize | download and destructive/admin operations | manually invocable only | out of current product scope | remove all four scripts |
| `security/legacy_quarantine.json` | temporary C7 denylist | stale paths after deletion | architecture tests | filesystem/AST absence tests | remove after paths are gone |
| `start.bat` | watch-only Dashboard launcher | normal local endpoint risk | supported entrypoint | itself, already foreground/unprivileged | maintain |
| `requirements/generate-windows-lock.ps1` | manual lock generation | build-only supply-chain operation | maintainer only | itself with target verification | maintain non-runtime |

Git history preserves historical implementation. No dangerous executable is kept
solely for archival value.
