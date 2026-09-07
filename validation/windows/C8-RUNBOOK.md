# C8 native Windows validation handoff

These scripts prepare, but do not replace, execution on the intended native
Windows 10/11 host. Run them from a reviewed checkout at the expected C8 commit.
Neither script downloads software, changes the firewall, changes adapters,
installs a service, starts Tor/Helios/Bitcoin Core, or uses a blockchain network.

1. Confirm the exact SHA published for the audit branch, review
   `c8-preflight.ps1`, then run it without elevation from the clean clone. The
   expected HEAD is supplied externally and is never hardcoded into the script:

   ```powershell
   & .\validation\windows\c8-preflight.ps1 `
     -ExpectedHead '<C8.2_REMOTE_HEAD>' `
     -ExpectedMain '5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f'
   ```

   Preserve its redacted JSON as the Windows baseline. Stop if `nativeWindows`
   is not true, branch/HEAD/main differ, the worktree is dirty, another worktree
   exists, any entry in `audit_output/50-c81-checksums.txt` fails, Defender is
   unexpectedly disabled, or a required port belongs to a preexisting process.
2. Generate Windows locks only on the exact CPython/Windows/AMD64 target, review
   every resolved artifact and hash, and populate a run-specific wheelhouse from
   official sources. Do not reuse the Linux locks.
3. Review `c8-python-matrix.ps1`. Invoke it with an explicit interpreter, three
   matching Windows locks, a preverified wheelhouse, and its JSON manifest stored
   under repository `requirements/`. The manifest must enumerate every
   wheelhouse filename and SHA-256; extra, missing, nested or reparse-point items
   fail closed. It installs only into its unique temporary virtualenv with
   `--isolated --no-index --require-hashes`, restores every modified process
   environment variable, and removes only its validated run directory in
   `finally`.
4. Execute operational Tor, regtest and Helios stages separately. Each stage must
   have its own run-id, manifest, preflight inventory, exact PIDs/ports, and
   teardown evidence. Never combine a failed provenance check with execution.
5. Do not promote Helios beyond `HELIOS_UNATTESTED` unless all eight repository
   attestation requirements are independently evidenced. Regtest interoperability
   may promote Bitcoin only to `VALIDATED_INTEROPERABILITY`.

## Manual physical air-gap checklist

Automated socket denial proves logical isolation only. A physical air gap needs
a dedicated signer device with radios and wired networking physically absent or
disabled by an independently inspected procedure, no shared online filesystem,
reviewed removable-media handling, verified offline dependencies, controlled
boot media, and a human comparison of network, destination, value, nonce and
maximum fee before confirmation. Record this separately; never infer it from a
passing unit test.
