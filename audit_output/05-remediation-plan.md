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
