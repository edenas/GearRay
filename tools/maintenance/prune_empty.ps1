$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Split-Path (Split-Path $PSScriptRoot -Parent) -Parent)).TrimEnd('\','/')
if($root -ine 'D:\mano_projektai\GearRay'){throw 'Unexpected root'}
$boundary=$root+[IO.Path]::DirectorySeparatorChar
$out=Join-Path $root 'docs/maintenance/2026-10-23/implementation'
$paths=Get-Content -LiteralPath (Join-Path $out 'empty-directory-candidates.json') -Raw -Encoding UTF8 | ConvertFrom-Json
$removed=New-Object 'Collections.Generic.List[string]'
foreach($relative in ($paths | Sort-Object Length -Descending)) {
    if([IO.Path]::IsPathRooted($relative) -or $relative.Contains(':') -or $relative.Contains('\') -or @($relative.Split('/')|Where-Object{$_ -in @('..','.','')}).Count){throw 'Unsafe directory path'}
    $path=[IO.Path]::GetFullPath((Join-Path $root $relative))
    if(!$path.StartsWith($boundary,[StringComparison]::OrdinalIgnoreCase)){throw 'Outside project'}
    $part=$path
    while($part -ine $root) {
        if(Test-Path -LiteralPath $part) {if((Get-Item -LiteralPath $part -Force).Attributes -band [IO.FileAttributes]::ReparsePoint){throw 'Reparse component'}}
        $part=[IO.Path]::GetDirectoryName($part)
    }
    if((Test-Path -LiteralPath $path -PathType Container) -and @(Get-ChildItem -LiteralPath $path -Force).Count -eq 0) {
        Remove-Item -LiteralPath $path -Force
        $removed.Add($relative)
    }
}
$removed|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'empty-directories-removed.json') -Encoding UTF8
Write-Output "Removed $($removed.Count) checked empty directories; nonempty directories retained"
