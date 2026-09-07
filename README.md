# Cold Wallets

Experimental Bitcoin and Ethereum coordinator/signer toolkit. **NO-GO for real
funds.** The browser Dashboard is an online watch-only coordinator, not a cold
wallet. Tor protects transport metadata only; it does not make an online signer
safe or attest an RPC response.

## Current safe boundary

```text
online coordinator -> versioned unsigned artifact -> offline signer
offline signer -> signed artifact -> online validator/broadcaster
```

- The Dashboard cannot generate/import keys, sign, launch Tor, or broadcast.
- Ethereum type-2 signing is implemented in a separate network-free module and
  verified with recovery tests using a public test scalar.
- Real broadcast is disabled. Tests use only injected fake RPC services.
- Bitcoin is restricted to mainnet PSBT v0, native P2WPKH, SIGHASH_ALL,
  send-all, and exactly one destination output.
- Bitcoin signing is currently **disabled** because the native secp256k1 binary
  shipped in `embit` has not been independently reproduced or approved.
- P2PKH, wrapped SegWit, Taproot, multisig, PSBT v2, arbitrary scripts,
  alternate sighashes, change outputs, and production testnet are unsupported.
- Legacy combined key-generation/sign/send implementations and executable RPC,
  Tor, Helios, VPN, reverse-proxy and L2 configurations were removed. The RPC
  tree now contains only disabled, non-executable evidence contracts for future
  operational validation.

## Start the watch-only Dashboard

After creating a reviewed environment, run `start.bat`. It starts only
`dashboard/server.py` in the foreground on `127.0.0.1:8888`. It does not elevate
privileges, install packages, start Tor, change the firewall/network, sign, or
broadcast.

The watch-only API can prepare/export Ethereum proposals, import and validate
signed Ethereum artifacts, register them locally without remote transmission,
track state, reserve disposable addresses, and review narrow-scope Bitcoin
PSBTs. It cannot sign or remotely broadcast. Requests use strict Host/Origin,
an ephemeral token, schemas/body limits, exact routes, and persistent
idempotency records. Unknown routes return 404 and unsupported methods return
405. Set `COLD_WALLETS_COORDINATOR_STATE` to an explicit non-wallet directory
before launch; otherwise workflow routes fail closed with 503.

## Reproducible dependencies

The verified environment is CPython 3.12 on Linux x86-64 only:

```text
python -m venv <isolated-path>
<isolated-python> -m pip install --require-hashes -r requirements/runtime-py312-linux.lock
<isolated-python> -m pip install --require-hashes -r requirements/build-py312.lock
<isolated-python> -m pip install --require-hashes --no-build-isolation -r requirements/psbt-py312-linux.lock
```

See `requirements/README.md`. Windows CPython 3.10, 3.12, and 3.14 locks remain
pending generation and verification on those actual targets. The launchers never
install dependencies automatically.

## Trust labels

- `PUBLIC_RPC_UNVERIFIED`: public provider responses are trusted inputs.
- `HELIOS_UNATTESTED`: a claimed/local Helios path lacks complete evidence.
- `HELIOS_ATTESTED`: permitted only when process/image, version/digest,
  configuration, chain, checkpoint, health, coherent response, and exclusive
  routing have all been verified. An open port is insufficient.

No Helios or Tor service is started by the Dashboard. No flow is described as
trustless merely because it uses Tor or localhost.

The descriptors under `rpc/` are deliberately `UNATTESTED` and `enabled:false`.
They do not contain a runnable image, Tor configuration, checkpoint or upstream.

## Tests

Run without Python bytecode residue:

```text
env PYTHONDONTWRITEBYTECODE=1 python -m unittest discover -s tests -v
```

Cryptographic integration tests require the exact hash-locked environment.
Tests use temporary per-run directories, ephemeral keys with no funds, fake
RPCs, and no external blockchain or broadcast.

## Secret-storage limitations

Do not place real keys in the Dashboard, repository, clipboard, logs, or test
fixtures. Legacy plaintext wallet storage is not approved. The migration tooling
is metadata-only/dry-run and must not be pointed at real wallet directories during
testing. Python managed memory cannot guarantee key zeroization, and SSD secure
deletion is not promised. Use a physically separate offline host and validated
backup/recovery procedures.

`storage/authenticated.py` defines a versioned scrypt + AES-256-GCM format and
`storage/backup.py` provides checksum-bound, atomic restore into an authorized
root. Round-trip, tamper, wrong-password, downgrade and synthetic restore tests
are executed only in the hash-locked environment. This validates the format for
fixtures; it does not approve migration of real keys. If the reviewed
PyCryptodome backend is unavailable, storage fails closed with no custom cipher
fallback.

Detailed evidence and remaining blockers are under `audit_output/`.
