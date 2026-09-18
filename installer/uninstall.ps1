# Indigo Park 日本語化 取り外しツール
#
# 置いたファイルを消し、言語の設定を英語に戻します。
# ゲーム本体のファイルは触りません。
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
