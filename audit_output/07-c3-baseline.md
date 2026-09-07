# C3-G0 — Baseline de revalidação

Data: 2026-09-07  
Resultado: **APROVADO**

| Verificação | Esperado | Observado | Resultado |
|---|---|---|---|
| Diretório raiz | `/home/mhx/projects/cold-wallets` | Correspondente | OK |
| Branch | `audit/cold-wallet-security-architecture-20260907` | Correspondente | OK |
| HEAD | `32f6e18fa8a936b7bd65c0984be4a015e77ad3dc` | Correspondente | OK |
| `main` | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | Correspondente | OK |
| Worktree | Limpo | Limpo antes/depois dos testes | OK |
| Baseline SHA-256 | `f4170979c73aa04ab2238e5eb3b621ad7fba7c4b789891abad995f7e5cec7dea` | Correspondente | OK |
| Relatórios anteriores | Íntegros | Checksums correspondentes | OK |
| Testes existentes | 13 aprovados | 13/13, 0,538 s | OK |
| Portas de teste | Liberadas | Porta efêmera 40901 liberada | OK |
| Temporários/caches | Zero resíduos | Zero diretórios temporários e `__pycache__` | OK |

## Interferência

Não foi detectada nova interferência durante este gate. A existência histórica da branch alternativa `audit/cold-wallet-security-architecture-20260907` e da branch de preservação `5dfe078...` permanece registrada; nenhum trabalho concorrente foi sobrescrito ou incorporado.

## Higiene do teste

O teste utilizou o run-id `c153e6889f4c4d50be3099c431a8f72a` e a porta efêmera `40901`. Nenhum subprocesso filho, container, rede ou volume foi criado. O teardown confirmou resíduo zero.

## Limitações

Este gate é apenas de integridade e revalidação local. Não houve rede externa, instalação de dependências, acesso a carteiras, assinatura ou broadcast.
