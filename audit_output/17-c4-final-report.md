# Relatório C4

Resultado do produto: **NO-GO**. Gate C4-G1: **BLOQUEADO** porque assinatura Ethereum real não pôde ser validada sem `eth-account`, PSBT não está disponível e clientes legados ainda contornam o adapter Tor.

## Matriz de rede

| Escopo | Cliente | Adapter central | Estado |
|---|---|---:|---|
| Novo código C4 | `transport.tor_http` | sim | fail-closed testado |
| Dashboard | nenhum | n/a | fisicamente sem rede externa |
| Signer | nenhum | n/a | proibição AST testada |
| `enviar_btc.py` / `enviar_eth.py` | `requests.Session` | não | legado, OPEN |
| `fetch_tx_data.py` / `broadcast_tor.py` | `requests.Session` | não | legado, OPEN |
| `eth_rpc_proxy.py` / `check_tor.py` | `requests.Session` | não | migração pendente |
| scripts Batch/PowerShell | curl/Invoke-WebRequest | não | fora do adapter, pendente |

## PSBT

Pesquisa local encontrou `bit=False`, `bitcoinlib=False`, `embit=False`, `bitcointx=False`. O requirements declara `bit` sem versão, mas ele não está instalado e o projeto não demonstra suporte PSBT. Nenhuma implementação manual foi criada. A seleção de biblioteca, versão/licença/manutenção e hashes exige avaliação externa autorizada; esta frente permanece isoladamente bloqueada.

## Segurança operacional

Nenhuma chave existente, wallet real, mainnet, Tor real, Docker ou serviço remoto foi acessado. Todos os testes utilizaram mocks/temporários locais e deixaram resíduo zero.
