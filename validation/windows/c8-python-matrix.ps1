param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [Parameter(Mandatory=$true)][string]$PythonExecutable,
    [Parameter(Mandatory=$true)][ValidateSet('3.10','3.12','3.14')][string]$PythonVersion,
    [Parameter(Mandatory=$true)][string]$RuntimeLock,
    [Parameter(Mandatory=$true)][string]$BuildLock,
    [Parameter(Mandatory=$true)][string]$PsbtLock,
    [Parameter(Mandatory=$true)][string]$Wheelhouse
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

if (-not [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows)) {
    throw 'C8 Python matrix requires native Windows.'
}

$repo = [System.IO.Path]::GetFullPath($RepoRoot)
$python = [System.IO.Path]::GetFullPath($PythonExecutable)
$wheelhouseRoot = [System.IO.Path]::GetFullPath($Wheelhouse)
$lockPaths = @($RuntimeLock, $BuildLock, $PsbtLock) | ForEach-Object { [System.IO.Path]::GetFullPath($_) }
if (-not (Test-Path -LiteralPath (Join-Path $repo '.git') -PathType Container)) { throw 'Invalid RepoRoot.' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw 'Explicit Python executable is missing.' }
if (-not (Test-Path -LiteralPath $wheelhouseRoot -PathType Container)) { throw 'Preverified wheelhouse is missing.' }
foreach ($lock in $lockPaths) {
    if (-not (Test-Path -LiteralPath $lock -PathType Leaf)) { throw "Required lock is missing: $lock" }
    if ((Split-Path -Leaf $lock) -notmatch "py$($PythonVersion.Replace('.',''))-windows-amd64\.lock$") {
        throw 'Lock name does not match the requested Windows interpreter.'
    }
}

$actual = & $python -c "import platform,sys; print(f'{sys.version_info.major}.{sys.version_info.minor}|{platform.system()}|{platform.machine()}')"
if ($LASTEXITCODE -ne 0 -or $actual -ne "$PythonVersion|Windows|AMD64") { throw 'Interpreter target mismatch.' }

$runId = "cold-wallets-c8-$([Guid]::NewGuid().ToString('N'))"
$tempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$runRoot = [System.IO.Path]::GetFullPath((Join-Path $tempBase $runId))
if (-not $runRoot.StartsWith($tempBase, [StringComparison]::OrdinalIgnoreCase) -or (Split-Path -Leaf $runRoot) -notlike 'cold-wallets-c8-*') {
    throw 'Unsafe run directory.'
}
$manifest = [ordered]@{ runId = $runId; created = @(); removed = @(); residue = @() }
$previousNoIndex = $env:PIP_NO_INDEX
$previousCache = $env:PIP_CACHE_DIR
$previousNoBytecode = $env:PYTHONDONTWRITEBYTECODE

try {
    New-Item -ItemType Directory -LiteralPath $runRoot | Out-Null
    $manifest.created += $runRoot
    $venv = Join-Path $runRoot 'venv'
    $cache = Join-Path $runRoot 'pip-cache'
    New-Item -ItemType Directory -LiteralPath $cache | Out-Null
    $manifest.created += $cache
    & $python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Virtualenv creation failed.' }
    $manifest.created += $venv
    $venvPython = Join-Path $venv 'Scripts\python.exe'
    $env:PIP_NO_INDEX = '1'
    $env:PIP_CACHE_DIR = $cache
    $env:PYTHONDONTWRITEBYTECODE = '1'
    & $venvPython -m pip install --no-index --require-hashes --find-links $wheelhouseRoot -r $BuildLock
    if ($LASTEXITCODE -ne 0) { throw 'Hash-locked offline build dependency installation failed.' }
    & $venvPython -m pip install --no-index --require-hashes --find-links $wheelhouseRoot -r $RuntimeLock
    if ($LASTEXITCODE -ne 0) { throw 'Hash-locked offline runtime installation failed.' }
    & $venvPython -m pip install --no-index --no-build-isolation --require-hashes --find-links $wheelhouseRoot -r $PsbtLock
    if ($LASTEXITCODE -ne 0) { throw 'Hash-locked offline PSBT installation failed.' }
    Push-Location $repo
    try {
        $testOutput = @(& $venvPython -m unittest discover -s tests -v 2>&1)
        $testOutput | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -ne 0) { throw 'Windows test suite failed.' }
        if (($testOutput | Out-String) -match '(?i)skipped\s*=|\bskipped\b') { throw 'Relevant skips are not accepted by C8.' }
    } finally {
        Pop-Location
    }
} finally {
    $env:PIP_NO_INDEX = $previousNoIndex
    $env:PIP_CACHE_DIR = $previousCache
    $env:PYTHONDONTWRITEBYTECODE = $previousNoBytecode
    if (Test-Path -LiteralPath $runRoot) {
        Remove-Item -LiteralPath $runRoot -Recurse -Force
        $manifest.removed += $runRoot
    }
    if (Test-Path -LiteralPath $runRoot) { $manifest.residue += $runRoot }
    $manifest | ConvertTo-Json -Depth 5
}
