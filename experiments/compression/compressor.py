"""
Compression Discovery — Custom Compressor
============================================
THIS IS THE FILE CLAUDE OPTIMIZES.

BEST VERSION: Experiment 8 — LZ77 (4-byte hash, 512K table) + dual Huffman
with deflate-style length and distance codes.

Results: ratio 0.2384 (vs gzip 0.2292), composite 0.6818 (vs gzip 0.7366)
"""

from struct import pack, unpack
from collections import Counter
import heapq


# Deflate-style tables
_LEN_TABLE = [
    (3,0),(4,0),(5,0),(6,0),(7,0),(8,0),(9,0),(10,0),
    (11,1),(13,1),(15,1),(17,1),(19,2),(23,2),(27,2),(31,2),
    (35,3),(43,3),(51,3),(59,3),(67,4),(83,4),(99,4),(115,4),
    (131,5),(163,5),(195,5),(227,5),(258,0),
]
_DIST_TABLE = [
    (1,0),(2,0),(3,0),(4,0),(5,1),(7,1),(9,2),(13,2),
    (17,3),(25,3),(33,4),(49,4),(65,5),(97,5),(129,6),(193,6),
    (257,7),(385,7),(513,8),(769,8),(1025,9),(1537,9),
    (2049,10),(3073,10),(4097,11),(6145,11),(8193,12),(12289,12),
    (16385,13),(24577,13),(32769,14),
]


def _encode_length(length):
    for i in range(len(_LEN_TABLE) - 1, -1, -1):
        if length >= _LEN_TABLE[i][0]:
            return 257 + i, _LEN_TABLE[i][1], length - _LEN_TABLE[i][0]
    return 257, 0, 0


def _encode_distance(dist):
    for i in range(len(_DIST_TABLE) - 1, -1, -1):
        if dist >= _DIST_TABLE[i][0]:
            return i, _DIST_TABLE[i][1], dist - _DIST_TABLE[i][0]
    return 0, 0, 0


def compress(data: bytes) -> bytes:
    """LZ77 + dual Huffman with deflate-style codes."""
    if not data:
        return b'\x00'

    tokens = _lz77_encode(data)

    ll_syms = []
    dist_info = []

    for tok in tokens:
        if isinstance(tok, int):
            ll_syms.append((tok, 0, 0))
        else:
            dist, length = tok
            lc, le_bits, le_val = _encode_length(length)
            ll_syms.append((lc, le_bits, le_val))
            dist_info.append(_encode_distance(dist))

    ll_freq = Counter(s[0] for s in ll_syms)
    ll_codes, ll_lens, ll_tree = _build_huffman(ll_freq)

    dc_freq = Counter(d[0] for d in dist_info)
    dc_codes, dc_lens, dc_tree = _build_huffman(dc_freq)

    # Encode interleaved bitstream
    buf = 0
    nbits = 0
    out = bytearray()

    di = 0
    for sym, le_bits, le_val in ll_syms:
        buf = (buf << ll_lens[sym]) | ll_codes[sym]
        nbits += ll_lens[sym]
        if le_bits:
            buf = (buf << le_bits) | le_val
            nbits += le_bits
        while nbits >= 16:
            nbits -= 8
            out.append((buf >> nbits) & 0xFF)
            buf &= (1 << nbits) - 1
        if sym >= 257:
            dc, de_bits, de_val = dist_info[di]; di += 1
            buf = (buf << dc_lens[dc]) | dc_codes[dc]
            nbits += dc_lens[dc]
            if de_bits:
                buf = (buf << de_bits) | de_val
                nbits += de_bits
            while nbits >= 16:
                nbits -= 8
                out.append((buf >> nbits) & 0xFF)
                buf &= (1 << nbits) - 1

    while nbits >= 8:
        nbits -= 8
        out.append((buf >> nbits) & 0xFF)
        buf &= (1 << nbits) - 1
    padding = 0
    if nbits > 0:
        padding = 8 - nbits
        out.append((buf << padding) & 0xFF)

    result = bytearray()
    result.append(0x0B)
    result.extend(pack('>I', len(data)))
    result.extend(pack('>I', len(ll_syms)))
    result.extend(pack('>H', len(ll_tree)))
    result.extend(ll_tree)
    result.extend(pack('>H', len(dc_tree)))
    result.extend(dc_tree)
    result.append(padding)
    result.extend(out)
    return bytes(result)


def _lz77_encode(data):
    """LZ77 with 4-byte hash and array-based hash chain."""
    WINDOW = 32767
    MAX_LEN = 258
    MIN_LEN = 3
    MAX_CHAIN = 64
    HMASK = 0x7FFFF  # 19-bit → 512K entries

    n = len(data)
    head = [-1] * (HMASK + 1)
    prev_arr = [-1] * n
    tokens = []
    i = 0

    while i < n - 2:
        if i + 3 < n:
            h = ((data[i] << 15) ^ (data[i+1] << 10) ^ (data[i+2] << 5) ^ data[i+3]) & HMASK
        else:
            h = ((data[i] << 10) ^ (data[i+1] << 5) ^ data[i+2]) & HMASK

        p = head[h]
        best_len = 0
        best_dist = 0
        steps = 0
        d0 = data[i]
        d1 = data[i+1]

        while p >= 0 and p < i and i - p <= WINDOW and steps < MAX_CHAIN:
            if data[p] == d0 and data[p+1] == d1:
                ml = 0
                limit = min(MAX_LEN, n - i)
                pp = p
                ii = i
                while ml < limit and data[pp] == data[ii]:
                    ml += 1; pp += 1; ii += 1
                if ml >= MIN_LEN and ml > best_len:
                    best_len = ml
                    best_dist = i - p
                    if ml >= MAX_LEN:
                        break
            p = prev_arr[p]
            steps += 1

        prev_arr[i] = head[h]
        head[h] = i

        if best_len >= MIN_LEN:
            tokens.append((best_dist, best_len))
            for k in range(1, min(best_len, 32)):
                j = i + k
                if j + 2 >= n:
                    break
                if j + 3 < n:
                    hk = ((data[j] << 15) ^ (data[j+1] << 10) ^ (data[j+2] << 5) ^ data[j+3]) & HMASK
                else:
                    hk = ((data[j] << 10) ^ (data[j+1] << 5) ^ data[j+2]) & HMASK
                prev_arr[j] = head[hk]
                head[hk] = j
            i += best_len
        else:
            tokens.append(data[i])
            i += 1

    while i < n:
        tokens.append(data[i])
        i += 1

    return tokens


def _build_huffman(freq):
    if len(freq) == 1:
        sym = list(freq.keys())[0]
        return {sym: 0}, {sym: 1}, pack('>HHB', 1, sym, 1)

    heap = [(cnt, idx, sym) for idx, (sym, cnt) in enumerate(freq.items())]
    heapq.heapify(heap)
    nid = len(heap)
    while len(heap) > 1:
        c1, _, n1 = heapq.heappop(heap)
        c2, _, n2 = heapq.heappop(heap)
        heapq.heappush(heap, (c1 + c2, nid, (n1, n2)))
        nid += 1

    root = heap[0][2]
    lengths = {}
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if isinstance(node, int):
            lengths[node] = max(depth, 1)
        else:
            stack.append((node[0], depth + 1))
            stack.append((node[1], depth + 1))

    for s in lengths:
        if lengths[s] > 15:
            lengths[s] = 15

    items = sorted(lengths.items(), key=lambda x: (x[1], x[0]))
    code_map = {}
    len_map = {}
    code = 0
    prev_l = 0
    for sym, bl in items:
        code <<= (bl - prev_l)
        code_map[sym] = code
        len_map[sym] = bl
        code += 1
        prev_l = bl

    tree = bytearray()
    tree.extend(pack('>H', len(items)))
    for sym, bl in items:
        tree.extend(pack('>HB', sym, bl))

    return code_map, len_map, bytes(tree)


def decompress(data: bytes) -> bytes:
    if not data or data[0] == 0x00:
        return b''
    if data[0] == 0x0B:
        return _decompress_v11(data)
    raise ValueError(f"Unknown method: {data[0]}")


def _decompress_v11(data):
    p = 1
    orig_len = unpack('>I', data[p:p+4])[0]; p += 4
    num_syms = unpack('>I', data[p:p+4])[0]; p += 4

    ll_tree_size = unpack('>H', data[p:p+2])[0]; p += 2
    ll_tree_data = data[p:p+ll_tree_size]; p += ll_tree_size
    dc_tree_size = unpack('>H', data[p:p+2])[0]; p += 2
    dc_tree_data = data[p:p+dc_tree_size]; p += dc_tree_size

    padding = data[p]; p += 1
    encoded = data[p:]

    ll_decode = _build_decode_tree(ll_tree_data)
    dc_decode = _build_decode_tree(dc_tree_data)

    total_enc_bits = len(encoded) * 8
    total_bits = total_enc_bits - padding
    bit_int = int.from_bytes(encoded, 'big') if encoded else 0

    result = bytearray(orig_len)
    ri = 0
    sym_count = 0
    bp = 0

    while sym_count < num_syms and bp < total_bits:
        node = ll_decode
        while 's' not in node:
            bit = (bit_int >> (total_enc_bits - 1 - bp)) & 1
            bp += 1
            node = node[bit]
        sym = node['s']
        sym_count += 1

        if sym < 256:
            result[ri] = sym
            ri += 1
        elif sym >= 257:
            lc = sym - 257
            base_len, eb = _LEN_TABLE[lc]
            length = base_len
            if eb:
                v = 0
                for _ in range(eb):
                    v = (v << 1) | ((bit_int >> (total_enc_bits - 1 - bp)) & 1)
                    bp += 1
                length += v

            node = dc_decode
            while 's' not in node:
                bit = (bit_int >> (total_enc_bits - 1 - bp)) & 1
                bp += 1
                node = node[bit]
            dc = node['s']
            base_dist, deb = _DIST_TABLE[dc]
            dist = base_dist
            if deb:
                v = 0
                for _ in range(deb):
                    v = (v << 1) | ((bit_int >> (total_enc_bits - 1 - bp)) & 1)
                    bp += 1
                dist += v

            start = ri - dist
            for k in range(length):
                result[ri] = result[start + k]
                ri += 1

    return bytes(result[:orig_len])


def _build_decode_tree(tree_data):
    p = 0
    nc = unpack('>H', tree_data[p:p+2])[0]; p += 2
    items = []
    for _ in range(nc):
        sym = unpack('>H', tree_data[p:p+2])[0]; p += 2
        bl = tree_data[p]; p += 1
        items.append((sym, bl))

    tree = {}
    code = 0
    prev_l = 0
    for sym, bl in items:
        code <<= (bl - prev_l)
        node = tree
        for bit_idx in range(bl - 1, -1, -1):
            bit = (code >> bit_idx) & 1
            if bit not in node:
                node[bit] = {}
            node = node[bit]
        node['s'] = sym
        code += 1
        prev_l = bl
    return tree
