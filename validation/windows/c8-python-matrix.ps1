param(
    [Parameter(Mandatory=$true)][string]$RepoRoot,
    [Parameter(Mandatory=$true)][string]$PythonExecutable,
    [Parameter(Mandatory=$true)][ValidateSet('3.10','3.12','3.14')][string]$PythonVersion,
    [Parameter(Mandatory=$true)][string]$RuntimeLock,
    [Parameter(Mandatory=$true)][string]$BuildLock,
    [Parameter(Mandatory=$true)][string]$PsbtLock,
    [Parameter(Mandatory=$true)][string]$Wheelhouse,
    [Parameter(Mandatory=$true)][string]$WheelhouseManifest,
    [Parameter(Mandatory=$true)][ValidateRange(1,10000)][int]$ExpectedTestCount
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
if (-not [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows)) { throw 'C8 Python matrix requires native Windows.' }

function Test-PathInside([string]$Root, [string]$Candidate) {
    $prefix = $Root.TrimEnd('\') + '\'
    return $Candidate.StartsWith($prefix, [System.StringComparison]::OrdinalIgnoreCase)
}
function Assert-RegularFile([string]$Path, [string]$Label) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "$Label is missing." }
    if ((Get-Item -LiteralPath $Path -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw "$Label reparse point rejected." }
}

$repo = (Resolve-Path -LiteralPath $RepoRoot).Path
$python = (Resolve-Path -LiteralPath $PythonExecutable).Path
$wheelhouseRoot = (Resolve-Path -LiteralPath $Wheelhouse).Path
$requirementsRoot = (Resolve-Path -LiteralPath (Join-Path $repo 'requirements')).Path
$manifestPath = (Resolve-Path -LiteralPath $WheelhouseManifest).Path
$lockPaths = @($RuntimeLock, $BuildLock, $PsbtLock) | ForEach-Object { (Resolve-Path -LiteralPath $_).Path }
$runtimeLockPath = $lockPaths[0]; $buildLockPath = $lockPaths[1]; $psbtLockPath = $lockPaths[2]
if (-not (Test-Path -LiteralPath (Join-Path $repo '.git') -PathType Container)) { throw 'Invalid RepoRoot.' }
if ((Get-Item -LiteralPath $repo -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse-point RepoRoot rejected.' }
Assert-RegularFile $python 'Explicit Python executable'
if (-not (Test-Path -LiteralPath $wheelhouseRoot -PathType Container)) { throw 'Preverified wheelhouse is missing.' }
if ((Get-Item -LiteralPath $wheelhouseRoot -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Wheelhouse reparse point rejected.' }
Assert-RegularFile $manifestPath 'Wheelhouse manifest'
if (-not (Test-PathInside $requirementsRoot $manifestPath)) { throw 'Wheelhouse manifest must be inside repository requirements.' }
foreach ($lock in $lockPaths) {
    Assert-RegularFile $lock 'Required lock'
    if (-not (Test-PathInside $requirementsRoot $lock)) { throw 'Lock outside repository requirements rejected.' }
    if ((Split-Path -Leaf $lock) -notmatch "py$($PythonVersion.Replace('.',''))-windows-amd64\.lock$") { throw 'Lock name does not match the requested Windows interpreter.' }
}

$wheelManifest = Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$topFields = @($wheelManifest.PSObject.Properties.Name | Sort-Object)
if (($topFields -join ',') -cne 'files,platform,python,schema,version') { throw 'Unknown wheelhouse manifest field rejected.' }
if ($wheelManifest.schema -cne 'cold-wallets.windows-wheelhouse' -or $wheelManifest.version -ne 1) { throw 'Unsupported wheelhouse manifest.' }
if ($wheelManifest.python -cne $PythonVersion -or $wheelManifest.platform -cne 'windows-amd64') { throw 'Wheelhouse target mismatch.' }
$approvedFiles = @{}
foreach ($entry in @($wheelManifest.files)) {
    $entryFields = @($entry.PSObject.Properties.Name | Sort-Object)
    if (($entryFields -join ',') -cne 'name,sha256') { throw 'Unknown wheelhouse file field rejected.' }
    if ($entry.name -cne [System.IO.Path]::GetFileName($entry.name) -or $entry.name -match '[/\\]') { throw 'Unsafe wheelhouse filename.' }
    if ($entry.sha256 -notmatch '^[0-9a-f]{64}$') { throw 'Invalid wheelhouse hash.' }
    if ($approvedFiles.ContainsKey($entry.name)) { throw 'Duplicate wheelhouse filename.' }
    $approvedFiles[$entry.name] = $entry.sha256
}
if ($approvedFiles.Count -eq 0) { throw 'Empty wheelhouse manifest rejected.' }
$actualItems = @(Get-ChildItem -LiteralPath $wheelhouseRoot -Force)
if ($actualItems.Count -ne $approvedFiles.Count) { throw 'Wheelhouse contains an unapproved or missing item.' }
foreach ($item in $actualItems) {
    if ($item.PSIsContainer -or ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Non-regular wheelhouse item rejected.' }
    if (-not (Test-PathInside $wheelhouseRoot $item.FullName)) { throw 'Wheelhouse item escaped authorized root.' }
    if (-not $approvedFiles.ContainsKey($item.Name)) { throw 'Unapproved wheelhouse file rejected.' }
    $actualHash = (Get-FileHash -LiteralPath $item.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actualHash -cne $approvedFiles[$item.Name]) { throw 'Wheelhouse hash mismatch.' }
}

$actual = & $python -c "import platform,sys; print(f'{sys.version_info.major}.{sys.version_info.minor}|{platform.system()}|{platform.machine()}')"
if ($LASTEXITCODE -ne 0 -or $actual -ne "$PythonVersion|Windows|AMD64") { throw 'Interpreter target mismatch.' }

$runId = "cold-wallets-c8-$([Guid]::NewGuid().ToString('N'))"
$tempBase = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath()).TrimEnd('\')
$runRoot = [System.IO.Path]::GetFullPath((Join-Path $tempBase $runId))
if ((Split-Path -Parent $runRoot) -cne $tempBase -or (Split-Path -Leaf $runRoot) -notmatch '^cold-wallets-c8-[0-9a-f]{32}$') { throw 'Unsafe run directory.' }
$resourceManifest = [ordered]@{ runId = $runId; created = @(); removed = @(); residue = @() }
$environmentNames = @('PIP_NO_INDEX','PIP_CONFIG_FILE','PIP_CACHE_DIR','PIP_INDEX_URL','PIP_EXTRA_INDEX_URL','PIP_TRUSTED_HOST','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY','PYTHONDONTWRITEBYTECODE')
$previousEnvironment = @{}
foreach ($name in $environmentNames) { $previousEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process') }

try {
    New-Item -ItemType Directory -LiteralPath $runRoot | Out-Null
    $resourceManifest.created += $runRoot
    $venv = Join-Path $runRoot 'venv'; $cache = Join-Path $runRoot 'pip-cache'
    New-Item -ItemType Directory -LiteralPath $cache | Out-Null; $resourceManifest.created += $cache
    & $python -m venv $venv
    if ($LASTEXITCODE -ne 0) { throw 'Virtualenv creation failed.' }
    $resourceManifest.created += $venv; $venvPython = Join-Path $venv 'Scripts\python.exe'
    [Environment]::SetEnvironmentVariable('PIP_NO_INDEX', '1', 'Process')
    [Environment]::SetEnvironmentVariable('PIP_CONFIG_FILE', 'NUL', 'Process')
    [Environment]::SetEnvironmentVariable('PIP_CACHE_DIR', $cache, 'Process')
    [Environment]::SetEnvironmentVariable('PYTHONDONTWRITEBYTECODE', '1', 'Process')
    foreach ($name in @('PIP_INDEX_URL','PIP_EXTRA_INDEX_URL','PIP_TRUSTED_HOST','HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY')) { [Environment]::SetEnvironmentVariable($name, $null, 'Process') }
    & $venvPython -m pip --isolated install --no-index --require-hashes --find-links $wheelhouseRoot -r $buildLockPath
    if ($LASTEXITCODE -ne 0) { throw 'Hash-locked offline build dependency installation failed.' }
    & $venvPython -m pip --isolated install --no-index --require-hashes --find-links $wheelhouseRoot -r $runtimeLockPath
    if ($LASTEXITCODE -ne 0) { throw 'Hash-locked offline runtime installation failed.' }
    & $venvPython -m pip --isolated install --no-index --no-build-isolation --require-hashes --find-links $wheelhouseRoot -r $psbtLockPath
    if ($LASTEXITCODE -ne 0) { throw 'Hash-locked offline PSBT installation failed.' }
    Push-Location $repo
    try {
        $testOutput = @(& $venvPython -m unittest discover -s tests -v 2>&1)
        $testOutput | ForEach-Object { Write-Host $_ }
        if ($LASTEXITCODE -ne 0) { throw 'Windows test suite failed.' }
        $summaries = @($testOutput | Select-String -Pattern '^Ran ([0-9]+) tests? in ')
        if ($summaries.Count -ne 1) { throw 'Missing or ambiguous Windows unittest summary.' }
        if ([int]$summaries[0].Matches[0].Groups[1].Value -ne $ExpectedTestCount) { throw 'Unexpected Windows test count.' }
        $combinedTestOutput = $testOutput -join "`n"
        if ($combinedTestOutput -match '(?i)\bskipped\b') { throw 'Relevant skips are not accepted by C8.' }
        if ($combinedTestOutput -match '(?im)^FAILED\b|(?:failures|errors)\s*=\s*[1-9]') { throw 'Windows test failures or errors are not accepted by C8.' }
    } finally { Pop-Location }
} finally {
    foreach ($name in $environmentNames) { [Environment]::SetEnvironmentVariable($name, $previousEnvironment[$name], 'Process') }
    $safeCleanup = ((Split-Path -Parent $runRoot) -ceq $tempBase) -and ((Split-Path -Leaf $runRoot) -match '^cold-wallets-c8-[0-9a-f]{32}$')
    if ((Test-Path -LiteralPath $runRoot) -and -not $safeCleanup) { throw 'Unsafe cleanup path refused.' }
    if (Test-Path -LiteralPath $runRoot) { Remove-Item -LiteralPath $runRoot -Recurse -Force; $resourceManifest.removed += $runRoot }
    if (Test-Path -LiteralPath $runRoot) { $resourceManifest.residue += $runRoot }
    $resourceManifest | ConvertTo-Json -Depth 5
}
