# C8 native Windows validation handoff

These scripts prepare, but do not replace, execution on the intended native
Windows 10/11 host. Run them from a fresh clone of the published `main` branch
after the C9.1 pull request has been squash-merged. Neither script downloads
software, changes the firewall, changes adapters, installs a service, starts
Tor/Helios/Bitcoin Core, or uses a blockchain network.

1. Create a new clone of the official repository and synchronize references:

   ```powershell
   git clone https://github.com/MHX-Digital/cold-wallets.git cold-wallets-c91
   cd .\cold-wallets-c91
   git fetch --prune origin
   git checkout main
   git rev-parse main
   git rev-parse origin/main
   ```

   Stop unless `main` and `origin/main` print the same 40-character SHA.
2. Obtain the SHA published on `main` after the C9.1 squash merge. Review
   `c8-preflight.ps1`, then run it without elevation from the clean clone. The
   expected HEAD is supplied externally and is never hardcoded into the script:

   ```powershell
   & .\validation\windows\c8-preflight.ps1 `
     -ExpectedHead '<SHA FINAL DA MAIN APOS PR C9.1>' `
     -ExpectedBranch 'main'
   ```

   Preserve its redacted JSON as the Windows baseline. Stop if `nativeWindows`
   is not true, the branch is not `main`, `HEAD`, `refs/heads/main`, and
   `refs/remotes/origin/main` do not all equal the supplied SHA, the origin
   remote is not the official repository, the worktree is dirty, another
   worktree exists, Defender is unexpectedly disabled, or a required port
   belongs to a preexisting process. Manifest 59 is the current operational
   checksum manifest. Manifest 57 is historical evidence authenticated by
   manifest 59, not an instruction to revalidate superseded file versions.
3. Generate Windows locks only on the exact CPython/Windows/AMD64 target, review
   every resolved artifact and hash, and populate a run-specific wheelhouse from
   official sources. Do not reuse the Linux locks.
4. Review `c8-python-matrix.ps1`. For each interpreter that is actually
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
     -ExpectedTestCount 89
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
     -ExpectedTestCount 89
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
     -ExpectedTestCount 89
   ```

   The harness rejects a missing or ambiguous `Ran N tests` conclusion, a count
   other than 89, and any skip, failure, or error. It installs only into its
   unique temporary virtualenv with `--isolated --no-index --require-hashes`,
   restores every modified process environment variable, and removes only its
   validated `cold-wallets-c8-<run-id>` directory in `finally`.
5. Execute operational Tor, regtest and Helios stages separately. Each stage must
   have its own run-id, manifest, preflight inventory, exact PIDs/ports, and
   teardown evidence. Never combine a failed provenance check with execution.
6. Do not promote Helios beyond `HELIOS_UNATTESTED` unless all eight repository
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
