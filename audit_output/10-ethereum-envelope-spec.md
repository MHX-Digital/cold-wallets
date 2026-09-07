# Envelope Ethereum canônico v1

Campos obrigatórios: `schema="cold-wallets.eth-tx"`, `version=1`, `network`, `chainId`, `type="2"`, `from`, `to`, `valueWei`, `nonce`, `gasLimit`, `maxFeePerGasWei`, `maxPriorityFeePerGasWei`, `data`, `createdAt`, `expiresAt`, `proposalId`, `sources`.

Todos os inteiros são strings decimais canônicas (`0` ou sem zero à esquerda); floats, booleanos, negativos e propriedades desconhecidas são rejeitados. `data` é hex lowercase com prefixo `0x` e comprimento par. `type` deve ser exatamente `2`; `maxPriorityFeePerGasWei ≤ maxFeePerGasWei`; expiração deve ser futura no momento da validação. Endereços são validados estruturalmente e o signer deve confirmar checksum/derivação da chave.

`proposalId = sha256(UTF-8(json canônico, sort_keys, separators=(',',':')))` do conjunto determinístico de rede, chain, tipo, from/to, valor, nonce, gas, taxas e calldata. Timestamps e `sources` ficam fora do hash. Limites de tamanho e valores são aplicados antes da assinatura. O signer rederiva o hash, exibe resumo independente e exige confirmação explícita.
