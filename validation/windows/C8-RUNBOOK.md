# C8 native Windows validation handoff

These scripts prepare, but do not replace, execution on the intended native
Windows 10/11 host. Run them from a reviewed checkout at the expected C8 commit.
Neither script downloads software, changes the firewall, changes adapters,
installs a service, starts Tor/Helios/Bitcoin Core, or uses a blockchain network.

1. After the checkpoint commit has been pushed, obtain the exact HEAD from the
   remote audit branch and PR #1. Review `c8-preflight.ps1`, then run it without
   elevation from the clean clone. Replace the single value shown below with
   that published 40-character SHA. The expected HEAD is supplied externally
   and is never hardcoded into the script:

   ```powershell
   & .\validation\windows\c8-preflight.ps1 `
     -ExpectedHead '<HEAD FINAL PUBLICADO>' `
     -ExpectedMain '5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f'
   ```

   Preserve its redacted JSON as the Windows baseline. Stop if `nativeWindows`
   is not true, branch/HEAD/main differ, the worktree is dirty, another worktree
   exists, any entry in the current checkpoint manifest 54 fails, Defender is
   unexpectedly disabled, or a required port belongs to a preexisting process.
   Manifest 54 authenticates the immutable historical manifests 50 and 52 as
   well as the current handoff files; the historical manifests are evidence,
   not instructions to validate superseded file versions directly.
2. Generate Windows locks only on the exact CPython/Windows/AMD64 target, review
   every resolved artifact and hash, and populate a run-specific wheelhouse from
   official sources. Do not reuse the Linux locks.
3. Review `c8-python-matrix.ps1`. For each interpreter that is actually
   installed, invoke exactly one matching command below. The lock and manifest
   files must already exist under repository `requirements/`; each wheelhouse
   is a preverified local directory and must contain exactly the files in its
   manifest.

   CPython 3.10 / Windows AMD64:

   ```powershell
   & .\validation\windows\c8-python-matrix.ps1 `
     -RepoRoot (Get-Location).Path `
     -PythonExecutable 'C:\Python310\python.exe' `
     -PythonVersion '3.10' `
     -RuntimeLock '.\requirements\runtime-py310-windows-amd64.lock' `
     -BuildLock '.\requirements\build-py310-windows-amd64.lock' `
     -PsbtLock '.\requirements\psbt-py310-windows-amd64.lock' `
     -Wheelhouse 'C:\ColdWallets-C8\wheelhouse-py310' `
     -WheelhouseManifest '.\requirements\wheelhouse-py310-windows-amd64.json' `
     -ExpectedTestCount 83
   ```

   CPython 3.12 / Windows AMD64:

   ```powershell
   & .\validation\windows\c8-python-matrix.ps1 `
     -RepoRoot (Get-Location).Path `
     -PythonExecutable 'C:\Python312\python.exe' `
     -PythonVersion '3.12' `
     -RuntimeLock '.\requirements\runtime-py312-windows-amd64.lock' `
     -BuildLock '.\requirements\build-py312-windows-amd64.lock' `
     -PsbtLock '.\requirements\psbt-py312-windows-amd64.lock' `
     -Wheelhouse 'C:\ColdWallets-C8\wheelhouse-py312' `
     -WheelhouseManifest '.\requirements\wheelhouse-py312-windows-amd64.json' `
     -ExpectedTestCount 83
   ```

   CPython 3.14 / Windows AMD64:

   ```powershell
   & .\validation\windows\c8-python-matrix.ps1 `
     -RepoRoot (Get-Location).Path `
     -PythonExecutable 'C:\Python314\python.exe' `
     -PythonVersion '3.14' `
     -RuntimeLock '.\requirements\runtime-py314-windows-amd64.lock' `
     -BuildLock '.\requirements\build-py314-windows-amd64.lock' `
     -PsbtLock '.\requirements\psbt-py314-windows-amd64.lock' `
     -Wheelhouse 'C:\ColdWallets-C8\wheelhouse-py314' `
     -WheelhouseManifest '.\requirements\wheelhouse-py314-windows-amd64.json' `
     -ExpectedTestCount 83
   ```

   The harness rejects a missing or ambiguous `Ran N tests` conclusion, a count
   other than 83, and any skip, failure, or error. It installs only into its
   unique temporary virtualenv with `--isolated --no-index --require-hashes`,
   restores every modified process environment variable, and removes only its
   validated `cold-wallets-c8-<run-id>` directory in `finally`.
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
