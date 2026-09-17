# -*- coding: utf-8 -*-
"""PO（gettext）ファイルの読み書き。

翻訳の管理はこの形式で行います。
`msgctxt`に`名前空間/キー`を入れ、`msgid`に原文、`msgstr`に訳文を置きます。
原文が同じで別のキーの項目があるため、`msgctxt`で区別します。
"""
import io

ESCAPES = [
    ("\\", "\\\\"),
    ('"', '\\"'),
    ("\r", "\\r"),
    ("\n", "\\n"),
    ("\t", "\\t"),
]

HEADER = (
    'msgid ""\n'
    'msgstr ""\n'
    '"Project-Id-Version: Indigo Park Localization\\n"\n'
    '"Language: ja\\n"\n'
    '"MIME-Version: 1.0\\n"\n'
    '"Content-Type: text/plain; charset=UTF-8\\n"\n'
    '"Content-Transfer-Encoding: 8bit\\n"\n'
    "\n"
)


def escape(s):
    for a, b in ESCAPES:
        s = s.replace(a, b)
    return s


def unescape(s):
    out = []
    i = 0
    table = {"n": "\n", "r": "\r", "t": "\t", '"': '"', "\\": "\\"}
    while i < len(s):
        c = s[i]
        if c == "\\" and i + 1 < len(s):
            out.append(table.get(s[i + 1], s[i + 1]))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def write(entries, path):
    """entries: [{'id','source','target','comment'}] を PO として書き出す"""
    with io.open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(HEADER)
        for e in entries:
            if e.get("comment"):
                f.write("#. %s\n" % e["comment"])
            f.write('msgctxt "%s"\n' % escape(e["id"]))
            f.write('msgid "%s"\n' % escape(e["source"]))
            f.write('msgstr "%s"\n\n' % escape(e.get("target") or ""))


def read(path):
    """PO を読み、id -> 訳文 の辞書にする。訳文が空の項目は入れない"""
    out = {}
    ctxt = None
    field = None
    buf = {"msgctxt": "", "msgid": "", "msgstr": ""}
    with io.open(path, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#"):
                if not line:
                    if buf["msgctxt"] and buf["msgstr"]:
                        out[buf["msgctxt"]] = buf["msgstr"]
                    buf = {"msgctxt": "", "msgid": "", "msgstr": ""}
                    field = None
                continue
            for name in ("msgctxt", "msgid", "msgstr"):
                if line.startswith(name + ' "'):
                    field = name
                    buf[name] = unescape(line[len(name) + 2 : -1])
                    break
            else:
                if line.startswith('"') and field:
                    buf[field] += unescape(line[1:-1])
    if buf["msgctxt"] and buf["msgstr"]:
        out[buf["msgctxt"]] = buf["msgstr"]
    return out
