# -*- coding: utf-8 -*-
"""配布物のzipの中身を確かめる。

    python tools/verify_release.py dist/IndigoParkJP_v0.6.0.zip

リリースを自動で公開すると、人が添付を開いて確かめる機会がなくなります。
その代わりに、ここで機械が確かめます。

見るのは次の4点です。

1. 要るファイルが入っているか
2. `README.txt`の版が、zipの名前と`package.json`の版と合っているか
3. 訳文がpakの中に入っているか
4. 訳文のはずの項目が、英語の原文のまま入っていないか

4は、設定の説明文が英語のまま出た件（Issue #16）と同じ形の崩れを捕まえます。
`.locres`は原文を持たず訳文だけを持つため、原文がpakの中に見えたら、
訳文の代わりに原文が書き込まれたということです。

pakを圧縮して作るようにした場合、3と4は文字列を見つけられなくなります。
そのときはこの道具の作りを変えてください。
"""
import io
import json
import os
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))

import po  # noqa: E402

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

REQUIRED = (
    "mod/IndigoParkJP_P.pak",
    "install.bat",
    "uninstall.bat",
    "tools/install.ps1",
    "tools/uninstall.ps1",
    "tools/retoc.exe",
    "README.txt",
    "licenses/LICENSE",
    "licenses/OFL.txt",
)

# 原文が短いと、キーやファイル名の一部にたまたま重なります。
# 空白を含む長めの文だけを「原文のまま残っていないか」の対象にします
MIN_SOURCE = 16


def load(path):
    with io.open(path, encoding="utf-8") as f:
        return json.load(f)


def check(zip_path):
    problems = []
    notes = []

    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        roots = {n.split("/")[0] for n in names}
        if len(roots) != 1:
            return ["zipの中に最上位のフォルダが%d個あります: %s" % (len(roots), sorted(roots))], notes
        root = roots.pop()

        missing = [f for f in REQUIRED if "%s/%s" % (root, f) not in names]
        if missing:
            problems.append("要るファイルがありません: %s" % ", ".join(missing))

        version = load(os.path.join(ROOT, "package.json"))["version"]
        if root != "IndigoParkJP_v%s" % version:
            problems.append(
                "zipの中のフォルダ名（%s）が package.json の版（%s）と合いません" % (root, version))

        readme = "%s/README.txt" % root
        if readme in names:
            text = z.read(readme).decode("utf-8", "replace")
            if ("v%s" % version) not in text:
                problems.append("README.txt に版（v%s）が書かれていません" % version)
            if "__VERSION__" in text:
                problems.append("README.txt に __VERSION__ が残っています")

        pak_name = "%s/mod/IndigoParkJP_P.pak" % root
        if pak_name not in names:
            return problems, notes
        pak = z.read(pak_name)
        notes.append("pak %.1f MB" % (len(pak) / 1048576))

    corpus = load(os.path.join(ROOT, "data", "corpus.json"))
    translation = po.read(os.path.join(ROOT, "data", "ja.po"))

    missing_target = []
    leftover_source = []
    checked = 0
    for e in corpus["entries"]:
        if not e["translate"]:
            continue
        target = translation.get(e["id"])
        if not target or target == e["source"]:
            # 規格名や製品名など、訳文が原文と同じ項目は見分けられないため飛ばす
            continue
        checked += 1
        if target.encode("utf-16-le") not in pak:
            missing_target.append("%s  %s" % (e["id"], target[:40]))
        source = e["source"]
        if len(source) >= MIN_SOURCE and " " in source:
            try:
                raw = source.encode("ascii")
            except UnicodeEncodeError:
                continue
            if raw in pak:
                leftover_source.append("%s  %s" % (e["id"], source[:60]))

    notes.append("訳文 %d件を照合" % checked)
    if missing_target:
        problems.append("訳文がpakに入っていません（%d件）:\n    %s" % (
            len(missing_target), "\n    ".join(missing_target[:10])))
    if leftover_source:
        problems.append("英語の原文がpakに残っています（%d件）:\n    %s" % (
            len(leftover_source), "\n    ".join(leftover_source[:10])))
    return problems, notes


def main():
    if len(sys.argv) < 2:
        print("使い方: python tools/verify_release.py <配布物のzip>")
        return 2
    zip_path = sys.argv[1]
    if not os.path.exists(zip_path):
        print("ありません: %s" % zip_path)
        return 2

    print("確かめる: %s（%.1f MB）" % (
        os.path.basename(zip_path), os.path.getsize(zip_path) / 1048576))
    problems, notes = check(zip_path)
    for n in notes:
        print("  " + n)
    if not problems:
        print("問題はありません")
        return 0
    for p in problems:
        print("")
        print("  " + p)
    return 1


if __name__ == "__main__":
    sys.exit(main())
