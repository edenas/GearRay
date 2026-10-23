# Historical optional compile experiment; excluded from Release/validation.
param([string]$OutputPath='build/experiments/row-base/measurement.json')
$ErrorActionPreference='Stop'
$root=Split-Path $PSScriptRoot -Parent
if(![IO.Path]::IsPathRooted($OutputPath)) {$OutputPath=Join-Path $root $OutputPath}
function Measure-Case([string]$Name,[int]$Left,[int]$Right,[int]$Top,[int]$Bottom,[int]$Column,[int]$Row,[int[]]$VisibleRay,[int]$Instances=1,[bool]$Dirty=$true) {
    $old=0;$new=0
    if($Dirty) {
        for($instance=0;$instance-lt$Instances;++$instance) {
            for($pixelY=0;$pixelY-lt8;++$pixelY) {
                $screenY=$Row*8+$pixelY
                if($screenY-lt$Top-or$screenY-ge$Bottom){continue}
                ++$new
                for($pixelX=0;$pixelX-lt8;++$pixelX) {
                    $screenX=$Column*8+$pixelX
                    if($screenX-lt$Left-or$screenX-ge$Right){continue}
                    if($VisibleRay -contains ($screenX-shr2)){++$old}
                }
            }
        }
    }
    [pscustomobject]@{Case=$Name;OldStrideMultiplies=$old;HoistedStrideMultiplies=$new;Delta=$new-$old;Dirty=$Dirty;Instances=$Instances}
}
$allRays=0..27
$cases=@(
    (Measure-Case 'visible substantial overlap' 16 40 8 32 3 2 $allRays),
    (Measure-Case 'partially clipped edge tile' -3 13 5 27 1 2 $allRays),
    (Measure-Case 'mostly wall occluded' 16 40 8 32 3 2 @(6)),
    (Measure-Case 'fully wall occluded after row entry' 16 40 8 32 3 2 @()),
    (Measure-Case 'several visible zombies' 8 56 4 44 4 3 $allRays 5),
    (Measure-Case 'corpse visible tile' 24 40 35 48 3 5 $allRays),
    (Measure-Case 'world pickup visible tile' 40 56 40 56 5 5 $allRays),
    (Measure-Case 'mostly clean viewport' 16 40 8 32 3 2 $allRays 1 $false)
)
$result=[ordered]@{Cases=$cases;TotalOld=($cases|Measure-Object OldStrideMultiplies -Sum).Sum;TotalHoisted=($cases|Measure-Object HoistedStrideMultiplies -Sum).Sum;Note='Counts only execution of texture_y * packed_row_stride. Pixel output and other work are unchanged; representative cases are comparative, not a scene-frequency profile.'}
$directory=Split-Path $OutputPath -Parent;if($directory){New-Item -ItemType Directory -Force $directory|Out-Null}
$result|ConvertTo-Json -Depth 5|Set-Content $OutputPath
$cases|Format-Table -AutoSize
Write-Output "Representative total: $($result.TotalOld) -> $($result.TotalHoisted)"
