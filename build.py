#!/usr/bin/env python3
"""Compile Rime flypy dictionaries into the single-file lookup page.

Sources (see data/README.md):
  data/flypy_chars.dict.yaml      single chars, full code <shuangpin>~<shape>
  data/flypy_chars_ext.dict.yaml  extended/rare chars, weight 0
  data/flyhe_chars.dict.yaml      char -> tone-marked pinyin + weight

Output: index.html (src/template.html with JSON injected) and icons/icon-*.png.

Usage: python3 build.py
"""

import json
import pathlib
import struct
import unicodedata
import zlib

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
REPO_URL = "https://github.com/cyriusweng/xhup-lookup"

C_GROUND = (0x07, 0x08, 0x0A, 255)
C_BONE = (0xE8, 0xE3, 0xD9, 255)
C_COBALT = (0x4B, 0x6F, 0xFF, 255)
C_GOLD = (0xC6, 0xA5, 0x6F, 255)


def parse_dict(path):
    """Yield (char, code, weight) from a Rime dict body after '...'."""
    rows = []
    started = False
    for line in path.read_text(encoding="utf-8").splitlines():
        if not started:
            if line.strip() == "...":
                started = True
            continue
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        char, code = parts[0].strip(), parts[1].strip()
        weight = int(parts[2]) if len(parts) > 2 and parts[2].strip().isdigit() else 0
        rows.append((char, code, weight))
    return rows


def strip_tone(pinyin):
    """xiǎo -> xiao, lǚ -> lü (keep the umlaut, drop only tone marks)."""
    tones = {"\u0300", "\u0301", "\u0304", "\u030C"}
    decomposed = unicodedata.normalize("NFD", pinyin)
    kept = "".join(c for c in decomposed if c not in tones)
    return unicodedata.normalize("NFC", kept)


def build_payload():
    code_rows = parse_dict(DATA / "flypy_chars.dict.yaml")
    code_rows += parse_dict(DATA / "flypy_chars_ext.dict.yaml")

    # char -> [(tone-marked pinyin, weight)] sorted by weight desc
    readings = {}
    for char, pinyin, weight in parse_dict(DATA / "flyhe_chars.dict.yaml"):
        bucket = readings.setdefault(char, [])
        if pinyin not in {p for p, _ in bucket}:
            bucket.append((pinyin, weight))
    for bucket in readings.values():
        bucket.sort(key=lambda r: r[1], reverse=True)

    # group full-code rows by 2-letter shuangpin, dedup
    groups = {}
    for char, code, weight in code_rows:
        if "~" not in code:
            continue
        sp, xm = code.split("~", 1)
        if len(sp) != 2 or len(xm) != 2 or not sp.isalpha() or not xm.isalpha():
            continue
        bucket = groups.setdefault(sp, {})
        key = (char, xm)
        if key not in bucket or weight > bucket[key]:
            bucket[key] = weight

    # One syllable per group, globally one-to-one: a syllable is claimed by
    # the group with the most votes for it (uw/shei vs uv/shui needs this).
    votes_by_group = {}
    for sp, bucket in groups.items():
        votes = {}
        for (char, _) in bucket:
            for pinyin, _ in readings.get(char, []):
                s = strip_tone(pinyin)
                votes[s] = votes.get(s, 0) + 1
        if votes:
            votes_by_group[sp] = votes

    claimed = {}
    label = {}
    def claim_strength(item):
        _, votes = item
        return votes[max(votes, key=lambda k: votes[k])]
    for sp, votes in sorted(votes_by_group.items(), key=claim_strength, reverse=True):
        for syl, _ in sorted(votes.items(), key=lambda kv: -kv[1]):
            if syl not in claimed:
                claimed[syl] = sp
                label[sp] = syl
                break
        else:
            label[sp] = max(votes, key=lambda k: votes[k])
            print(f"WARN unclaimed duplicate label: {sp} -> {label[sp]}")

    payload = {}
    for sp, bucket in groups.items():
        syl = label.get(sp, "")
        rows = []
        for (char, xm), weight in bucket.items():
            py = syl  # a char's code implies this syllable whatever its dict reading
            for pinyin, _ in readings.get(char, []):
                if strip_tone(pinyin) == syl:
                    py = pinyin
                    break
            rows.append([char, xm, weight, py])
        rows.sort(key=lambda r: (r[2] == 0, -r[2], r[0]))
        payload[sp] = [syl, rows]
    return payload


# --- icon generation: abstract field mark (DESIGN.md 6.2) -------------------
# black ground, bone axis at 38.2% x, cobalt force line rising through it,
# gold return dot. Small sizes keep axis + force line only.


def write_png(path, pixels, size):
    buf = bytearray()
    for row in pixels:
        buf.append(0)
        for cell in row:
            buf.extend(cell)
    raw = bytes(buf)
    def chunk(tag, data):
        c = tag + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c))
    header = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header)
        + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b"")
    )


def dist_to_segment(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    cx, cy = ax + t * dx, ay + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def blend(dst, src, alpha):
    return tuple(round(s * alpha + d * (1 - alpha)) for s, d in zip(src, dst))


def make_icon(size):
    px = [[C_GROUND] * size for _ in range(size)]
    ax = size * 0.382  # bone axis, vertical
    axis_w = max(1.0, size / 32)
    # cobalt force line: from lower-left toward upper-right, crossing the axis
    x0, y0 = size * 0.14, size * 0.86
    x1, y1 = size * 0.84, size * 0.16
    force_w = max(1.6, size / 12)
    for yy in range(size):
        for xx in range(size):
            d_axis = abs(xx - ax)
            if d_axis <= axis_w:
                a = 0.9 if d_axis <= axis_w * 0.5 else 0.55
                px[yy][xx] = blend(px[yy][xx], C_BONE, a)
            d_force = dist_to_segment(xx, yy, x0, y0, x1, y1)
            if d_force <= force_w:
                a = min(1.0, (force_w - d_force) / force_w + 0.35)
                px[yy][xx] = blend(px[yy][xx], C_COBALT, a)
    if size >= 64:  # gold return dot, lower right
        r = max(2.0, size / 22)
        gx, gy = size * 0.80, size * 0.82
        for yy in range(size):
            for xx in range(size):
                if (xx - gx) ** 2 + (yy - gy) ** 2 <= r * r:
                    px[yy][xx] = blend(px[yy][xx], C_GOLD, 0.95)
    return px


def main():
    payload = build_payload()
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))

    template = (ROOT / "src" / "template.html").read_text(encoding="utf-8")
    assert "/*__DATA__*/{}" in template, "template missing data placeholder"
    assert "__REPO_URL__" in template, "template missing repo placeholder"
    html = template.replace("/*__DATA__*/{}", body).replace("__REPO_URL__", REPO_URL)
    (ROOT / "index.html").write_text(html, encoding="utf-8")

    icons = ROOT / "icons"
    icons.mkdir(exist_ok=True)
    for size in (16, 32, 64, 128, 192, 512):
        write_png(icons / f"icon-{size}.png", make_icon(size), size)

    chars = {r[0] for v in payload.values() for r in v[1]}
    entries = sum(len(v[1]) for v in payload.values())
    print(
        f"groups={len(payload)} entries={entries} chars={len(chars)} "
        f"json_kb={len(body.encode()) // 1024} "
        f"html_kb={(ROOT / 'index.html').stat().st_size // 1024}"
    )


if __name__ == "__main__":
    main()
