param(
    [Parameter(Mandatory=$true)][ValidateSet('3.10','3.12','3.14')][string]$PythonVersion,
    [Parameter(Mandatory=$true)][string]$PythonExe
)
$ErrorActionPreference = 'Stop'
$actual = & $PythonExe -c "import platform,sys; print(f'{sys.version_info.major}.{sys.version_info.minor}|{platform.system()}|{platform.machine()}')"
$expected = "$PythonVersion|Windows|AMD64"
if ($actual -ne $expected) { throw "Target mismatch: expected $expected, observed $actual" }
$output = Join-Path $PSScriptRoot "runtime-py$($PythonVersion.Replace('.',''))-windows-amd64.lock"
if (Test-Path $output) { throw "Refusing to overwrite existing lock: $output" }
& $PythonExe -m piptools compile --generate-hashes --resolver backtracking --output-file $output (Join-Path $PSScriptRoot 'runtime.in')
if ($LASTEXITCODE -ne 0) { throw 'Lock generation failed' }
Write-Host "Generated $output. It is UNVERIFIED until clean-room installation and tests pass."
