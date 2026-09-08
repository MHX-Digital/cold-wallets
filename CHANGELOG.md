# Changelog

All notable project changes will be recorded here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project intends
to use semantic versioning after a stable API exists.

## [Unreleased]

### Fixed

- Corrected the native Windows handoff after the C9 squash merge so preflight
  validation targets `main`, uses the post-merge SHA supplied by the operator,
  and treats checksum manifest 57 as historical evidence authenticated by the
  new operational manifest 59.
- Closed short-lived SQLite connections explicitly so Windows test cleanup can
  remove run-owned temporary database files.

## [0.1.0-alpha.1] - 2026-09-08

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
