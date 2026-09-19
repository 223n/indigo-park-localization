# 調査記録

Steam版Indigo Park（Chapter 1）を日本語化するための、技術的な調べものの記録です。
2026年9月18日に、実際のゲームで確かめた内容をまとめます。

## まとめ

日本語化に必要な入口は見つかりました。
暗号化と署名はありません。
MODの載せ方も実機で確かめてあります。

| やりたいこと                 | できるか                   | 方法                                                       |
|------------------------------|----------------------------|------------------------------------------------------------|
| フォントの差し替え           | **できます（実機で確認）** | `~mods`にpakを置いて`.ufont`を上書きします                 |
| UIの文章の差し替え           | **できます（実機で確認）** | `Content/Localization/Game/<文化>/Game.locres`を置きます   |
| 日本語を選択肢に出す         | **できます（実機で確認）** | `DA_GameLanguage`を書き換えたIoStore形式のMODを足します    |
| 本編の字幕の差し替え         | **できます**               | 字幕は音声アセットの中のFTextです。`.locres`で差し替えます |
| エンディングの歌詞の訳を出す | **できます（実機で確認）** | UE4SSのLua MODで、動画の上に字幕を重ねます                 |

メニューと設定画面が日本語で表示されるところまで、実機で確認しました。
「つづきから」「はじめから」「ゲームプレイ」「音声」「映像」「操作」「カメラの遅延効果」などが出ます。
日本語を出すにはフォントの差し替えが要ります。
差し替えないと、文字が描画されずに消えます。

## ゲームの構成

| 項目            | 内容                                                              |
|-----------------|-------------------------------------------------------------------|
| エンジン        | Unreal Engine 5.2（実行ファイル内に`++UE5+Release-5.2`）          |
| プロジェクト名  | `RaccoonCh1`                                                      |
| 導入先          | `C:\Program Files (x86)\Steam\steamapps\common\Indigo Park`       |
| SteamのアプリID | `2504480`                                                         |
| パッケージ      | IoStore有効。`.utoc`版5、26,759チャンク、18,395パッケージ         |
| `.pak`          | 版11、4,372ファイル                                               |
| 暗号化          | ありません（AESキーのGUIDはゼロ）                                 |
| 署名            | ありません（`.sig`が存在しません）                                |
| 圧縮            | Oodle（実行ファイルに静的リンク。`oo2core`の単体DLLはありません） |

`.pak`には`.uasset`が1件も入っていません。
中身は`.locres`、`.ufont`、`.ttf`、`.ini`、ICUのデータなど、パッケージ以外の資源だけです。
cooked済みのアセットはすべてIoStore側にあります。

## フォント

ゲームが使うフォントの実体（`.ufont`）は、すべて`.pak`側にあります。

| 用途           | ファイル                                                                       |
|----------------|--------------------------------------------------------------------------------|
| メニューと字幕 | `RefinedMainMenu/Menu/Fonts/Font_Quicksand-*.ufont`                            |
| 設定画面       | `MenuSystemPro/ExampleContent/Art/Fonts/Oswald-*.ufont`、`Kanit-Regular.ufont` |
| 調査システム   | `InspectionSystemPro/ExampleContent/Fonts/Questrial-Regular.ufont`             |

`.ufont`は生のTrueTypeです。
日本語のフォントで上書きすれば差し替わります。

エンジンの最終フォールバックである`Engine/Content/EngineFonts/Faces/DroidSansFallback.ufont`は3.94MBあり、「あ」「ア」「日」を収録しています。
それでも、フォントを差し替えないと日本語は描画されませんでした（後述の「フォントは差し替えが要ります」）。

### 確認できたこと

`Content/Paks/~mods/`に置いたpakは読み込まれ、`.ufont`の上書きが効きます。
`Oswald-Regular.ufont`と`Font_Quicksand-Regular.ufont`を`DroidSansFallback.ufont`で置き換えたところ、設定画面の本文の書体と折り返し位置が変わりました。

## 文章の置き場所

### 読み込まれるのは1か所だけです

`RaccoonCh1/Config/DefaultGame.ini`に`[Internationalization]`のセクションがありません。
そのため、エンジンの既定である`%GAMEDIR%Content/Localization/Game`だけが読まれます。

出荷物には次の2つが入っています。
しかし、**どちらも読み込まれません**。

- `RaccoonCh1/Content/Localization/MenuSystemPro/en/MenuSystemPro.locres`
- `RaccoonCh1/Content/Localization/InspectionSystemPro/en/InspectionSystemPro.locres`

これらはマーケットプレイスのプラグインに付いてきたもので、ゲーム本体の文章とはキーが違います。
書き換えても画面には出ません。

`Content/Localization/Game/de/Game.locres`を`~mods`のpakで足すと、エンジンが実際に読みに行くことは確認しました。

### 画面の文字はウィジェットの中にあります

設定画面の文字列は`MenuSystemPro/ExampleContent/Designs/Design_R/Menus/Settings/WBP_GameSettings_R`の中にFTextとして埋まっています。
FTextは名前空間が空で、キーは32桁の16進数です。

```text
6E1443844C98C1EF9065D481339AE1CF  Camera Delay Effect
47C2816747C534B96C0092B98D855FE8  Viewbob
18F5510A405981AD8523ED8940B4E1D7  Toggles camera following your flashlight effect...
```

この形なら`.locres`で差し替えられます。
キーはアセットから機械的に取り出せます。

## 言語の選択

設定画面に「LANGUAGE」の項目があります。

選べる値は`MenuSystemPro/Blueprints/Settings/SettingsData/DA_GameLanguage`に入っており、74バイトの中身は`GameLanguage`、`en`、`en`、`de`だけです。
つまり**英語とドイツ語の2つしかありません**。

適用は`BP_GameLanguageApply`が行い、`Array_Find`で値を探してから`SetCurrentCulture`を呼びます。
一覧にない値は見つからないため、`ja`を指定しても英語に戻されます。

選んだ値は次の2か所に保存されます。

| ファイル                                                              | 項目             |
|-----------------------------------------------------------------------|------------------|
| `%LOCALAPPDATA%\RaccoonCh1\Saved\Config\MenuSystemConfig.json`        | `"GameLanguage"` |
| `%LOCALAPPDATA%\RaccoonCh1\Saved\Config\Windows\GameUserSettings.ini` | `Culture`        |

`MenuSystemConfig.json`の`"GameLanguage"`を`de`にすると、文化の切り替えは働きます。
LANGUAGEの値の表示が「ENGLISH」から「ENGLISCH」に変わることで確かめました。

ICUのデータは日本語の分も同梱されています（`ja.res`と`ja_JP.res`）。
そのためICU側の制約はありません。

## 道具

| 道具  | 版    | 用途                                    |
|-------|-------|-----------------------------------------|
| repak | 0.2.3 | `.pak`の読み書き。Oodleの解凍も行います |
| retoc | 0.1.5 | IoStoreとレガシー形式の相互変換         |

置き場所は`%LOCALAPPDATA%\Programs\ue-modding-tools`です。
どちらもSHA256を照合して導入しました。

`retoc to-legacy`で18,395アセットをすべて展開できました（失敗0件、約17GB）。

ゲームの起動にはDirectX End-User Runtime（June 2010）が要ります。
`XINPUT1_3.dll`がないと起動しません。
Steam経由で起動すると、Steamが持つ再頒布パッケージを導入してくれます。

## 原文の在りか

cooked済みの18,395アセットを走査し、原文を集めました。
結果は[data/corpus.json](../data/corpus.json)にあります。

| 区分                | 件数 | 置き場所                                         |
|---------------------|------|--------------------------------------------------|
| 本編の台詞（字幕）  | 212  | `RambleyFiles/Voice/`の音声アセットの中のFText   |
| `ST_Menu`の文字列表 | 291  | `MenuSystemPro/ExampleContent/Text/Menu/ST_Menu` |
| そのほかのUI        | 106  | ウィジェットやデータアセットの中のFText          |
| 合計（翻訳の対象）  | 609  |                                                  |

集めたFTextは全部で1,230件です。
残る621件は、内部の列挙、コンソールコマンド、仮置きの文言、見本に付いてきた文章（153件）で、訳しません。
件数は`python tools/check_translation.py`が出します。

置き場所が見本でも、本編が使っている画面の文章は対象に入れます。
設定画面の`Designs/Design_R/`と`Designs/Design_IndigoPark/`がこれにあたります。

字幕は`SoundWave`の中にFTextとして入っています。
たとえば`RooftopRacesBeBroke`には`Ehhh, Looks like Mollie crashed into the Ride again!`が入っています。
名前空間は空で、キーは32桁の16進数です。
UIの文章と同じ扱いで差し替えられます。

## 言語の選択肢に日本語を足す

`DA_GameLanguage`の配列は`["en", "de"]`です。
ドイツ語の訳は入っていないため、`de`を`ja`に書き換えました。
文字数が同じなのでファイルの大きさは変わりません。

書き換えたアセットは`retoc to-zen`でIoStore形式にします。
でき上がる`.pak`、`.ucas`、`.utoc`の3つを`~mods`に置きます。

```bash
retoc to-zen --version UE5_2 <書き換えたアセットのディレクトリ> zzz_lang_P.utoc
```

これで`MenuSystemConfig.json`の`"GameLanguage"`に`ja`を入れると通ります。
`GameUserSettings.ini`の`Culture`が`ja`のまま保存されることで確かめました。

## エンディングの歌詞

2026年9月19日に、実際のゲームで確かめた内容です。

### 曲は動画です

エンディングの曲は`RaccoonCh1/Content/Movies/CreditsSong.mp4`です。
`Manifest_NonUFSFiles_Win64.txt`に載る、pakの外に置かれたファイルです。

| 項目           | 内容             |
|----------------|------------------|
| 映像           | H.264、1920x1080 |
| 音声           | AAC              |
| 長さ           | 191.6秒          |
| 字幕のトラック | ありません       |

英語の歌詞は映像に描き込まれています。
画面の中央にクレジットの窓が流れ、歌詞の窓は左下と右下を行き来します。
ゲームの文章（FText）ではないため、`.locres`では訳を出せません。

### 再生の流れ

レベル`Levels/CreditsCutscene`のレベルブループリントが再生します。

1. `Widgets/W_CreditsCutscene`を画面に足します。中の`Image`（`OpeningVideo`）が動画を映します
1. `/Game/Movies/CreditsSongMediaPlayer`の`OpenSource`で`/Game/Movies/CreditsSong`（`FileMediaSource`）を開きます。音は`Movies/BP_MediaSoundCredits`の`MediaSoundComponent`が出します
1. 再生が終わると（`OnEndReached`）、`W_CreditsCutscene`を外し、「開発者からのメッセージ」（`WBP_MessageFromtheDevs_R`）を出します

`W_CreditsCutscene`だけが画面から外れ、動画の再生は続くことがあります。
確認中に、何もしていないはずの場面で1度起きました。
ゲームのウィンドウに入った操作で、エンディングが飛ばされたと見ています。

ゲームの字幕は、エンジンの字幕の仕組みが描きます。
`DefaultEngine.ini`の`SubtitleFontName`は`Subtitle_Font_Quicksand`で、`LegacyFontSize`は24です。

### UE4SSで字幕を重ねる

[UE4SS](https://github.com/UE4SS-RE/RE-UE4SS) v3.0.1は、このゲームで動きます。
`dwmapi.dll`、`UE4SS.dll`、`UE4SS-settings.ini`と`Mods`フォルダーを、`RaccoonCh1/Binaries/Win64`に置きます。
MODのフォルダーに`enabled.txt`があれば、`mods.txt`に書かなくても読み込まれます。
UE4SSが自分で作るファイルは`UE4SS.log`だけでした。

字幕のMOD（`ue4ss/IndigoParkJP_Lyrics/Scripts/main.lua`）は、100ミリ秒ごとに次を行います。

1. `CreditsSongMediaPlayer`が再生中かを確かめます
1. 再生中なら、UMGのウィジェット（`Overlay`、`Border`、`TextBlock`）を作って画面に足します
1. 再生の時刻に合う字幕を出します。フォントは`Subtitle_Font_Quicksand`を使います。日本語化のMODが中身をM PLUS 1pに差し替えています

UE4SS v3.0.1には、次の制約がありました。

| 制約                                                                         | 対処                                                                                                        |
|------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| 関数が返すFStringが壊れて届きます。`GetCurrentCulture`の値が読めませんでした | 言語は確かめず、MODがあれば字幕を出します                                                                   |
| `FTimespan`はリフレクションの項目を持たず、`GetTime()`は空の表で返ります     | `GetTimeStamp()`が返す`MediaTimeStampInfo`の`Time`の位置を、`RegisterCustomProperty`で`int64`として読みます |
| 再生の始まる前の一瞬は、時刻が`FTimespan`の最小値になります                  | 負の時刻では字幕を出しません                                                                                |
| MODのスクリプトの場所をANSIの文字列にして読みます                            | ゲームの場所に英数字以外の文字があると読み込めません。導入ツールはその場合UE4SSを置きません                 |

エンディングが飛ばされたときは、動画の再生が続いていても、`W_CreditsCutscene`が画面から外れた時点で字幕を止めます。
確認用のMODで`W_CreditsCutscene`を外し、字幕が消えることを確かめました。

## 未解決

- 言語の選択画面に出る名前の対応づけは未調整です
- エンディングの歌詞の訳（`data/lyrics.ja.srt`）はまだありません

## 解決した点

### `.locres`の形式

書き出しは[tools/](../tools/README.md)で行えます。
つまずいた点は2つでした。

1つ目はマジックのバイト順です。
正しくは`0e147475 674a03fc 4a15909d c3377f1b`です。
間違えるとUEがLegacy形式と誤認し、壊れた読み方をしてクラッシュします。

2つ目はキーのハッシュです。
`CityHash64`をUTF-16LEに掛けたうえで、`下位32ビット + 上位32ビット * 23`にします。
下位32ビットをそのまま使うのではありません。
この実装は、出荷ファイルの値300件すべてと一致することを確かめました。

### フォントは差し替えが要ります

`.locres`だけを入れると、日本語の部分が描画されずに消えます。
豆腐（□）も出ません。
`.ufont`を日本語のフォントで上書きすると表示されます。

動作確認では、同梱の`DroidSansFallback.ufont`を次のファイルに上書きしました。

- `MenuSystemPro/ExampleContent/Art/Fonts/`の`DCC_-_Ash`、`Kanit-Regular`、`Oswald-*`
- `RefinedMainMenu/Menu/Fonts/`の`Font_Quicksand-*`

配布物では、再配布できるM PLUS 1p（SIL Open Font License 1.1）に差し替えています。
置き換える対象は[tools/fonts.json](../tools/fonts.json)にあります。
