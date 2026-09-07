# Achados consolidados

## Atualização C3

Os achados permanecem abertos ou parcialmente mitigados; a documentação C3 não constitui verificação. Separação física do signer, PSBT, envelope Ethereum integrado, supply chain bloqueada e broadcaster idempotente seguem pendentes.

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

## Estado após as correções isoladas deste ciclo

| ID | Estado | Evidência |
|---|---|---|
| CW-001 | CONTIDO NO DASHBOARD | rotas que geram, abrem, preparam ou assinam com chaves retornam erro fail-closed; campos de chave removidos da UI. Código legado/CLI e funções agora não roteadas permanecem e exigem migração posterior |
| CW-002 | PARCIALMENTE MITIGADO | Host/Origin/token/content-type/body/métodos cobertos; idempotência transacional continua pendente para o futuro coordinator/broadcaster |
| CW-003 | MITIGADO PARA ENDEREÇOS MAINNET SUPORTADOS | Base58Check, HRP `bc`, checksum Bech32/Bech32m, mixed case, witness version/program e rede; vetores públicos BIP84/BIP350 e Base58 |
| CW-008 | PARCIALMENTE CONTIDO | nenhuma chave real entra na UI pelas rotas expostas; helpers legados com `innerHTML` ainda devem ser removidos na refatoração watch-only |
| CW-015 | PARCIALMENTE MITIGADO | exceções HTTP inesperadas não retornam mais `str(e)`; redactor central para todos os módulos permanece pendente |
| CW-018 | MITIGADO NO HANDLER PRINCIPAL | somente `/` e `/index.html` servem HTML; demais rotas 404; headers de segurança e timeout de socket adicionados |

Todos os demais findings permanecem abertos. “Contido” não equivale a correção arquitetural nem autoriza fundos reais.

## Estado C4

| ID | Estado anterior | Estado C4 | Evidência |
|---|---|---|---|
| CW-001 | contido | VERIFIED | Dashboard sem imports, handlers, caminhos ou UI secret-bearing; testes AST/HTTP |
| CW-002 | partial | VERIFIED no Dashboard | única API status, Host/Origin/token/body/métodos testados |
| CW-003 | mitigado | VERIFIED | vetores Base58Check/Bech32(m) |
| CW-004 | open | OPEN | PSBT indisponível localmente |
| CW-005 | open | PARTIAL | envelope/política signer; dados RPC ainda não verificados |
| CW-006 | open | PARTIAL | runtime pip/Tor bloqueados; lock/hash ainda pendentes |
| CW-007 | partial | PARTIAL | UI declara watch-only/RPC não verificado |
| CW-008 | partial | VERIFIED no Dashboard | JS secret-bearing removido; resposta exibida como texto |
| CW-009 | open | OPEN | depende de PSBT |
| CW-010 | open | PARTIAL | signer aceita somente tipo 2; cliente legado permanece |
| CW-011 | open | PARTIAL | artefatos atômicos; chaves legadas plaintext permanecem |
| CW-012 | open | PARTIAL | signer estruturalmente sem rede; host operacional não validado |
| CW-013 | open | OPEN | estado descartável não migrado |
| CW-014 | open | VERIFIED na camada nova | SQLite/unique/concorrência/restart/retries |
| CW-015 | partial | PARTIAL | Dashboard não loga requests; redactor global pendente |
| CW-016 | partial | PARTIAL | UI não afirma Helios; attestation pendente |
| CW-017 | open | PARTIAL | adapter fail-closed testado; clientes legados não migrados |
| CW-018 | mitigado | VERIFIED | rotas/headers/métodos testados |
| CW-019 | open | PARTIAL | runtime install bloqueado; lockfile/hashes pendentes |
| CW-020 | open | OPEN | backup/recovery pendente |
| CW-021 | open | ACCEPTED TEMPORARILY | bind IPv4 loopback documentado |
| CW-022 | informational | VERIFIED | gates e commits isolados; sem interferência C4 |

## Estado C5

| ID | Estado C4 | Estado C5 | Evidência |
|---|---|---|---|
| CW-001 | VERIFIED | VERIFIED | fronteira Dashboard preservada |
| CW-002 | VERIFIED no Dashboard | VERIFIED no Dashboard | regressão HTTP |
| CW-003 | VERIFIED | VERIFIED | vetores de endereço |
| CW-004 | OPEN | PARTIAL | PSBT v0 P2WPKH com prevout completo; escopo amplo pendente |
| CW-005 | PARTIAL | VERIFIED no signer | assinatura type 2/recovery/custos reais; verdade RPC permanece separada |
| CW-006 | PARTIAL | PARTIAL | locks Python verificados; Tor binário ainda sem manifest oficial |
| CW-007 | PARTIAL | PARTIAL | NO-GO e limites preservados |
| CW-008 | VERIFIED no Dashboard | VERIFIED no Dashboard | regressão UI/API |
| CW-009 | OPEN | PARTIAL | fee PSBT recalculada e limitada para P2WPKH |
| CW-010 | PARTIAL | VERIFIED no signer | somente type 2; legado online ainda deprecado |
| CW-011 | PARTIAL | PARTIAL | detector metadata-only; destino autenticado pendente |
| CW-012 | PARTIAL | PARTIAL | socket bloqueado em teste; validação host pendente |
| CW-013 | OPEN | VERIFIED na camada nova | SQLite, estados, reserva concorrente, expiração e histórico |
| CW-014 | VERIFIED na camada nova | VERIFIED | estado incerto/reconciliação/already-known adicionados |
| CW-015 | PARTIAL | PARTIAL | exceções de chave redigidas; redactor global pendente |
| CW-016 | PARTIAL | PARTIAL | Helios sem attestation |
| CW-017 | PARTIAL | VERIFIED para clientes Python inventariados | AST: requests só no adapter; scripts Batch/PS continuam pendentes |
| CW-018 | VERIFIED | VERIFIED | regressão web |
| CW-019 | PARTIAL | VERIFIED para CPython 3.12/Linux | runtime/build locks instalados offline com hashes |
| CW-020 | OPEN | OPEN | backup/recovery real pendente |
| CW-021 | ACCEPTED TEMPORARILY | ACCEPTED TEMPORARILY | bind IPv4 loopback |
| CW-022 | VERIFIED | VERIFIED | Gate C5 estável |

## Estado C6

Os níveis de severidade originais não foram reduzidos. `VERIFIED` abaixo significa
que a barreira citada possui teste; não significa que o produto está liberado.

| ID | Estado C5 | Estado C6 | Evidência C6 |
|---|---|---|---|
| CW-001 | VERIFIED | VERIFIED | árvore transitiva do Dashboard não alcança signer/legado; serviço coordinator watch-only |
| CW-002 | VERIFIED no Dashboard | VERIFIED no Dashboard | regressão HTTP, API permanece status-only e broadcast normal desabilitado |
| CW-003 | VERIFIED | VERIFIED | vetores Base58Check/Bech32(m) preservados |
| CW-004 | PARTIAL | PARTIAL | PSBT v0 mainnet P2WPKH valida prevouts completos e consistentes; assinatura bloqueada por backend não aprovado |
| CW-005 | VERIFIED no signer | PARTIAL | signer e broadcaster validam a tx real contra envelope; dados de proposta de RPC público continuam não verificados |
| CW-006 | PARTIAL | PARTIAL | launcher primário não eleva/instala/baixa; downloader Tor e instaladores legados permanecem |
| CW-007 | PARTIAL | PARTIAL | README/UI corrigidos; documentação RPC histórica ainda requer saneamento |
| CW-008 | VERIFIED no Dashboard | VERIFIED no Dashboard | UI sem segredos/raw tx e apenas `textContent` para status |
| CW-009 | PARTIAL | PARTIAL | um output, fee positiva/absoluta/rate e prevouts P2WPKH; validação independente/regtest pendente |
| CW-010 | VERIFIED no signer | PARTIAL | fluxo novo é apenas type 2; cliente legado combinado ainda está fisicamente presente |
| CW-011 | PARTIAL | PARTIAL | nenhum segredo nos stores novos; migração autenticada/ACL Windows pendente |
| CW-012 | PARTIAL | PARTIAL | fronteira de imports sem rede verificada; host air-gapped não validado |
| CW-013 | VERIFIED na camada nova | VERIFIED E INTEGRADO | coordinator consome reserva/transições SQLite; concorrência, restart e idempotência testados |
| CW-014 | VERIFIED | VERIFIED | broadcaster Ethereum usa hash real, unique key, estado incerto, reconciliação, restart e concorrência |
| CW-015 | PARTIAL | PARTIAL | erros novos são de domínio/redigidos; legado ainda imprime exceções/dados |
| CW-016 | PARTIAL | PARTIAL | enum explícito e attestation exige oito evidências; Helios real não foi atestado |
| CW-017 | VERIFIED Python / scripts pendentes | PARTIAL | três entrypoints Python de rede legados abortam antes de imports; scripts Batch/PS permanecem |
| CW-018 | VERIFIED | VERIFIED | regressão de rotas/headers/métodos |
| CW-019 | VERIFIED Linux 3.12 | PARTIAL | Linux 3.12 reproduzido; automação Windows criada, locks Windows não alegados |
| CW-020 | OPEN | OPEN | restore real não executado |
| CW-021 | ACCEPTED TEMPORARILY | ACCEPTED TEMPORARILY | somente loopback IPv4 documentado |
| CW-022 | VERIFIED | VERIFIED | Gate C6 estável; commits locais isolados |

## Estado C7

| ID | Severidade | Estado C7 | Evidência |
|---|---|---|---|
| CW-001 | CRITICAL | VERIFIED | Dashboard/API continuam sem signer; árvore transitiva e rotas testadas |
| CW-002 | CRITICAL | VERIFIED | Host, Origin, token, body, métodos, schemas e idempotência persistente |
| CW-003 | CRITICAL | VERIFIED | vetores de endereço preservados |
| CW-004 | CRITICAL | PARTIAL | revisão PSBT watch-only existe; signing permanece bloqueado |
| CW-005 | CRITICAL | PARTIAL | envelope/importação validam intenção; dados RPC continuam não verificados |
| CW-006 | CRITICAL | PARTIAL | launcher seguro e quarentena; instaladores/downloaders 0644 continuam presentes |
| CW-007 | CRITICAL | PARTIAL | README/UI alinhados; árvore RPC histórica permanece em quarentena |
| CW-008 | HIGH | VERIFIED NO DASHBOARD | sem segredo/raw por padrão, sem local/session storage ou console payload |
| CW-009 | HIGH | PARTIAL | política PSBT estreita; regtest/independência pendentes |
| CW-010 | HIGH | PARTIAL | fluxo novo type 2; signers/senders antigos não foram fisicamente removidos |
| CW-011 | HIGH | PARTIAL | formato scrypt/AES-GCM implementado; validação real C7 bloqueada pela dependência ausente |
| CW-012 | HIGH | PARTIAL | isolamento estrutural; Windows/air gap não validados |
| CW-013 | HIGH | VERIFIED | store integrado à API e reserva idempotente |
| CW-014 | HIGH | VERIFIED LOCALMENTE | registro local e broadcaster persistentes; remoto continua desabilitado |
| CW-015 | HIGH | PARTIAL | respostas novas redigidas; legado ainda contém logs inseguros |
| CW-016 | HIGH | PARTIAL | classificação explícita; Helios real não atestado |
| CW-017 | MEDIUM | PARTIAL | adapter central e denylist; scripts diretos permanecem |
| CW-018 | MEDIUM | VERIFIED | rotas exatas, headers e métodos testados |
| CW-019 | MEDIUM | PARTIAL | lock Linux anterior; Windows não validado |
| CW-020 | MEDIUM | PARTIAL | backup/restore autenticado implementado; execução real da primitive pulada |
| CW-021 | LOW | ACCEPTED TEMPORARILY | loopback IPv4 |
| CW-022 | INFORMATIONAL | PARTIAL | conteúdo estável; ownership e buckets Git mistos persistem |
