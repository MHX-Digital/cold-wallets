# Plano de remediação

## C3

P0: remover alcançabilidade de módulos secretos do Dashboard e estabelecer signer offline. P1: integrar PSBT, envelope ETH, transporte Tor fail-closed e idempotência persistente. P2: lockfile/hashes e migração de armazenamento. P3: UX guiada e governança.

| ID | Prioridade | Problema | Correção proposta | Dependências | Risco da mudança | Testes | Critério de aceite |
|---|---|---|---|---|---|---|---|
| CW-001/002 | P0 | Dashboard recebe/gera/assina chaves | remover rotas secret-bearing e tornar coordinator watch-only | decisão de produto para xpub/descriptors | breaking change alto, segurança positiva | HTTP/route tests | nenhuma private key cruza API/DOM |
| CW-003 | P0 | BTC sem checksum | validação completa Base58Check e SegWit Bech32/Bech32m, rede explícita | preferir biblioteca auditada; stdlib só para encoding | baixo/médio | vetores BIP173/BIP350/Base58 | inválidos e rede errada rejeitados |
| CW-004 | P0 | prevout remoto vira verdade | adotar PSBT e validar ownership/prevout/política | biblioteca Bitcoin com PSBT | migração média | vetores e mutações | signer rejeita qualquer mismatch |
| CW-005/010 | P0 | ETH remoto/legacy silencioso | envelope type 2, chainId consultado, pending nonce, bounds, divergência fail-closed | adapter RPC/Helios | médio | mocks divergentes | intenção canônica = tx assinada |
| CW-006 | P0 | download executável sem prova | desabilitar download no Dashboard; manifest de hash/assinatura e instalação explícita | hashes oficiais/release process | baixo para bloqueio; médio para distribuição | hash mismatch | nada executa sem verificação |
| CW-007/016 | P0 | trustless falso | identidade explícita do backend; “unverified public RPC” por padrão | endpoint/version attestation Helios | baixo | status mocks | UI nunca infere Helios por porta |
| CW-008/018 | P1 | DOM XSS/rotas/headers | textContent/DOM APIs, rota estrita e security headers | nenhuma | baixo | XSS/404/headers | payload nunca vira markup |
| CW-002 | P1 | Host/Origin/CSRF/body | token efêmero, allowlists exatas, JSON e limite | bootstrap seguro do token | médio | matriz HTTP | requisições inválidas falham antes do handler |
| CW-014 | P1 | repetição | idempotency key + armazenamento transacional | desenho do coordinator | médio | concorrência/retry | mesma intenção executada no máximo uma vez |
| CW-015 | P1 | vazamento em erro/log | erros de domínio e redactor recursivo | nenhuma | baixo | canários | zero segredo em resposta/log |
| CW-011 | P1 | arquivos sensíveis frágeis | retirar do online; modo legado com temp seguro, fsync, replace e ACL | adapter storage Windows | médio | crash/permission mocks | write completo ou estado anterior |
| CW-012 | P1 | offline não comprovado | remover bypass para signer seguro; documentar warm/offline; preferir air gap | decisão operacional | alto UX | state-machine mocks | falha de isolamento impede assinatura |
| CW-017 | P1 | Tor inconsistente | adapter único, DNS remoto, `trust_env=False`, redirects/size/retry limitados | requests/PySocks pinados | baixo | transporte mock | nenhuma conexão direta possível |
| CW-013 | P2 | descartáveis | estados `unused→reserved→presented→detected→confirmed→sweep_prepared→swept` + falhas/journal | storage transacional | médio | property/recovery | transições válidas, recovery idempotente |
| CW-009 | P2 | fee BTC aproximada | política por input real, dust e fee caps | PSBT/lib | médio | vetores/mixed inputs | fee efetiva dentro do aprovado |
| CW-019 | P2 | supply chain Python | venv, lock com hashes, SBOM/licenças, matriz 3.10–3.14 | processo de build aprovado | médio | instalação offline | ambiente reproduzível |
| CW-020 | P2 | backup/recovery | formato versionado, criptografia e restore periódico em temp | decisão de custódia | médio | restore isolado | recuperação comprovada sem segredo em log |
| CW-021/022 | P3 | operação/Git/IPv6 | gates, lock de worktree, documentação de listeners | governança | baixo | preflight | evidência não sofre interferência |

## Correções pequenas candidatas neste ciclo

Somente após estes documentos e associadas aos findings:

1. CW-003: validação BTC completa com vetores públicos e sem dependência externa.
2. CW-018/CW-002: rotas estritas, limite de corpo, Content-Type, Host e Origin.
3. CW-015: respostas de erro genéricas/redigidas.
4. Infraestrutura de teste stdlib com diretório exclusivo, manifesto em memória, teardown e auditoria de resíduos.

Não serão implementados neste ciclo PSBT, coordinator completo, migração de storage, Docker/Tor real, rede Windows ou operação blockchain.

## Execução neste ciclo

- CW-003 implementado e testado sem dependência externa. A implementação manual foi limitada ao **encoding/decoding de endereços**, não a assinatura ou curva elíptica; foi escolhida para evitar instalação de supply chain durante esta fase. Revisão por implementação independente continua recomendada.
- CW-001 contido no Dashboard: endpoints com chaves falham fechados e a UI não solicita WIF/private key.
- CW-002/CW-018 parcialmente implementados: token efêmero, allowlists exatas de Host/Origin, JSON estrito, limite de 64 KiB, rejeição de Transfer-Encoding, rotas exatas, métodos, timeout e headers.
- CW-007/CW-016 parcialmente implementados na UI: o botão/aviso identifica o serviço iniciado pelo Dashboard como RPC público via Tor, não verificado por Helios.
- CW-015 parcialmente implementado: erro interno HTTP genérico e log apenas do tipo da exceção.

Pendências mantidas no plano: remover código legado não roteado, coordinator watch-only real, idempotência persistente, PSBT, envelope Ethereum, storage, Tor/supply chain e attestation Helios.

## Protocolo de teste aplicável

Cada execução terá `run-id`, raiz sob `/tmp/cold-wallets-test-<run-id>`, manifesto de recursos próprios e ciclo `preflight → start → readiness → execute → collect → stop → cleanup → verify`. Testes puros não criarão chaves. Testes HTTP, se necessários, usarão porta efêmera e encerrarão somente o PID/thread/socket criado pela própria fixture. Resíduo permitido: zero.

## Pendências após C4

P0: instalar somente após aprovação a dependência Ethereum pinada e executar vetores reais; selecionar e pinnear biblioteca PSBT. P1: migrar clientes legados ao adapter Tor e integrar broadcaster remoto simulado completo. P2: lockfile com hashes, storage legado e estado descartável. P3: validação operacional Windows/air-gap e recuperação.

## Pendências após C5

P0: ampliar PSBT para vetores oficiais, P2PKH/P2SH-P2WPKH e validação independente. P1: broadcaster Ethereum, scripts Batch/PowerShell Tor e attestation Helios. P2: integrar stores novos, formato autenticado de migração e locks Windows/Python adicionais. P3: testes operacionais air-gap/backup.

## Pendências após C6

| ID | Prioridade | Problema restante | Próxima correção | Dependências | Risco | Teste | Critério de aceite |
|---|---|---|---|---|---|---|---|
| CW-004/009 | P0 | backend nativo embit não reproduzido/aprovado | reproduzir libsecp256k1 de fonte fixada ou substituir por backend auditado; manter bloqueio até lá | build Bitcoin independente | alto | BIP174 + Bitcoin Core regtest | diagnóstico `approved`, hash allowlisted e vetores externos passam |
| CW-005/016 | P0 | verdade remota e Helios não atestado | executar attestation completa e divergência multi-backend fail-closed | Helios controlado | alto | checkpoint/chain/digest/route | oito evidências presentes e coerentes |
| CW-006/010/017 | P0 | scripts e módulos legados somente leitura | corrigir ownership de forma operacional aprovada; remover do Git e substituir por comandos novos | ação do mantenedor | médio | AST + busca + execução fail-closed | zero import legado, download, rede direta ou autoelevação alcançável |
| CW-011/012 | P1 | host offline e storage legado | CLI signer de processo único, formato autenticado e validação Windows offline | Windows isolado | alto | interrupção/recovery/canários | chave nunca cruza host online; recovery comprovado |
| CW-019 | P1 | locks Windows ausentes | gerar/verificar em Windows x86-64 CPython 3.10/3.12/3.14 | runners Windows | médio | clean-room hash install | lock por alvo, backend registrado, suíte completa |
| CW-020 | P2 | backup/restore | teste de restauração sintética e runbook operacional | decisão de custódia | médio | restore em mídia temporária | recuperação íntegra sem logs/segredos residuais |

## Pendências após C7

| Prioridade | Escopo | Critério objetivo |
|---|---|---|
| P0 | corrigir ownership somente dos oito diretórios legados listados em `28-c7-ownership-inventory.md`; remover arquivos Git específicos | zero `bit`, signers/senders antigos, install/download/admin entrypoints |
| P0 | executar suíte hash-locked e testes AES-GCM/backup que foram pulados | adulteração, senha errada, downgrade, backup e restore passam com primitive real |
| P0 | reproduzir/auditar secp256k1 e validar Bitcoin Core regtest | backend em estado APPROVED comprovado; E2E Bitcoin externo |
| P1 | validar API/UI no Windows e gerar locks 3.10/3.12/3.14 | clean-room installs e suíte completa por alvo |
| P1 | validar Tor e attestation Helios controlados | nenhuma rota direta; oito evidências Helios |
| P2 | persistir política operacional/retention de artefatos e testar restore em mídia | recuperação sem dados reais ou resíduos |

## Pendências após C7.1

| Prioridade | Escopo restante | Critério objetivo |
|---|---|---|
| P0 | corrigir ownership dos sete subdiretórios RPC listados no baseline e remover seus 13 arquivos individualmente | `rpc/` sem arquivo rastreado ou diretamente invocável; teste de filesystem passa |
| P0 | aprovar backend secp256k1 por reprodução/auditoria independente | um estado `APPROVED_*`, vetores externos e Bitcoin Core regtest passam |
| P1 | validar Windows x86-64 e gerar locks 3.10/3.12/3.14 | instalação clean-room e suíte completa em cada alvo |
| P1 | validar Tor e attestation Helios em ambiente controlado | ausência comprovada de clearnet e oito evidências coerentes |
| P2 | executar ensaio de retenção/restore em mídia sintética controlada | integridade e cleanup comprovados sem dados reais |

## Pendências após C7.2

| Prioridade | Validação operacional | Critério objetivo |
|---|---|---|
| P0 | backend secp256k1 e Bitcoin Core regtest | build/backend aprovado e transações PSBT comparadas com Core |
| P0 | Windows offline signer | rede fisicamente separada, locks por Python e recovery comprovado |
| P1 | Tor controlado | binário/config verificados, DNS remoto e ausência de clearnet observada |
| P1 | Helios controlado | oito evidências de attestation, checkpoint e rota exclusiva |
| P2 | ownership da raiz/`.git` e diretório L2 vazio | ownership operacional consistente sem alteração de conteúdo |

## Pendências após C8 bloqueado por plataforma

| Prioridade | Execução no Windows nativo | Critério objetivo |
|---|---|---|
| P0 | executar preflight C8 read-only e validar locks CPython disponíveis | Windows 10/11 nativo, Git esperado, Defender ativo, locks alvo e zero resolução dinâmica |
| P0 | Bitcoin Core exclusivamente regtest | PSBT P2WPKH interoperável, txid/fee/vsize/witness independentes e backend classificado sem promoção indevida |
| P1 | isolamento do signer + Tor oficial verificado | nenhum socket/DNS do signer; aplicação conecta apenas ao SOCKS loopback e falha sem Tor |
| P1 | Helios temporário e atestado | oito evidências coerentes ou estado permanece `HELIOS_UNATTESTED` |
| P1 | launcher, filesystem, ACL e interrupções Windows | foreground, porta configurável liberada, atomicidade/ACL e cleanup em todas as falhas |
| P2 | backup/restore em mídia sintética | autenticação, checksum, interrupção e cleanup com resíduo zero |

O harness em `validation/windows/` não executa downloads nem serviços e não
substitui nenhuma dessas evidências. A correção de ownership Linux continua uma
tarefa separada, por caminhos explícitos.
