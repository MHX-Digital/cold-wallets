# Changelog

All notable project changes will be recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project intends
to use semantic versioning after a stable API exists.

## [Unreleased]

### Added

- Open source governance, vulnerability reporting guidance, CODEOWNERS, issue
  forms, pull request template, Dependabot configuration, and minimal CI.
- Audited coordinator/signer/broadcaster boundaries, versioned artifact
  transport, authenticated fixture storage, and reproducible Linux locks.

### Changed

- Dashboard is watch-only and remote broadcast remains blocked.
- Project status and unsupported functionality are documented explicitly.

### Removed

- Legacy online key generation/signing/sending paths, automatic dependency/Tor
  installation, administrative network scripts, and unsupported RPC stacks.

### Security

- Product remains **EXPERIMENTAL — NO-GO FOR REAL FUNDS**.
- Windows, Tor, Helios, and Bitcoin Core regtest operational validation remains
  pending.
