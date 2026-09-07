# Evidência de testes e Gate G2

## Escopo

Validação local, determinística e sem dependências externas das duas correções isoladas:

- CW-003: Base58Check e SegWit Bech32/Bech32m mainnet.
- CW-001/CW-002/CW-018: bloqueio de operações com chave, Host, Origin, token, Content-Type, limite de corpo, métodos, rotas e headers.

Não houve teste de assinatura, broadcast, Tor, Docker, Windows, Helios, RPC externo, filesystem de carteira ou fundos.

## Comandos e resultados

| Comando | Resultado | Duração | Invariante |
|---|---|---:|---|
| `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_address_validation -v` | 8/8 PASS | 0,001 s | checksums/rede/formato rejeitam mutações conhecidas |
| `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` | 13/13 PASS | 0,543 s (wall 0,545 s) | validação BTC + matriz HTTP e teardown |
| `git diff --check` | PASS | <1 s | sem whitespace inválido |

Vetores públicos usados: dois endereços Base58Check mainnet amplamente publicados, endereço de recebimento BIP84 e string de checksum Bech32m `A1LQFN3A` do BIP350. Nenhuma chave correspondente foi usada ou derivada.

## Higiene — execução consolidada

Run ID: `95942f6c2458436e93fd07654ca47bba`
Porta efêmera: `35533`

| Recurso | Antes | Criado pelo teste | Encerrado/removido | Resíduo |
|---|---:|---:|---:|---:|
| Processo adicional | 0 | 0 (thread no runner) | 0 | 0 |
| Thread HTTP | 0 | 1 | 1 (`shutdown`, `server_close`, `join`) | 0 |
| Porta `35533` | livre | 1 listener loopback | 1 liberada; `ss` vazio | 0 |
| Diretório `/tmp/cold-wallets-test-95942f6c2458436e93fd07654ca47bba-*` | 0 | 1 | 1 por `TemporaryDirectory.cleanup` | 0 |
| Arquivos temporários/manifesto | 0 | somente estrutura temporária/manifesto em memória | removidos com a raiz/processo | 0 |
| `__pycache__` no repositório | 0 | 0 (`PYTHONDONTWRITEBYTECODE=1`) | N/A | 0 |
| Containers Docker | 0 criados pela auditoria | 0 | 0 | 0 |
| Redes Docker | 0 criadas pela auditoria | 0 | 0 | 0 |
| Volumes Docker | 0 criados pela auditoria | 0 | 0 | 0 |
| Carteiras/fixtures com segredo | 0 | 0 | 0 | 0 |

O inventário `ss -ltn` antes/depois mostrou serviços preexistentes não relacionados; nenhum foi encerrado ou alterado. As portas relevantes `8888`, `9050`, `8545` e `8332` não foram ocupadas pela suíte. Docker não foi consultado nem iniciado.

## Limitações

- `ruff`, `pytest`, `mypy`, `bandit`, PowerShell e `pip` não estão disponíveis; nada foi instalado.
- A validação Bech32m possui vetor público de checksum, mas ainda merece comparação futura com outra implementação Bitcoin madura.
- Não há prova dinâmica Windows, Tor, Helios, RPC ou criptografia de transações nesta fase.
- A API ainda contém funções legadas não roteadas; o bloqueio é de exposição, não remoção arquitetural.
- Findings críticos de construção/assinatura BTC/ETH, storage e supply chain permanecem.

## Gate G2

Resultado: **APROVADO COM RESSALVAS**.

- Git permaneceu na branch esperada durante os testes.
- Nenhum segredo/diretório real de carteira foi acessado.
- Nenhuma transação, rede externa ou serviço remoto foi usado.
- Zero resíduo de processo, porta, arquivo temporário, cache, container, rede ou volume criado pelos testes.
- A fase documental e as correções pequenas são reproduzíveis no ambiente disponível.
- As ressalvas são os riscos críticos residuais e a ausência da toolchain/ambiente Windows, não falhas ocultadas da suíte executada.
