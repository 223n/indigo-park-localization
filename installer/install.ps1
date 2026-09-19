# Indigo Park 日本語化 導入ツール
#
# ゲームを探して MOD を置き、言語の一覧に「日本語」を足します。
# 言語の一覧を足すファイルは、お使いのゲームから作ります。配布物には含みません。
# エンディングの歌詞の訳を出すため、UE4SS をゲームの実行ファイルのフォルダに置きます。
#
#   .\install.ps1                  自動でゲームを探す
#   .\install.ps1 -GamePath "..."  場所を指定する
#   .\install.ps1 -NoLanguage      言語の一覧は触らない
#   .\install.ps1 -NoLyrics        エンディングの歌詞の字幕（UE4SS）は入れない
#   .\install.ps1 -DryRun          何をするかだけ表示する

[CmdletBinding()]
param(
    [string]$GamePath,
    [switch]$NoLanguage,
    [switch]$NoLyrics,
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$ModPak = 'IndigoParkJP_P.pak'
$LangName = 'zzz_IndigoParkJP_lang_P'
$EngineVersion = 'UE5_2'

# エンディングの歌詞の字幕。uninstall.ps1 と揃える
$LyricsMod = 'IndigoParkJP_Lyrics'
$Ue4ssFiles = @('dwmapi.dll', 'UE4SS.dll', 'UE4SS-settings.ini')
# この導入ツールが UE4SS を置いた印。取り外しで UE4SS を消してよいかの判断に使う
$Ue4ssMarker = 'IndigoParkJP_UE4SS.txt'

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
$win64 = Join-Path $game 'RaccoonCh1\Binaries\Win64'

# --- 配布物を確かめる
Step '配布物を確かめる'
$srcPak = Join-Path $Root "mod\$ModPak"
if (-not (Test-Path $srcPak)) { Die "$ModPak が見つかりません。zip を展開し直してください" }
Ok ("{0}（{1:N1} MB）" -f $ModPak, ((Get-Item $srcPak).Length / 1MB))

if ($DryRun) {
    Write-Host ''
    Write-Host '  -DryRun のため、ここから先は行いません' -ForegroundColor Yellow
    Write-Host "  置く場所: $mods"
    Write-Host "  歌詞の字幕（UE4SS）を置く場所: $win64"
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

# --- エンディングの歌詞の字幕を入れる
if ($NoLyrics) {
    Warn '-NoLyrics のため、エンディングの歌詞の字幕は入れません'
} else {
    Step 'エンディングの歌詞の字幕を入れる（UE4SS）'
    $srcUe4ss = Join-Path $Root 'ue4ss'
    $srcMod = Join-Path $srcUe4ss "Mods\$LyricsMod"
    $srcLyrics = Join-Path $srcMod 'lyrics.srt'
    $marker = Join-Path $win64 $Ue4ssMarker
    $ours = Test-Path $marker
    if (-not (Test-Path $srcLyrics)) {
        Warn '字幕のファイルが見つかりません。入れません'
    } elseif (-not (Select-String -LiteralPath $srcLyrics -Pattern '-->' -SimpleMatch -Quiet)) {
        Ok '歌詞の訳がまだ無いため、入れません'
    } elseif (-not (Test-Path (Join-Path $win64 'RaccoonCh1-Win64-Shipping.exe'))) {
        Warn "ゲームの実行ファイルが見つからないため、入れません: $win64"
    } elseif ($win64 -match '[^\x00-\x7F]') {
        # UE4SS は MOD のスクリプトの場所を ANSI の文字列にして読むため、英数字以外が入ると読めない
        Warn 'ゲームの場所に英数字以外の文字が入っているため、入れません'
        Warn 'UE4SS が、このような場所にある MOD を読み込めないためです'
    } else {
        $modsDir = $null
        if (Test-Path (Join-Path $win64 'ue4ss\UE4SS.dll')) {
            # 利用者が入れた新しい並びの UE4SS。本体には触らず、MOD だけ足す
            $modsDir = Join-Path $win64 'ue4ss\Mods'
            Ok 'すでにある UE4SS を使います'
        } elseif ((Test-Path (Join-Path $win64 'UE4SS.dll')) -and -not $ours) {
            $modsDir = Join-Path $win64 'Mods'
            Ok 'すでにある UE4SS を使います'
        } elseif ((Test-Path (Join-Path $win64 'dwmapi.dll')) -and -not $ours) {
            Warn '同じ名前のファイル（dwmapi.dll）がすでにあるため、入れません'
            Warn 'ほかの MOD の道具が使っている可能性があります'
        } else {
            foreach ($f in $Ue4ssFiles) {
                Copy-Item (Join-Path $srcUe4ss $f) (Join-Path $win64 $f) -Force
            }
            $utf8 = New-Object System.Text.UTF8Encoding($false)
            [System.IO.File]::WriteAllText($marker,
                "Indigo Park 日本語化の導入ツールが UE4SS を置いた印です。`r`n" +
                "取り外しツールが、UE4SS を消してよいかの判断に使います。`r`n", $utf8)
            $modsDir = Join-Path $win64 'Mods'
            Ok "UE4SS を置いた: $win64"
        }
        if ($modsDir) {
            $dst = Join-Path $modsDir $LyricsMod
            if (Test-Path $dst) { Remove-Item $dst -Recurse -Force }
            New-Item -ItemType Directory -Path $modsDir -Force | Out-Null
            Copy-Item $srcMod $dst -Recurse -Force
            Ok '字幕の MOD を置いた（エンディングで歌詞の訳が画面の下に出ます）'
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
