# -*- coding: utf-8 -*-
"""翻訳とフォントからMODの中身を組み立てる。

使い方:
    python tools/build_mod.py --translation data/ja.po --out build

翻訳ファイルはPOです。JSON Linesも読めます。
訳文が空の項目は原文のままにします。

出来上がった build/ を repak で固めるとMODになります。

    repak pack build IndigoParkJP_P.pak --version V11 --mount-point ../../../

フォントは tools/fonts.json の指定に従って取得します。
足したいフォントがあるときは fonts.json に項目を増やします。
"""
import argparse
import hashlib
import io
import json
import os
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import po  # noqa: E402
from build_locres import build as build_locres  # noqa: E402

CULTURES = ("ja", "de")
CACHE = os.path.join(ROOT, ".fontcache")


def load_json(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def load_translation(path):
    out = {}
    if not path:
        return out
    if path.endswith(".po"):
        return po.read(path)
    with io.open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            if d.get("target"):
                out[d["id"]] = d["target"]
    return out


def fetch_font(base_url, name, sha256):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name)
    if os.path.exists(path):
        got = hashlib.sha256(open(path, "rb").read()).hexdigest()
        if got == sha256:
            return path
    sys.stderr.write("取得: %s\n" % name)
    urllib.request.urlretrieve(base_url + name, path)
    got = hashlib.sha256(open(path, "rb").read()).hexdigest()
    if got != sha256:
        raise SystemExit("SHA256が一致しません: %s\n  期待 %s\n  実際 %s" % (name, sha256, got))
    return path


def build_fonts(cfg, outdir):
    fid = cfg["default_font"]
    font = cfg["fonts"][fid]
    weights = {}
    for w, meta in font["files"].items():
        weights[w] = fetch_font(font["base_url"], meta["file"], meta["sha256"])
    for name, sha in font.get("extra", {}).items():
        fetch_font(font["base_url"], name, sha)
    n = 0
    for rep in cfg["replace"]:
        src = weights.get(rep["weight"])
        if not src:
            raise SystemExit("ウェイトがありません: %s" % rep["weight"])
        dst = os.path.join(outdir, rep["target"].replace("/", os.sep))
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy(src, dst)
        n += 1
    return fid, font["name"], n


def build_text(corpus, translation, outdir):
    nsmap = {}
    translated = 0
    for e in corpus["entries"]:
        tr = translation.get(e["id"], e["source"])
        if tr != e["source"]:
            translated += 1
        nsmap.setdefault(e["namespace"], []).append((e["key"], e["source"], tr))
    for culture in CULTURES:
        path = os.path.join(
            outdir, "RaccoonCh1", "Content", "Localization", "Game", culture, "Game.locres"
        )
        total, strings, size = build_locres(nsmap, path)
    return total, translated, size


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--translation", help="翻訳ファイル（PO か JSON Lines）")
    ap.add_argument("--out", default="build", help="出力先ディレクトリ")
    ap.add_argument("--no-fonts", action="store_true", help="フォントを入れない")
    a = ap.parse_args()

    outdir = os.path.join(ROOT, a.out)
    shutil.rmtree(outdir, ignore_errors=True)
    os.makedirs(outdir, exist_ok=True)

    corpus = load_json(os.path.join(ROOT, "data", "corpus.json"))
    translation = load_translation(a.translation)
    total, translated, size = build_text(corpus, translation, outdir)
    print("翻訳: %d件中 %d件を訳出 / locres %s バイト" % (total, translated, format(size, ",")))

    if not a.no_fonts:
        cfg = load_json(os.path.join(ROOT, "tools", "fonts.json"))
        fid, fname, n = build_fonts(cfg, outdir)
        print("フォント: %s を %d ファイルに適用" % (fname, n))

    print("出力先: %s" % outdir)


if __name__ == "__main__":
    main()
