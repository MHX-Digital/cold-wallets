# C7.2 test evidence

## Reproducible environment

Linux x86-64, CPython 3.12.3. A download virtualenv populated a temporary
wheelhouse using committed locks and `--require-hashes`. A second virtualenv was
installed from that wheelhouse with `--no-index`; embit used pinned build tools
and `--no-build-isolation`. `PIP_CACHE_DIR` was confined to the run root.

Critical hashes matched the locks:

| Artifact | SHA-256 |
|---|---|
| eth-account 0.14.0 wheel | `efdcb57f32f133e9152510e44772a4bcfe519317dfd8f7e7c5ead8189f73a2b6` |
| PyCryptodome 3.23.0 wheel | `c8987bd3307a39bc03df5c8e0e3d8be0c4c3518b7f044b0f4c15d1aa78f52575` |
| embit 0.8.0 sdist | `8bf4b10073c67400370ce523fb16f035fe759f6fdd987c579bdcc268d75ed770` |

## Results

| Suite/check | Result | Duration / invariant |
|---|---|---|
| architecture before full suite | 9/9 pass | 0.183 s; actual filesystem and JSON semantics |
| full hash-locked discovery | 74/74 pass; zero skips/failures/errors | 3.354 s |
| resource harness | pass | port 41329; processes/containers/networks/volumes/residue all zero |
| `git diff --check` | pass | formatting |
| `git fsck --no-dangling` | pass | object integrity |

No Tor, Helios, Docker, Bitcoin Core, RPC, blockchain network, broadcast,
administrator operation, real wallet, or real backup was accessed.
