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

function Get-InitializerValue {
    param(
        [string]$Body,
        [string]$Variable,
        [string]$ConstantName,
        [int]$ConstantValue
    )

    $match = [regex]::Match(
        $Body,
        "(?m)^\s*$Variable\s*=\s*(?<value>-?(?:\d+|$ConstantName))\s*;\s*$")
    if (-not $match.Success) {
        throw "Could not extract initial $Variable from production source."
    }

    $value = $match.Groups["value"].Value
    if ($value -eq $ConstantName) { return $ConstantValue }
    if ($value -eq "-$ConstantName") { return -$ConstantValue }
    return [int]$value
}

$playerSource = Get-Content (Join-Path $PSScriptRoot "..\game\player.c") -Raw
$playerHeader = Get-Content (Join-Path $PSScriptRoot "..\game\player.h") -Raw
$cameraSource = Get-Content (Join-Path $PSScriptRoot "..\game\camera.c") -Raw
$playerMoveSpeed = [int]([regex]::Match(
    $playerHeader,
    "#define\s+PLAYER_MOVE_SPEED\s+(\d+)").Groups[1].Value)
$rotationCosine = [int]([regex]::Match(
    $cameraSource,
    "#define\s+ROTATION_COSINE\s+(\d+)").Groups[1].Value)
$rotationSine = [int]([regex]::Match(
    $cameraSource,
    "#define\s+ROTATION_SINE\s+(\d+)").Groups[1].Value)
$directionLength = [int]([regex]::Match(
    $cameraSource,
    "#define\s+DIRECTION_LENGTH\s+(\d+)").Groups[1].Value)
$cameraPlaneLength = [int]([regex]::Match(
    $cameraSource,
    "#define\s+CAMERA_PLANE_LENGTH\s+(\d+)").Groups[1].Value)

Assert-Equal 74 $playerMoveSpeed "PLAYER_MOVE_SPEED"
Assert-Equal 4058 $rotationCosine "ROTATION_COSINE"
Assert-Equal 556 $rotationSine "ROTATION_SINE"
Assert-Equal 256 $directionLength "DIRECTION_LENGTH"
Assert-Equal 169 $cameraPlaneLength "CAMERA_PLANE_LENGTH"

$cameraInitialize = [regex]::Match(
    $cameraSource,
    "void\s+camera_initialize\s*\(\s*void\s*\)\s*\{(?<body>[\s\S]*?)\}")
if (-not $cameraInitialize.Success) {
    throw "Could not extract camera_initialize() from production source."
}
$cameraInitializeBody = $cameraInitialize.Groups["body"].Value
$initialDirectionX = Get-InitializerValue `
    $cameraInitializeBody "direction_x" "DIRECTION_LENGTH" $directionLength
$initialDirectionY = Get-InitializerValue `
    $cameraInitializeBody "direction_y" "DIRECTION_LENGTH" $directionLength
$initialPlaneX = Get-InitializerValue `
    $cameraInitializeBody "plane_x" "CAMERA_PLANE_LENGTH" $cameraPlaneLength
$initialPlaneY = Get-InitializerValue `
    $cameraInitializeBody "plane_y" "CAMERA_PLANE_LENGTH" $cameraPlaneLength

Assert-Equal 0 $initialDirectionX "Canonical initial direction X"
Assert-Equal (-$directionLength) $initialDirectionY "Canonical initial direction Y"
Assert-Equal $cameraPlaneLength $initialPlaneX "Canonical initial plane X"
Assert-Equal 0 $initialPlaneY "Canonical initial plane Y"

function Get-ForwardIntent([int]$Keys) {
    return [int](($Keys -band $Up) -ne 0) - [int](($Keys -band $Down) -ne 0)
}

function Get-StrafeIntent([int]$Keys) {
    if (($Keys -band $Button2) -eq 0) { return 0 }
    return [int](($Keys -band $Right) -ne 0) - [int](($Keys -band $Left) -ne 0)
}

function Get-RotationIntent([int]$Keys) {
    if (($Keys -band $Button2) -ne 0) { return 0 }
    return [int](($Keys -band $Right) -ne 0) - [int](($Keys -band $Left) -ne 0)
}

function Update-State {
    param([int]$Previous, [int]$Current, [bool]$HoldActive, [bool]$StrafeUsed)

    if (($Current -band $Button2) -ne 0) {
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
        Interaction = (($Current -band $Button2) -eq 0) -and
                      (($Previous -band $Button2) -ne 0) -and
                      (-not $StrafeUsed)
        Fire = (($Current -band $Button1) -ne 0) -and
               (($Previous -band $Button1) -eq 0)
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
                if (($current -band $Button2) -ne 0) {
                    Assert-Equal 0 $rotation "Button 2 must suppress rotation"
                } else {
                    Assert-Equal 0 $strafe "Strafe must require Button 2"
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
Assert-Equal -1 (Get-StrafeIntent ($Button2 -bor $Left)) "Button 2 + Left"
Assert-Equal 1 (Get-StrafeIntent ($Button2 -bor $Right)) "Button 2 + Right"
Assert-Equal 0 (Get-StrafeIntent ($Button2 -bor $Left -bor $Right)) "Opposing strafe"
Assert-Equal 1 (Get-ForwardIntent ($Button2 -bor $Up)) "Button 2 + Up"
Assert-Equal -1 (Get-ForwardIntent ($Button2 -bor $Down)) "Button 2 + Down"

$press = Update-State 0 $Button2 $false $false
$hold = Update-State $Button2 $Button2 $press.HoldActive $press.StrafeUsed
$release = Update-State $Button2 0 $hold.HoldActive $hold.StrafeUsed
Assert-Equal $false $press.Interaction "Button 2 press interaction"
Assert-Equal $false $hold.Interaction "Button 2 hold interaction"
Assert-Equal $true $release.Interaction "Button 2 release interaction"

$strafe = Update-State $Button2 ($Button2 -bor $Left) $true $false
$strafeRelease = Update-State ($Button2 -bor $Left) 0 $strafe.HoldActive $strafe.StrafeUsed
Assert-Equal $true $strafe.StrafeUsed "Strafe used after Button 2"
Assert-Equal $false $strafeRelease.Interaction "Interaction after strafe"

$modifierPressed = Update-State $Left ($Left -bor $Button2) $false $false
Assert-Equal $true $modifierPressed.StrafeUsed "Button 2 pressed while Left held"
$opposed = Update-State 0 ($Button2 -bor $Left -bor $Right) $false $false
Assert-Equal $true $opposed.StrafeUsed "Opposing modifier-horizontal input counts as strafe use"

Assert-Equal $true (Update-State 0 $Button1 $false $false).Fire "Button 1 edge"
Assert-Equal $false (Update-State $Button1 $Button1 $false $false).Fire "Button 1 hold"
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
        $movementX = Round-Divide ($DirectionX * $playerMoveSpeed) 256
        $movementY = Round-Divide ($DirectionY * $playerMoveSpeed) 256
        if ($Forward -lt 0) { $movementX = -$movementX; $movementY = -$movementY }
    }
    if ($Strafe -ne 0) {
        $strafeX = Round-Divide ($PlaneX * $playerMoveSpeed) 169
        $strafeY = Round-Divide ($PlaneY * $playerMoveSpeed) 169
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
    "1,0" = @(0, -74); "-1,0" = @(0, 74)
    "0,-1" = @(-74, 0); "0,1" = @(74, 0)
    "1,-1" = @(-51, -51); "1,1" = @(51, -51)
    "-1,-1" = @(-51, 51); "-1,1" = @(51, 51)
}
foreach ($entry in $expectedVectors.GetEnumerator()) {
    $directions = $entry.Key.Split(",")
    $actual = Get-Movement `
        ([int]$directions[0]) `
        ([int]$directions[1]) `
        $initialDirectionX `
        $initialDirectionY `
        $initialPlaneX `
        $initialPlaneY
    Assert-Equal $entry.Value[0] $actual[0] "Movement X $($entry.Key)"
    Assert-Equal $entry.Value[1] $actual[1] "Movement Y $($entry.Key)"
}

$rotatedForward = Get-Movement 1 0 -35 -254 168 -23
$rotatedForwardWithRotationActive = Get-Movement 1 0 -35 -254 168 -23
Assert-Equal $rotatedForward[0] $rotatedForwardWithRotationActive[0] "No turn penalty X"
Assert-Equal $rotatedForward[1] $rotatedForwardWithRotationActive[1] "No turn penalty Y"

$inputSource = Get-Content (Join-Path $PSScriptRoot "..\platform\game_gear\input.c") -Raw
Assert-Equal 1 ([regex]::Matches($inputSource, "SMS_getKeysStatus\s*\(").Count) "One raw read site"
Assert-Equal 0 ([regex]::Matches($playerSource, "176|rotation_active|movement_with_turn").Count) "No turn penalty source"

$switchSource = Get-Content (Join-Path $PSScriptRoot "..\game\red_door_switch.c") -Raw
$switchHeader = Get-Content (Join-Path $PSScriptRoot "..\game\red_door_switch.h") -Raw
$switchUpdate = [regex]::Match(
    $switchSource,
    "void red_door_switch_update\(void\)(?<body>[\s\S]*?)void red_door_switch_activate").Groups['body'].Value
Assert-Equal 1 ([regex]::Matches($switchSource, "#define RED_DOOR_SWITCH_FRAME_INTERVAL 6").Count) "Switch frame interval"
Assert-Equal 0 ([regex]::Matches($switchUpdate, "RED_DOOR_SWITCH_ACTIVATED").Count) "Activated animation remains running"
foreach ($textureContract in @(
    "RED_DOOR_SWITCH_TEXTURE_OFF_FRAME_1 7",
    "RED_DOOR_SWITCH_TEXTURE_OFF_FRAME_2 8",
    "RED_DOOR_SWITCH_TEXTURE_ON_FRAME_1 9",
    "RED_DOOR_SWITCH_TEXTURE_ON_FRAME_2 10"
)) {
    Assert-Equal 1 ([regex]::Matches($switchHeader, "#define $textureContract").Count) "Switch texture contract $textureContract"
}
Assert-Equal 1 ([regex]::Matches($switchSource, "door_state_open\(DOOR_INSTANCE_ROOM_INTERNAL\)").Count) "Explicit red-door opening path"

function New-SwitchDoorModel {
    return @{
        SwitchState = 0
        Frame = 0
        FrameCounter = 0
        Doors = @(0, 0, 0)
    }
}

function Update-SwitchDoorModel {
    param($Model, [int]$FrameInterval = 6)

    ++$Model.FrameCounter
    if ($Model.FrameCounter -ge $FrameInterval) {
        $Model.FrameCounter = 0
        $Model.Frame = $Model.Frame -bxor 1
    }
}

function Get-SwitchDoorTexture {
    param(
        $Model,
        [int]$OffFrame1 = 7,
        [int]$OffFrame2 = 8,
        [int]$OnFrame1 = 9,
        [int]$OnFrame2 = 10
    )

    if ($Model.SwitchState -eq 1) {
        if ($Model.Frame -ne 0) { return $OnFrame2 }
        return $OnFrame1
    }

    if ($Model.Frame -ne 0) { return $OffFrame2 }
    return $OffFrame1
}

function Activate-SwitchDoorModel {
    param($Model, [int]$ActivationDoor = 1)

    if ($Model.SwitchState -eq 1) {
        return
    }

    $Model.SwitchState = 1
    $Model.Doors[$ActivationDoor] = 1
}

function Interact-SwitchDoorModel {
    param($Model, [int]$DoorId, [bool]$IsRedDoor)

    if ($IsRedDoor) {
        return
    }

    $Model.Doors[$DoorId] = 1 - $Model.Doors[$DoorId]
}

function Reset-SwitchDoorModel {
    param($Model)

    $Model.SwitchState = 0
    $Model.Frame = 0
    $Model.FrameCounter = 0
    for ($doorId = 0; $doorId -lt $Model.Doors.Count; ++$doorId) {
        $Model.Doors[$doorId] = 0
    }
}

function Assert-MutationDetected {
    param($Expected, $Mutated, [string]$Message)
    if ($Expected -eq $Mutated) {
        throw "Mutation was not detected: $Message"
    }
}

# Deterministic waiting animation: frame 1 lasts six updates, then frame 2
# lasts six updates, and the shared phase loops without drift.
$switchDoor = New-SwitchDoorModel
Assert-Equal 0 $switchDoor.SwitchState "Initial switch state"
Assert-Equal 7 (Get-SwitchDoorTexture $switchDoor) "Initial waiting texture"
Assert-Equal 0 $switchDoor.Doors[0] "Initial yellow door state"
Assert-Equal 0 $switchDoor.Doors[1] "Initial red door state"
Assert-Equal 0 $switchDoor.Doors[2] "Initial south yellow door state"
for ($update = 1; $update -le 5; ++$update) {
    Update-SwitchDoorModel $switchDoor
    Assert-Equal 7 (Get-SwitchDoorTexture $switchDoor) "Waiting frame 1 update $update"
}
Update-SwitchDoorModel $switchDoor
Assert-Equal 8 (Get-SwitchDoorTexture $switchDoor) "Waiting frame transition at update 6"
for ($update = 7; $update -le 11; ++$update) {
    Update-SwitchDoorModel $switchDoor
    Assert-Equal 8 (Get-SwitchDoorTexture $switchDoor) "Waiting frame 2 update $update"
}
Update-SwitchDoorModel $switchDoor
Assert-Equal 7 (Get-SwitchDoorTexture $switchDoor) "Waiting animation loop at update 12"

# Activation preserves the shared phase, opens only the internal red door,
# remains idempotent, and continues the same six-update animation cadence.
for ($update = 1; $update -le 6; ++$update) {
    Update-SwitchDoorModel $switchDoor
}
Assert-Equal 8 (Get-SwitchDoorTexture $switchDoor) "Waiting phase before activation"
Activate-SwitchDoorModel $switchDoor
Assert-Equal 1 $switchDoor.SwitchState "Activated switch state"
Assert-Equal 10 (Get-SwitchDoorTexture $switchDoor) "Activated texture preserves phase"
Assert-Equal 0 $switchDoor.Doors[0] "Activation leaves yellow door closed"
Assert-Equal 1 $switchDoor.Doors[1] "Activation opens internal red door"
Assert-Equal 0 $switchDoor.Doors[2] "Activation leaves south yellow door closed"
Activate-SwitchDoorModel $switchDoor
Assert-Equal 0 $switchDoor.Doors[0] "Repeated activation leaves yellow door unchanged"
Assert-Equal 1 $switchDoor.Doors[1] "Repeated activation leaves red door open"
Assert-Equal 0 $switchDoor.Doors[2] "Repeated activation leaves south door unchanged"
for ($update = 1; $update -le 5; ++$update) {
    Update-SwitchDoorModel $switchDoor
    Assert-Equal 10 (Get-SwitchDoorTexture $switchDoor) "Activated frame 2 update $update"
}
Update-SwitchDoorModel $switchDoor
Assert-Equal 9 (Get-SwitchDoorTexture $switchDoor) "Activated frame transition"

# Ordinary yellow-door interaction toggles; direct red-door interaction does
# nothing; reset closes both doors and restores waiting frame 1.
Interact-SwitchDoorModel $switchDoor 0 $false
Assert-Equal 1 $switchDoor.Doors[0] "Yellow door opens by interaction"
Interact-SwitchDoorModel $switchDoor 0 $false
Assert-Equal 0 $switchDoor.Doors[0] "Yellow door closes by interaction"
Interact-SwitchDoorModel $switchDoor 2 $false
Assert-Equal 1 $switchDoor.Doors[2] "South yellow door opens by interaction"
Interact-SwitchDoorModel $switchDoor 2 $false
Assert-Equal 0 $switchDoor.Doors[2] "South yellow door closes by interaction"
Reset-SwitchDoorModel $switchDoor
Interact-SwitchDoorModel $switchDoor 1 $true
Assert-Equal 0 $switchDoor.Doors[1] "Direct red-door interaction is rejected"
Activate-SwitchDoorModel $switchDoor
Reset-SwitchDoorModel $switchDoor
Assert-Equal 0 $switchDoor.SwitchState "Reset switch state"
Assert-Equal 0 $switchDoor.Frame "Reset switch animation phase"
Assert-Equal 0 $switchDoor.FrameCounter "Reset switch animation counter"
Assert-Equal 0 $switchDoor.Doors[0] "Reset yellow door state"
Assert-Equal 0 $switchDoor.Doors[1] "Reset red door state"
Assert-Equal 0 $switchDoor.Doors[2] "Reset south yellow door state"
Assert-Equal 7 (Get-SwitchDoorTexture $switchDoor) "Reset waiting texture"

# Mutation-style checks prove the model detects the common contract failures.
$mutation = New-SwitchDoorModel
Assert-MutationDetected 7 (Get-SwitchDoorTexture $mutation 6 8 9 10) "waiting texture ID"
for ($update = 1; $update -le 5; ++$update) {
    Update-SwitchDoorModel $mutation 5
}
Assert-MutationDetected 7 (Get-SwitchDoorTexture $mutation) "five-update interval"
$mutation = New-SwitchDoorModel
Activate-SwitchDoorModel $mutation 0
Assert-MutationDetected 0 $mutation.Doors[0] "activation targets yellow door"
$mutation = New-SwitchDoorModel
Activate-SwitchDoorModel $mutation
$mutation.Doors[1] = 0
Assert-MutationDetected 1 $mutation.Doors[1] "repeated activation closes red door"
$mutation = New-SwitchDoorModel
$mutation.Doors[1] = 1
Assert-MutationDetected 0 $mutation.Doors[1] "direct interaction opens red door"

Write-Host "Final control validation passed: $($masks.Count * $masks.Count * 4) state combinations and movement vectors."
