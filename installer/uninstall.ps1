# Indigo Park 日本語化 取り外しツール
#
# 置いたファイルを消し、言語の設定を英語に戻します。
# ゲーム本体のファイルは触りません。
# UE4SS は、導入ツールが置いたもので、ほかの UE4SS の MOD が無いときだけ消します。
#
#   .\uninstall.ps1                  自動でゲームを探す
#   .\uninstall.ps1 -GamePath "..."  場所を指定する
#   .\uninstall.ps1 -KeepLanguage    言語の設定は戻さない

[CmdletBinding()]
param(
    [string]$GamePath,
    [switch]$KeepLanguage
)

$ErrorActionPreference = 'Stop'

$Targets = @(
    'IndigoParkJP_P.pak',
    'zzz_IndigoParkJP_lang_P.pak',
    'zzz_IndigoParkJP_lang_P.ucas',
    'zzz_IndigoParkJP_lang_P.utoc'
)

# エンディングの歌詞の字幕。install.ps1 と揃える
$LyricsMod = 'IndigoParkJP_Lyrics'
# UE4SS.log は UE4SS が動いたときに作る
$Ue4ssFiles = @('dwmapi.dll', 'UE4SS.dll', 'UE4SS-settings.ini', 'UE4SS.log')
$Ue4ssMarker = 'IndigoParkJP_UE4SS.txt'

function Step($text) { Write-Host "▶ $text" -ForegroundColor Cyan }
function Ok($text)   { Write-Host "  ✓ $text" -ForegroundColor Green }
function Warn($text) { Write-Host "  ! $text" -ForegroundColor Yellow }
function Die($text)  { Write-Host "  × $text" -ForegroundColor Red; exit 1 }

function Test-GameDir([string]$dir) {
    if (-not $dir) { return $false }
    Test-Path (Join-Path $dir 'RaccoonCh1\Content\Paks\RaccoonCh1-Windows.utoc')
}

function Find-Game {
    $candidates = @()
    try {
        $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -Name SteamPath -ErrorAction Stop).SteamPath
    } catch { $steam = $null }
    if ($steam) {
        $steam = $steam -replace '/', '\'
        $candidates += Join-Path $steam 'steamapps\common\Indigo Park'
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            $text = Get-Content $vdf -Raw
            foreach ($m in [regex]::Matches($text, '"path"\s+"([^"]+)"')) {
                $lib = $m.Groups[1].Value -replace '\\\\', '\'
                $candidates += Join-Path $lib 'steamapps\common\Indigo Park'
            }
        }
    }
    $candidates += 'C:\Program Files (x86)\Steam\steamapps\common\Indigo Park'
    foreach ($c in $candidates | Select-Object -Unique) {
        if (Test-GameDir $c) { return $c }
    }
    return $null
}

Write-Host ''
Write-Host 'Indigo Park 日本語化 取り外しツール' -ForegroundColor White
Write-Host ''

Step 'ゲームの場所を調べる'
if ($GamePath) {
    if (-not (Test-GameDir $GamePath)) { Die "指定の場所にゲームが見つかりません: $GamePath" }
    $game = $GamePath
} else {
    $game = Find-Game
    if (-not $game) { Die 'ゲームが見つかりません。-GamePath で場所を指定してください' }
}
Ok $game

$mods = Join-Path $game 'RaccoonCh1\Content\Paks\~mods'

Step '置いたファイルを消す'
$removed = 0
foreach ($t in $Targets) {
    $p = Join-Path $mods $t
    if (Test-Path $p) { Remove-Item $p -Force; Ok $t; $removed++ }
}
if ($removed -eq 0) { Warn '消すものがありませんでした' }

if ((Test-Path $mods) -and -not (Get-ChildItem $mods -Force)) {
    Remove-Item $mods -Force
    Ok '空になった ~mods を消した'
}

Step 'エンディングの歌詞の字幕を消す'
$win64 = Join-Path $game 'RaccoonCh1\Binaries\Win64'
$found = $false
foreach ($dir in @((Join-Path $win64 'Mods'), (Join-Path $win64 'ue4ss\Mods'))) {
    $p = Join-Path $dir $LyricsMod
    if (Test-Path $p) { Remove-Item $p -Recurse -Force; Ok $LyricsMod; $found = $true }
}
$marker = Join-Path $win64 $Ue4ssMarker
if (Test-Path $marker) {
    $found = $true
    $modsDir = Join-Path $win64 'Mods'
    if (@(Get-ChildItem $modsDir -Force -ErrorAction SilentlyContinue).Count -gt 0) {
        Warn 'ほかの UE4SS の MOD があるため、UE4SS は残します'
    } else {
        foreach ($f in $Ue4ssFiles) {
            $p = Join-Path $win64 $f
            if (Test-Path $p) { Remove-Item $p -Force }
        }
        if (Test-Path $modsDir) { Remove-Item $modsDir -Force }
        Remove-Item $marker -Force
        Ok 'UE4SS を消した'
    }
}
if (-not $found) { Warn '消すものがありませんでした' }

if (-not $KeepLanguage) {
    Step '言語の設定を英語に戻す'
    $cfg = Join-Path $env:LOCALAPPDATA 'RaccoonCh1\Saved\Config\MenuSystemConfig.json'
    if (Test-Path $cfg) {
        # ゲームは BOM 無しの UTF-8 で書く。Windows PowerShell 5.1 の Get-Content と Set-Content は
        # これを ANSI として読み、書くときに BOM を付けるため、.NET で UTF-8 のまま読み書きする
        $text = [System.IO.File]::ReadAllText($cfg)
        if ($text -match '"GameLanguage":"ja"') {
            $utf8 = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText($cfg, ($text -replace '"GameLanguage":"ja"', '"GameLanguage":"en"'), $utf8)
            Ok '戻した'
        } else {
            Ok '日本語ではなかったため、そのままにした'
        }
    } else {
        Warn '設定ファイルが見つかりませんでした'
    }
}

Write-Host ''
Write-Host '▶ 済みました' -ForegroundColor White
Write-Host ''
