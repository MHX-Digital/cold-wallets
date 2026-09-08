# Modelo formal de ameaças

## Escopo e conclusão

O sistema reúne dois produtos incompatíveis na mesma fronteira: um signer com material privado e um coordenador/broadcaster online. No Dashboard, essa composição é uma **hot wallet local**. O CLI pode executar assinatura com interfaces administrativamente desabilitadas, mas isso é apenas **offline signing transitório**, não air gap. Tor fornece privacidade de transporte; Helios, quando realmente iniciado e sincronizado, fornece verificação parcial de consenso/estado. Nenhum deles protege chave presente em host ou navegador comprometido.

## Ativos

| Ativo | Local observado | Confidencialidade | Integridade/risco principal |
|---|---|---:|---|
| Private keys/WIFs | memória Python, JSON em `generated/` e `address_pool/`, DOM/clipboard | CRITICAL | roubo permite gasto irreversível |
| Seeds/mnemonics | não implementados no snapshot | CRITICAL | promessa futura deve evitar logs/DOM |
| Dados não assinados | entrada interativa/JSON remoto, memória | HIGH | substituição altera destino/valor/taxa |
| Raw transactions assinadas | console, JSON, payload de broadcast | HIGH | replay/broadcast duplicado e perda de privacidade |
| UTXOs/prevouts/fees | APIs Bitcoin públicas | HIGH integridade | servidor malicioso induz assinatura incorreta |
| Saldo/nonce/fees/chain | RPC Ethereum público | HIGH integridade | nonce/rede/fee incorretos |
| Endereços e histórico | API, arquivos, logs | MEDIUM | correlação e perda de privacidade |
| Configuração RPC/Helios/checkpoint | arquivos e imagens Docker | HIGH integridade | falso estado “verificado” |
| Backups, logs e credenciais RPC/WireGuard/Tor | filesystem Windows/Docker | HIGH | exposição persistente e recuperação falha |

## Adversários

- Malware/local admin: lê memória, DOM, arquivos, clipboard e injeta binários/dependências.
- Usuário local não autorizado: chama APIs localhost e lê arquivos conforme ACL herdada.
- Navegador/extensão/site malicioso: CSRF, DNS rebinding, DOM XSS e captura de clipboard.
- Dependência Python/imagem/binário malicioso: executa no contexto do Dashboard elevado.
- Provedor RPC/nó/API Bitcoin malicioso: falsifica dados usados na construção da transação.
- Observador de rede/exit Tor: correlaciona timing e destino; TLS ainda é necessário.
- Atacante de disco/backup: recupera JSON plaintext e metadados.
- Erro operacional: rede/chain/endereço/taxa errados, duplo clique e restauração incompleta.
- Corrida/crash: duplica reserva/broadcast ou corrompe transição de estado.

## Fronteiras de confiança

| Fronteira | Autenticado? | Verificado criptograficamente? | Confiança residual |
|---|---:|---:|---|
| Navegador → Dashboard `127.0.0.1:8888` | Não | Não | qualquer origem/processo local pode tentar operar |
| Dashboard → módulos Python | Apenas import local | assinatura depende da biblioteca; intenção não é vinculada | código/dependências/host |
| Dashboard → subprocessos Tor/RPC | Não há attestation | Não | PATH/binário/download/processo |
| Aplicação → arquivos | ACL explícita ausente | Não | usuário, malware, symlink, crash |
| Aplicação → SOCKS Tor | Porta + consulta `IsTor` em Python | Não para identidade do daemon | processo local na porta e Tor Project |
| Tor → serviços HTTPS | TLS do cliente | Certificado WebPKI, não conteúdo blockchain | CA, endpoint, exit timing |
| Proxy local → RPC público | Sem autenticação própria | Não | provedor pode mentir/censurar |
| Helios → execution/consensus RPC | Conforme Helios | estado/header quando fluxo é realmente Helios | código Helios, checkpoint, configuração |
| Host online → signer | Mesma máquina/processo no Dashboard | Não | comprometimento do host é fatal |
| Storage normal → backup | Scripts/procedimento | Não comprovado | senha, ferramenta 7-Zip, mídia e operador |

## Cenários prioritários

1. Página maliciosa chama endpoint local sem token/Origin; gera chaves ou solicita assinatura/broadcast.
2. XSS por resposta RPC/API entra em `innerHTML` e exfiltra a chave mantida no DOM.
3. Tor baixado sem verificação executa como usuário/admin e rouba arquivos/chaves.
4. API Bitcoin fornece prevout/valor/script adulterado; signer não reconstrói/verifica fonte independente.
5. RPC Ethereum fornece `latest` nonce, saldo e fee inconsistentes; transação assinada conflita ou reserva taxa inadequada.
6. Porta 8545 contém proxy público, mas UI/docs inferem Helios “trustless”.
7. Crash entre rename/rewrite de endereço descartável perde ou duplica estado.
8. Falha de energia durante rede desabilitada deixa estado operacional não restaurado; caminho de bypass assina online.

## Garantias impossíveis na arquitetura atual

- Dashboard online não pode garantir cold storage nem segredo contra host/browser comprometido.
- Desabilitar adaptadores por software no mesmo Windows não prova air gap.
- Tor não autentica dados blockchain, não verifica consenso e não protege memória/clipboard/disco.
- Localhost não é autenticação e não bloqueia CSRF, rebinding ou malware local.
- `.gitignore` não cifra, restringe ACL, limpa SSD ou protege backup.
- Helios só oferece garantias quando a requisição realmente atravessa a instância correta, com checkpoint/configuração válidos; uma porta respondendo não prova isso.

## Arquitetura-alvo incremental

1. **Coordinator watch-only online:** endereços/xpub ou descritores, consulta e preparação; nenhuma private key.
2. **Signer offline/air-gapped:** recebe envelope canônico, mostra rede/destino/valor/taxa/hash e só então assina.
3. **Bitcoin:** PSBT com `witness_utxo`/`non_witness_utxo`, validação de ownership e política antes da assinatura.
4. **Ethereum:** envelope type 2 canônico com `chainId`, nonce, `to`, value, gas, fees, type e data, mais resumo/hashes.
5. **Retorno:** somente PSBT final/raw transaction assinada, nunca chave.
6. **Broadcaster separado:** decodifica e compara a transação assinada com o manifesto aprovado, usa rede explícita e idempotência.
