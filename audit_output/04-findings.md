# Achados consolidados

## Contagem

| Severidade | Quantidade |
|---|---:|
| CRITICAL | 7 |
| HIGH | 9 |
| MEDIUM | 4 |
| LOW | 1 |
| INFORMATIONAL | 1 |

## Tabela completa

| ID | Severidade | Componente | Evidência | Cenário de exploração | Impacto | Correção | Teste |
|---|---|---|---|---|---|---|---|
| CW-001 | CRITICAL | Dashboard/chaves | `server.py:203-226,321-548`; HTML `316-357` | origem local/web aciona fluxo com chave online | roubo/perda de fundos | Dashboard watch-only; remover endpoints secretos | rotas ausentes; payload de chave rejeitado |
| CW-002 | CRITICAL | API local | handler `673-762` | CSRF/rebinding/cliente local chama operação | geração, processos ou broadcast indevido | token, Host/Origin, content-type, limite, métodos | matriz HTTP negativa |
| CW-003 | CRITICAL | Bitcoin validation | `address_validation.py:56-85` | endereço com caracteres válidos e checksum errado passa | fundos irrecuperáveis | decoder de biblioteca madura ou implementação mínima de encoding, vetores | Base58Check/Bech32(m) oficiais |
| CW-004 | CRITICAL | BTC prevouts | `enviar_btc.py`; `sign_btc.py` | API falsifica valor/script/outpoint | assinatura errada/rejeitada/fee falsa | PSBT + prevout/ownership/política | prevout adulterado rejeitado |
| CW-005 | CRITICAL | Ethereum truth | `enviar_eth.py`; API Dashboard | RPC mente sobre saldo/nonce/fee; nonce usa latest | conflito, fee/perda, rede errada | chain check, pending, bounds, quorum/Helios | respostas divergentes/falsas |
| CW-006 | CRITICAL | Supply chain | `tor_manager.py`; installers | download comprometido é executado, possivelmente elevado | controle total do host/chaves | download explícito, hash/assinatura, diretório seguro | mismatch impede extração/execução |
| CW-007 | CRITICAL | Garantias/QA | README “trustless” e PASS sem testes | usuário confia em proxy público/fluxo inseguro | falsa segurança com fundos reais | rotulagem fail-closed e evidência reproduzível | UI/status distingue backend |
| CW-008 | HIGH | Frontend XSS/clipboard | `innerHTML`, Show/Copy | resposta maliciosa injeta DOM e lê chave | exfiltração | DOM seguro; nunca chave no DOM | payload XSS renderizado como texto |
| CW-009 | HIGH | BTC fee/send-all | tabelas vsize, sem dust/bounds | fee real difere; rate extrema | rejeição ou fee excessiva | medir tx/PSBT final e política | mixed inputs/dust/fee bounds |
| CW-010 | HIGH | ETH fallback | `feeHistory` → legacy | fallback muda tipo sem aprovação | intenção divergente | erro explícito/nova revisão | ausência feeHistory falha fechada |
| CW-011 | HIGH | Storage | JSON direto/plaintext | malware/local/crash acessa/corrompe chave | roubo/perda | signer externo; compatibilidade com ACL/write atômico | permissões e crash simulation |
| CW-012 | HIGH | Network control | `network_control.py` | virtual/IPv6 permanece; crash não restaura | assinatura online/falha host | não alegar air gap; journal/rollback ou separação física | mocks de estado/falha |
| CW-013 | HIGH | Disposable state | diretórios + rename/rewrite | concorrência/crash duplica/abandona | perda/privacidade | máquina de estados + journal/lock | transições e recovery |
| CW-014 | HIGH | Idempotência | `api_send_*`, botão cliente | retry/duplo clique retransmite | broadcast duplicado/confusão | idempotency key e ledger | concorrência mesma chave |
| CW-015 | HIGH | Erros/logs | `str(e)`, responses/logs | exceção inclui entrada/caminho | segredo/metadado vazado | erros de domínio + redactor | canários nunca aparecem |
| CW-016 | HIGH | Helios | tag, checkpoint implícito, porta ambígua | proxy ocupa :8545 e é tratado como Helios | dados não verificados | attestation de backend/config/checkpoint/digest | status não aceita mera porta |
| CW-017 | MEDIUM | Tor clients | Python `socks5h`, Batch `--socks5` | DNS/comportamento inconsistente | privacidade degradada | `socks5h`/`--socks5-hostname`, fail-closed | mock impede conexão direta |
| CW-018 | MEDIUM | Rotas/headers | qualquer GET serve HTML; headers mínimos | superfície rebinding/cache/frame | abuso local | rotas exatas + CSP/frame/nosniff | 404 e headers |
| CW-019 | MEDIUM | Python/deps | path 3.14 fixo; sem lock | ambiente divergente | falha/reprodutibilidade | venv, versões/hashes, matriz | install offline verificado |
| CW-020 | MEDIUM | Backup/delete | runbook e scripts | backup incompleto/overwrite SSD | perda ou falsa exclusão | recovery testado; documentar SSD | restore em temp isolado |
| CW-021 | LOW | IPv6 Dashboard | bind AF_INET loopback | expectativa de dual-stack não existe | compatibilidade | documentar ou listener separado seguro | socket inventory |
| CW-022 | INFORMATIONAL | Git/runner | interferência e workflow histórico | processo externo troca checkout | evidência inválida | isolamento/lock operacional | Gate G1/G2 |
