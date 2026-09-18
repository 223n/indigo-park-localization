# -*- coding: utf-8 -*-
"""cooked済みのアセットから、翻訳の対象になる文字列を集める。

    python tools/harvest.py <展開したアセットのディレクトリ> > harvest.json

FTextの置かれ方は2通りあります。どちらも拾います。

1. プロパティに置かれたもの（ウィジェットなど）
     長さ付きの文字列で、名前空間 → キー → 原文 の順
2. Blueprintのバイトコードに置かれたもの（レベルや関数の中）
     `0x1F`に続くヌル終端の文字列で、原文 → キー → 名前空間 の順

2は`EX_TextConst`の並びです。1だけを見ていると、
目標の表示や操作の案内を取りこぼします。
"""
import json
import os
import re
import struct
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

# 自動で作られるキーは32桁の16進数。
# プロパティでは長さ33のFString、バイトコードでは 0x1F に続くヌル終端になる
KEY_PROPERTY = re.compile(rb"\x21\x00\x00\x00([0-9A-F]{32})\x00")
KEY_BYTECODE = re.compile(rb"\x1f([0-9A-F]{32})\x00")
MAX_BACK = 8000


def read_fstring(b, o):
    """oの位置からFStringを読む。読めなければ(None, o)"""
    if o + 4 > len(b):
        return None, o
    (n,) = struct.unpack_from("<i", b, o)
    o += 4
    if n == 0:
        return "", o
    if n > 0:
        if n > 20000 or o + n > len(b) or b[o + n - 1] != 0:
            return None, o
        try:
            return b[o:o + n - 1].decode("utf-8"), o + n
        except Exception:
            return None, o
    n = -n
    if n > 20000 or o + n * 2 > len(b):
        return None, o
    try:
        return b[o:o + n * 2 - 2].decode("utf-16-le"), o + n * 2
    except Exception:
        return None, o


def read_fstring_ending_at(b, end):
    """endの位置で終わるFStringを、長さを逆にたどって読む"""
    lo = max(0, end - MAX_BACK)
    for start in range(end - 5, lo - 1, -1):
        if start + 4 > len(b):
            continue
        (n,) = struct.unpack_from("<i", b, start)
        if n > 0:
            if start + 4 + n != end or n > 20000 or b[end - 1] != 0:
                continue
            try:
                return b[start + 4:end - 1].decode("utf-8"), start
            except Exception:
                continue
        elif n < 0:
            m = -n
            if start + 4 + m * 2 != end or m > 20000:
                continue
            try:
                return b[start + 4:end - 2].decode("utf-16-le"), start
            except Exception:
                continue
    return None, None


def read_cstring_ending_at(b, end):
    """endの直前で終わるヌル終端文字列を読む。0x1F（ANSI）と0x32（UTF-16）に対応"""
    # ANSI: 0x1F <本体> 0x00
    lo = max(0, end - MAX_BACK)
    for start in range(end - 2, lo - 1, -1):
        if b[start] != 0x1F:
            continue
        body = b[start + 1:end - 1]
        if b"\x00" in body:
            return None, None
        try:
            return body.decode("utf-8"), start
        except Exception:
            return None, None
    return None, None


def harvest(b):
    """(名前空間, キー, 原文, 置かれ方) を返す"""
    out = []
    seen = set()

    # 1. プロパティ: 名前空間 → キー → 原文
    for m in KEY_PROPERTY.finditer(b):
        ks, ke = m.start(), m.end()
        key = m.group(1).decode()
        if ks < 4:
            continue
        (nlen,) = struct.unpack_from("<i", b, ks - 4)
        ns = None
        if nlen == 0:
            ns = ""
        elif 0 < nlen < 200 and ks - 4 - nlen >= 0 and b[ks - 5] == 0:
            try:
                ns = b[ks - 4 - nlen:ks - 5].decode("utf-8")
            except Exception:
                ns = None
        if ns is None:
            continue
        src, _ = read_fstring(b, ke)
        if src:
            out.append((ns, key, src, "property"))
            seen.add(key)

    # 2. バイトコード: 原文 → キー → 名前空間
    for m in KEY_BYTECODE.finditer(b):
        key = m.group(1).decode()
        if key in seen:
            continue
        src, _ = read_cstring_ending_at(b, m.start())
        if not src:
            continue
        ns = ""
        after = m.end()
        if after < len(b) and b[after] == 0x1F:
            j = b.find(b"\x00", after + 1)
            if 0 <= j - (after + 1) < 200:
                try:
                    ns = b[after + 1:j].decode("utf-8")
                except Exception:
                    ns = ""
        out.append((ns, key, src, "bytecode"))
        seen.add(key)
    return out


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "full"
    found = {}
    scanned = 0
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".uexp"):
                continue
            path = os.path.join(dirpath, fn)
            rel = os.path.relpath(path, root).replace(os.sep, "/")
            try:
                b = open(path, "rb").read()
            except Exception:
                continue
            scanned += 1
            order = {}
            for ns, key, src, kind in harvest(b):
                ident = (ns, key)
                if ident not in found:
                    found[ident] = {
                        "namespace": ns, "key": key, "source": src,
                        "kind": kind, "asset": rel,
                        "order": order.get(rel, 0),
                    }
                    order[rel] = order.get(rel, 0) + 1
            if scanned % 2000 == 0:
                sys.stderr.write("  %d件走査 / %d件\n" % (scanned, len(found)))
    sys.stderr.write("走査 %d件 / FText %d件\n" % (scanned, len(found)))
    json.dump(sorted(found.values(), key=lambda e: (e["asset"], e["order"])),
              sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
