# Gate G1 — estabilização Git

Data: 2026-09-07 UTC
Resultado: **APROVADO COM RESSALVAS**

## Resultado das verificações

| Verificação | Esperado | Observado | Resultado |
|---|---|---|---|
| Raiz real | `/home/mhx/projects/cold-wallets` | `/home/mhx/projects/cold-wallets` | APROVADO |
| Branch atual | Branch isolada da auditoria | `audit/cold-wallet-security-architecture-20260907` | APROVADO |
| HEAD | Base estabilizada `5374c1c...` | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | APROVADO |
| Base original informada | `5374c1c...` | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | APROVADO |
| `main` local | Não atualizar; apenas observar | `5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f` | APROVADO |
| Diferença HEAD/base original | Nenhuma | Nenhuma | APROVADO |
| Diferença HEAD/`main` | Nenhuma | Nenhuma | APROVADO |
| Diferença base original/`main` | Nenhuma | Nenhuma | APROVADO |
| Upstream da branch | Registrar, sem configurar | Nenhum upstream configurado | APROVADO COM RESSALVA |
| Worktrees | Não haver worktree concorrente registrado | Um worktree, nesta raiz, nesta branch e HEAD | APROVADO |
| Branch exigida original | Preservar sem sobrescrever | `audit/cold-wallet-security-architecture` em `5dfe0781479829655d9177cded7e4e7ca6c3ba7d` | APROVADO |
| Baseline SHA-256 | `f4170979c73aa04ab2238e5eb3b621ad7fba7c4b789891abad995f7e5cec7dea` | `f4170979c73aa04ab2238e5eb3b621ad7fba7c4b789891abad995f7e5cec7dea` | APROVADO |
| Baseline alterado externamente | Não | Conteúdo/checksum idênticos ao encerramento da Fase Zero | APROVADO |
| Worktree antes deste relatório | Somente baseline intencional | `?? audit_output/00-baseline.md` | APROVADO |
| Arquivos de origem desconhecida | Nenhum | Nenhum | APROVADO |

## Evidência de comandos

Foram executadas apenas operações Git e de hashing somente leitura:

- `git rev-parse --show-toplevel`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git status --short --branch --untracked-files=all`
- `git rev-parse --abbrev-ref --symbolic-full-name @{upstream}`
- `git worktree list --porcelain`
- `git branch -vv --list 'main' 'audit/*'`
- `git rev-parse main`
- `git diff --stat` entre HEAD, base original e `main`
- `sha256sum audit_output/00-baseline.md`

## Interferência anterior e efeito no baseline

Na Fase Zero, outro processo realizou checkout para `main` e reset para `origin/main`. Essa interferência ocorreu antes da criação do baseline atual e está registrada no próprio relatório. Não houve nova alteração entre o encerramento da Fase Zero e este gate.

O baseline anterior **não está invalidado** para esta base porque:

1. o SHA de base informado, o HEAD atual e `main` são idênticos;
2. não há diferença Git entre esses três pontos;
3. o checksum do relatório é idêntico ao informado;
4. o único arquivo existente fora do commit-base era o baseline deliberado.

A ressalva permanece operacional: a sincronização externa já demonstrou capacidade de trocar checkout/resetar o worktree. Antes de cada lote de escrita e antes de cada commit devem ser reconfirmados branch, HEAD e status. Se qualquer um mudar, as alterações param imediatamente.

## Restrições durante o gate

- Nenhum teste foi executado.
- Nenhum processo, porta, container, rede, volume ou arquivo temporário foi criado.
- Nenhuma rede externa foi usada.
- Nenhum diretório de carteira, segredo ou backup foi acessado.
- Nenhuma branch foi trocada, e `main` não foi atualizado.
- Nenhum merge, rebase, reset, stash, cherry-pick ou push foi realizado.
