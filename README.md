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
- Legacy combined generation/sign/send scripts are unsafe and pending physical
  removal where repository permissions currently prevent editing them.

## Start the watch-only Dashboard

After creating a reviewed environment, run `start.bat`. It starts only
`dashboard/server.py` in the foreground on `127.0.0.1:8888`. It does not elevate
privileges, install packages, start Tor, change the firewall/network, sign, or
broadcast.

The only active API is `POST /api/status`, protected by strict Host/Origin,
an ephemeral session token, JSON/content limits, and exact routing. Unknown
routes return 404 and unsupported methods return 405.

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

Detailed evidence and remaining blockers are under `audit_output/`.
