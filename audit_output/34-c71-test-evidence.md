# C7.1 test and hygiene evidence

## Hash-locked environment

- Platform: Linux x86-64, CPython 3.12.3.
- Download virtualenv and test virtualenv were separate.
- Downloads were constrained by the committed locks and `--require-hashes`.
- The second environment was installed with `--no-index` from the temporary
  wheelhouse. The embit sdist was built with pinned build tools and
  `--no-build-isolation`.
- Critical artifact hashes matched the locks:
  - eth-account 0.14.0: `efdcb57f32f133e9152510e44772a4bcfe519317dfd8f7e7c5ead8189f73a2b6`
  - PyCryptodome 3.23.0: `c8987bd3307a39bc03df5c8e0e3d8be0c4c3518b7f044b0f4c15d1aa78f52575`
  - embit 0.8.0 sdist: `8bf4b10073c67400370ce523fb16f035fe759f6fdd987c579bdcc268d75ed770`

## Results

| Suite | Result | Invariant |
|---|---|---|
| focused real storage + signer | 12/12 pass, zero skips, 1.628 s | AES-GCM, backup/restore and real Ethereum signing/recovery |
| local Dashboard regression | 9/9 pass, zero skips, 0.601 s | Host/Origin/token/routes/secrets/idempotency |
| final hash-locked discovery | 73 run, 72 pass, 1 fail, zero skips, 3.521 s | all dependency-gated cases executed |
| architecture subset | 8 run, 7 pass, 1 fail | the only failure lists the 13 protected RPC files |
| `git diff --check` | pass | patch formatting |

The full failure is deliberate evidence, not a skipped test:
`test_legacy_paths_are_physically_absent` found exactly the 13 files remaining
under seven `nobody:nogroup` RPC subdirectories.

## Cryptographic storage invariants

The current version fixes scrypt to N=16384, r=8, p=1 and a 32-byte derived key.
The approximate ROMix memory parameter is 128 * N * r = 16 MiB per derivation.
Parameters are checked against policy before scrypt runs, preventing an artifact
from requesting unbounded work. AES-256-GCM uses a fresh 16-byte salt, 12-byte
nonce, 16-byte tag, and authenticates schema, version, KDF, cipher configuration,
and metadata as AAD. This is validated only for synthetic fixtures and is not an
approval to migrate real keys. Python memory zeroization is not guaranteed.

## Hygiene

Run roots `nuMjn9Sn`, `r1FcdQcO`, and `MJps95Ft` were removed by guarded traps.
The first embit build unexpectedly wrote one wheel and `origin.json` to an exact
global pip-cache leaf; that leaf and its three newly empty parent directories
were identified and specifically removed. Subsequent runs set `PIP_CACHE_DIR`
inside the run root and used `--no-cache-dir` for downloads.

No wallet, real backup, blockchain network, broadcast, Tor, Helios, Docker,
Bitcoin Core, administrator operation, container, network, or volume was used.
Test resource summaries reported zero residual processes and resources.
