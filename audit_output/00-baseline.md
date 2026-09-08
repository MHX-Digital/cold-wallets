# Fase Zero — inventário e baseline

Data: 2026-09-07 UTC. Escopo: código e arquivos rastreados, sem acessar carteiras, pools, backups, credenciais ou artefatos assinados.

## Contenção aplicada

- Nenhum arquivo em `generated/`, `address_pool/`, `signed_transactions/`, `tx_data/`, `broadcast_logs/`, `backups/`, runtimes Tor ou equivalentes foi aberto.
- Buscas de segredos retornaram apenas nomes de arquivos. Nenhum valor foi impresso.
- `audit_output/PATCHES/` foi inventariado, mas não aberto: patches de remoção de credenciais podem conservar o valor removido.
- Não houve rede, download, instalação, broadcast, container, execução do projeto ou comando administrativo do Windows.
- Nenhum código de produção foi alterado antes deste baseline.

## Git e interferência concorrente

| Evento | Evidência |
|---|---|
| Snapshot inicial | `main`, `6d239caade16cb06f77a8defb38eda4bee0ec386`, limpo |
| Interferência | Durante a leitura, outro processo fez checkout de `main` e `reset` para `origin/main`; reflog de 08:20:48 UTC |
| Novo estado de base | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` |
| Branch requerida | Passou a existir em `5dfe0781479829655d9177cded7e4e7ca6c3ba7d`; não foi sobrescrita |
| Branch desta auditoria | `audit/cold-wallet-security-architecture-20260907`, baseada em `5374c1c...` |
| Permissões | Com autorização explícita, `.git` e `audit_output/` receberam grupo `vps-shared-projects` e escrita de grupo; proprietário não foi alterado |

O SHA de base desta rodada é `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f`. O SHA inicial é preservado apenas como evidência pré-sincronização.

## Ambiente e inventário

- Host de auditoria Linux; alvo operacional declarado Windows 10/11.
- Python 3.12.3; `python` ausente e `python3` sem `pip`.
- Git 2.43.0; Node.js 24.18.0; npm 11.16.0.
- `ruff`, `pytest`, `mypy`, `bandit` e PowerShell ausentes do PATH.
- 66 arquivos rastreados no snapshot inicial; nenhum teste automatizado rastreado.
- Dependências diretas: `eth-account`, `bit`, `requests[socks]`, `PySocks`, sem versões ou hashes.
- Sem lockfile, constraints com hashes, SBOM, matriz CI ou política de proveniência.
- Workflow usa `actions/checkout@v4` por tag e `rsync --delete` em runner self-hosted.
- Nenhum `AGENTS.md` no repositório ou nos dois diretórios pais.

## Baseline de alegações e observações

| Item | Estado alegado | Estado observado | Evidência | Risco |
|---|---|---|---|---|
| Produto | Cold/offline-first | Dashboard cria, recebe, deriva, exibe e assina com chaves no processo online | `README.md`; `dashboard/server.py:203-226,321-548` | CRITICAL |
| CLI offline | Internet fisicamente desabilitada | Parser de `netsh` cobre somente adaptadores reconhecidos; há bypass e assinatura online confirmável | `network_control.py`; `sign_*.py`; `enviar_*.py` | HIGH |
| Recuperação de rede | Reconexão segura | Estado apenas em memória; não cobre crash/energia, IPv6/virtuais ou restauração transacional | `network_control.py:126-161` | HIGH |
| Tor-only | Toda rede via Tor | Python usa `socks5h`; Batch usa `curl --socks5`; teste consulta IP real por clearnet; não há teste de ausência de fallback | módulos de rede; `rpc/test-privacy.bat` | HIGH |
| Tor ativo | Validado | Python valida `IsTor`; vários Batch aceitam mero sucesso HTTP pelo SOCKS | `dashboard/server.py:67-88`; `tools/*.bat` | MEDIUM |
| Tor one-click | Download seguro | Download em runtime sem hash/assinatura, `tempfile.mktemp`, extração e execução | `tools/tor_manager.py:20-215` | CRITICAL |
| Dependências | Setup automático | `pip install` global em runtime, sem pin/hash/venv | `start.bat`; `cold_wallets/install.bat`; `requirements.txt` | HIGH |
| BTC validation | Base58Check/Bech32/Bech32m | Só prefixo, tamanho e alfabeto; não valida checksum, witness program ou rede completa | `address_validation.py:56-85` | CRITICAL |
| ETH validation | EIP-55 | Falha de import aceita mixed-case silenciosamente; lower/upper aceitos por política | `address_validation.py:16-53` | HIGH |
| BTC prevouts | `scriptPubKey` obrigatório | Valores/scripts de APIs são tratados como verdade; sem prova do prevout ou pertencimento à chave | `enviar_btc.py:89-193`; `sign_btc.py:84-172` | CRITICAL |
| BTC send-all | Vsize exato | Tabela fixa pré-serialização, sem mixed inputs, recálculo real, dust ou limites de fee | `enviar_btc.py:40-69,299-350`; `sign_btc.py` | HIGH |
| BTC tipos | Native/wrapped/legacy | Gerador padrão entrega wrapped; Native é derivação manual no fluxo online; detecção Taproot excede suporte | `generate_wallets.py`; `enviar_btc.py` | HIGH |
| ETH type 2 | Send-all EIP-1559 | `chainId=1`; nonce `latest`; primeiro RPC vence; sem `eth_chainId`, `pending` ou quorum | `enviar_eth.py`; `dashboard/server.py:476-548` | CRITICAL |
| ETH fallback | Fallback compatível | Falta de `feeHistory` muda silenciosamente para legacy | `enviar_eth.py:110-140` | HIGH |
| Trustless RPC | Helios verifica | Dashboard inicia `eth_rpc_proxy.py`, retransmissor de RPC público; status só prova porta/resposta | `dashboard/server.py:103-121,572-610`; `tools/eth_rpc_proxy.py` | CRITICAL |
| Helios | Verificação criptográfica | Imagem somente por tag `0.11.0`, sem digest; checkpoint/config real não executados | `rpc/helios/*` | HIGH |
| Bind Dashboard | Localhost | Bind IPv4 explícito `127.0.0.1:8888`; nenhum listener IPv6 no código | `dashboard/server.py:769-770` | LOW |
| API local | Localhost seguro | Sem autenticação/token, Host/Origin/CSRF, Content-Type, limite de corpo, timeout ou idempotência | `dashboard/server.py:673-762` | CRITICAL |
| GET routing | `/` serve UI | Todo GET não-API serve HTML | `dashboard/server.py:698-710` | MEDIUM |
| Erros | Sem vazamento | `str(e)` é devolvido ao cliente | `dashboard/server.py:734-736` | HIGH |
| Frontend | HTML escapado | Respostas entram em `innerHTML` sem escape consistente; chave fica no DOM e clipboard | `dashboard/index.html:271-357` | CRITICAL |
| Operações críticas | Proteção contra clique | Apenas botão cliente; sem idempotência ou confirmação ligada ao payload | frontend; `api_send_*` | CRITICAL |
| Segredos em disco | Protegidos por `.gitignore` | JSON plaintext, permissão padrão, write direto, sem fsync/lock/criptografia | geradores, signer e Dashboard | CRITICAL |
| Descartáveis | Ciclo consistente | Só `unused/active/funded/spent`; rename+rewrite não é transação; CLI e API duplicam lógica | `disposable_manager.py`; `sweep_to_cold.py`; Dashboard | HIGH |
| Temporários | Extração segura | `mktemp`; writes sensíveis por timestamp e não atômicos | `tor_manager.py`; módulos de wallet | HIGH |
| Admin Windows | Hardening | `start.bat` eleva Dashboard, downloads e subprocessos inteiros | `start.bat` | HIGH |
| Bitcoin/Tor installer | Procedência validada | Downloads sem hash/assinatura; senha RPC impressa no console | `hardware/install_bitcoin_core.ps1` | CRITICAL |
| Firewall | Idempotente | Remove regras por wildcard e altera serviços globais sem snapshot/rollback | `rpc/hardening/*.ps1` | HIGH |
| Backup/delete | Seguro | Promessa não comprovada; runbook sugere overwrite como secure delete, inválido em SSD | `rpc/docs/runbook.md`; `rpc/scripts/backup.ps1` | HIGH |
| QA | Resultados PASS | Nenhum teste rastreado e toolchain ausente no host | `README.md:197-211`; inventário | CRITICAL |
| Python | 3.10–3.14 | Só 3.12.3 observável; Batch fixa `C:\Python314` | README e Batch | MEDIUM |

## Mapa inicial de riscos

### P0 — bloquear fundos reais

1. Remover do Dashboard online geração, entrada, exibição, armazenamento e assinatura com chaves.
2. Desabilitar `send-*` e geração de segredos até existir intercâmbio offline explícito.
3. Implementar validação Bitcoin completa e rede explícita.
4. Bloquear downloads/execução sem hash e procedência.
5. Corrigir “trustless”: proxy público por Tor não é Helios.
6. Tornar signer fail-closed para rede e dados não validados.

### P1 — segurança e integridade

1. Rota estrita, token efêmero, Host/Origin/CSRF, limites, timeouts e erros redigidos.
2. Idempotência e separação prepare → revisão → assinatura offline → broadcast.
3. Adapter Tor fail-closed com teste de DNS/clearnet.
4. Escrita sensível atômica, permissões, locking e recuperação.
5. Chain ID, nonce `pending`, limites EIP-1559 e divergência de provedores.
6. Validação de prevouts BTC, ownership e taxa sobre a transação real.

### P2 — arquitetura

1. Coordinator watch-only, signer offline, broadcaster e adapters separados.
2. PSBT para Bitcoin; envelope canônico não assinado para Ethereum.
3. Journal e estados recuperáveis para descartáveis.
4. Dependências/imagens por hash ou digest, venv e instalação offline verificável.

### P3 — UX/manutenção

1. Rotular hot/warm/offline/air-gapped, Tor e RPC verificado/não verificado.
2. Remover private key do DOM/clipboard; revisão humana vinculada ao payload.
3. Centralizar contratos, validação e erros; reduzir duplicação CLI/Dashboard.

## Limitações

- Diagnóstico estático inicial, não valida comportamento real de Windows, Tor, Docker, Helios ou redes blockchain.
- Sem instalação, não foi possível resolver transitivas, licenças ou CVEs localmente.
- Versões atuais, advisories e hashes oficiais exigem pesquisa externa posterior e separada.
- Patches históricos seguem em quarentena lógica por possível retenção de credenciais.
- A sincronização externa do worktree é um risco operacional ativo; branch/HEAD/status devem ser verificados antes de cada lote.
