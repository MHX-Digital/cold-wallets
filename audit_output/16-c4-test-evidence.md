# Evidência C4

Suíte consolidada: `env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 32/32 testes aprovados em 0,365 s. Run-id HTTP `b2800e3e503144438700ae372f491fd8`, porta 43049 liberada, processos/containers/redes/volumes/resíduos zero. `git diff --check` aprovado.

Invariantes verificadas: Dashboard sem imports/rotas secretas; confirmação Ethereum vinculada ao proposalId; política de custo inteira; ausência estrutural de rede no signer; artefatos atômicos confinados à raiz; SOCKS5h/HTTPS/sem redirect e sem `trust_env`; ledger SQLite único, concorrente, persistente e com transições/retries; instalação e download Tor automáticos bloqueados.

Limitações: `eth-account` não existe no ambiente, portanto assinatura/recovery real não foi executada. Nenhuma biblioteca PSBT está instalada. Chamadas legadas fora dos novos componentes ainda não foram migradas ao adapter.
