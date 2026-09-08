# Contributing

Cold Wallets is experimental security-sensitive software and remains NO-GO for
real funds. Contributions are welcome only when they preserve that boundary.

## Before changing code

Open an issue or discussion before architectural, cryptographic, persistence,
network, signing, or dependency changes. Base work on the current `main` and
keep each branch narrowly scoped. Security vulnerabilities must follow
[SECURITY.md](SECURITY.md), not a public issue.

## Required practices

- Use clear, reviewable commits and explain the invariant each change protects.
- Add deterministic tests and run the complete suite in an isolated environment.
- Use only public vectors, synthetic fixtures, and keys explicitly created for
  tests with no funds.
- Never access or commit a wallet, private key, seed, mnemonic, WIF, credential,
  raw production transaction, or identifying financial log.
- Never perform blockchain broadcast, mainnet activity, automatic installation,
  deployment, or privileged network changes as part of a contribution.
- Pin direct and transitive dependencies and require verified hashes.
- Give every test run a unique temporary root and remove only its owned
  processes, listeners, files, virtualenvs, caches, databases, and bytecode.
- Do not claim a security property without code-level and independent test
  evidence. Mocks must be identified as mocks.
- Update documentation and residual risks whenever behavior changes.

Pull requests require maintainer and CODEOWNER review. Passing CI is necessary
but not evidence that the software is safe for real funds.

## Developer Certificate of Origin

This project uses the [Developer Certificate of Origin 1.1](https://developercertificate.org/).
Sign off every commit with `git commit -s` to certify that you have the right to
submit the contribution. A `Signed-off-by:` line is a provenance statement, not
a cryptographic signature or security endorsement.
