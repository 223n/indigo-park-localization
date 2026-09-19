# -*- coding: utf-8 -*-
"""配布用のzipを組み立てる。

    python tools/make_release.py

package.json の version を使って dist/IndigoParkJP_vX.Y.Z.zip を作ります。
repak、retoc、UE4SS は取得してSHA256で照合します。

でき上がるzipの中身は次のとおりです。

    install.bat / uninstall.bat   導入と取り外し
    README.txt                    手順
    mod/IndigoParkJP_P.pak        翻訳とフォント
    ue4ss/                        エンディングの歌詞の字幕（UE4SS と、その MOD）
    tools/install.ps1 など        中身
    licenses/                     このMODと同梱物のライセンス
"""
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
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

# 取得する道具。版を上げるときはSHA256も更新する。
# repak は組み立てに使うため動かす側のOSのものを、
# retoc は配布物に入れて利用者のWindowsで動かすため、常にWindows版を取る。
REPAK_WINDOWS = {
    "url": "https://github.com/trumank/repak/releases/download/v0.2.3/repak_cli-x86_64-pc-windows-msvc.zip",
    "sha256": "6720d602144d75df477a99d5bedb6ea780997546afc335901d4937cafeaa73fa",
    "member": "repak.exe",
}
REPAK_LINUX = {
    "url": "https://github.com/trumank/repak/releases/download/v0.2.3/repak_cli-x86_64-unknown-linux-gnu.tar.xz",
    "sha256": "933bdb8e26f34e8fd70ea50201efca39df041de58aa83b1cd6eb83da124a2046",
    "member": "repak",
}
RETOC_WINDOWS = {
    "url": "https://github.com/trumank/retoc/releases/download/v0.1.5/retoc_cli-x86_64-pc-windows-msvc.zip",
    "sha256": "cc036b06ad3bdcf7003690b00d82719980c374e48a95bf0654f9959148d263aa",
    "member": "retoc.exe",
}
ON_WINDOWS = os.name == "nt"
TOOLS = {
    "repak": REPAK_WINDOWS if ON_WINDOWS else REPAK_LINUX,
    "retoc.exe": RETOC_WINDOWS,
}

LICENSES = {
    "LICENSE": os.path.join(ROOT, "LICENSE"),
}

# エンディングの歌詞の字幕を出すのに使う UE4SS。
# 配布物に入れ、導入ツールがゲームの実行ファイルのフォルダに置く。
# 版を上げるときは SHA256 を更新し、UE4SS_SETTINGS の書き換えが効くかも確かめる。
UE4SS = {
    "url": "https://github.com/UE4SS-RE/RE-UE4SS/releases/download/v3.0.1/UE4SS_v3.0.1.zip",
    "sha256": "4b47d4bceddd2f561a4e395bfa00924ccfc945af576a2d0c613e6537846c57ec",
    "members": ("dwmapi.dll", "UE4SS.dll"),
    "settings": "UE4SS-settings.ini",
    "license_url": "https://raw.githubusercontent.com/UE4SS-RE/RE-UE4SS/v3.0.1/LICENSE",
    "license_sha256": "ddc030e25d0ea87aca4ae84c0ed3f868d69273c00c0c12ea1e26f1c6130f5d2e",
}
# UE4SS の設定のうち、既定から変えるもの。
# 調べもの用の画面（GUIのコンソール）は、遊ぶ人には要らないため作らない
UE4SS_SETTINGS = {
    "GuiConsoleEnabled": "0",
}
LYRICS_MOD = "IndigoParkJP_Lyrics"


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url, want, name=None):
    """取得してSHA256で照合し、控えの場所を返す。すでに控えがあれば使い回す"""
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, name or url.rsplit("/", 1)[-1])
    if not os.path.exists(path):
        sys.stderr.write("取得: %s\n" % os.path.basename(path))
        urllib.request.urlretrieve(url, path)
    got = sha256(path)
    if not want:
        sys.stderr.write("  SHA256（sha256 に書いてください）: %s\n" % got)
    elif got != want:
        raise SystemExit("SHA256が一致しません: %s\n  期待 %s\n  実際 %s" % (
            os.path.basename(path), want, got))
    return path


def fetch_tool(name, meta):
    """道具を取得して展開する。すでにあれば使い回す"""
    out = os.path.join(CACHE, name)
    if os.path.exists(out):
        return out
    archive = download(meta["url"], meta["sha256"])
    if archive.endswith(".zip"):
        with zipfile.ZipFile(archive) as z:
            with z.open(meta["member"]) as src, open(out, "wb") as dst:
                shutil.copyfileobj(src, dst)
    else:
        with tarfile.open(archive) as t:
            member = next(m for m in t.getmembers()
                          if os.path.basename(m.name) == meta["member"])
            with t.extractfile(member) as src, open(out, "wb") as dst:
                shutil.copyfileobj(src, dst)
    if not ON_WINDOWS:
        os.chmod(out, 0o755)
    return out


def version():
    with io.open(os.path.join(ROOT, "package.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit("失敗: %s\n%s" % (" ".join(cmd), r.stderr[-2000:]))
    return r.stdout


def stage_ue4ss(stage):
    """UE4SS と、エンディングの歌詞の字幕を出す MOD を stage/ue4ss に置き、字幕の行数を返す"""
    import check_translation

    cues, problems = check_translation.check_lyrics(check_translation.LYRICS)
    if problems:
        raise SystemExit("エンディングの歌詞の字幕に問題があります。"
                         "python tools/check_translation.py で確かめてください")

    out = os.path.join(stage, "ue4ss")
    mod = os.path.join(out, "Mods", LYRICS_MOD)
    os.makedirs(os.path.join(mod, "Scripts"))

    archive = download(UE4SS["url"], UE4SS["sha256"])
    with zipfile.ZipFile(archive) as z:
        for member in UE4SS["members"]:
            with z.open(member) as src, open(os.path.join(out, member), "wb") as dst:
                shutil.copyfileobj(src, dst)
        # BOM と CRLF を保つため、読んだ文字列をそのまま書き戻す
        settings = z.read(UE4SS["settings"]).decode("utf-8")
    for key, value in UE4SS_SETTINGS.items():
        settings, n = re.subn(r"(?m)^(%s\s*=\s*)\S*" % re.escape(key), r"\g<1>" + value, settings)
        if n != 1:
            raise SystemExit("UE4SS の設定に %s が見つかりません。UE4SS_SETTINGS を見直してください" % key)
    with io.open(os.path.join(out, UE4SS["settings"]), "w", encoding="utf-8", newline="") as f:
        f.write(settings)

    src = os.path.join(ROOT, "ue4ss", LYRICS_MOD)
    shutil.copy(os.path.join(src, "Scripts", "main.lua"), os.path.join(mod, "Scripts", "main.lua"))
    shutil.copy(os.path.join(src, "settings.ini"), os.path.join(mod, "settings.ini"))
    shutil.copy(check_translation.LYRICS, os.path.join(mod, "lyrics.srt"))
    # UE4SS は、このファイルがある MOD を mods.txt に書かれていなくても読み込む
    with io.open(os.path.join(mod, "enabled.txt"), "w", encoding="utf-8", newline="\r\n") as f:
        f.write("このファイルがあると、UE4SS がこの MOD を読み込みます。\n")

    lic = download(UE4SS["license_url"], UE4SS["license_sha256"], "UE4SS-LICENSE")
    shutil.copy(lic, os.path.join(stage, "licenses", "UE4SS-LICENSE"))
    return len(cues)


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
    repak = fetch_tool("repak", TOOLS["repak"])
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

    print("▶ エンディングの歌詞の字幕（UE4SS）を入れる")
    lines = stage_ue4ss(stage)
    if lines:
        print("  字幕 %d行" % lines)
    else:
        print("  ! 歌詞の訳がまだありません。導入ツールは UE4SS を入れません")

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
