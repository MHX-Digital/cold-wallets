# C7.2 review of the thirteen residual RPC files

| Path | Type | Function | Risk | Future need | Substitute | Action |
|---|---|---|---|---:|---|---|
| `rpc/docs/quickstart.md` | documentation | launch old stack | unverified trust/admin instructions | no | current root RPC README | DOC_MIGRATE |
| `rpc/docs/runbook.md` | documentation | operate Docker/Tor/Helios | commands for unsupported deployment | no | future controlled validation runbook | REMOVE |
| `rpc/docs/threat-model.md` | documentation | old Helios claims | declares trustless guarantees without attestation | no | audit threat model + current RPC README | DOC_MIGRATE |
| `rpc/helios/config.example.toml` | configuration | active Helios example | upstream/checkpoint assumptions | yes | disabled attestation descriptor | REPLACE |
| `rpc/helios/docker-compose.yml` | executable configuration | launch Helios | tag/digest/runtime not approved | yes | non-executable disabled descriptor | REPLACE |
| `rpc/l2-templates/arbitrum/docker-compose.yml` | executable configuration | Arbitrum node | unsupported L2 and external endpoints | no | none | REMOVE |
| `rpc/l2-templates/optimism/docker-compose.yml` | executable configuration | Optimism node | unsupported L2 and external endpoints | no | none | REMOVE |
| `rpc/reverse-proxy/docker-compose.yml` | executable configuration | launch proxy | extra exposed routing surface | no | Dashboard binds directly to loopback | REMOVE |
| `rpc/reverse-proxy/nginx.conf` | configuration | proxy RPC/CORS | bypass/route ambiguity | no | none | REMOVE |
| `rpc/tor/docker-compose.yml` | executable configuration | launch Tor | unverified image and implicit service lifecycle | yes | disabled transport-policy descriptor | REPLACE |
| `rpc/tor/torrc` | active configuration | SOCKS/hidden service | unverified runtime and unnecessary hidden service | yes | future generated loopback-only torrc after binary verification | REPLACE |
| `rpc/wireguard/client.conf.example` | configuration | remote access | unsupported remote surface | no | none | REMOVE |
| `rpc/wireguard/wg0.conf.example` | configuration | VPN server | external exposure and unused keys/routes | no | none | REMOVE |

No old executable/configuration file is retained. Helios and Tor future intent is
preserved only as strict, disabled JSON evidence contracts; they cannot start a
service.
