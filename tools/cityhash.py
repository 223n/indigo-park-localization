import struct
M = (1 << 64) - 1
K0 = 0xc3a5c85c97cb3127
K1 = 0xb492b66fbe98f273
K2 = 0x9ae16a3b2f90404f

def m(v): return v & M
def f64(s, i): return struct.unpack_from('<Q', s, i)[0]
def f32(s, i): return struct.unpack_from('<I', s, i)[0]
def rot(v, sh): return v if sh == 0 else m((v >> sh) | (v << (64 - sh)))
def shiftmix(v): return v ^ (v >> 47)
def bswap(v): return int.from_bytes(m(v).to_bytes(8, 'little'), 'big')

def hash128to64(low, high):
    kmul = 0x9ddfea08eb382d69
    a = m((low ^ high) * kmul); a ^= a >> 47
    b = m((high ^ a) * kmul);   b ^= b >> 47
    return m(b * kmul)

def hashlen16(u, v): return hash128to64(u, v)

def hashlen16m(u, v, mul):
    a = m((u ^ v) * mul); a ^= a >> 47
    b = m((v ^ a) * mul); b ^= b >> 47
    return m(b * mul)

def hashlen0to16(s):
    l = len(s)
    if l >= 8:
        mul = m(K2 + 2 * l)
        a = m(f64(s, 0) + K2)
        b = f64(s, l - 8)
        c = m(m(rot(b, 37) * mul) + a)
        d = m(m(rot(a, 25) + b) * mul)
        return hashlen16m(c, d, mul)
    if l >= 4:
        mul = m(K2 + 2 * l)
        a = f32(s, 0)
        return hashlen16m(m(l + m(a << 3)), f32(s, l - 4), mul)
    if l > 0:
        a = s[0]; b = s[l >> 1]; c = s[l - 1]
        y = m(a + (b << 8))
        z = m(l + (c << 2))
        return m(shiftmix(m(y * K2) ^ m(z * K0)) * K2)
    return K2

def hashlen17to32(s):
    l = len(s); mul = m(K2 + 2 * l)
    a = m(f64(s, 0) * K1)
    b = f64(s, 8)
    c = m(f64(s, l - 8) * mul)
    d = m(f64(s, l - 16) * K2)
    return hashlen16m(m(rot(m(a + b), 43) + rot(c, 30) + d),
                      m(a + rot(m(b + K2), 18) + c), mul)

def weak32(w, x, y, z, a, b):
    a = m(a + w)
    b = rot(m(b + a + z), 21)
    c = a
    a = m(a + x); a = m(a + y)
    b = m(b + rot(a, 44))
    return (m(a + z), m(b + c))

def weak32s(s, off, a, b):
    return weak32(f64(s, off), f64(s, off + 8), f64(s, off + 16), f64(s, off + 24), a, b)

def hashlen33to64(s):
    l = len(s); mul = m(K2 + 2 * l)
    a = m(f64(s, 0) * K2)
    b = f64(s, 8)
    c = f64(s, l - 24)
    d = f64(s, l - 32)
    e = m(f64(s, 16) * K2)
    f = m(f64(s, 24) * 9)
    g = f64(s, l - 8)
    h = m(f64(s, l - 16) * mul)
    u = m(rot(m(a + g), 43) + m(m(rot(b, 30) + c) * 9))
    v = m(m(m(a + g) ^ d) + f + 1)
    w = m(bswap(m(m(u + v) * mul)) + h)
    x = m(rot(m(e + f), 42) + c)
    y = m(m(bswap(m(m(v + w) * mul)) + g) * mul)
    z = m(e + f + c)
    a = m(bswap(m(m(m(x + z) * mul) + y)) + b)
    b = m(shiftmix(m(m(m(z + a) * mul) + d + h)) * mul)
    return m(b + x)

def cityhash64(s):
    l = len(s)
    if l <= 32:
        return hashlen0to16(s) if l <= 16 else hashlen17to32(s)
    if l <= 64:
        return hashlen33to64(s)
    x = f64(s, l - 40)
    y = m(f64(s, l - 16) + f64(s, l - 56))
    z = hashlen16(m(f64(s, l - 48) + l), f64(s, l - 24))
    v = weak32s(s, l - 64, l, z)
    w = weak32s(s, l - 32, m(y + K1), x)
    x = m(m(x * K1) + f64(s, 0))
    n = (l - 1) & ~63
    off = 0
    while True:
        x = m(rot(m(x + y + v[0] + f64(s, off + 8)), 37) * K1)
        y = m(rot(m(y + v[1] + f64(s, off + 48)), 42) * K1)
        x ^= w[1]
        y = m(y + v[0] + f64(s, off + 40))
        z = m(rot(m(z + w[0]), 33) * K1)
        v = weak32s(s, off, m(v[1] * K1), m(x + w[0]))
        w = weak32s(s, off + 32, m(z + w[1]), m(y + f64(s, off + 16)))
        z, x = x, z
        off += 64; n -= 64
        if n == 0: break
    return hashlen16(m(hashlen16(v[0], w[0]) + m(shiftmix(y) * K1) + z),
                     m(hashlen16(v[1], w[1]) + x))

def text_key_hash(s):
    if s == '': return 0
    h = cityhash64(s.encode('utf-16-le'))
    return ((h & 0xFFFFFFFF) + ((h >> 32) & 0xFFFFFFFF) * 23) & 0xFFFFFFFF
