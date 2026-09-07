"""Rasterise the AI Quota brand icon to real PNGs.

Mirrors custom_components/ai_quota/brand/icon.svg geometry exactly. Renders at 3x
and box-downsamples, which both antialiases and produces the 512/256 pair.
No third-party deps: analytic coverage + a minimal zlib/struct PNG writer.
"""
import math, struct, sys, zlib
from pathlib import Path

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "custom_components" / "ai_quota" / "brand"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
SS = 3                      # supersample factor
BASE = 512                  # SVG user-space size
N = BASE * SS

# ---- palette (matches icon.svg) -------------------------------------------
BG_TOP, BG_BOT = (0x28, 0x2D, 0x37), (0x12, 0x14, 0x1A)
ARC_STOPS = [(0.0, (0x4A, 0xDE, 0x80)), (0.45, (0x5E, 0xE9, 0xA0)),
             (0.8, (0xA8, 0x55, 0xF7)), (1.0, (0xA8, 0x55, 0xF7))]
DOT_RGB = (0x4B, 0x55, 0x63)
BOLT_RGB = (0xFF, 0xFF, 0xFF)

# ---- geometry (matches icon.svg) ------------------------------------------
CORNER_R = 112.0
CX = CY = 256.0
ARC_R = 150.0
ARC_HW = 13.0               # stroke-width 26
HALO_HW = 26.0              # stroke-width 52
HALO_A = 0.22
A_START, A_END = 60.0, 300.0            # sweep, degrees, y-down clockwise
P_START = (CX + ARC_R * math.cos(math.radians(A_START)),
           CY + ARC_R * math.sin(math.radians(A_START)))
P_END = (CX + ARC_R * math.cos(math.radians(A_END)),
         CY + ARC_R * math.sin(math.radians(A_END)))
DOT_HW = 7.0                # stroke-width 14
N_DOTS = 8                  # dotted remainder across the 120-degree gap
DOTS = []
for i in range(N_DOTS):
    a = math.radians(A_END + (360.0 - (A_END - A_START)) * (i + 0.5) / N_DOTS)
    DOTS.append((CX + ARC_R * math.cos(a), CY + ARC_R * math.sin(a)))

BOLT = [(272, 176), (212, 266), (246, 266), (240, 336), (300, 242), (266, 242)]

# gradient axis (120,400) -> (392,112)
GX, GY, GDX, GDY = 120.0, 400.0, 272.0, -288.0
GLEN2 = GDX * GDX + GDY * GDY


def arc_colour(x, y):
    t = ((x - GX) * GDX + (y - GY) * GDY) / GLEN2
    t = 0.0 if t < 0 else (1.0 if t > 1 else t)
    for i in range(len(ARC_STOPS) - 1):
        t0, c0 = ARC_STOPS[i]
        t1, c1 = ARC_STOPS[i + 1]
        if t <= t1:
            f = (t - t0) / (t1 - t0)
            return (c0[0] + (c1[0] - c0[0]) * f,
                    c0[1] + (c1[1] - c0[1]) * f,
                    c0[2] + (c1[2] - c0[2]) * f)
    return ARC_STOPS[-1][1]


def in_round_rect(x, y):
    if CORNER_R <= x <= BASE - CORNER_R or CORNER_R <= y <= BASE - CORNER_R:
        return 0.0 <= x <= BASE and 0.0 <= y <= BASE
    kx = CORNER_R if x < CORNER_R else BASE - CORNER_R
    ky = CORNER_R if y < CORNER_R else BASE - CORNER_R
    return (x - kx) ** 2 + (y - ky) ** 2 <= CORNER_R * CORNER_R


def in_bolt(x, y):
    inside = False
    n = len(BOLT)
    j = n - 1
    for i in range(n):
        xi, yi = BOLT[i]
        xj, yj = BOLT[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def on_arc(x, y, hw):
    dx, dy = x - CX, y - CY
    r = math.hypot(dx, dy)
    if abs(r - ARC_R) <= hw:
        a = math.degrees(math.atan2(dy, dx)) % 360.0
        if A_START <= a <= A_END:
            return True
    return ((x - P_START[0]) ** 2 + (y - P_START[1]) ** 2 <= hw * hw or
            (x - P_END[0]) ** 2 + (y - P_END[1]) ** 2 <= hw * hw)


def on_dots(x, y):
    for dx0, dy0 in DOTS:
        if (x - dx0) ** 2 + (y - dy0) ** 2 <= DOT_HW * DOT_HW:
            return True
    return False


def sample(x, y):
    """-> (r, g, b, a) floats 0..255 / 0..1 for one point in SVG user space."""
    if not in_round_rect(x, y):
        return (0.0, 0.0, 0.0, 0.0)
    f = y / BASE
    r = BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * f
    g = BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * f
    b = BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * f
    if on_dots(x, y):
        r, g, b = DOT_RGB
    if on_arc(x, y, HALO_HW):
        ar, ag, ab = arc_colour(x, y)
        r += (ar - r) * HALO_A
        g += (ag - g) * HALO_A
        b += (ab - b) * HALO_A
    if on_arc(x, y, ARC_HW):
        r, g, b = arc_colour(x, y)
    if in_bolt(x, y):
        r, g, b = BOLT_RGB
    return (r, g, b, 1.0)


def render():
    """Full-res RGBA accumulation buffer at N x N."""
    buf = bytearray(N * N * 4)
    step = BASE / N
    half = step / 2.0
    for py in range(N):
        y = py * step + half
        row = py * N * 4
        for px in range(N):
            r, g, b, a = sample(px * step + half, y)
            o = row + px * 4
            buf[o] = int(r + 0.5)
            buf[o + 1] = int(g + 0.5)
            buf[o + 2] = int(b + 0.5)
            buf[o + 3] = 255 if a else 0
        if py % 256 == 0:
            print(f"  row {py}/{N}", flush=True)
    return buf


def downsample(buf, out_size):
    k = N // out_size
    assert N % out_size == 0, (N, out_size)
    rows = []
    k2 = k * k
    for oy in range(out_size):
        row = bytearray()
        for ox in range(out_size):
            ar = ag = ab = aa = 0
            for sy in range(k):
                base = ((oy * k + sy) * N + ox * k) * 4
                for sx in range(k):
                    o = base + sx * 4
                    al = buf[o + 3]
                    aa += al
                    if al:
                        ar += buf[o]; ag += buf[o + 1]; ab += buf[o + 2]
            if aa:
                n_op = aa // 255
                row += bytes((ar // n_op, ag // n_op, ab // n_op, aa // k2))
            else:
                row += b"\0\0\0\0"
        rows.append(bytes(row))
    return rows


def write_png(rows, w, h, path, interlace=0):
    raw = b"".join(b"\x00" + r for r in rows)
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, interlace))
           + chunk(b"IDAT", zlib.compress(raw, 9))
           + chunk(b"IEND", b""))
    path.write_bytes(png)
    print(f"  wrote {path.name}  {w}x{h}  {len(png)}b")


print(f"rendering {N}x{N} ({SS}x supersample)...")
buf = render()
for size, name in ((512, "icon@2x.png"), (256, "icon.png")):
    write_png(downsample(buf, size), size, size, OUT / name)
print("done")
