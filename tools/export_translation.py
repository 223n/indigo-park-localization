# -*- coding: utf-8 -*-
"""data/corpus.json から翻訳作業用のファイルを書き出す。

使い方:
    python tools/export_translation.py po    > ja.po
    python tools/export_translation.py jsonl > ja.jsonl
    python tools/export_translation.py tsv   > ja.tsv

scope が core の項目だけを出します。--all を付けると demo も含めます。
既存の訳を引き継ぐときは --merge <jsonlファイル> で読み込みます。
"""
import io
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ESCAPES = [
    ("\\", "\\\\"),
    ('"', '\\"'),
    ("\r", "\\r"),
    ("\n", "\\n"),
    ("\t", "\\t"),
]


def load_corpus():
    path = os.path.join(ROOT, "data", "corpus.json")
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)["entries"]


def load_existing(path):
    """既存の訳（JSON Lines）を id -> target で読み込む"""
    if not path or not os.path.exists(path):
        return {}
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


def esc(s):
    for a, b in ESCAPES:
        s = s.replace(a, b)
    return s


def to_po(rows, out):
    out.write('msgid ""\nmsgstr ""\n')
    out.write('"Project-Id-Version: Indigo Park Localization\\n"\n')
    out.write('"Language: ja\\n"\n')
    out.write('"MIME-Version: 1.0\\n"\n')
    out.write('"Content-Type: text/plain; charset=UTF-8\\n"\n')
    out.write('"Content-Transfer-Encoding: 8bit\\n"\n\n')
    for e in rows:
        out.write("#. %s: %s\n" % (e["kind"], e["asset"]))
        out.write('msgctxt "%s"\n' % esc(e["id"]))
        out.write('msgid "%s"\n' % esc(e["source"]))
        out.write('msgstr "%s"\n\n' % esc(e.get("target", "")))


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
        cols = [esc(e["id"]), esc(e["source"]), esc(e.get("target", "")), e["asset"]]
        out.write("\t".join(cols) + "\n")


WRITERS = {"po": to_po, "jsonl": to_jsonl, "tsv": to_tsv}


def main(argv):
    fmt = argv[1] if len(argv) > 1 and not argv[1].startswith("-") else "jsonl"
    if fmt not in WRITERS:
        sys.stderr.write("形式は po / jsonl / tsv のどれかです\n")
        return 1
    rows = load_corpus()
    if "--all" not in argv:
        rows = [e for e in rows if e["scope"] == "core"]
    merge = argv[argv.index("--merge") + 1] if "--merge" in argv else None
    existing = load_existing(merge)
    for e in rows:
        e["target"] = existing.get(e["id"], "")
    out = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", newline="\n")
    try:
        WRITERS[fmt](rows, out)
        out.flush()
    except BrokenPipeError:
        # head などで途中まで読まれた場合
        os.dup2(os.open(os.devnull, os.O_WRONLY), sys.stdout.fileno())
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
