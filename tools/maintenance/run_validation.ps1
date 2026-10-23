param([ValidateSet('Build','Regression')][string]$Phase='Build')
$ErrorActionPreference='Stop'
$root=[IO.Path]::GetFullPath((Split-Path (Split-Path $PSScriptRoot -Parent) -Parent))
if($root.TrimEnd('\') -ine 'D:\mano_projektai\GearRay'){throw 'Unexpected root'}
Set-Location -LiteralPath $root
$out=Join-Path $root 'docs/maintenance/2026-10-23/implementation'
$temp=Join-Path $root 'build/maintenance/tmp'
New-Item -ItemType Directory -Force -Path $temp | Out-Null
$savedTemp=$env:TEMP;$savedTmp=$env:TMP;$savedModules=$env:PSModulePath
function Run([string]$Name,[string]$Program,[string[]]$Arguments) {
    & $Program @Arguments *> (Join-Path $out ($Name+'.log'))
    if($LASTEXITCODE -ne 0){throw "$Name failed with exit $LASTEXITCODE; retained log"}
    Write-Output "$Name PASS"
}
function Release-Identity {
    $rom=Join-Path $root 'rom/GearRay.gg'
    if((Get-Item -LiteralPath $rom).Length -ne 65536 -or (Get-FileHash -LiteralPath $rom).Hash -ine '3632006ED68FCBCBACF9AA693C92560520DF496E1E4AC23CF2CB6E1DF88D3340'){throw 'Unexplained accepted ROM identity change'}
}
try {
    $env:TEMP=$temp;$env:TMP=$temp
    $env:PSModulePath='C:\Windows\System32\WindowsPowerShell\v1.0\Modules;'+$savedModules
    if($Phase -eq 'Build') {
        if(Test-Path -LiteralPath 'build/release'){throw 'Fresh Release requires absent build/release'}
        Run 'release-clean-build' 'cmd.exe' @('/d','/c',(Join-Path $root 'build.bat'))
        Release-Identity
        $other=Join-Path $root 'build/maintenance/launcher-cwd';New-Item -ItemType Directory -Force -Path $other|Out-Null
        Push-Location -LiteralPath $other
        try {Run 'release-launcher-other-cwd' 'cmd.exe' @('/d','/c',(Join-Path $root 'build.bat'))} finally {Pop-Location}
        Release-Identity
        Run 'profile-build' 'cmd.exe' @('/d','/c',(Join-Path $root 'build-profile.bat'))
        Release-Identity
        Run 'release-full-audit' 'powershell' @('-NoProfile','-ExecutionPolicy','Bypass','-File','tools/full_z80_audit.ps1','-BuildDirectory','build/release','-RomPath','rom/GearRay.gg','-RunValidators')
        $results=Get-Content -LiteralPath 'build/release/full-z80-audit/validators.json' -Raw|ConvertFrom-Json
        if($results.Count -ne 24 -or @($results|Where-Object ExitCode -ne 0).Count){throw 'Validator count/result gate failed'}
        Run 'release-dispatch-mutations' 'powershell' @('-NoProfile','-ExecutionPolicy','Bypass','-File','tools/test_production_dispatch_scan.ps1','-BuildDirectory','build/release')
        Run 'profile-structural-audit' 'powershell' @('-NoProfile','-ExecutionPolicy','Bypass','-File','tools/full_z80_audit.ps1','-BuildDirectory','build/profile','-RomPath','build/profile/rom/GearRay-profile.gg')
        Release-Identity
        @{status='PASS';fresh_release=$true;canonical_sha256=(Get-FileHash -LiteralPath 'rom/GearRay.gg').Hash;profile_did_not_clobber_release=$true;launcher_other_cwd=$other;validators=$results.Count}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'phase-8-build-gate.json') -Encoding UTF8
    } else {
        Release-Identity
        Run 'release-driver-build' 'py' @('-3.12','tools/performance/build_driver.py','--java-tools','build/release/java-tools')
        Run 'release-profiler-self-test' 'py' @('-3.12','tools/performance/test_profiler.py','--java-tools','build/release/java-tools','--output','docs/maintenance/2026-10-23/implementation/release-profiler-self-test.json')
        Run 'release-replay' 'py' @('-3.12','tools/performance/benchmark.py','256','--warmup','32','--logical-input','--build','build/release','--java-tools','build/release/java-tools','--only','A_static,B_rotation,C_forward,F_geometry,G_zombies,I_pistol,I_shotgun,J_lod,L_mixed,M_authored','--output','build/release/cleanup-replay')
        Run 'restore-accepted-replay' 'py' @('-3.12','tools/maintenance/restore_history.py','--entry','docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/selected-replay/frame-samples.csv','--dest','build/history-restore/accepted-replay')
        Run 'release-replay-comparison' 'py' @('-3.12','tools/maintenance/compare_replay.py','--actual','build/release/cleanup-replay','--accepted','build/history-restore/accepted-replay/docs/performance/2026-10-19/post-implementation-followup/astra-final-review/evidence/selected-replay/frame-samples.csv','--output','docs/maintenance/2026-10-23/implementation/release-replay-comparison.json')
        foreach($mode in @('sprite','occlusion','wrapper','hud','playthrough','wall','ray','material','camera','prep','transitions')) {
            Run ('compiled-'+$mode) 'py' @('-3.12','tools/maintenance/run_regression.py',$mode,'--build','build/release','--rom','rom/GearRay.gg','--java-tools','build/release/java-tools','--output',('docs/maintenance/2026-10-23/implementation/compiled-regressions/'+$mode))
        }
        Release-Identity
        @{status='PASS';full_replay_records=2880;compiled_modes=11}|ConvertTo-Json|Set-Content -LiteralPath (Join-Path $out 'phase-9-regression-gate.json') -Encoding UTF8
    }
} finally {$env:TEMP=$savedTemp;$env:TMP=$savedTmp;$env:PSModulePath=$savedModules}
