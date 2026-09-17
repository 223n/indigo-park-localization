# 調査記録

Steam版Indigo Park（Chapter 1）を日本語化するための、技術的な調べものの記録です。
2026年9月18日に、実際のゲームで確かめた内容をまとめます。

## まとめ

日本語化に必要な入口は見つかりました。
暗号化と署名はありません。
MODの載せ方も実機で確かめてあります。

| やりたいこと | できるか | 方法 |
| ---- | ---- | ---- |
| フォントの差し替え | できます（確認済み） | `~mods`にpakを置いて`.ufont`を上書きします |
| UIの文章の差し替え | できる見込みです | `Content/Localization/Game/<文化>/`に`.locres`を置きます |
| 日本語を選択肢に出す | 追加の作業が要ります | 言語の一覧がIoStore内のアセットに固定されています |
| 本編の字幕の差し替え | 未調査です | 格納先を特定していません |

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

### `.locres`の形式

自作した`.locres`は反映されないか、ゲームを不安定にしました。
版2を3通り試しましたが、いずれも成功していません。

キーのハッシュ方式を特定できていません。
CityHash64、CityHash32、CRC32の各変種を試しましたが、出荷ファイルの値と一致しませんでした。
一方、`SourceStringHash`が`FCrc::StrCrc32`であることは297件すべてで一致を確認しています。

自作を続けるより、`.locres`とCSVを相互変換できる既存の道具を使うほうが確実です。

### そのほか

- 画面上で日本語の字形が出るかどうかは未確認です
- 本編の字幕の格納先を特定していません。`RambleyFiles/Voice/`のSoundWaveを次に調べます
- `DA_GameLanguage`に`ja`を足すには、IoStore形式のMODを作る必要があります

## 次にやること

1. `.locres`を正しい形式で書き出せる道具を導入します
1. 展開済みのアセットからFTextのキーと原文をすべて集めます
1. `DA_GameLanguage`に`ja`を足すMODを作ります。まずは`de`の枠を流用して確かめます
1. 本編の字幕の所在を特定します
