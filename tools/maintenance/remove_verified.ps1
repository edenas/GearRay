param(
    [ValidateSet('DryRun','Execute')][string]$Mode='DryRun',
    [ValidateSet('Build','Rom','Raw','Stub','Scratch','Execution')][string]$Group='Build',
    [string]$ManifestName='removal-manifest.json',
    [string]$GateName='phase-3-gate.json'
)
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)).TrimEnd('\','/')
if ($root -ine 'D:\mano_projektai\GearRay') { throw 'Unexpected project root' }
$boundary=$root+[IO.Path]::DirectorySeparatorChar
$out=Join-Path $root 'docs/maintenance/2026-10-23/implementation'
if($ManifestName -notmatch '^[a-zA-Z0-9-]+\.json$' -or $GateName -notmatch '^[a-zA-Z0-9-]+\.json$'){throw 'Unsafe execution record filename'}
$manifestPath=Join-Path $out $ManifestName
$gate=Get-Content -LiteralPath (Join-Path $out $GateName) -Raw -Encoding UTF8 | ConvertFrom-Json
if ($gate.status -ne 'PASS') { throw 'Retention/migration/restore gate has not passed' }
if ((Get-FileHash -LiteralPath $manifestPath).Hash -ine $gate.removal_manifest_sha256) { throw 'Manifest changed after retention gate' }
if ((Get-FileHash -LiteralPath (Join-Path $root 'docs/history/2026-10-23/catalog.json')).Hash -ine $gate.catalog_sha256) { throw 'Catalog changed after retention gate' }
$manifest=Get-Content -LiteralPath $manifestPath -Raw -Encoding UTF8 | ConvertFrom-Json
$roots=(Get-Content -LiteralPath (Join-Path $out 'phase-2-3-retention.json') -Raw | ConvertFrom-Json).build_roots
function Checked-Path([string]$relative) {
    if (!$relative -or [IO.Path]::IsPathRooted($relative) -or $relative.Contains(':') -or $relative.Contains('\') -or @($relative.Split('/') | Where-Object {$_ -in @('','..','.')}).Count) { throw 'Unsafe manifest path' }
    $path=[IO.Path]::GetFullPath((Join-Path $root $relative))
    if (!$path.StartsWith($boundary,[StringComparison]::OrdinalIgnoreCase)) { throw 'Path escapes project' }
    $part=$path
    while ($part -ine $root) {
        if (Test-Path -LiteralPath $part) {
            $item=Get-Item -LiteralPath $part -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Reparse component forbidden' }
        }
        $part=[IO.Path]::GetDirectoryName($part)
    }
    return $path
}
function Protected([string]$relative) {
    foreach($prefix in @('.git/','assets/','game/','engine/','platform/','.artifact-quarantine/','tools/','docs/history/','artifacts/')) {
        if ($relative.StartsWith($prefix,[StringComparison]::OrdinalIgnoreCase)) { return $true }
    }
    return $false
}
$selected=New-Object 'Collections.Generic.List[object]'
$rootSet=New-Object 'Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
foreach($buildRoot in $roots) {[void]$rootSet.Add($buildRoot)}
for($i=0;$i -lt $manifest.Count;$i++) {
    $r=$manifest[$i];$isBuild=$r.path.Contains('/') -and $rootSet.Contains($r.path.Split('/')[0])
    $match=switch($Group) {
        Build {$isBuild}
        Rom {$r.path.StartsWith('rom/',[StringComparison]::OrdinalIgnoreCase)}
        Raw {$r.path.StartsWith('docs/performance/',[StringComparison]::OrdinalIgnoreCase)}
        Stub {$r.path -eq 'source/main.c'}
        Scratch {$r.path.StartsWith('build/history-restore/',[StringComparison]::OrdinalIgnoreCase) -or $r.path.StartsWith('build/maintenance/',[StringComparison]::OrdinalIgnoreCase)}
        Execution {$r.path.StartsWith('docs/maintenance/2026-10-23/implementation/',[StringComparison]::OrdinalIgnoreCase)}
    }
    if($match) {$selected.Add(@{Index=$i;Row=$r})}
}
if(!$selected.Count) {throw 'Empty selection'}
$journal=Join-Path $out ($Group.ToLower()+'-'+$Mode.ToLower()+'-'+(Get-Date -Format 'yyyyMMddTHHmmssfff')+'-journal.jsonl')
if(Test-Path -LiteralPath $journal) {throw 'Refusing to replace an execution journal'}
$writer=New-Object IO.StreamWriter($journal,$false,(New-Object Text.UTF8Encoding($false)))
$writer.AutoFlush=$true
function Journal($value) {$writer.WriteLine(($value|ConvertTo-Json -Compress -Depth 5))}
$verifiedKeepers=@{};$parents=New-Object 'Collections.Generic.HashSet[string]' ([StringComparer]::OrdinalIgnoreCase)
$removed=0;$bytes=0L;$refused=0
try {
    Journal @{state='begin';mode=$Mode;group=$Group;manifest_sha256=$gate.removal_manifest_sha256;catalog_sha256=$gate.catalog_sha256;files=$selected.Count}
    foreach($entry in $selected) {
        $r=$entry.Row
        try {
            if(Protected $r.path) {throw 'Protected path exclusion'}
            $path=Checked-Path $r.path;$keeper=Checked-Path $r.keeper
            if(!$verifiedKeepers.ContainsKey($keeper)) {
                if((Get-FileHash -LiteralPath $keeper).Hash -ine $r.keeper_sha256) {throw 'Keeper hash mismatch'}
                $verifiedKeepers[$keeper]=$r.keeper_sha256
            }
            $item=Get-Item -LiteralPath $path -Force
            if($item.PSIsContainer -or $item.Length -ne $r.size) {throw 'Candidate type/size changed'}
            $actual=(Get-FileHash -LiteralPath $path).Hash
            if($actual -ine $r.sha256) {throw 'Candidate hash changed'}
            Journal @{state='verified';index=$entry.Index;path=$r.path;size=$r.size;sha256=$actual}
            if($Mode -eq 'Execute') {
                Remove-Item -LiteralPath $path -Force
                if(Test-Path -LiteralPath $path) {throw 'File remains after removal'}
                Journal @{state='removed';index=$entry.Index;size=$r.size}
                $removed++;$bytes+=$r.size
                $parent=[IO.Path]::GetDirectoryName($path)
                while($parent -ine $root) {[void]$parents.Add($parent);$parent=[IO.Path]::GetDirectoryName($parent)}
            }
        } catch {
            $refused++;Journal @{state='refused';index=$entry.Index;path=$r.path;reason=$_.Exception.Message}
        }
    }
    if($Mode -eq 'Execute') {
        foreach($directory in ($parents | Sort-Object Length -Descending)) {
            if($directory -in @((Join-Path $root 'build'),(Join-Path $root 'rom'),(Join-Path $root 'docs'))) {continue}
            $relative=$directory.Substring($boundary.Length).Replace('\','/')
            $checked=Checked-Path $relative
            if((Test-Path -LiteralPath $checked -PathType Container) -and @(Get-ChildItem -LiteralPath $checked -Force).Count -eq 0) {
                Remove-Item -LiteralPath $checked -Force
                Journal @{state='empty-directory-removed';path=$relative}
            }
        }
    }
    foreach($keeper in $verifiedKeepers.Keys) {if((Get-FileHash -LiteralPath $keeper).Hash -ine $verifiedKeepers[$keeper]) {throw 'Keeper changed during cleanup'}}
    Journal @{state='complete';verified=$selected.Count-$refused;removed=$removed;logical_removed=$bytes;refused=$refused}
} finally {$writer.Dispose()}
Write-Output "$Mode $Group verified $($selected.Count-$refused); removed $removed files / $bytes logical bytes; refused $refused"
if($refused) {exit 1}
