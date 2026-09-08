# Evidências C5

- Ambiente: CPython 3.12.3/Linux x86_64; raiz temporária `/tmp/cold-wallets-c5-Um6vIJ`.
- Instalação runtime offline repetida em virtualenv novo com `--no-index --require-hashes`: aprovada.
- Build tools e embit instalados offline com hashes e `--no-build-isolation`: aprovado.
- Ethereum: assinatura EIP-1559 real, endereço público do escalar 1, recovery e Keccak independente: aprovado; socket substituído por função bloqueadora durante signing.
- Bitcoin: PSBT v0 P2WPKH sintética com prevout completo, fee, output, confirmação, signing e finalização: aprovado.
- Rede: AST confirma `requests` somente em `transport/requests_client.py`.
- Broadcast/disposable/storage: SQLite/fakes/fixtures exclusivamente temporários.

Python 3.10, 3.11, 3.13, 3.14 e Windows não foram testados por indisponibilidade local.
