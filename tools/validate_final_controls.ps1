$ErrorActionPreference = "Stop"

$Up = 0x01
$Down = 0x02
$Left = 0x04
$Right = 0x08
$Button1 = 0x10
$Button2 = 0x20
$Start = 0x8000

function Assert-Equal {
    param($Expected, $Actual, [string]$Message)
    if ($Expected -ne $Actual) {
        throw "$Message (expected $Expected, got $Actual)"
    }
}

function Get-ForwardIntent([int]$Keys) {
    return [int](($Keys -band $Up) -ne 0) - [int](($Keys -band $Down) -ne 0)
}

function Get-StrafeIntent([int]$Keys) {
    if (($Keys -band $Button1) -eq 0) { return 0 }
    return [int](($Keys -band $Right) -ne 0) - [int](($Keys -band $Left) -ne 0)
}

function Get-RotationIntent([int]$Keys) {
    if (($Keys -band $Button1) -ne 0) { return 0 }
    return [int](($Keys -band $Right) -ne 0) - [int](($Keys -band $Left) -ne 0)
}

function Update-State {
    param([int]$Previous, [int]$Current, [bool]$HoldActive, [bool]$StrafeUsed)

    if (($Current -band $Button1) -ne 0) {
        if (-not $HoldActive) {
            $HoldActive = $true
            $StrafeUsed = $false
        }
        if (($Current -band ($Left -bor $Right)) -ne 0) {
            $StrafeUsed = $true
        }
    } else {
        $HoldActive = $false
    }

    return @{
        HoldActive = $HoldActive
        StrafeUsed = $StrafeUsed
        Interaction = (($Current -band $Button1) -eq 0) -and
                      (($Previous -band $Button1) -ne 0) -and
                      (-not $StrafeUsed)
        Fire = (($Current -band $Button2) -ne 0) -and
               (($Previous -band $Button2) -eq 0)
        Menu = (($Current -band $Start) -ne 0) -and
               (($Previous -band $Start) -eq 0)
    }
}

$relevantBits = @($Up, $Down, $Left, $Right, $Button1, $Button2, $Start)
$masks = for ($combination = 0; $combination -lt (1 -shl $relevantBits.Count); $combination++) {
    $mask = 0
    for ($bit = 0; $bit -lt $relevantBits.Count; $bit++) {
        if (($combination -band (1 -shl $bit)) -ne 0) {
            $mask = $mask -bor $relevantBits[$bit]
        }
    }
    $mask
}

foreach ($previous in $masks) {
    foreach ($current in $masks) {
        foreach ($holdActive in @($false, $true)) {
            foreach ($strafeUsed in @($false, $true)) {
                $state = Update-State $previous $current $holdActive $strafeUsed
                $rotation = Get-RotationIntent $current
                $strafe = Get-StrafeIntent $current
                if (($rotation -ne 0) -and ($strafe -ne 0)) {
                    throw "Simultaneous rotation and strafe for mask $current"
                }
                if (($current -band $Button1) -ne 0) {
                    Assert-Equal 0 $rotation "Button 1 must suppress rotation"
                } else {
                    Assert-Equal 0 $strafe "Strafe must require Button 1"
                }
            }
        }
    }
}

Assert-Equal 1 (Get-ForwardIntent $Up) "Up"
Assert-Equal -1 (Get-ForwardIntent $Down) "Down"
Assert-Equal 0 (Get-ForwardIntent ($Up -bor $Down)) "Up + Down"
Assert-Equal -1 (Get-RotationIntent $Left) "Left rotation"
Assert-Equal 1 (Get-RotationIntent $Right) "Right rotation"
Assert-Equal 0 (Get-RotationIntent ($Left -bor $Right)) "Left + Right rotation"
Assert-Equal -1 (Get-StrafeIntent ($Button1 -bor $Left)) "Button 1 + Left"
Assert-Equal 1 (Get-StrafeIntent ($Button1 -bor $Right)) "Button 1 + Right"
Assert-Equal 0 (Get-StrafeIntent ($Button1 -bor $Left -bor $Right)) "Opposing strafe"
Assert-Equal 1 (Get-ForwardIntent ($Button1 -bor $Up)) "Button 1 + Up"
Assert-Equal -1 (Get-ForwardIntent ($Button1 -bor $Down)) "Button 1 + Down"

$press = Update-State 0 $Button1 $false $false
$hold = Update-State $Button1 $Button1 $press.HoldActive $press.StrafeUsed
$release = Update-State $Button1 0 $hold.HoldActive $hold.StrafeUsed
Assert-Equal $false $press.Interaction "Button 1 press interaction"
Assert-Equal $false $hold.Interaction "Button 1 hold interaction"
Assert-Equal $true $release.Interaction "Button 1 release interaction"

$strafe = Update-State $Button1 ($Button1 -bor $Left) $true $false
$strafeRelease = Update-State ($Button1 -bor $Left) 0 $strafe.HoldActive $strafe.StrafeUsed
Assert-Equal $true $strafe.StrafeUsed "Strafe used after Button 1"
Assert-Equal $false $strafeRelease.Interaction "Interaction after strafe"

$modifierPressed = Update-State $Left ($Left -bor $Button1) $false $false
Assert-Equal $true $modifierPressed.StrafeUsed "Button 1 pressed while Left held"
$opposed = Update-State 0 ($Button1 -bor $Left -bor $Right) $false $false
Assert-Equal $true $opposed.StrafeUsed "Opposing modifier-horizontal input counts as strafe use"

Assert-Equal $true (Update-State 0 $Button2 $false $false).Fire "Button 2 edge"
Assert-Equal $false (Update-State $Button2 $Button2 $false $false).Fire "Button 2 hold"
Assert-Equal $true (Update-State 0 $Start $false $false).Menu "Start edge"
Assert-Equal $false (Update-State $Start $Start $false $false).Menu "Start hold"

function Round-Divide([int]$Value, [int]$Scale) {
    if ($Value -lt 0) { $Value -= [int]($Scale / 2) }
    else { $Value += [int]($Scale / 2) }
    return [int][Math]::Truncate($Value / $Scale)
}

function Get-Movement {
    param([int]$Forward, [int]$Strafe, [int]$DirectionX, [int]$DirectionY,
          [int]$PlaneX, [int]$PlaneY)
    $movementX = 0
    $movementY = 0
    if ($Forward -ne 0) {
        $movementX = Round-Divide ($DirectionX * 44) 256
        $movementY = Round-Divide ($DirectionY * 44) 256
        if ($Forward -lt 0) { $movementX = -$movementX; $movementY = -$movementY }
    }
    if ($Strafe -ne 0) {
        $strafeX = Round-Divide ($PlaneX * 44) 169
        $strafeY = Round-Divide ($PlaneY * 44) 169
        if ($Strafe -lt 0) { $strafeX = -$strafeX; $strafeY = -$strafeY }
        $movementX += $strafeX
        $movementY += $strafeY
    }
    if (($Forward -ne 0) -and ($Strafe -ne 0)) {
        $movementX = Round-Divide ($movementX * 177) 256
        $movementY = Round-Divide ($movementY * 177) 256
    }
    return @($movementX, $movementY)
}

$expectedVectors = @{
    "1,0" = @(-44, 0); "-1,0" = @(44, 0)
    "0,-1" = @(0, -44); "0,1" = @(0, 44)
    "1,-1" = @(-30, -30); "1,1" = @(-30, 30)
    "-1,-1" = @(30, -30); "-1,1" = @(30, 30)
}
foreach ($entry in $expectedVectors.GetEnumerator()) {
    $directions = $entry.Key.Split(",")
    $actual = Get-Movement ([int]$directions[0]) ([int]$directions[1]) -256 0 0 169
    Assert-Equal $entry.Value[0] $actual[0] "Movement X $($entry.Key)"
    Assert-Equal $entry.Value[1] $actual[1] "Movement Y $($entry.Key)"
}

$rotatedForward = Get-Movement 1 0 -255 -27 -18 168
$rotatedForwardWithRotationActive = Get-Movement 1 0 -255 -27 -18 168
Assert-Equal $rotatedForward[0] $rotatedForwardWithRotationActive[0] "No turn penalty X"
Assert-Equal $rotatedForward[1] $rotatedForwardWithRotationActive[1] "No turn penalty Y"

$inputSource = Get-Content (Join-Path $PSScriptRoot "..\platform\game_gear\input.c") -Raw
$playerSource = Get-Content (Join-Path $PSScriptRoot "..\game\player.c") -Raw
Assert-Equal 1 ([regex]::Matches($inputSource, "SMS_getKeysStatus\s*\(").Count) "One raw read site"
Assert-Equal 0 ([regex]::Matches($playerSource, "176|rotation_active|movement_with_turn").Count) "No turn penalty source"

Write-Host "Final control validation passed: $($masks.Count * $masks.Count * 4) state combinations and movement vectors."
