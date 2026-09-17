# 道具

`.locres`（Unreal Engineの翻訳ファイル）を作るための道具です。
Python 3で動きます。外部のパッケージは要りません。

| ファイル | 中身 |
| ---- | ---- |
| `cityhash.py` | UEがキーのハッシュに使うCityHash64の実装です |
| `build_locres.py` | 名前空間とキーと訳文から`.locres`を書き出します |
| `export_translation.py` | 原文の一覧から、翻訳作業用のファイルを書き出します |
| `build_mod.py` | 翻訳とフォントからMODの中身を組み立てます |
| `fonts.json` | 使うフォントと、ゲームのどのフォントを置き換えるかの設定です |

## MODを作る

```bash
python tools/export_translation.py jsonl > data/ja.jsonl   # 翻訳の雛形を作る
python tools/build_mod.py --translation data/ja.jsonl      # build/ に組み立てる
repak pack build IndigoParkJP_P.pak --version V11 --mount-point ../../../
```

出来上がった`.pak`を`RaccoonCh1/Content/Paks/~mods/`に置きます。

翻訳の形式は`po`、`jsonl`、`tsv`から選べます。
`build_mod.py`が読むのは`jsonl`です。

## フォントを足す

`fonts.json`の`fonts`に項目を増やし、`default_font`を切り替えます。
取得元のURLとSHA256を書くと、`build_mod.py`が取得して照合します。
置き換える対象は`replace`にあり、ウェイト（`Light`、`Regular`、`Medium`、`Bold`）を指定します。

いまの既定はM PLUS 1p（SIL Open Font License 1.1）です。
配布するときはライセンス文（`OFL.txt`）を同梱してください。

## 使い方

```python
from build_locres import build

nsmap = {
    '': [('6E1443844C98C1EF9065D481339AE1CF', 'Camera Delay Effect', 'カメラの遅延効果')],
    'ST_Menu': [('MainMenu_Continue', 'Continue', 'つづきから')],
}
build(nsmap, 'Game.locres')
```

`nsmap`は`{名前空間: [(キー, 原文, 訳文), ...]}`の形です。
原文は`SourceStringHash`の計算に使います。
訳す必要が無い項目は、訳文に原文をそのまま入れます。

書き出したファイルは`Content/Localization/Game/<文化>/Game.locres`に置きます。

## 検証

`cityhash.py`のハッシュは、ゲームに入っている`.locres`の値300件すべてと一致することを確かめてあります。
書き出したファイルは[UnrealLocres](https://github.com/akintos/UnrealLocres)でも読めます。

## 形式のまとめ

`.locres`の版3の並びです。
つまずきやすい点を書き残します。

| 位置 | 内容 |
| ---- | ---- |
| 0-15 | マジック。`0e147475 674a03fc 4a15909d c3377f1b`です。バイト順を間違えるとUEがLegacy形式と誤認します |
| 16 | 版。3を書きます |
| 17-24 | 文字列表の位置（int64） |
| 25-28 | エントリ数（uint32） |
| 29-32 | 名前空間の数（uint32） |
| 以降 | 名前空間ごとに、キーのハッシュ、名前、キー数、各キー |
| 文字列表 | 個数（int32）のあと、文字列と参照数（int32）の繰り返し |

キーと名前空間のハッシュは`CityHash64`をUTF-16LEに掛けたうえで、`下位32ビット + 上位32ビット * 23`にします。
空文字列のハッシュは0です。
`SourceStringHash`はこれとは別で、`FCrc::StrCrc32`（各文字を4バイトに広げたCRC32）です。
