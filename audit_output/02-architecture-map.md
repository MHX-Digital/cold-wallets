# Mapa de arquitetura e confiança

## Arquitetura executável encontrada

```text
Browser
  | HTTP sem autenticação/CSRF
  v
Dashboard :8888 (frequentemente elevado por start.bat)
  |-- geração/signing Python ----> JSON plaintext + DOM/clipboard
  |-- requests+socks5h ----------> Tor :9050/:9150 -> APIs BTC/RPC ETH
  |-- subprocess ----------------> tor_manager -> download/extract/tor.exe
  `-- subprocess ----------------> eth_rpc_proxy :8545 -> Tor -> RPC público

CLI signer
  |-- network_control/netsh (isolamento transitório e incompleto)
  |-- entrada manual/tx_data não autenticado
  `-- bit / eth-account -> raw transaction JSON

Stack opcional separado
  Browser/dApp -> Helios container :8545 -> execution + consensus RPC
                   ^ tag de imagem/config/checkpoint não atestados
```

## Componentes e responsabilidades reais

| Componente | Responsabilidade real | Acoplamento/risco |
|---|---|---|
| `dashboard/server.py` | UI, status, geração, storage, consulta, assinatura, broadcast e processos | concentração crítica; segredo cruza fronteira online |
| `dashboard/index.html` | forms, confirmação, render e clipboard | private keys no DOM; `innerHTML` inseguro |
| `generate_wallets.py` | chaves BTC/ETH e JSON | plaintext e exibição no console |
| `sign_btc.py` / `sign_eth.py` | coleta + política + assinatura + storage | dados não autenticados; chain fixo; fee aproximada |
| `enviar_btc.py` / `enviar_eth.py` | chave + rede + assinatura + broadcast | hot wallet monolítica |
| `address_validation.py` | validação superficial | fail-open para checksums |
| `network_control.py` | netsh/ping e restauração | não cobre interfaces/IPv6/crash |
| `fetch_tx_data.py` | dados remotos para offline | arquivo não autenticado vira verdade assinável |
| `broadcast_tor.py` | load e broadcast multi-endpoint | não decodifica/compara manifesto; sem idempotência |
| `hot_disposable/*` | geração e estados por diretório | chave plaintext, estado parcial, concorrência |
| `tools/eth_rpc_proxy.py` | relay RPC público por Tor | não é light client/trustless |
| `tools/tor_manager.py` | download/extract/start/stop | supply-chain e temp race |
| `rpc/helios/*` | stack Helios opcional | não integrada ao Dashboard; porta ambígua |
| `rpc/hardening/*` | firewall/UPnP | mutação global sem snapshot/rollback |

## Fluxos de RPC reais

| Operação | Origem dos dados | Tor | Helios | Verificado | Fallback |
|---|---|---:|---:|---:|---|
| Dashboard BTC balance/UTXO | Blockstream ou mempool.space | Sim, sessão Python | Não | TLS apenas | próximo endpoint |
| Dashboard BTC fee | mempool.space | Sim | Não | Não | constantes silenciosas |
| Dashboard BTC broadcast | Blockstream/mempool | Sim | Não | resposta do endpoint | próximo endpoint |
| Dashboard ETH balance/nonce/fee | Cloudflare/PublicNode/Llama | Sim | Não | Não | primeiro RPC com resultado |
| Dashboard ETH broadcast | mesmos RPCs | Sim | Não | Não | próximo RPC |
| `eth_rpc_proxy.py` | quatro RPCs públicos | Sim | Não | Não | round-robin até HTTP 200 |
| Helios Docker opcional | execution + consensus configurados | Pretendido, não comprovado | Sim | conforme Helios/checkpoint | lista em config; sem teste local |
| Dashboard status :8545 | qualquer serviço na porta | N/A | Indeterminado | Não | nenhum |

## Estratégia incremental

- Etapa A: desabilitar no Dashboard todos os endpoints que recebem/retornam chave e rotular RPC pela implementação comprovada.
- Etapa B: API local endurecida e coordinator somente watch-only.
- Etapa C: envelopes versionados, PSBT e Ethereum type 2 com hash de intenção.
- Etapa D: signer em host separado/air-gapped, com import/export removível e revisão humana.
- Etapa E: broadcaster decodifica, compara e registra idempotência sem segredo.
