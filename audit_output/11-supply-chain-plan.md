# Plano de supply chain

Instalação em runtime e downloads automáticos de Tor são riscos de execução não reproduzível. Sem hash oficial verificado disponível no repositório, o download automático deve ser bloqueado e substituído por procedimento manual auditável: fonte oficial, versão fixa, SHA-256 publicado independentemente, assinatura quando disponível, validação antes da execução e rollback documentado.

Dependências devem migrar para arquivo versionado/lockfile com hashes e instalação explícita (inclusive modo offline). Nenhum pacote ou binário foi baixado ou instalado neste ciclo.
