# Reproducible dependency locks

The only verified lock in this checkout targets Linux x86-64, CPython 3.12. It
must be installed in a dedicated virtual environment with:

```text
python -m pip install --require-hashes -r requirements/runtime-py312-linux.lock
```

The PSBT package is distributed only as an sdist. Install its build tools from
`build-py312.lock`, verify the sdist SHA-256 in `psbt-py312-linux.lock`, and do
not enable Bitcoin signing unless `signer.psbt_backend` reports an approved
backend.

Windows x86-64 locks for CPython 3.10, 3.12, and 3.14 are intentionally absent.
They must be generated and tested on each real Windows interpreter; a Linux
lock must never be copied or renamed. Run `generate-windows-lock.ps1` manually
on the target Windows host after reviewing and installing `pip-tools` in an
isolated build environment. Committing a generated lock requires a clean-room
install with `--require-hashes`, backend diagnostics, and the complete test
suite on that exact interpreter.
