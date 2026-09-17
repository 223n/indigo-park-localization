# 調査記録

Steam版Indigo Park（Chapter 1）を日本語化するための、技術的な調べものの記録です。
2026年9月18日に、実際のゲームで確かめた内容をまとめます。

## まとめ

日本語化に必要な入口は見つかりました。
暗号化と署名はありません。
MODの載せ方も実機で確かめてあります。

| やりたいこと | できるか | 方法 |
| ---- | ---- | ---- |
| フォントの差し替え | **できます（実機で確認）** | `~mods`にpakを置いて`.ufont`を上書きします |
| UIの文章の差し替え | **できます（実機で確認）** | `Content/Localization/Game/<文化>/Game.locres`を置きます |
| 日本語を選択肢に出す | 追加の作業が要ります | 言語の一覧がIoStore内のアセットに固定されています |
| 本編の字幕の差し替え | 未調査です | 格納先を特定していません |

メニューと設定画面が日本語で表示されるところまで、実機で確認しました。
「つづきから」「はじめから」「ゲームプレイ」「音声」「映像」「操作」「カメラの遅延効果」などが出ます。
日本語を出すにはフォントの差し替えが要ります。
差し替えないと、文字が描画されずに消えます。

## ゲームの構成

| 項目 | 内容 |
| ---- | ---- |
| エンジン | Unreal Engine 5.2（実行ファイル内に`++UE5+Release-5.2`） |
| プロジェクト名 | `RaccoonCh1` |
| 導入先 | `C:\Program Files (x86)\Steam\steamapps\common\Indigo Park` |
| SteamのアプリID | `2504480` |
| パッケージ | IoStore有効。`.utoc`版5、26,759チャンク、18,395パッケージ |
| `.pak` | 版11、4,372ファイル |
| 暗号化 | ありません（AESキーのGUIDはゼロ） |
| 署名 | ありません（`.sig`が存在しません） |
| 圧縮 | Oodle（実行ファイルに静的リンク。`oo2core`の単体DLLはありません） |

`.pak`には`.uasset`が1件も入っていません。
中身は`.locres`、`.ufont`、`.ttf`、`.ini`、ICUのデータなど、パッケージ以外の資源だけです。
cooked済みのアセットはすべてIoStore側にあります。

## フォント

ゲームが使うフォントの実体（`.ufont`）は、すべて`.pak`側にあります。

| 用途 | ファイル |
| ---- | ---- |
| メニューと字幕 | `RefinedMainMenu/Menu/Fonts/Font_Quicksand-*.ufont` |
| 設定画面 | `MenuSystemPro/ExampleContent/Art/Fonts/Oswald-*.ufont`、`Kanit-Regular.ufont` |
| 調査システム | `InspectionSystemPro/ExampleContent/Fonts/Questrial-Regular.ufont` |

`.ufont`は生のTrueTypeです。
日本語のフォントで上書きすれば差し替わります。

エンジンの最終フォールバックである`Engine/Content/EngineFonts/Faces/DroidSansFallback.ufont`は3.94MBあり、「あ」「ア」「日」「」を収録しています。
フォントを差し替えないままでも日本語を表示できる見込みがあります。
ただし実際の表示は未確認です。

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
一覧に無い値は見つからないため、`ja`を指定しても英語に戻されます。

選んだ値は次の2か所に保存されます。

| ファイル | 項目 |
| ---- | ---- |
| `%LOCALAPPDATA%\RaccoonCh1\Saved\Config\MenuSystemConfig.json` | `"GameLanguage"` |
| `%LOCALAPPDATA%\RaccoonCh1\Saved\Config\Windows\GameUserSettings.ini` | `Culture` |

`MenuSystemConfig.json`の`"GameLanguage"`を`de`にすると、文化の切り替えは働きます。
LANGUAGEの値の表示が「ENGLISH」から「ENGLISCH」に変わることで確かめました。

ICUのデータは日本語の分も同梱されています（`ja.res`と`ja_JP.res`）。
そのためICU側の制約はありません。

## 道具

| 道具 | 版 | 用途 |
| ---- | ---- | ---- |
| repak | 0.2.3 | `.pak`の読み書き。Oodleの解凍も行います |
| retoc | 0.1.5 | IoStoreとレガシー形式の相互変換 |

置き場所は`%LOCALAPPDATA%\Programs\ue-modding-tools`です。
どちらもSHA256を照合して導入しました。

`retoc to-legacy`で18,395アセットをすべて展開できました（失敗0件、約17GB）。

ゲームの起動にはDirectX End-User Runtime（June 2010）が要ります。
`XINPUT1_3.dll`が無いと起動しません。
Steam経由で起動すると、Steamが持つ再頒布パッケージを導入してくれます。

## 未解決

### そのほか

- 本編の字幕の格納先を特定していません。`RambleyFiles/Voice/`のSoundWaveを次に調べます
- `DA_GameLanguage`に`ja`を足すには、IoStore形式のMODを作る必要があります。いまは使われていない`de`の枠で代用できます
- 翻訳したのは動作確認のための一部だけです。全文の収集はこれからです

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

配布するときは、再配布できるライセンスのフォント（Noto Sans JPなど）に差し替えます。

## 次にやること

1. 展開済みのアセットからFTextのキーと原文をすべて集めます
1. `DA_GameLanguage`に`ja`を足すMODを作ります。まずは`de`の枠を流用して確かめます
1. 本編の字幕の所在を特定します
