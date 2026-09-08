# C6 final report

Result: **NO-GO**. Gate C6-G1: **BLOCKED**.

Implemented code, not only design: evidence-based PSBT backend blocking; narrower
mainnet P2WPKH PSBT validation; atomic binary PSBT transport; real EIP-1559 decode,
signature recovery, transaction-hash derivation and persistent fake-RPC broadcast;
proposal/disposable/broadcast stores integrated behind a watch-only coordinator;
explicit RPC identity; unprivileged foreground launcher; and reachable network
entrypoints blocked where filesystem permissions allowed.

The Ethereum local end-to-end flow passes. Bitcoin end-to-end intentionally stops
at the signing gate because its cryptographic backend is unapproved. Physical
legacy removal and Windows/Tor/Helios/regtest validation remain required.

The checkout also contains mixed filesystem ownership. This prevented edits to
the legacy tree and caused one local Git object-write collision; no ownership or
permission was changed by the audit.
