# Fluxos de dados e segredos

## Dashboard — ciclo da chave

| Etapa | BTC | ETH | Resíduo/observação |
|---|---|---|---|
| Criação | `bit.Key()` | `Account.create()` | objeto permanece até GC/fim do request/processo; sem zeroização confiável |
| Resposta HTTP | campo `wif` | campo `private_key` | JSON cru sobre localhost sem autenticação |
| DOM | input/value/string HTML | input/value/string HTML | sidebar persiste enquanto página/processo mantém estado |
| Clipboard | botão Copy | botão Copy | clipboard é global; não há limpeza confiável |
| Entrada de envio | JSON `wif` | JSON `private_key` | browser → Dashboard; pode existir em devtools/memória |
| Consulta online | chave deriva endereço no processo com sessão Tor ativa | idem | segredo não é enviado ao RPC, mas está no host/processo online |
| Persistência | `generated/*.json`, `address_pool/**/*.json` | mesmos locais | plaintext, modo herdado, write não atômico |
| Logs/erros | logging reduz rota `send`, mas `str(e)` retorna ao cliente | idem | não há redactor central; risco indireto |
| Encerramento | processo/GC | processo/GC | arquivos, clipboard, browser/devtools e swap podem persistir |

Quem pode acessar depende das ACLs herdadas do diretório Windows; o código não aplica ACL restritiva. Não há remoção segura comprovável, e SSD não oferece garantia de overwrite.

## Verdade assinável Bitcoin

| Dado | Origem | Validação atual | Comparação | Risco |
|---|---|---|---|---|
| UTXO/txid/vout | API pública ou usuário | presença/tipos parciais | nenhuma | outpoint falso/gasto |
| Valor | API/usuário | inteiro implícito | nenhuma | output/fee calculados errados |
| `scriptPubKey` | segundo fetch ou usuário | presença | não confirma prevout nem ownership | assinatura inválida/perigosa |
| Confirmações | API | reduzido a 0/1 | nenhuma | reorg/unconfirmed ignorado |
| Fee rate | mempool.space/usuário | `int`, sem bounds | nenhuma | fee extrema/negativa |
| Estado de gasto | resposta UTXO | não revalidado antes do broadcast | nenhuma | double-spend/conflito |
| Vsize | tabela por tipo declarado | estimativa | não mede tx final | fee rate efetiva divergente |

O signer deve receber PSBT e validar cada prevout, script, valor, rede, derivação/ownership, sighash, outputs, fee absoluta e fee rate. Fonte remota não deve ser autoridade única.

## Verdade assinável Ethereum

| Dado | Origem | Validação atual | Comparação | Risco |
|---|---|---|---|---|
| Saldo | primeiro RPC | parse hex | nenhuma | send-all errado |
| Nonce | `latest` | parse hex | nenhuma | ignora pendentes/conflitos |
| Chain ID | constante local `1` | não consulta RPC | nenhuma | rede/UI podem divergir |
| Gas limit | constante `21000`/usuário | bounds ausentes | nenhuma estimativa | falha para contratos/dados |
| Base/priority/max fee | `feeHistory` ou `gasPrice` | estrutura parcial | nenhuma | fee abusiva/inconsistente |
| Tipo | type 2 ou fallback legacy | fallback implícito | confirmação não é renovada | mudança de semântica |
| Destino/self-send/data | usuário | formato/checksum degradável | sem política | gasto inútil/contrato inesperado |

O coordinator deve consultar `eth_chainId`, nonce `pending`, múltiplas fontes ou Helios identificado, aplicar bounds e gerar envelope canônico. O signer recalcula endereço de origem, hash e resumo e recusa campos ausentes/extra.

## Classificações corretas

- **Cold wallet:** chave criada/mantida fora de sistemas online; não descreve o Dashboard.
- **Air-gapped:** separação física persistente; `netsh` não a fornece.
- **Offline signing:** signer temporariamente sem rede; possível apenas como alegação limitada do CLI.
- **Watch-only:** não contém material capaz de assinar; arquitetura-alvo do Dashboard.
- **Hot wallet:** chave em host/processo online; estado atual do Dashboard e `enviar_*` sem isolamento.
- **Warm wallet:** controles adicionais, ainda conectável; descrição possível do CLI no mesmo Windows.
- **Tor:** privacidade de transporte, não integridade blockchain nem segredo local.
- **Helios:** verificação light-client apenas no caminho comprovado; não se transfere ao proxy público.
