# -*- coding: utf-8 -*-
"""SRT（字幕）ファイルの読み込み。

エンディングの歌詞の訳は`data/lyrics.ja.srt`にこの形式で書きます。
ゲームの中で表示するUE4SSのMOD（`ue4ss/IndigoParkJP_Lyrics/Scripts/main.lua`）も、
同じ読み方をします。片方の読み方を変えたときは、もう片方も合わせてください。

    1
    00:00:12,500 --> 00:00:16,000
    1行目の訳

    2
    00:00:16,500 --> 00:00:20,000
    2行目の訳
    （改行した続き）

行の頭に`{\\an8}`と書いた行は中央上に、`{\\an2}`と書いた行は中央下に出します。
字幕の編集ソフトが位置の指定に使う書き方で、数字はテンキーの並びです（7〜9が上、1〜3が下）。
中央の4〜6には対応していません。

字幕の編集ソフトが付ける書式（`<i>`や`{\\an8}`）は、画面にそのまま出てしまうため除きます。
"""
import io
import re

TIME = re.compile(
    r"^\s*(\d+):(\d\d):(\d\d)[,.](\d+)\s*-->\s*(\d+):(\d\d):(\d\d)[,.](\d+)")
INDEX = re.compile(r"^\s*\d+\s*$")
MARKUP = re.compile(r"<[^>]*>|\{\\[^}]*\}")
ALIGN = re.compile(r"\{\\an(\d)\}")


def seconds(h, m, s, frac):
    return int(h) * 3600 + int(m) * 60 + int(s) + int(frac) / 10 ** len(frac)


def position(body):
    """{\\an数字} から位置を返す。"top"、"bottom"、対応しない数字なら "middle"、無ければ None"""
    m = ALIGN.search(body)
    if not m:
        return None
    an = int(m.group(1))
    if an >= 7:
        return "top"
    if an <= 3:
        return "bottom"
    return "middle"


def parse(text):
    """SRTを読み、(字幕の一覧, 読めなかった塊の一覧) を返す。

    字幕は {"from": 秒, "to": 秒, "text": 文, "position": 位置, "line": 塊の先頭の行番号} で、
    開始の早い順に並べる。位置は position() の値です。
    読めなかった塊は (行番号, 先頭の行) の一覧で返す。
    """
    text = text.lstrip("﻿").replace("\r\n", "\n").replace("\r", "\n")
    cues = []
    bad = []
    block = []
    start = 0

    def flush():
        if not block:
            return
        i = 1 if INDEX.match(block[0]) and len(block) > 1 else 0
        m = TIME.match(block[i])
        raw = "\n".join(block[i + 1:])
        body = MARKUP.sub("", raw)
        if m and body:
            cues.append({
                "from": seconds(*m.groups()[:4]),
                "to": seconds(*m.groups()[4:]),
                "text": body,
                "position": position(raw),
                "line": start,
            })
        else:
            bad.append((start, block[0]))

    for n, line in enumerate(text.split("\n"), 1):
        # Lua の %s と同じく、ASCII の空白だけを空白とみなす。全角の空白は文字として残す
        if line.strip(" \t\v\f"):
            if not block:
                start = n
            block.append(line)
        else:
            flush()
            block = []
    flush()
    cues.sort(key=lambda c: c["from"])
    return cues, bad


def read(path):
    """UTF-8のSRTを読む。UTF-8でなければ UnicodeDecodeError になる"""
    with io.open(path, encoding="utf-8-sig") as f:
        return parse(f.read())
