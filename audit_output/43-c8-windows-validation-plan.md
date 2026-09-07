# C8 native Windows execution plan

Status: **prepared, not executed**. The present host is Linux.

## Entry conditions

1. Checkout the expected audit branch and commit on the intended native Windows
   10/11 device without accessing any existing wallet directory.
2. Run `validation/windows/c8-preflight.ps1` unprivileged. It emits redacted JSON
   to stdout and performs only read-only inventory. Review Git, checksums,
   Defender, tools, relevant PIDs/listeners, adapters, volumes and containers.
3. Allocate one `cold-wallets-c8-<run-id>` root. Every later resource must be in
   its manifest and owned by that run.
4. Stop if a required port is occupied; choose another port rather than touching
   a preexisting process.

## Ordered operational stages

| Stage | Inputs | Mandatory proof | Cleanup |
|---|---|---|---|
| Python 3.10/3.12/3.14 | exact interpreter, target locks, verified wheelhouse | offline `--require-hashes`, full suite/no skip, backend identity | virtualenv, cache and wheelhouse owned by run |
| Launcher/filesystem | temporary coordinator state and ephemeral port | no UAC/install/download/background child; spaces/Unicode/ACL/replace/Ctrl+C | PID, port, state root |
| Offline signer | public vectors and ephemeral no-fund key | socket/DNS/process denial, proposal-bound confirmation, redacted output | signer PID and fixture root |
| Tor | verified official binary/config | app connects only to loopback SOCKS using `socks5h`; fail-closed after Tor stop | exact PID, port, datadir/config/log |
| Bitcoin regtest | verified Core binary and isolated regtest datadir | PSBT/fee/vsize/witness/txid interoperability; local-only broadcast | exact PID, RPC/P2P ports, wallet/datadir |
| Helios | verified digest/hash and generated temporary config | all eight attestation facts and exclusive route | owned container/network/volume/files |
| Backup/restore | synthetic fixture only | authenticated round-trip and adversarial interruption cases | temporary media/root and logs |

No stage may promote a later stage. In particular, a listening port is not
Helios attestation, a Core-accepted signature is not independent backend review,
logical socket denial is not a physical air gap, and fixture storage is not a
real-key migration.

## Windows Python matrix

Windows lockfiles do not exist yet. `c8-python-matrix.ps1` therefore fails
closed until target-specific runtime, build and PSBT locks plus a preverified
wheelhouse have been produced and reviewed. A version absent from the host is
`NOT TESTED`, not failed or approved.

## Separate Linux debt

Do not modify Linux ownership from Windows. The repository root and `.git`
remain mixed-owner, and two empty untracked L2 leaf directories remain. Any
future Linux correction must use an explicit inventory and `rmdir` only for
confirmed-empty directories; no recursive ownership or deletion command is
authorized.
