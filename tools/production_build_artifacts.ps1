# The generated SDCC linker command file defines production object membership.
# Files merely present beside those objects can be retained development artifacts.
function Get-ProductionBuildRom([string]$BuildDirectory) {
    $directory=[IO.Path]::GetFullPath($BuildDirectory)
    $cache=Get-Content -LiteralPath (Join-Path $directory 'CMakeCache.txt') -Raw
    $name=[regex]::Match($cache,'(?m)^GEAR_RAY_ROM_FILENAME:STRING=(.+)\r?$').Groups[1].Value.Trim()
    $source=[regex]::Match($cache,'(?m)^CMAKE_HOME_DIRECTORY:INTERNAL=(.+)\r?$').Groups[1].Value.Trim()
    if (!$name -or !$source) { throw "Missing configured ROM identity: $directory" }
    $output=[regex]::Match($cache,'(?m)^GEAR_RAY_ROM_DIR:PATH=(.+)\r?$').Groups[1].Value.Trim()
    if (!$output) { $output=Join-Path $source 'rom' } # Frozen historical caches.
    return Join-Path $output $name
}

function Test-ProductionRomPayload([string]$BuildDirectory,[string]$RomPath) {
    $image=[IO.File]::ReadAllBytes($RomPath)
    $upper=0; $checked=0
    foreach($line in Get-Content -LiteralPath (Join-Path $BuildDirectory 'GearRay.ihx')) {
        if(!$line.StartsWith(':')) { continue }
        $count=[Convert]::ToInt32($line.Substring(1,2),16)
        $address=[Convert]::ToInt32($line.Substring(3,4),16)
        $type=[Convert]::ToInt32($line.Substring(7,2),16)
        if($type -eq 4) { $upper=[Convert]::ToInt32($line.Substring(9,4),16)*65536 }
        elseif($type -eq 2) { $upper=[Convert]::ToInt32($line.Substring(9,4),16)*16 }
        elseif($type -eq 0) {
            for($i=0;$i -lt $count;++$i) {
                $virtual=$upper+$address+$i
                $physical=if($virtual -lt 65536){$virtual}else{($virtual -shr 16)*16384+($virtual -band 0x3fff)}
                if($physical -in @(0x7ffa,0x7ffb)) {continue} # makesms checksum owns these bytes.
                $expected=[Convert]::ToInt32($line.Substring(9+2*$i,2),16)
                if($physical -ge $image.Length -or $image[$physical] -ne $expected) { throw "IHX/ROM payload mismatch at virtual 0x$($virtual.ToString('X')) / physical 0x$($physical.ToString('X'))" }
                ++$checked
            }
        }
    }
    Write-Output "- all $checked linked IHX payload bytes match the selected physical ROM (checksum pair excluded)"
}

function Get-ProductionBuildObjects([string]$BuildDirectory) {
    $directory=[IO.Path]::GetFullPath($BuildDirectory).TrimEnd('\','/')
    $linkPath=Join-Path $directory 'GearRay.lk'
    if (!(Test-Path -LiteralPath $linkPath)) { throw "Production linker inputs missing: $linkPath" }
    $objects=@()
    foreach($line in Get-Content -LiteralPath $linkPath) {
        if($line -notmatch '^(.+\.rel)\s*$') { continue }
        $path=$Matches[1].Trim()
        if(![IO.Path]::IsPathRooted($path)) { $path=Join-Path $directory $path }
        $path=[IO.Path]::GetFullPath($path)
        # External crt0/library code is audited separately from local C modules.
        if(!$path.StartsWith($directory+[IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { continue }
        if(!(Test-Path -LiteralPath $path)) { throw "Linked production object missing: $path" }
        $objects+=Get-Item -LiteralPath $path
    }
    foreach($required in @('main','pause_map','startup_logo')) {
        if($required -notin $objects.BaseName) { throw "Required production linker input missing: $required" }
    }
    $objects
}

function Get-ProductionBuildAssembly([string]$BuildDirectory) {
    foreach($object in Get-ProductionBuildObjects $BuildDirectory) {
        $path=[IO.Path]::ChangeExtension($object.FullName,'.asm')
        if(!(Test-Path -LiteralPath $path)) { throw "Linked production assembly missing: $path" }
        Get-Item -LiteralPath $path
    }
}
