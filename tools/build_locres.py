import struct, zlib, os, sys
from cityhash import text_key_hash

MAGIC = bytes.fromhex('0e147475674a03fc4a15909dc3377f1b')

def wr(s):
    if s == '': return struct.pack('<i', 0)
    try:
        a = s.encode('ascii'); return struct.pack('<i', len(a) + 1) + a + b'\x00'
    except UnicodeEncodeError:
        u = s.encode('utf-16-le'); return struct.pack('<i', -(len(u) // 2 + 1)) + u + b'\x00\x00'

def src_hash(s):
    return zlib.crc32(b''.join(struct.pack('<I', ord(c)) for c in s)) & 0xFFFFFFFF

def build(nsmap, path):
    """nsmap: {namespace: [(key, source, translation), ...]} を version 3 の .locres にする"""
    strings = []; idx = {}
    def sid(t):
        if t not in idx: idx[t] = len(strings); strings.append(t)
        return idx[t]
    conv = {ns: [(k, src_hash(src), sid(tr)) for k, src, tr in v] for ns, v in nsmap.items()}
    total = sum(len(v) for v in conv.values())
    body = struct.pack('<I', total) + struct.pack('<I', len(conv))
    for ns, ents in conv.items():
        body += struct.pack('<I', text_key_hash(ns)) + wr(ns) + struct.pack('<I', len(ents))
        for k, sh, i in ents:
            body += struct.pack('<I', text_key_hash(k)) + wr(k) + struct.pack('<I', sh) + struct.pack('<i', i)
    head = MAGIC + bytes([3])
    arr = len(head) + 8 + len(body)
    out = head + struct.pack('<q', arr) + body + struct.pack('<i', len(strings))
    for s in strings: out += wr(s) + struct.pack('<i', 1)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'wb').write(out)
    return total, len(strings), len(out)
