# -*- coding: utf-8 -*-
"""data/corpus.json から翻訳作業用のファイルを書き出す。

翻訳の管理はPO形式で行います。
`data/ja.po`を作り直すときは、いまの訳を引き継ぐために --merge を付けます。

    python tools/export_translation.py --merge data/ja.po > data/ja.po.new

JSON LinesやTSVでも出せます。ほかの道具に渡すときに使います。

    python tools/export_translation.py --format jsonl > ja.jsonl
    python tools/export_translation.py --format tsv   > ja.tsv

scope が core の項目だけを出します。--all を付けると demo も含めます。
"""
import argparse
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import po  # noqa: E402


def load_corpus():
    path = os.path.join(ROOT, "data", "corpus.json")
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)["entries"]


def load_existing(path):
    """既存の訳を id -> 訳文 で読む。PO と JSON Lines に対応する"""
    if not path or not os.path.exists(path):
        return {}
    if path.endswith(".po"):
        return po.read(path)
    out = {}
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d.get("target"):
                out[d["id"]] = d["target"]
    return out


def to_po(rows, out):
    out.write(po.HEADER)
    for e in rows:
        out.write("#. %s: %s\n" % (e["kind"], e["asset"]))
        out.write('msgctxt "%s"\n' % po.escape(e["id"]))
        out.write('msgid "%s"\n' % po.escape(e["source"]))
        out.write('msgstr "%s"\n\n' % po.escape(e.get("target", "")))


def to_jsonl(rows, out):
    for e in rows:
        rec = {
            "id": e["id"],
            "source": e["source"],
            "target": e.get("target", ""),
            "asset": e["asset"],
        }
        out.write(json.dumps(rec, ensure_ascii=False) + "\n")


def to_tsv(rows, out):
    out.write("id\tsource\ttarget\tasset\n")
    for e in rows:
        cols = [
            po.escape(e["id"]),
            po.escape(e["source"]),
            po.escape(e.get("target", "")),
            e["asset"],
        ]
        out.write("\t".join(cols) + "\n")


WRITERS = {"po": to_po, "jsonl": to_jsonl, "tsv": to_tsv}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", default="po", choices=sorted(WRITERS), help="出力の形式")
    ap.add_argument("--merge", help="引き継ぐ既存の訳（.po か .jsonl）")
    ap.add_argument("--all", action="store_true", help="見本由来の項目も含める")
    a = ap.parse_args()

    rows = load_corpus()
    if not a.all:
        rows = [e for e in rows if e["scope"] == "core"]
    existing = load_existing(a.merge)
    for e in rows:
        e["target"] = existing.get(e["id"], "")

    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
    try:
        WRITERS[a.format](rows, out)
        out.flush()
    except BrokenPipeError:
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0


if __name__ == "__main__":
    sys.exit(main())
