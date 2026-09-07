# C6 test evidence

## Environment

- Ubuntu/Linux x86-64; CPython 3.12.3.
- Isolated root: `/tmp/cold-wallets-c6-zeWV1U` (removed after evidence capture).
- Runtime dependencies installed with `--require-hashes` from the committed lock.
- `embit` sdist downloaded from official PyPI file URL; observed SHA-256:
  `8bf4b10073c67400370ce523fb16f035fe759f6fdd987c579bdcc268d75ed770`.
- Loaded embit backend: native Linux x86-64 prebuilt library, SHA-256
  `602c643b17d7d863e801d4a4eca12711b2724698d0e2d822711fd724cf9b74c1`;
  policy result: **unapproved; signing disabled**.

## Commands and results

| Command | Result | Duration / invariant |
|---|---|---|
| system `python3 -m unittest discover -s tests -v` | 44 run, 2 skipped, pass | 1.27 s; dependency-gated baseline, residue 0 |
| hash-locked venv full unittest discovery (final) | 59/59 pass | 2.60 s; Ethereum crypto and embit diagnostics enabled, residue 0 |
| focused PSBT + transport | 9/9 pass | 0.03 s; prevout consistency, scope, binary hash/atomic path |
| focused broadcaster/coordinator | 13/13 pass | 1.43 s; mutation, concurrency, restart, unknown/reconcile |
| `git diff --check` | pass at checkpoints | no whitespace errors |

No mainnet/testnet/regtest RPC, Tor, Docker, Helios, VPS, external broadcast, or
administrative command ran. The only test listener was loopback port `41539`,
created and released by the Dashboard fixture. Fake RPC objects were used for
all broadcast behavior. The final fixture used loopback port `44057`; its resource
summary reported processes, containers, networks, volumes, and residue all zero.

Public sources: [BIP174](https://github.com/bitcoin/bips/blob/master/bip-0174.mediawiki)
and [embit 0.8.0 on PyPI](https://pypi.org/project/embit/0.8.0/).
