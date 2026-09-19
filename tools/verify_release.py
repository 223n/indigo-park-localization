# -*- coding: utf-8 -*-
"""配布物のzipの中身を確かめる。

    python tools/verify_release.py dist/IndigoParkJP_vX.Y.Z.zip

リリースを自動で公開すると、人が添付を開いて確かめる機会がなくなります。
その代わりに、ここで機械が確かめます。

見るのは次の5点です。

1. 要るファイルが入っているか
2. zipの中のフォルダ名と`README.txt`の版が、`package.json`の版と合っているか
3. 訳文がpakの中に入っているか
4. 訳文のはずの項目が、英語の原文のまま入っていないか
5. エンディングの歌詞の字幕（UE4SSのMOD）が、リポジトリのとおりに入っているか

4は、設定の説明文が英語のまま出た件（Issue #16）と同じ形の崩れを捕まえます。

3と4は、pakの中の`.locres`を項目ごとに読み解き、(名前空間, キー)で引いて
`data/ja.po`の訳文と突き合わせます。
バイト列のまま探すと、別の項目の訳文として書かれた同じ英語と区別できないためです。
照合の基準は、手元のチェックアウトにある`package.json`と`data/ja.po`です。

pakを圧縮して作るようにした場合、`.locres`を見つけられなくなります。
そのときはこの道具の作りを変えてください。
"""
import io
import json
import os
import re
import struct
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
    "licenses/UE4SS-LICENSE",
    "ue4ss/dwmapi.dll",
    "ue4ss/UE4SS.dll",
    "ue4ss/UE4SS-settings.ini",
    "ue4ss/Mods/IndigoParkJP_Lyrics/enabled.txt",
)

# 配布物の中身が、リポジトリのファイルと同じであるべきもの
SAME_AS_REPO = {
    "ue4ss/Mods/IndigoParkJP_Lyrics/Scripts/main.lua": "ue4ss/IndigoParkJP_Lyrics/Scripts/main.lua",
    "ue4ss/Mods/IndigoParkJP_Lyrics/settings.ini": "ue4ss/IndigoParkJP_Lyrics/settings.ini",
    "ue4ss/Mods/IndigoParkJP_Lyrics/lyrics.srt": "data/lyrics.ja.srt",
}

# 照合できた件数がこれを下回ったら、読み込みそのものが壊れていると見ます。
# 訳文が1件も読めていないのに「問題なし」で通ると、検査の意味がなくなります
MIN_RATIO = 0.9

# .locres の先頭に入っている印。tools/build_locres.py の MAGIC と同じ
LOCRES_MAGIC = bytes.fromhex("0e147475674a03fc4a15909dc3377f1b")


def read_fstring(b, o):
    """oの位置からFStringを読み、(文字列, 次の位置)を返す"""
    (n,) = struct.unpack_from("<i", b, o)
    o += 4
    if n == 0:
        return "", o
    if n > 0:
        return b[o:o + n - 1].decode("utf-8"), o + n
    n = -n
    return b[o:o + n * 2 - 2].decode("utf-16-le"), o + n * 2


def read_locres(pak, start):
    """pakの中のstartの位置にある.locresを読み、(名前空間, キー) -> 訳文 にする"""
    o = start + len(LOCRES_MAGIC)
    version = pak[o]
    o += 1
    if version != 3:
        raise ValueError(".locres の版が3ではありません: %d" % version)
    (array,) = struct.unpack_from("<q", pak, o)
    o += 8
    (total,) = struct.unpack_from("<I", pak, o)
    o += 4
    (namespaces,) = struct.unpack_from("<I", pak, o)
    o += 4

    so = start + array
    (count,) = struct.unpack_from("<i", pak, so)
    so += 4
    strings = []
    for _ in range(count):
        s, so = read_fstring(pak, so)
        so += 4  # 参照数
        strings.append(s)

    out = {}
    for _ in range(namespaces):
        o += 4  # 名前空間のハッシュ
        ns, o = read_fstring(pak, o)
        (keys,) = struct.unpack_from("<I", pak, o)
        o += 4
        for _ in range(keys):
            o += 4  # キーのハッシュ
            key, o = read_fstring(pak, o)
            o += 4  # 原文のハッシュ
            (index,) = struct.unpack_from("<i", pak, o)
            o += 4
            out[(ns, key)] = strings[index]
    if len(out) != total:
        raise ValueError("項目数が合いません: 見出しは%d件、読めたのは%d件" % (total, len(out)))
    return out


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

        for inner, repo in sorted(SAME_AS_REPO.items()):
            name = "%s/%s" % (root, inner)
            if name not in names:
                problems.append("要るファイルがありません: %s" % inner)
                continue
            with open(os.path.join(ROOT, repo), "rb") as f:
                if z.read(name) != f.read():
                    problems.append("%s が %s と違います" % (inner, repo))

        settings = "%s/ue4ss/UE4SS-settings.ini" % root
        if settings in names:
            text = z.read(settings).decode("utf-8", "replace")
            if not re.search(r"(?m)^GuiConsoleEnabled\s*=\s*0\s*$", text):
                problems.append("UE4SS の設定で、GUIのコンソールが切られていません")

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

    # pakの中から.locresを見つけて読む。
    # 圧縮せずに詰めているため、印を手掛かりに位置を出せる
    offsets = []
    at = pak.find(LOCRES_MAGIC)
    while at >= 0:
        offsets.append(at)
        at = pak.find(LOCRES_MAGIC, at + 1)
    if not offsets:
        problems.append("pakの中に.locresがありません。pakを圧縮して作っていないか確かめてください")
        return problems, notes

    tables = []
    for at in offsets:
        try:
            tables.append(read_locres(pak, at))
        except Exception as ex:
            problems.append("位置%dの.locresを読めません: %s" % (at, ex))
    if not tables:
        return problems, notes
    notes.append(".locres %d個 / 項目 %d件" % (len(tables), len(tables[0])))

    missing = []
    wrong = []
    leftover = []
    checked = 0
    targets = 0
    for e in corpus["entries"]:
        if not e["translate"]:
            continue
        targets += 1
        target = translation.get(e["id"])
        if not target or target == e["source"]:
            # 規格名や製品名など、訳文が原文と同じ項目は見分けられないため飛ばす
            continue
        checked += 1
        for table in tables:
            got = table.get((e["namespace"], e["key"]))
            if got is None:
                missing.append("%s  %s" % (e["id"], e["source"][:50]))
            elif got == e["source"]:
                leftover.append("%s  %s" % (e["id"], e["source"][:60]))
            elif got != target:
                wrong.append("%s  期待 %s / 実際 %s" % (e["id"], target[:30], got[:30]))
            break

    notes.append("訳文 %d件を照合（翻訳対象 %d件）" % (checked, targets))
    if targets and checked < targets * MIN_RATIO:
        problems.append(
            "照合できた訳文が%d件しかありません（翻訳対象は%d件）。data/ja.po を読めていない恐れがあります"
            % (checked, targets))
    for title, rows in (
        ("項目が.locresにありません", missing),
        ("英語の原文のまま入っています", leftover),
        ("訳文が data/ja.po と違います", wrong),
    ):
        if rows:
            problems.append("%s（%d件）:\n    %s" % (
                title, len(rows), "\n    ".join(rows[:10])))
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
