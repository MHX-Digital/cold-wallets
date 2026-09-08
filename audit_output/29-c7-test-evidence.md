# C7 test evidence

## Executed

| Command/suite | Result | Invariant |
|---|---|---|
| initial system unittest discovery | 48 run; four dependency-gated skips; pass | C6 baseline and zero residue |
| architecture suite after quarantine | 7/7 pass | all 38 Windows legacy scripts denylisted and unreachable from launcher/UI |
| Dashboard local API suite | 9/9 pass | exact routes, token/Host/Origin, secrets rejected, idempotency and cleanup |
| final system unittest discovery | 57 run; six skip events; pass | API/UI/storage fail-closed and complete regression |
| `git diff --check` checkpoints | pass | patch formatting |

The final full suite used loopback port 33367 and reported zero processes,
containers, networks, volumes, and residue. No external network, Tor, Helios,
Docker, Bitcoin Core, RPC, wallet, broadcast, or administrator command was used.

## Limitations

The environment lacks `eth-account`, `embit`, and PyCryptodome. Consequently,
the previously verified C6 real Ethereum/PSBT cases and the new real AES-GCM
round-trip/backup cases were dependency-gated. The storage unavailable-backend
contract passed and fails closed. This cycle does not claim real primitive
validation until the hash-locked suite is executed again.
