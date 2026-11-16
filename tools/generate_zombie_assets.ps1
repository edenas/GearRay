param(
    [Parameter(Mandatory=$true)][string]$RepositoryRoot,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [Parameter(Mandatory=$true)][string]$SpriteGenerator,
    [Parameter(Mandatory=$true)][string]$Stamp
)

$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath($RepositoryRoot)
$out = [IO.Path]::GetFullPath($OutputDirectory)
$assets = Join-Path $root 'assets/sprites/enemies/zombie'
New-Item -ItemType Directory -Force -Path $out | Out-Null

$basePoses = @('standing','walking_01','walking_02','shot_01','shot_02','shot_dead','corps')
$middlePoses = @('standing','walking_01','walking_02','shot_01','shot_dead','corps')
$nearPoses = @('standing','walking_01','walking_02','standing_attack','attack_01','attack_02','shot_01','corps')
$nearSymbolPose = @{
    standing='stand'; walking_01='walk1'; walking_02='walk2'; standing_attack='melee'
    attack_01='attack1'; attack_02='attack2'; shot_01='hit'; corps='body'
}
$allOutputs = [Collections.Generic.List[string]]::new()
$baseHeaders = @{}
$middleHeaders = @{}
$nearHeaders = @{}

function Invoke-SpriteGeneration([string]$InputName, [string]$Stem, [string]$Symbol, [string]$Kind, [switch]$Lod) {
    $inputPath = Join-Path $assets $InputName
    $sourcePath = Join-Path $out ($Stem + '.c')
    $headerPath = Join-Path $out ($Stem + '.h')
    $args = @('-NoProfile','-ExecutionPolicy','Bypass','-File',$SpriteGenerator,
        '-InputPath',$inputPath,'-OutputSource',$sourcePath,'-OutputHeader',$headerPath,
        '-Symbol',$Symbol,'-SpriteKind',$Kind)
    if ($Lod) { $args += '-GenerateWalkingLod' }
    & powershell @args
    if ($LASTEXITCODE -ne 0) { throw "Sprite generation failed for $InputName (exit $LASTEXITCODE)." }
    $allOutputs.Add($sourcePath)
    $allOutputs.Add($headerPath)
}

foreach ($species in @('01','02')) {
    $type = if ($species -eq '01') { 'security' } else { 'scientist' }
    foreach ($pose in $basePoses) {
        $stem = "zombie_${type}_${pose}_8x8"
        $symbol = "zombie_${type}_${pose}_pixels"
        $file = "zombie_${species}_${pose}.png"
        Invoke-SpriteGeneration $file $stem $symbol 'WorldSprite' -Lod
        $baseHeaders["${type}_${pose}"] = "$stem.h"
    }
    foreach ($pose in $middlePoses) {
        $stem = "zombie_${type}_${pose}_16x16"
        $symbol = "zombie_${type}_middle_${pose}_pixels"
        $file = "zombie_${species}_${pose}_16x16.png"
        Invoke-SpriteGeneration $file $stem $symbol 'MiddleZombie'
        $middleHeaders["${type}_${pose}"] = "$stem.h"
    }
    foreach ($pose in $nearPoses) {
        $assetPose = if ($pose -eq 'corps') { 'corps' } else { $pose }
        $stem = "zombie_near_${type}_${pose}_32x32"
        $shortType = if ($type -eq 'security') { 'sec' } else { 'sci' }
        $symbol = "znear_${shortType}_$($nearSymbolPose[$pose])"
        $file = "zombie_${species}_${assetPose}_32x32.png"
        Invoke-SpriteGeneration $file $stem $symbol 'NearZombie'
        $nearHeaders["${type}_${pose}"] = "$stem.h"
    }
}

$bank1 = [Collections.Generic.List[string]]::new()
foreach ($type in @('security','scientist')) {
    foreach ($pose in $basePoses) { $bank1.Add("#include `"zombie_${type}_${pose}_8x8.c`"") }
    foreach ($pose in $middlePoses) { $bank1.Add("#include `"zombie_${type}_${pose}_16x16.c`"") }
}
$bank1.Add('#include "security-lod-reference.c"')
$bank1.Add('const unsigned char * const zombie_visual_base[2][7] = {')
foreach ($type in @('security','scientist')) {
    $members = foreach ($pose in $basePoses) { "zombie_${type}_${pose}_pixels" }
    $bank1.Add('    {' + ($members -join ', ') + '},')
}
$bank1.Add('};')
$bank1.Add('const unsigned char * const zombie_visual_middle[2][9] = {')
foreach ($type in @('security','scientist')) {
    $members = @("zombie_${type}_middle_standing_pixels", "zombie_${type}_middle_walking_01_pixels", "zombie_${type}_middle_walking_02_pixels", "zombie_${type}_middle_shot_01_pixels", "zombie_${type}_middle_shot_dead_pixels", "zombie_${type}_middle_corps_pixels", "zombie_${type}_middle_walking_01_pixels", "zombie_${type}_middle_walking_01_pixels", "zombie_${type}_middle_walking_01_pixels")
    $bank1.Add('    {' + ($members -join ', ') + '},')
}
$bank1.Add('};')
$bank1.Add('const unsigned char * const zombie_visual_lod_medium[2][7] = {')
$bank1.Add('    {zombie_standing_medium_lod_pixels, zombie_security_walking_01_pixels_medium_lod, zombie_security_walking_02_pixels_medium_lod, zombie_shot_01_medium_lod_pixels, zombie_shot_02_medium_lod_pixels, zombie_shot_dead_medium_lod_pixels, zombie_corpse_lod_pixels},')
$bank1.Add('    {zombie_scientist_standing_pixels_medium_lod, zombie_scientist_walking_01_pixels_medium_lod, zombie_scientist_walking_02_pixels_medium_lod, zombie_scientist_shot_01_pixels_medium_lod, zombie_scientist_shot_02_pixels_medium_lod, zombie_scientist_shot_dead_pixels_medium_lod, zombie_scientist_corps_pixels_simple_lod,}')
$bank1.Add('};')
$bank1.Add('const unsigned char * const zombie_visual_lod_simple[2][7] = {')
$bank1.Add('    {zombie_standing_simple_lod_pixels, zombie_security_walking_01_pixels_simple_lod, zombie_security_walking_02_pixels_simple_lod, zombie_shot_01_simple_lod_pixels, zombie_shot_02_simple_lod_pixels, zombie_shot_dead_simple_lod_pixels, zombie_corpse_lod_pixels},')
$bank1.Add('    {zombie_scientist_standing_pixels_simple_lod, zombie_scientist_walking_01_pixels_simple_lod, zombie_scientist_walking_02_pixels_simple_lod, zombie_scientist_shot_01_pixels_simple_lod, zombie_scientist_shot_02_pixels_simple_lod, zombie_scientist_shot_dead_pixels_simple_lod, zombie_scientist_corps_pixels_simple_lod,}')
$bank1.Add('};')
$bank1Source = Join-Path $out 'zombie_visuals_assets.c'
Set-Content -LiteralPath $bank1Source -Value ($bank1 -join "`r`n") -Encoding Ascii
$allOutputs.Add($bank1Source)

$bank4 = [Collections.Generic.List[string]]::new()
foreach ($type in @('security','scientist')) {
    foreach ($pose in $nearPoses) { $bank4.Add("#include `"zombie_near_${type}_${pose}_32x32.c`"") }
}
$bank4.Add('const unsigned char * const near_zombie_texture_pixels[16] = {')
foreach ($type in @('security','scientist')) {
    $shortType = if ($type -eq 'security') { 'sec' } else { 'sci' }
    foreach ($pose in $nearPoses) { $bank4.Add("    znear_${shortType}_$($nearSymbolPose[$pose]),") }
}
$bank4.Add('};')
$bank4Source = Join-Path $out 'near_zombie_assets.c'
Set-Content -LiteralPath $bank4Source -Value ($bank4 -join "`r`n") -Encoding Ascii
$allOutputs.Add($bank4Source)

# A single manifest makes source->generated identity reviewable and avoids any
# directory glob or accidental selection of protected editor copies.
$manifest = [ordered]@{ inputs = @(); outputs = @() }
foreach ($species in @('01','02')) {
    foreach ($pose in $basePoses) { $manifest.inputs += "assets/sprites/enemies/zombie/zombie_${species}_${pose}.png" }
    foreach ($pose in $middlePoses) { $manifest.inputs += "assets/sprites/enemies/zombie/zombie_${species}_${pose}_16x16.png" }
    foreach ($pose in $nearPoses) { $manifest.inputs += "assets/sprites/enemies/zombie/zombie_${species}_${pose}_32x32.png" }
}
$manifest.outputs = @($allOutputs | ForEach-Object { [IO.Path]::GetFileName($_) })
Set-Content -LiteralPath (Join-Path $out 'zombie_asset_manifest.json') -Value ($manifest | ConvertTo-Json -Depth 4) -Encoding Ascii
New-Item -ItemType File -Force -Path $Stamp | Out-Null
