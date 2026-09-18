# Indigo Park 日本語化 導入ツール
#
# ゲームを探して MOD を置き、言語の一覧に「日本語」を足します。
# 言語の一覧を足すファイルは、お使いのゲームから作ります。配布物には含みません。
#
#   .\install.ps1                  自動でゲームを探す
#   .\install.ps1 -GamePath "..."  場所を指定する
#   .\install.ps1 -NoLanguage      言語の一覧は触らない
#   .\install.ps1 -DryRun          何をするかだけ表示する

[CmdletBinding()]
param(
    [string]$GamePath,
    [switch]$NoLanguage,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$AppId = '2504480'
$ModPak = 'IndigoParkJP_P.pak'
$LangName = 'zzz_IndigoParkJP_lang_P'
$EngineVersion = 'UE5_2'

$Root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $Root 'mod'))) { $Root = $PSScriptRoot }

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
Write-Host 'Indigo Park 日本語化 導入ツール' -ForegroundColor White
Write-Host ''

# --- ゲームを探す
Step 'ゲームの場所を調べる'
if ($GamePath) {
    if (-not (Test-GameDir $GamePath)) { Die "指定の場所にゲームが見つかりません: $GamePath" }
    $game = $GamePath
} else {
    $game = Find-Game
    if (-not $game) {
        Warn 'Steam から見つけられませんでした'
        $entered = Read-Host '  ゲームのフォルダを入力してください（Indigo Park フォルダ）'
        if (-not (Test-GameDir $entered)) { Die "その場所にゲームが見つかりません: $entered" }
        $game = $entered
    }
}
Ok $game

$paks = Join-Path $game 'RaccoonCh1\Content\Paks'
$mods = Join-Path $paks '~mods'

# --- 配布物を確かめる
Step '配布物を確かめる'
$srcPak = Join-Path $Root "mod\$ModPak"
if (-not (Test-Path $srcPak)) { Die "$ModPak が見つかりません。zip を展開し直してください" }
Ok ("{0}（{1:N1} MB）" -f $ModPak, ((Get-Item $srcPak).Length / 1MB))

if ($DryRun) {
    Write-Host ''
    Write-Host '  -DryRun のため、ここから先は行いません' -ForegroundColor Yellow
    Write-Host "  置く場所: $mods"
    exit 0
}

# --- 翻訳とフォントを置く
Step '翻訳とフォントを置く'
New-Item -ItemType Directory -Path $mods -Force | Out-Null
Copy-Item $srcPak (Join-Path $mods $ModPak) -Force
Ok "$mods に置いた"

# --- 言語の一覧に日本語を足す
if ($NoLanguage) {
    Warn '-NoLanguage のため、言語の一覧は触りません'
} else {
    Step '言語の一覧に「日本語」を足す'
    $retoc = Join-Path $PSScriptRoot 'retoc.exe'
    if (-not (Test-Path $retoc)) { $retoc = Join-Path $Root 'tools\retoc.exe' }
    if (-not (Test-Path $retoc)) {
        Warn 'retoc.exe が見つかりません。言語の一覧は足しません'
    } else {
        $work = Join-Path ([System.IO.Path]::GetTempPath()) ("ipjp_" + [guid]::NewGuid().ToString('N'))
        New-Item -ItemType Directory -Path $work -Force | Out-Null
        try {
            & $retoc to-legacy -f DA_GameLanguage --no-shaders --version $EngineVersion $paks $work 2>&1 | Out-Null
            $uexp = Get-ChildItem $work -Recurse -Filter 'DA_GameLanguage.uexp' | Select-Object -First 1
            if (-not $uexp) { throw '言語のデータが取り出せませんでした' }

            $bytes = [System.IO.File]::ReadAllBytes($uexp.FullName)
            # FString "de" は 03 00 00 00 'd' 'e' 00 の並び。同じ長さの "ja" に置き換える
            $pattern = @(0x03,0x00,0x00,0x00,0x64,0x65,0x00)
            $at = -1
            for ($i = 0; $i -le $bytes.Length - $pattern.Length; $i++) {
                $hit = $true
                for ($j = 0; $j -lt $pattern.Length; $j++) {
                    if ($bytes[$i + $j] -ne $pattern[$j]) { $hit = $false; break }
                }
                if ($hit) { $at = $i; break }
            }
            if ($at -lt 0) { throw '書き換える場所が見つかりませんでした（ゲームの更新で変わった可能性があります）' }
            $bytes[$at + 4] = 0x6A   # j
            $bytes[$at + 5] = 0x61   # a
            [System.IO.File]::WriteAllBytes($uexp.FullName, $bytes)

            $out = Join-Path $mods "$LangName.utoc"
            & $retoc to-zen --version $EngineVersion $work $out 2>&1 | Out-Null
            if (-not (Test-Path $out)) { throw 'IoStore への書き出しに失敗しました' }
            Ok '足した（設定の「言語」で日本語を選べます）'
        } catch {
            Warn "できませんでした: $_"
            Warn 'ドイツ語（Deutsch）を選ぶと日本語で表示されます'
        } finally {
            Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

Write-Host ''
Write-Host '▶ 済みました' -ForegroundColor White
Write-Host ''
Write-Host '  ゲームを起動し、次の順に選んでください。'
Write-Host '    OPTIONS → GAMEPLAY → LANGUAGE → 日本語 → APPLY'
Write-Host ''
Write-Host '  取り外すときは uninstall.bat を実行します。'
Write-Host ''
