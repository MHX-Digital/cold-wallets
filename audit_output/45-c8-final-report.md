# C8 final report

Product: **NO-GO**. Gate C8-G0 and C8-G1: **BLOCKED**.

The repository reference was exact and stable, but the execution host was native
Linux rather than the required Windows 10/11 machine. Per the explicit safety
gate, no Linux simulation and no operational Tor, Helios, Docker, Bitcoin Core,
RPC, broadcast, network, or administrative action was performed.

The independent work completed in this cycle is deliberately preparatory:

- a native-Windows-only redacted preflight inventories Git/checksums, host,
  privileges, Defender, tools, relevant processes/listeners, adapters, volumes
  and preexisting containers without changing the host;
- an explicit-interpreter matrix harness refuses missing/mismatched Windows
  locks, installs only from a preverified wheelhouse using `--no-index` and
  `--require-hashes`, rejects relevant skips, and removes only its run root;
- `start.bat` now requires an explicit isolated virtualenv instead of silently
  falling back to global Python;
- the Dashboard port is configurable and strictly bounded, allowing an occupied
  8888 to remain untouched;
- the runbook separates logical signer isolation from a physical air gap and
  preserves honest Bitcoin/Helios classifications.

Static/pure checks passed 14/14. This does not advance CW-004, CW-005, CW-009,
CW-012, CW-016, CW-017, CW-019, CW-020 or CW-022 beyond their prior operational
limits. Native execution, Windows lock creation, Tor routing observation,
regtest interoperability, Helios attestation, ACL/interruption testing and
synthetic-media recovery remain required. The product remains prohibited for
real funds.
