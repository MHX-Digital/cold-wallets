# RPC transport status

No RPC, Tor, Helios, reverse proxy, VPN, L2 node, container, or remote broadcast
is launched by this repository. Runtime deployment configuration is intentionally
absent until a controlled operational validation supplies independently verified
artifacts and evidence.

The only valid identities are:

- `PUBLIC_RPC_UNVERIFIED`: provider responses are trusted inputs.
- `HELIOS_UNATTESTED`: Helios is claimed or planned but required evidence is
  incomplete. It must not be described as verified or trustless.
- `HELIOS_ATTESTED`: allowed only after process/image identity, version/digest,
  configuration, chain ID, checkpoint, health, coherent response, and exclusive
  routing have all been checked.

The JSON files below are non-executable evidence contracts. Both are disabled
and fail closed. They are not service configuration and must not be converted
into runnable files until the future Windows/Tor/Helios validation cycle.
