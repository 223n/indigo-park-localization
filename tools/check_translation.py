# -*- coding: utf-8 -*-
"""原文の一覧と訳文の突き合わせを行う。

    python tools/check_translation.py

`data/corpus.json`の`translate`が`true`の項目は、すべて`data/ja.po`に
空でない訳文があるという決まりです。
この決まりが崩れると、ゲームの画面に英語のまま残ります。
実際に、設定画面の説明文2件が原文の分類の誤りで抜けたことがあります。

見るのは次の6点です。

1. `count`と`translate_count`の記載が、実際の件数と合っているか
2. 翻訳対象の項目が、すべてPOにあり訳文が空でないか
3. POに、原文の一覧に無い項目が混じっていないか
4. POに、翻訳しない項目が混じっていないか
5. リッチテキストのタグが、原文と訳文で同じか
6. 改行の数が、原文と訳文で同じか

どれかに引っかかると、終了コード1で終わります。
訳文が原文のままの項目は、規格名や製品名のことがあるため注意として出すだけです。
"""
import io
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import po  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

TAG = re.compile(r"</?[A-Za-z][^<>]{0,30}>")


def load_corpus():
    with io.open(os.path.join(ROOT, "data", "corpus.json"), encoding="utf-8") as f:
        return json.load(f)


def category(entry):
    """翻訳対象の項目を、置かれ方で3つに分ける"""
    asset = entry["asset"]
    if "/Voice/" in asset:
        return "台詞"
    if asset.endswith("ST_Menu"):
        return "ST_Menu"
    return "その他のUI"


def check(corpus, translation):
    """見つけた問題を (見出し, [詳しい行]) の一覧で返す"""
    entries = corpus["entries"]
    targets = [e for e in entries if e["translate"]]
    known = {e["id"] for e in entries}
    problems = []

    counts = []
    if corpus.get("count") != len(entries):
        counts.append("count が %s、実際は %d件" % (corpus.get("count"), len(entries)))
    if corpus.get("translate_count") != len(targets):
        counts.append(
            "translate_count が %s、実際は %d件" % (corpus.get("translate_count"), len(targets))
        )
    if counts:
        problems.append(("原文の一覧の件数が合いません", counts))

    missing = [e for e in targets if not translation.get(e["id"])]
    if missing:
        problems.append((
            "翻訳対象なのに訳文がありません",
            ["%s  %s（%s）" % (e["id"], e["source"][:60], e["asset"]) for e in missing],
        ))

    unknown = [i for i in translation if i not in known]
    if unknown:
        problems.append(("原文の一覧に無い項目がPOにあります", sorted(unknown)))

    skipped = {e["id"] for e in entries if not e["translate"]}
    strays = [i for i in translation if i in skipped]
    if strays:
        problems.append(("翻訳しない項目がPOにあります", sorted(strays)))

    tags = []
    breaks = []
    for e in targets:
        tr = translation.get(e["id"])
        if not tr:
            continue
        if sorted(TAG.findall(e["source"])) != sorted(TAG.findall(tr)):
            tags.append("%s  %s" % (e["id"], e["source"][:60]))
        for mark, name in (("\n", "改行"), ("\r", "復帰")):
            if e["source"].count(mark) != tr.count(mark):
                breaks.append("%s  %sの数が %d と %d" % (
                    e["id"], name, e["source"].count(mark), tr.count(mark)))
    if tags:
        problems.append(("リッチテキストのタグが原文と違います", tags))
    if breaks:
        problems.append(("改行の数が原文と違います", breaks))

    return problems


def report(corpus, translation):
    entries = corpus["entries"]
    targets = [e for e in entries if e["translate"]]
    kinds = {}
    for e in targets:
        name = category(e)
        kinds[name] = kinds.get(name, 0) + 1
    same = [e for e in targets if translation.get(e["id"]) == e["source"]]

    print("原文 %d件 / 翻訳対象 %d件 / 訳さない項目 %d件（うち見本 %d件）" % (
        len(entries),
        len(targets),
        len(entries) - len(targets),
        sum(1 for e in entries if e["scope"] == "demo"),
    ))
    print("翻訳対象の内訳: " + " / ".join(
        "%s %d件" % (k, kinds[k]) for k in sorted(kinds, key=lambda k: -kinds[k])))
    if same:
        print("注意: 訳文が原文のままの項目が%d件あります（規格名や製品名なら問題ありません）" % len(same))
        for e in same:
            print("  %s  %s" % (e["id"], e["source"][:60]))


def main():
    corpus = load_corpus()
    translation = po.read(os.path.join(ROOT, "data", "ja.po"))
    problems = check(corpus, translation)
    report(corpus, translation)
    if not problems:
        print("問題はありません")
        return 0
    for title, lines in problems:
        print("")
        print("%s（%d件）" % (title, len(lines)))
        for line in lines[:20]:
            print("  " + line)
        if len(lines) > 20:
            print("  ほか%d件" % (len(lines) - 20))
    return 1


if __name__ == "__main__":
    sys.exit(main())
