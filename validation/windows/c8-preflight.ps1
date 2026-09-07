param(
    [Parameter(Mandatory=$true)][ValidatePattern('^[0-9a-fA-F]{40}$')][string]$ExpectedHead,
    [Parameter(Mandatory=$false)][ValidatePattern('^[0-9a-fA-F]{40}$')][string]$ExpectedMain = '5374c1c0ac17aed4fe6e56582ec3c517f4fcfb9f',
    [Parameter(Mandatory=$false)][string]$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$ExpectedBranch = 'audit/cold-wallet-security-architecture-20260907'

if (-not [System.Runtime.InteropServices.RuntimeInformation]::IsOSPlatform(
    [System.Runtime.InteropServices.OSPlatform]::Windows)) {
    throw 'C8 preflight requires native Windows; WSL and Linux are not accepted.'
}

function Get-MaskedIdentifier([string]$Value) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $digest = $sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($Value))
        return ([System.BitConverter]::ToString($digest).Replace('-', '').Substring(0, 12).ToLowerInvariant())
    } finally { $sha.Dispose() }
}

function Invoke-GitText([string[]]$Arguments) {
    $text = & git -C $script:RepoPath @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) { throw "Git inventory failed: $($Arguments[0])" }
    return (($text | Out-String).Trim())
}

function Get-ConfinedManifestFile([string]$Root, [string]$RelativePath) {
    if ([System.IO.Path]::IsPathRooted($RelativePath)) { throw 'Absolute checksum path rejected.' }
    $rootPrefix = $Root.TrimEnd('\') + '\'
    $candidate = [System.IO.Path]::GetFullPath((Join-Path $Root $RelativePath))
    if (-not $candidate.StartsWith($rootPrefix, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Checksum path escaped RepoRoot.'
    }
    if (-not (Test-Path -LiteralPath $candidate -PathType Leaf)) { throw 'Checksum target is missing.' }
    if ((Get-Item -LiteralPath $candidate -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) {
        throw 'Checksum target reparse point rejected.'
    }
    return $candidate
}

$script:RepoPath = [System.IO.Path]::GetFullPath($RepoRoot)
if (-not (Test-Path -LiteralPath (Join-Path $script:RepoPath '.git') -PathType Container)) { throw 'RepoRoot is not the Cold Wallets checkout.' }
if ((Get-Item -LiteralPath $script:RepoPath -Force).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse-point RepoRoot rejected.' }

$branch = Invoke-GitText @('branch', '--show-current')
$head = Invoke-GitText @('rev-parse', 'HEAD')
$main = Invoke-GitText @('rev-parse', 'main')
$status = Invoke-GitText @('status', '--porcelain=v1', '--untracked-files=all')
$worktreeCount = ((Invoke-GitText @('worktree', 'list', '--porcelain')) -split "`n" | Where-Object { $_ -like 'worktree *' }).Count
if ($branch -cne $ExpectedBranch) { throw 'Audit branch mismatch.' }
if ($head -cne $ExpectedHead.ToLowerInvariant()) { throw 'HEAD mismatch.' }
if ($main -cne $ExpectedMain.ToLowerInvariant()) { throw 'main/base mismatch.' }
if (-not [string]::IsNullOrWhiteSpace($status)) { throw 'Worktree must be clean.' }
if ($worktreeCount -ne 1) { throw 'Additional Git worktree rejected.' }

$checksumResults = @()
$seenChecksumPaths = @{}
$checksumManifests = @('audit_output\50-c81-checksums.txt','audit_output\52-c82-checksums.txt')
foreach ($checksumManifestName in $checksumManifests) {
    $checksumManifest = Join-Path $script:RepoPath $checksumManifestName
    if (-not (Test-Path -LiteralPath $checksumManifest -PathType Leaf)) { throw 'Required checkpoint checksum manifest is missing.' }
    foreach ($line in Get-Content -LiteralPath $checksumManifest -Encoding UTF8) {
        if ($line -notmatch '^([0-9a-f]{64})\s+(.+)$') { throw 'Malformed checkpoint checksum manifest.' }
        $expected = $Matches[1]; $manifestPath = $Matches[2]
        if ($seenChecksumPaths.ContainsKey($manifestPath)) { throw 'Duplicate checksum path rejected.' }
        $seenChecksumPaths[$manifestPath] = $true
        $target = Get-ConfinedManifestFile $script:RepoPath $manifestPath.Replace('/', [System.IO.Path]::DirectorySeparatorChar)
        $actual = (Get-FileHash -LiteralPath $target -Algorithm SHA256).Hash.ToLowerInvariant()
        if ($actual -cne $expected) { throw 'Checkpoint checksum mismatch.' }
        $checksumResults += [ordered]@{ file = $manifestPath; matches = $true }
    }
}
if ($checksumResults.Count -eq 0) { throw 'Empty checksum manifest rejected.' }

$os = Get-CimInstance Win32_OperatingSystem
$computer = Get-CimInstance Win32_ComputerSystem
$principal = [Security.Principal.WindowsPrincipal]::new([Security.Principal.WindowsIdentity]::GetCurrent())
$isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
$trackedSymlinkCount = ((Invoke-GitText @('ls-files', '-s')) -split "`n" | Where-Object { $_ -match '^120000 ' }).Count
$relevantNames = @('python', 'pythonw', 'tor', 'bitcoind', 'bitcoin-qt', 'helios', 'com.docker.backend')
$processes = @(Get-Process -ErrorAction SilentlyContinue | Where-Object { $relevantNames -contains $_.ProcessName } | ForEach-Object { [ordered]@{ name = $_.ProcessName; pid = $_.Id } })
$relevantPorts = @(8888, 9050, 8545, 8332)
$listeners = @(Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | Where-Object { $relevantPorts -contains $_.LocalPort } | ForEach-Object { [ordered]@{ address = $_.LocalAddress; port = $_.LocalPort; pid = $_.OwningProcess } })
$adapters = @(Get-NetAdapter -ErrorAction SilentlyContinue | Group-Object Status | ForEach-Object { [ordered]@{ status = $_.Name; count = $_.Count } })
$volumes = @(Get-Volume -ErrorAction SilentlyContinue | Where-Object DriveLetter | ForEach-Object { [ordered]@{ drive = "$($_.DriveLetter):"; filesystem = $_.FileSystem; sizeBytes = $_.Size; freeBytes = $_.SizeRemaining } })
$defender = Get-MpComputerStatus -ErrorAction SilentlyContinue
$pythonVersions = @()
if (Get-Command py -ErrorAction SilentlyContinue) {
    foreach ($line in @(& py -0 2>$null)) { if ($line -match '(\d+\.\d+)') { $pythonVersions += $Matches[1] } }
    $pythonVersions = @($pythonVersions | Sort-Object -Unique)
}
$dockerContainers = $null
if ((Get-Command docker -ErrorAction SilentlyContinue) -and (Get-Process -Name 'com.docker.backend' -ErrorAction SilentlyContinue)) {
    $containerIds = @(& docker ps -a --quiet 2>$null)
    if ($LASTEXITCODE -eq 0) { $dockerContainers = $containerIds.Count }
}
$acl = Get-Acl -LiteralPath $script:RepoPath

$result = [ordered]@{
    schema = 'cold-wallets.c8-windows-preflight'; version = 2
    runId = "cold-wallets-c8-$([Guid]::NewGuid().ToString('N'))"; timestampUtc = [DateTime]::UtcNow.ToString('o'); nativeWindows = $true
    host = [ordered]@{ productName = $os.Caption; version = $os.Version; build = $os.BuildNumber; architecture = $os.OSArchitecture; machineIdMasked = Get-MaskedIdentifier $env:COMPUTERNAME; userIdMasked = Get-MaskedIdentifier ([Security.Principal.WindowsIdentity]::GetCurrent().Name); administrator = $isAdmin; powershell = $PSVersionTable.PSVersion.ToString(); domainRole = $computer.DomainRole }
    repository = [ordered]@{ branch = $branch; head = $head; main = $main; clean = $true; worktreeCount = $worktreeCount; trackedSymlinkCount = $trackedSymlinkCount; ownerMasked = Get-MaskedIdentifier $acl.Owner; readOnlyAttributeSet = [bool]((Get-Item -LiteralPath $script:RepoPath).Attributes -band [IO.FileAttributes]::ReadOnly); aclRuleCount = @($acl.Access).Count; explicitDenyRuleCount = @($acl.Access | Where-Object AccessControlType -eq 'Deny').Count; c81Checksums = $checksumResults }
    tools = [ordered]@{ git = [bool](Get-Command git -ErrorAction SilentlyContinue); pythonLauncher = [bool](Get-Command py -ErrorAction SilentlyContinue); pythonVersions = $pythonVersions; docker = [bool](Get-Command docker -ErrorAction SilentlyContinue); bitcoinCore = [bool](Get-Command bitcoind -ErrorAction SilentlyContinue); tor = [bool](Get-Command tor -ErrorAction SilentlyContinue) }
    defender = [ordered]@{ available = [bool]$defender; antivirusEnabled = if ($defender) { [bool]$defender.AntivirusEnabled } else { $null }; realtimeProtectionEnabled = if ($defender) { [bool]$defender.RealTimeProtectionEnabled } else { $null } }
    adapters = $adapters; listeners = $listeners; relevantProcesses = $processes; dockerContainerCount = $dockerContainers; volumes = $volumes
}
$result | ConvertTo-Json -Depth 8
