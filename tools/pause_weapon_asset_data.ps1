# Development-only decoder for the production precomposed row format.
function Get-PauseWeaponArrays([string]$Header,[int]$ScrollX,[int]$ScrollY) {
    $case=[regex]::Match($Header,"(?s)#if SCROLL_X == $ScrollX && SCROLL_Y == $ScrollY\s*(.*?)#endif")
    if(!$case.Success){throw 'Missing pause weapon scroll case'}
    $arrays=@{}
    foreach($m in [regex]::Matches($case.Groups[1].Value,'(?s)static const unsigned char (\w+)\[(\d+)\]\s*=\s*\{(.*?)\};')){
        $bytes=@([regex]::Matches($m.Groups[3].Value,'0x[0-9a-f]+')|ForEach-Object {[Convert]::ToInt32($_.Value.Substring(2),16)})
        if($bytes.Count -ne [int]$m.Groups[2].Value){throw 'Pause weapon declared payload size mismatch'}
        $arrays[$m.Groups[1].Value]=$bytes
    }
    return $arrays
}
function Expand-PauseWeaponData($Arrays,[string]$Symbol,[int]$ScrollX,[int]$ScrollY,[bool]$Side) {
    $rows=$Arrays["${Symbol}_rows"]
    $name=if($Side){"${Symbol}_side"}else{$Symbol}
    $tokens=$Arrays[$name];$ids=[Collections.Generic.List[int]]::new()
    for($t=0;$t -lt $tokens.Count;$t++){
        $token=$tokens[$t];$id=$token -band 127;$ids.Add($id)
        if($token -band 128){
            $t++
            if($t -ge $tokens.Count -or $tokens[$t] -le 0){throw 'Invalid pause row repeat token'}
            for($r=0;$r -lt $tokens[$t];$r++){$ids.Add($id)}
        }
    }
    $count=(4-[int]($ScrollX -ne 0))*(4-[int]($ScrollY -ne 0))*8
    if(!$rows -or $rows.Count % 4 -ne 0 -or $rows.Count/4 -gt 128 -or $ids.Count -ne $count){throw 'Invalid pause weapon row dictionary/index dimensions'}
    $result=foreach($id in $ids){
        if($id -lt 0 -or $id*4+3 -ge $rows.Count){throw 'Pause weapon row index outside dictionary'}
        $rows[($id*4)..($id*4+3)]
    }
    return ,([int[]]$result)
}
