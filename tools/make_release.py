# -*- coding: utf-8 -*-
"""配布用のzipを組み立てる。

    python tools/make_release.py

package.json の version を使って dist/IndigoParkJP_vX.Y.Z.zip を作ります。
repak と retoc は取得してSHA256で照合します。

でき上がるzipの中身は次のとおりです。

    install.bat / uninstall.bat   導入と取り外し
    README.txt                    手順
    mod/IndigoParkJP_P.pak        翻訳とフォント
    tools/install.ps1 など        中身
    licenses/                     このMODと同梱物のライセンス
"""
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import urllib.request
import zipfile

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, ".toolcache")
DIST = os.path.join(ROOT, "dist")
BUILD = os.path.join(ROOT, "build")

# 取得する道具。版を上げるときはSHA256も更新する
TOOLS = {
    "repak.exe": {
        "url": "https://github.com/trumank/repak/releases/download/v0.2.3/repak_cli-x86_64-pc-windows-msvc.zip",
        "sha256": "6720d602144d75df477a99d5bedb6ea780997546afc335901d4937cafeaa73fa",
        "member": "repak.exe",
    },
    "retoc.exe": {
        "url": "https://github.com/trumank/retoc/releases/download/v0.1.5/retoc_cli-x86_64-pc-windows-msvc.zip",
        "sha256": "cc036b06ad3bdcf7003690b00d82719980c374e48a95bf0654f9959148d263aa",
        "member": "retoc.exe",
    },
}

LICENSES = {
    "LICENSE": os.path.join(ROOT, "LICENSE"),
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_tool(name, meta):
    """道具を取得して展開する。すでにあれば使い回す"""
    os.makedirs(CACHE, exist_ok=True)
    exe = os.path.join(CACHE, name)
    if os.path.exists(exe):
        return exe
    zip_path = os.path.join(CACHE, name + ".zip")
    if not os.path.exists(zip_path):
        sys.stderr.write("取得: %s\n" % meta["url"].rsplit("/", 1)[-1])
        urllib.request.urlretrieve(meta["url"], zip_path)
    got = sha256(zip_path)
    want = meta["sha256"]
    if got != want:
        raise SystemExit("SHA256が一致しません: %s\n  期待 %s\n  実際 %s" % (name, want, got))
    with zipfile.ZipFile(zip_path) as z:
        with z.open(meta["member"]) as src, open(exe, "wb") as dst:
            shutil.copyfileobj(src, dst)
    return exe


def version():
    with io.open(os.path.join(ROOT, "package.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("失敗: %s\n%s" % (" ".join(cmd), r.stderr[-2000:]))
    return r.stdout


def main():
    ver = version()
    name = "IndigoParkJP_v%s" % ver
    stage = os.path.join(DIST, name)
    shutil.rmtree(stage, ignore_errors=True)
    os.makedirs(os.path.join(stage, "mod"), exist_ok=True)
    os.makedirs(os.path.join(stage, "tools"), exist_ok=True)
    os.makedirs(os.path.join(stage, "licenses"), exist_ok=True)

    print("▶ MODの中身を組み立てる")
    run([sys.executable, os.path.join(ROOT, "tools", "build_mod.py"),
         "--translation", os.path.join(ROOT, "data", "ja.po"),
         "--out", "build"])

    print("▶ pakにまとめる")
    repak = fetch_tool("repak.exe", TOOLS["repak.exe"])
    pak = os.path.join(stage, "mod", "IndigoParkJP_P.pak")
    run([repak, "pack", BUILD, pak, "--version", "V11", "--mount-point", "../../../"])
    print("  %s（%.1f MB）" % (os.path.basename(pak), os.path.getsize(pak) / 1048576))

    print("▶ 導入ツールを入れる")
    inst = os.path.join(ROOT, "installer")
    for f in ("install.bat", "uninstall.bat"):
        shutil.copy(os.path.join(inst, f), os.path.join(stage, f))
    # Windows PowerShell 5.1 は BOM が無いと UTF-8 と判定しない。
    # リポジトリ内は BOM 無しのままにし、配布するものにだけ付ける。
    for f in ("install.ps1", "uninstall.ps1"):
        with io.open(os.path.join(inst, f), encoding="utf-8") as src:
            text = src.read()
        with io.open(os.path.join(stage, "tools", f), "w",
                     encoding="utf-8-sig", newline="\r\n") as dst:
            dst.write(text)
    retoc = fetch_tool("retoc.exe", TOOLS["retoc.exe"])
    shutil.copy(retoc, os.path.join(stage, "tools", "retoc.exe"))

    print("▶ 説明とライセンスを入れる")
    with io.open(os.path.join(inst, "README.txt"), encoding="utf-8") as f:
        readme = f.read().replace("__VERSION__", "v" + ver)
    with io.open(os.path.join(stage, "README.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write(readme)
    for dst, src in LICENSES.items():
        shutil.copy(src, os.path.join(stage, "licenses", dst))
    ofl = os.path.join(ROOT, ".fontcache", "OFL.txt")
    if os.path.exists(ofl):
        shutil.copy(ofl, os.path.join(stage, "licenses", "OFL.txt"))
    else:
        print("  ! OFL.txt がありません。build_mod.py を先に実行してください")
    retoc_lic = os.path.join(CACHE, "retoc-LICENSE")
    if not os.path.exists(retoc_lic):
        urllib.request.urlretrieve(
            "https://raw.githubusercontent.com/trumank/retoc/master/LICENSE", retoc_lic)
    shutil.copy(retoc_lic, os.path.join(stage, "licenses", "retoc-LICENSE"))

    print("▶ zipにまとめる")
    zip_path = os.path.join(DIST, name + ".zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    # 日時を固定し、名前順に入れる。
    # repak がファイルの順を固定しないため、pak 自体は毎回変わる。
    # そのため zip も毎回変わる。公開するときは、出したSHA256をReleaseに載せる。
    entries = []
    for dirpath, _, files in os.walk(stage):
        for fn in files:
            full = os.path.join(dirpath, fn)
            entries.append((os.path.relpath(full, DIST).replace(os.sep, "/"), full))
    entries.sort()
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, full in entries:
            info = zipfile.ZipInfo(rel, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            with open(full, "rb") as f:
                z.writestr(info, f.read())
    print("  %s（%.1f MB）" % (os.path.basename(zip_path), os.path.getsize(zip_path) / 1048576))
    print("  SHA256: %s" % sha256(zip_path))
    print("▶ 済みました: %s" % zip_path)


if __name__ == "__main__":
    main()
