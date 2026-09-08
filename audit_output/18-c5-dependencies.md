# Dependências C5

Escopo validado: CPython 3.12.3, Linux x86_64. Não implica validação Windows ou Python 3.10/3.14.

| Pacote | Versão | Origem | Licença | Python | Hashes | Finalidade | Risco |
|---|---:|---|---|---|---|---|---|
| eth-account | 0.14.0 | PyPI/ApeWorX | MIT | 3.10–3.14 declarado | wheel fixada | type-2 signing/recovery | classificador Alpha; ampla árvore transitiva |
| requests | 2.34.2 | PyPI/PSF | Apache-2.0 | >=3.10 | wheel fixada | adapter HTTP | somente permitido no adapter central |
| PySocks | 1.7.1 | PyPI/Anorov | BSD | metadata antiga | wheel fixada | SOCKS5h | última release 2019; risco de manutenção |
| embit | 0.8.0 | PyPI/stepansnigirev | MIT | Python 3 | sdist fixado | PSBT v0/P2WPKH | release 2024; sdist inclui binários prebuilt; build wheel não bit-reproduzível |

Todos os 29 pacotes runtime transitivos estão fixados com o hash do artefato instalado em `requirements/runtime-py312-linux.lock`. `setuptools` e `wheel` estão separados no lock de build. O lock PSBT fixa o sdist oficial e é instalado offline com `--no-build-isolation` após o lock de build.

Fontes primárias: `https://pypi.org/project/eth-account/0.14.0/`, `https://pypi.org/project/requests/`, `https://pypi.org/project/PySocks/`, `https://pypi.org/project/embit/`.
