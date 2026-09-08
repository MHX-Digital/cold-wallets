# Cold Wallets

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Status: experimental](https://img.shields.io/badge/status-experimental-orange.svg)

Experimental offline-first Bitcoin and Ethereum coordinator/signer toolkit with
a watch-only Dashboard, versioned artifacts, and privacy-focused transport.

> [!CAUTION]
> **EXPERIMENTAL — NO-GO FOR REAL FUNDS.** This software has not completed
> native Windows, Tor, Helios, or Bitcoin Core regtest validation. Do not use it
> with a funded key, wallet, transaction, or production system.

## Project status

The repository is an auditable security-architecture prototype. Local Linux
tests validate important contracts, but they do not prove a physical air gap,
host integrity, operational Tor routing, Ethereum consensus, or production
Bitcoin signing. Remote broadcast is disabled and no stable release exists.

## Architecture

```text
online watch-only coordinator
        ↓ versioned unsigned artifact
controlled transfer
        ↓
offline signer
        ↓ signed artifact (never the key)
controlled transfer
        ↓
online validator / persistent broadcaster
```

The browser Dashboard talks only to coordinator application services. It cannot
import or generate keys, invoke a signer, start Tor, or perform remote
broadcast. Ethereum and Bitcoin signing components are separate processes or
modules intended for an explicitly offline host.

## Trust boundaries

- **Dashboard → coordinator:** local HTTP still requires Host, Origin, ephemeral
  token, strict schema, body limit, exact route, and idempotency checks.
- **Coordinator → remote data:** balances, UTXOs, nonces, fees, gas, and RPC
  responses remain potentially malicious unless independently verified.
- **Coordinator → signer:** an unsigned artifact is untrusted input. The signer
  recalculates policy-critical values and binds confirmation to its hash.
- **Signer → broadcaster:** signed transactions contain no private key, but are
  sensitive financial metadata and must not be logged casually.
- **Application → Tor:** the central adapter is statically fail-closed; real Tor
  routing and absence of clearnet fallback have not yet been observed on the
  Windows target.
- **Host and storage:** localhost, encryption at rest, and Python process
  isolation do not protect against a compromised operating system.

See [the threat model](audit_output/01-threat-model.md) and
[architecture map](audit_output/02-architecture-map.md).

## Implemented functionality

- Watch-only Dashboard and coordinator workflow API.
- Canonical Ethereum type-2 proposal envelope and offline EIP-1559 signing.
- Sender recovery and confirmation bound to proposal identity.
- Versioned, size-limited artifact transport with atomic writes.
- Persistent SQLite broadcaster state, idempotency, uncertain-result handling,
  and fake-RPC integration tests.
- Transactional disposable-address lifecycle without private keys in its
  operational table.
- Authenticated synthetic storage using versioned scrypt and AES-256-GCM.
- Bitcoin PSBT v0 review for the narrow scope described below.
- Central Tor-only HTTP adapter with strict TLS, redirect, timeout, retry, and
  response-size policy.

## Blocked or unsupported functionality

- All real remote broadcast and any use with funds.
- Key generation, key import, or signing in the Dashboard.
- Bitcoin signing until the secp256k1 backend is reproducibly built and
  independently reviewed.
- P2PKH, P2SH-P2WPKH, Taproot, multisig, PSBT v2, change outputs, arbitrary
  scripts, alternate sighashes, and public testnet operation.
- Automatic downloads, runtime dependency installation, Tor/Helios startup,
  firewall changes, network-adapter control, deploy, and service installation.
- Claims that a public RPC is trustless or that a responding Helios port is
  attested.

## Verified platforms

| Platform | Status |
|---|---|
| Linux x86-64, CPython 3.12 | Hash-locked local suite verified |
| Windows 10/11, CPython 3.10 | Not tested |
| Windows 10/11, CPython 3.12 | Not tested |
| Windows 10/11, CPython 3.14 | Not tested |
| macOS | Not tested |

The Windows scripts under `validation/windows/` are a fail-closed handoff, not
evidence of Windows compatibility.

## Reproducible installation

Only the Linux x86-64 CPython 3.12 locks are currently verified. Create a fresh
virtualenv outside wallet directories and install exact hashes:

```bash
python3.12 -m venv /tmp/cold-wallets-reviewed-venv
/tmp/cold-wallets-reviewed-venv/bin/python -m pip install \
  --require-hashes -r requirements/build-py312.lock
/tmp/cold-wallets-reviewed-venv/bin/python -m pip install \
  --require-hashes -r requirements/runtime-py312-linux.lock
/tmp/cold-wallets-reviewed-venv/bin/python -m pip install \
  --no-build-isolation --require-hashes -r requirements/psbt-py312-linux.lock
```

This installation contacts the configured Python package index. For a stronger
workflow, first populate and verify an isolated wheelhouse from the locks, then
install into a second virtualenv using `--no-index --require-hashes`. See
[requirements documentation](requirements/README.md). Never install
automatically, globally, or from an unreviewed floating version.

## Running the watch-only Dashboard

On the target Windows host, set `COLD_WALLETS_PYTHON` to the absolute interpreter
inside the reviewed virtualenv. Set `COLD_WALLETS_COORDINATOR_STATE` to a new,
explicit non-wallet directory. Optionally select an unused loopback port with
`COLD_WALLETS_PORT`, then run `start.bat` without administrator privileges.

The launcher runs only `dashboard/server.py` in the foreground. It does not
install packages, download or start Tor, modify the firewall, disable adapters,
sign, broadcast, or start a background service. Follow the
[Windows runbook](validation/windows/C8-RUNBOOK.md) before using the Dashboard.

## Tests

Run the full suite without bytecode:

```bash
env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

Cryptographic integration tests require the exact hash-locked environment.
Tests use public vectors, ephemeral unfunded test keys, temporary per-run roots,
and fake RPCs. A passing suite is evidence for its named invariants only, not a
general security certification.

CI has two boundaries: the static integrity job performs no package download;
the dependency job contacts GitHub's hosted Python/action infrastructure and the
Python package index only to fetch artifacts constrained by committed hashes.
It then installs and tests from a local wheelhouse with `--no-index`. CI never
starts Tor, Helios, Bitcoin Core, Docker, or any deploy workflow.

## Bitcoin limitations

Bitcoin scope is mainnet PSBT v0, native SegWit P2WPKH, SIGHASH_ALL, send-all,
and exactly one destination output. Review and fee-policy validation are
implemented. Signing remains fail-closed because the observed `embit` native
backend identity is not proof of trustworthy provenance. Bitcoin Core regtest
interoperability and independent backend review remain pending.

## Ethereum limitations

Ethereum supports a canonical type-2 envelope, integer-only cost limits,
explicit chain policy, calldata denial by default, sender recovery, and offline
signing. Nonce, gas, balance, and fee inputs from a coordinator or RPC remain
untrusted inputs requiring policy and human confirmation. No Ethereum broadcast
or Helios attestation is enabled.

## Tor and Helios limitations

Tor improves transport privacy; it does not make an online signer cold, protect
against local malware, or validate blockchain data. The adapter requires a
configured `socks5h` proxy and has no direct fallback, but operational Windows
capture is still pending.

RPC identity is explicit:

- `PUBLIC_RPC_UNVERIFIED`: provider data is trusted, not consensus-verified.
- `HELIOS_UNATTESTED`: a Helios claim lacks complete operational evidence.
- `HELIOS_ATTESTED`: reserved for eight independently verified process,
  artifact, configuration, chain, checkpoint, health, response, and exclusive
  route facts.

An open port or HTTP 200 is never sufficient for `HELIOS_ATTESTED`.

## Roadmap

1. Validate the full matrix on native Windows without administrative changes.
2. Verify Tor provenance, SOCKS routing, remote DNS, and fail-closed behavior.
3. Validate PSBT interoperability with Bitcoin Core exclusively in regtest.
4. Reproduce and independently review the Bitcoin cryptographic backend.
5. Exercise Helios attestation or keep the path explicitly blocked.
6. Obtain independent security review before considering any limited pilot.

## Contributing and support

Read [CONTRIBUTING.md](CONTRIBUTING.md), the
[Code of Conduct](CODE_OF_CONDUCT.md), and [SUPPORT.md](SUPPORT.md). Security
reports must use the private process in [SECURITY.md](SECURITY.md), never a
public issue.

## License and unofficial projects

The source code is distributed under the [MIT License](LICENSE). MIT permits
third parties to use, modify, distribute, sublicense, sell, and deploy copies.
Such forks and deployments are not official or endorsed by MHX Digital.

The MIT software license does not grant rights to the “Cold Wallets” name,
visual identity, official domains, or official hosted services as trademarks or
indications of endorsement. The software is provided without warranty and is
not approved for real funds.

## Audit evidence

The complete staged audit reports and reproducible evidence are preserved under
[`audit_output/`](audit_output/). See [CHANGELOG.md](CHANGELOG.md) for the
release-oriented summary. Documentation is evidence only when it matches the
executable code and tests.
