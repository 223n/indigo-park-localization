# 道具

`.locres`（Unreal Engineの翻訳ファイル）を作るための道具です。
Python 3で動きます。外部のパッケージは要りません。

| ファイル | 中身 |
| ---- | ---- |
| `cityhash.py` | UEがキーのハッシュに使うCityHash64の実装です |
| `build_locres.py` | 名前空間とキーと訳文から`.locres`を書き出します |

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
