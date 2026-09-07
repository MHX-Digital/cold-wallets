# Avaliação Bitcoin/PSBT

A dependência atual `bit` não fornece, no código auditado, uma fronteira PSBT BIP174/BIP370 comprovada. Não foi instalada dependência nem escrito parser manual. A adoção deve avaliar biblioteca madura (por exemplo, `embit` ou `python-bitcointx`) quanto a manutenção, licença, versões e suporte a SegWit, prevouts, sighash, finalização e campos desconhecidos.

Contrato requerido: coordinator produz PSBT e manifesto de rede/inputs/outputs/fee; signer revalida cada prevout, script, pertencimento da chave, outputs, fee/vsize, dust, RBF e send-all antes da confirmação humana. Para send-all, `fee = Σinputs − Σoutputs` é recalculado no signer. Ausência, truncamento, duplicidade, rede errada ou output inesperado falham fechado.

Status: **bloqueado para assinatura real** até dependência e vetores públicos serem aprovados. Nenhum broadcast foi realizado.
