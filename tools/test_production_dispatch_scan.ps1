param([string]$BuildDirectory='build/release')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
$build=if([IO.Path]::IsPathRooted($BuildDirectory)){$BuildDirectory}else{Join-Path $root $BuildDirectory}
. "$PSScriptRoot/production_build_artifacts.ps1"
$stage=Join-Path ([IO.Path]::GetTempPath()) ('gearray-dispatch-test-'+[guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item -LiteralPath (Join-Path $build 'generated') -Destination $stage -Recurse
foreach($object in Get-ProductionBuildObjects $build) {
    Copy-Item -LiteralPath $object.FullName -Destination $stage
    Copy-Item -LiteralPath ([IO.Path]::ChangeExtension($object.FullName,'.asm')) -Destination $stage
}
$link=Get-Content (Join-Path $build 'GearRay.lk') -Raw
foreach($object in Get-ProductionBuildObjects $build) {
    $link=$link.Replace($object.FullName.Replace('\','/'),(Join-Path $stage $object.Name).Replace('\','/')).Replace($object.FullName,(Join-Path $stage $object.Name))
}
[IO.File]::WriteAllText((Join-Path $stage 'GearRay.lk'),$link)
$results=@()
function Run-Case([string]$Name,[bool]$ExpectedPass) {
    $ErrorActionPreference='Continue'
    & powershell -NoProfile -ExecutionPolicy Bypass -File "$PSScriptRoot/validate_weapon_runtime.ps1" -BuildDirectory $stage *> (Join-Path $stage "$Name.log")
    $actualPass=$LASTEXITCODE -eq 0
    if($actualPass -ne $ExpectedPass) {throw "Dispatch self-test $Name failed; evidence: $stage"}
    if(!$ExpectedPass -and (Get-Content (Join-Path $stage "$Name.log") -Raw) -notmatch 'Unexpected Bank 3 dispatch|dispatch') {throw "Wrong rejection reason for $Name"}
    $script:results+=@{Case=$Name;ExpectedPass=$ExpectedPass;Verified=$true}
}
Run-Case 'legitimate-production-main' $true
Copy-Item (Join-Path $stage 'main.asm') (Join-Path $stage 'pause-baseline-main.asm')
Run-Case 'unlinked-main-snapshot' $true
$mutation="`r`n`tld`te, #b_game_gear_startup_logo_show`r`n`tld`thl, #_game_gear_startup_logo_show`r`n`tcall`t___sdcc_bcall_ehl`r`n"
foreach($case in @(@('world','unexpected-gameplay'),@('pause_map','unexpected-pause'))) {
    $path=Join-Path $stage "$($case[0]).asm"
    $original=Get-Content $path -Raw
    [IO.File]::WriteAllText($path,$original+$mutation)
    Run-Case $case[1] $false
    [IO.File]::WriteAllText($path,$original)
}
Run-Case 'unchanged-production-restored' $true
$results|ConvertTo-Json|Set-Content (Join-Path $stage 'results.json')
Write-Output "Production dispatch self-test PASS: five cases; evidence $stage"
