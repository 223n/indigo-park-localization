# 道具

`.locres`（Unreal Engineの翻訳ファイル）、MOD、配布物を作る道具と、それらを検査する道具です。
Python 3で動きます。外部のパッケージは要りません。

| ファイル | 中身 |
| ---- | ---- |
| `cityhash.py` | UEがキーのハッシュに使うCityHash64の実装です。GoogleのCityHash v1.1をPythonに移したもので、MIT Licenseです |
| `build_locres.py` | 名前空間とキーと訳文から`.locres`を書き出します |
| `export_translation.py` | 原文の一覧から、翻訳作業用のファイルを書き出します |
| `po.py` | PO（gettext）の読み書きです |
| `harvest.py` | cooked済みのアセットから原文を集めます |
| `build_mod.py` | 翻訳とフォントからMODの中身を組み立てます |
| `make_release.py` | MODをpakにまとめ、導入の道具と合わせて配布物のzipを作ります |
| `check_translation.py` | 原文の一覧と訳文の突き合わせを検査します |
| `verify_release.py` | 配布物のzipの中身を検査します |
| `fonts.json` | 使うフォントと、ゲームのどのフォントを置き換えるかの設定です |

## MODを作る

```bash
python tools/build_mod.py --translation data/ja.po    # build/ に組み立てる
repak pack build IndigoParkJP_P.pak --version V11 --mount-point ../../../
```

でき上がった`.pak`を`RaccoonCh1/Content/Paks/~mods/`に置きます。

言語の選択肢に日本語を足すファイルは、このpakには入りません。
導入のときに`installer/install.ps1`が、利用者のゲームのデータから作ります。
仕組みは[docs/RESEARCH.md](../docs/RESEARCH.md)にあります。

## 翻訳する

翻訳はPO形式の[data/ja.po](../data/ja.po)で管理します。
Poeditなどの翻訳ツールでそのまま開けます。

原文が増えたときは、いまの訳を引き継いだまま作り直せます。

```bash
python tools/export_translation.py --merge data/ja.po > data/ja.po.new
```

出すのは`translate`が`true`の項目だけです。
訳さない項目も見たいときは`--all`を付けます。

訳し終えたら、突き合わせを検査します。

```bash
python tools/check_translation.py
```

翻訳対象なのに訳文が無い項目、POに混じった余計な項目、タグや改行の数が原文と違う項目を見つけます。
`data/corpus.json`に書いた件数が、実際の件数と合っているかも見ます。
見つかると終了コード1で終わります。
CIの「翻訳データの検査」でも同じものを動かします。

ほかの形式でも出せます。別の道具へ渡すときに使います。

```bash
python tools/export_translation.py --format jsonl > ja.jsonl
python tools/export_translation.py --format tsv   > ja.tsv
```

## 原文を集め直す

ゲームが更新されたときは、集め直します。

```bash
retoc to-legacy --no-shaders --version UE5_2 "<ゲーム>/RaccoonCh1/Content/Paks" full
python tools/harvest.py full/RaccoonCh1/Content > harvest.json
```

FTextの置かれ方は2通りあり、`harvest.py`は両方を拾います。
片方だけだと、目標の表示や操作の案内が抜けます。
詳しくは[docs/TRANSLATION.md](../docs/TRANSLATION.md)にあります。

集めた結果を`data/corpus.json`へ反映する道具は、まだありません。
反映したら、上の「翻訳する」の手順でPOを作り直し、`check_translation.py`で確かめます。

## 配布物を確かめる

でき上がったzipの中身は、道具で確かめられます。

```bash
python tools/verify_release.py dist/IndigoParkJP_vX.Y.Z.zip
```

照合の基準は、手元のチェックアウトにある`package.json`と`data/ja.po`です。
過去の版のzipを確かめるときは、その版のタグをチェックアウトしてから動かします。

要るファイルが入っているか、版が合っているか、訳文が`data/ja.po`のとおりに入っているか、英語の原文のまま入っていないかを見ます。
pakの中の`.locres`を項目ごとに読み解いて突き合わせます。
最後の1つは、設定の説明文が英語のまま出た件（Issue #16）と同じ形の崩れを捕まえます。
リリースのワークフローは、Releaseを自動で公開する前にこれを動かします。
落ちるとドラフトのまま止まります。

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
訳す必要がない項目は、訳文に原文をそのまま入れます。

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
