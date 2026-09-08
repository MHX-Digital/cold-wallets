# Desenho Coordinator/Signer/Broadcaster

O Dashboard será somente coordinator online/watch-only. Ele consulta fontes externas via adapters, constrói propostas e exporta artefatos; não importa módulos de geração, leitura ou assinatura de chaves.

Fluxo controlado: `proposal → transferência manual verificável → signer offline → signed artifact → transferência → broadcaster`. O signer não possui clientes HTTP/RPC, Tor ou subprocessos de rede. O broadcaster aceita apenas artefato assinado, valida rede e hash operacional e aplica idempotência persistente.

Fronteiras: arquivos são versionados, limitados, hash SHA-256 e escritos atomicamente; confirmação humana ocorre no signer a partir do artefato, nunca do resumo do coordinator. Chaves permanecem exclusivamente no ambiente offline.

Migração incremental: remover alcançabilidade de código secreto do Dashboard; introduzir contratos compartilhados puros; adicionar PSBT/envelope; somente depois conectar adapters e broadcaster real. Até a conclusão, produto permanece NO-GO.
