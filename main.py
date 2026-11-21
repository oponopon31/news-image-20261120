#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- front page for Friday 20 November 2026.

Draws a 1024x1024 newspaper front page procedurally with Python 3 stdlib
only (struct + zlib for the PNG encoder, a hand-defined 5x7 bitmap font,
and geometric pictograms). No network, no external files, no randomness:
two runs produce byte-identical output.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (fallback /output).

Layout: 35 stories in 7 regions, every one dated Friday 20 November 2026.
  TOP     1 Kyiv bridges hit -- 2 Cyclone Akvan landfall -- 3 AI sell-off
  MID     4 UK-EU reset deal -- 5 COP31 no deal -- 6 missile in Poland --
          7 Iraqi army in -- 8 Italy general strike
  LOW     9 Japan inflation -- 10 Seoul impeach -- 11 Kenya first oil --
          12 Bukele third term -- 13 Phillips 118
  ALSO    14-35: two-column list of 22 more stories, numbered on the map.
  DATE CHECK: stories deliberately left out because they are
  Thursday 19 November news -- the World Court's ruling on Myanmar,
  the three-leader declaration in Shenzhen, Tonga's drought emergency
  and the migrant boat lost off Senegal. Not yet shown: BepiColombo's
  entry into orbit round Mercury and any final COP31 text.

Facts follow the 35-story reference page for 20 November 2026; the
load-bearing claims were re-verified against live reporting on
21 Nov 2026: Akvan landfall near Gopalpur 07:30-08:30 IST 20 Nov,
300,000+ evacuated, no deaths (IMD); Taiex -6.23% on 20 Nov, worst
week since 1991, Nikkei -5.1%, KOSPI -5.2%, Hang Seng -1.9%
(Reuters/AP); Kh-101 cruise missile down near Nowy Lipowiec, Poland,
on 20 Nov, Rzeszow airport briefly suspended (Polish defence
ministry). All drawings are original geometric work in code.
"""
import hashlib
import math
import os
import struct
import zlib

W = H = 1024

PAPER = (250, 246, 236)   # warm newsprint
INK = (17, 17, 17)        # near-black
GRAY = (74, 74, 74)       # body text
RED = (176, 30, 30)       # accent: date, kickers, alert marks
PANEL = (238, 232, 214)   # light tint for pictogram boxes
NAVY = (24, 40, 72)       # night sky / caption strips
SEA = (70, 110, 170)      # cyclone sea
LAND = (198, 180, 140)    # map land
GREEN = (46, 110, 60)     # fields / region bar
YELLOW = (255, 200, 60)   # bursts / sun
BLUE = (30, 70, 160)      # EU flag blue

# ---------------------------------------------------------------- font ----
# Hand-defined 5x7 bitmap font. '#' = set pixel, '.' = empty.
# Uppercase letters, digits and the punctuation used on the page.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
}

# -------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = c[0]
            self.buf[i + 1] = c[1]
            self.buf[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i] = c[0]
                self.buf[i + 1] = c[1]
                self.buf[i + 2] = c[2]

    def hline(self, x0, x1, y, c, t=1):
        if x1 < x0:
            x0, x1 = x1, x0
        for yy in range(y, y + t):
            for xx in range(x0, x1 + 1):
                self.set(xx, yy, c)

    def vline(self, x, y0, y1, c, t=1):
        if y1 < y0:
            y0, y1 = y1, y0
        for xx in range(x, x + t):
            for yy in range(y0, y1 + 1):
                self.set(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        # Bresenham; thickness by stamping a t x t block on each step.
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x, y, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cx + dx, cy + dy, c)

    def circle(self, cx, cy, r, c, t=1):
        # outline via midpoint steps
        x, y, d = 0, r, 1 - r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.fill_rect(px, py, t, t, c)
            if d < 0:
                d += 2 * x + 3
            else:
                d += 2 * (x - y) + 5
                y -= 1
            x += 1

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        n = len(pts)
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(n):
                x1, y1 = pts[i]
                x2, y2 = pts[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.hline(int(xs[i]), int(xs[i + 1]), y, c)

    def star(self, cx, cy, r, c, t=2):
        # 8-point burst: 4 straight + 4 diagonal spokes, centre dot.
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)):
            self.line(cx, cy, cx + dx * r, cy + dy * r, c, t)
        self.fill_circle(cx, cy, max(2, r // 4), c)

    # ------------------------------------------------------------ text ----
    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[' '])
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.fill_rect(cx + col * scale, y + row * scale,
                                       scale, scale, c)
            cx += 6 * scale
        return cx  # x just past the last glyph

    def text_width(self, s, scale):
        return len(s) * 6 * scale - scale

    def text_centred(self, cx, y, s, scale, c):
        x = cx - self.text_width(s, scale) // 2
        self.text(x, y, s, scale, c)
        return x

    def text_right(self, x_right, y, s, scale, c):
        x = x_right - self.text_width(s, scale)
        self.text(x, y, s, scale, c)
        return x

    def wrap(self, s, scale, max_w):
        max_chars = max(1, max_w // (6 * scale))
        lines, cur = [], ''
        for word in s.upper().split(' '):
            trial = (cur + ' ' + word).strip() if cur else word
            if len(trial) <= max_chars:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines


# ------------------------------------------------------------------ png ----
def write_png(path, canvas):
    w, h = canvas.w, canvas.h
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += canvas.buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(typ, data):
        out = struct.pack('>I', len(data)) + typ + data
        out += struct.pack('>I', zlib.crc32(typ + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', comp) + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return png

# ---------------------------------------------------------- pictograms ----
# Every picture is drawn from geometric primitives in code -- original
# work, no images, no copying of any reference artwork.

def dashed(cv, x0, y0, x1, y1, c):
    n = max(abs(x1 - x0), abs(y1 - y0)) // 8
    if n == 0:
        return
    for i in range(n):
        t0 = i / n
        t1 = (i + 0.55) / n
        cv.line(int(x0 + (x1 - x0) * t0), int(y0 + (y1 - y0) * t0),
                int(x0 + (x1 - x0) * t1), int(y0 + (y1 - y0) * t1), c, 1)


def pic_box(cv, x, y, w, h, bg=PANEL):
    cv.fill_rect(x, y, w, h, bg)
    cv.hline(x, x + w - 1, y, INK, 1)
    cv.hline(x, x + w - 1, y + h - 1, INK, 1)
    cv.vline(x, y, y + h - 1, INK, 1)
    cv.vline(x + w - 1, y, y + h - 1, INK, 1)


def tag(cv, x, y, s, scale=1):
    """Red tag with paper text; returns its width."""
    w = cv.text_width(s, scale) + 8
    cv.fill_rect(x, y, w, 7 * scale + 6, RED)
    cv.text(x + 4, y + 3, s, scale, PAPER)
    return w


def tag_white(cv, x, y, s, scale=1):
    """Paper tag with ink text and ink frame; returns its width."""
    w = cv.text_width(s, scale) + 8
    h = 7 * scale + 6
    cv.fill_rect(x, y, w, h, PAPER)
    cv.hline(x, x + w - 1, y, INK, 1)
    cv.hline(x, x + w - 1, y + h - 1, INK, 1)
    cv.vline(x, y, y + h - 1, INK, 1)
    cv.vline(x + w - 1, y, y + h - 1, INK, 1)
    cv.text(x + 4, y + 3, s, scale, INK)
    return w


def caption_strip(cv, x, y, w, s):
    cv.fill_rect(x, y, w, 12, NAVY)
    cv.text(x + 4, y + 3, s, 1, PAPER)


def pic_kyiv(cv, ox, oy, w, h):
    """Night sky over a river bridge: missile trails, two blasts."""
    cv.fill_rect(ox, oy, w, h, NAVY)
    for sx, sy in ((0.12, 0.16), (0.30, 0.10), (0.52, 0.18),
                   (0.72, 0.08), (0.88, 0.22), (0.42, 0.30)):
        cv.fill_rect(ox + int(w * sx), oy + int(h * sy), 2, 2, PAPER)
    # dashed missile trails down to the bridge
    dashed(cv, ox + int(w * 0.98), oy + 2,
           ox + int(w * 0.62), oy + int(h * 0.55), PAPER)
    dashed(cv, ox + int(w * 0.80), oy + 2,
           ox + int(w * 0.45), oy + int(h * 0.55), PAPER)
    # bridge deck, arch and supports
    dy = oy + int(h * 0.58)
    cv.hline(ox + 6, ox + w - 7, dy, (150, 150, 150), 4)
    cv.line(ox + int(w * 0.15), dy + 4, ox + w // 2, dy + 14,
            (150, 150, 150), 3)
    cv.line(ox + w // 2, dy + 14, ox + int(w * 0.85), dy + 4,
            (150, 150, 150), 3)
    for fx in (0.20, 0.50, 0.80):
        cv.vline(ox + int(w * fx), dy + 4, oy + int(h * 0.82),
                 (150, 150, 150), 3)
    # blasts on the deck
    cv.star(ox + int(w * 0.30), dy - 6, 9, YELLOW, 2)
    cv.star(ox + int(w * 0.66), dy - 4, 8, RED, 2)
    # water
    wy = oy + int(h * 0.84)
    cv.fill_rect(ox, wy, w, h - int(h * 0.84), (40, 70, 120))
    for wx in range(ox + 6, ox + w - 10, 16):
        cv.line(wx, wy + 6, wx + 8, wy + 3, PAPER, 1)
        cv.line(wx + 8, wy + 3, wx + 16, wy + 6, PAPER, 1)


def pic_cyclone(cv, ox, oy, w, h):
    """Spiral storm over the sea, rain bands, landfall dot on the coast."""
    cv.fill_rect(ox, oy, w, h, SEA)
    cx, cy = ox + int(w * 0.42), oy + int(h * 0.52)
    for i, r in enumerate((6, 12, 19, 26, 33)):
        cv.circle(cx - i * 2, cy, r, PAPER, 2)
    # rain slashes on the left
    for rx, ry in ((0.06, 0.15), (0.12, 0.35), (0.04, 0.55), (0.10, 0.75)):
        cv.line(ox + int(w * rx), oy + int(h * ry),
                ox + int(w * rx) + 8, oy + int(h * ry) + 10, PAPER, 2)
    # coast strip on the right
    cv.fill_rect(ox + int(w * 0.82), oy, w - int(w * 0.82), h, LAND)
    # dashed path from the eye to the landfall dot
    lx, ly = ox + int(w * 0.80), oy + int(h * 0.45)
    dashed(cv, cx + 30, cy, lx - 4, ly, RED)
    cv.fill_circle(lx, ly, 5, RED)
    cv.circle(lx, ly, 8, PAPER, 1)


def pic_selloff(cv, ox, oy, w, h):
    """Falling bars, red down-trend, Friday closing numbers."""
    cv.fill_rect(ox, oy, w, h, NAVY)
    # descending bars, left half
    bw = int(w * 0.07)
    bx0 = ox + int(w * 0.06)
    for i, bh in enumerate((0.55, 0.42, 0.30)):
        bhpx = int(h * bh)
        cv.fill_rect(bx0 + i * (bw + 6), oy + int(h * 0.80) - bhpx,
                     bw, bhpx, PAPER)
    # red down-trend line with arrowhead
    x0, y0 = ox + int(w * 0.05), oy + int(h * 0.12)
    x1, y1 = ox + int(w * 0.50), oy + int(h * 0.72)
    cv.line(x0, y0, x1, y1, RED, 3)
    cv.fill_poly([(x1, y1), (x1 - 12, y1 - 2), (x1 - 2, y1 - 12)], RED)
    # closing numbers, right half
    nx = ox + int(w * 0.55)
    for i, s in enumerate(("TAIPEI -6.2%", "SEOUL -5.2%",
                           "TOKYO -5.1%", "HONG KONG -1.9%")):
        cv.text(nx, oy + 16 + i * 16, s, 1, PAPER)


def pic_flags(cv, ox, oy, w, h):
    """EU circle of stars beside a UK cross flag."""
    # EU flag
    ex, ey, ew, eh = ox + int(w * 0.06), oy + int(h * 0.18), \
        int(w * 0.40), int(h * 0.62)
    cv.fill_rect(ex, ey, ew, eh, BLUE)
    ecx, ecy = ex + ew // 2, ey + eh // 2
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        cv.fill_circle(int(ecx + (eh * 0.30) * math.cos(a)),
                       int(ecy + (eh * 0.30) * math.sin(a)), 2, YELLOW)
    # UK flag: blue field, white cross, red cross
    ux, uy, uw, uh = ox + int(w * 0.54), oy + int(h * 0.18), \
        int(w * 0.40), int(h * 0.62)
    cv.fill_rect(ux, uy, uw, uh, BLUE)
    # saltire diagonals, then white cross, then red cross
    cv.line(ux, uy, ux + uw, uy + uh, PAPER, 4)
    cv.line(ux + uw, uy, ux, uy + uh, PAPER, 4)
    cv.fill_rect(ux + uw // 2 - 5, uy, 10, uh, PAPER)
    cv.fill_rect(ux, uy + uh // 2 - 5, uw, 10, PAPER)
    cv.fill_rect(ux + uw // 2 - 2, uy, 4, uh, RED)
    cv.fill_rect(ux, uy + uh // 2 - 2, uw, 4, RED)


def pic_globe(cv, ox, oy, w, h):
    """A globe crossed by a red slash: no deal."""
    cx, cy = ox + w // 2, oy + int(h * 0.48)
    r = int(h * 0.30)
    cv.circle(cx, cy, r, INK, 2)
    # meridians and parallels
    cv.vline(cx, cy - r, cy + r, INK, 1)
    cv.hline(cx - r, cx + r, cy, INK, 1)
    cv.line(cx - int(r * 0.7), cy - int(r * 0.7),
            cx - int(r * 0.7), cy + int(r * 0.7), INK, 1)
    cv.line(cx + int(r * 0.7), cy - int(r * 0.7),
            cx + int(r * 0.7), cy + int(r * 0.7), INK, 1)
    # red slash across the globe
    cv.line(cx - r - 4, cy + r + 4, cx + r + 4, cy - r - 4, RED, 4)


def pic_poland(cv, ox, oy, w, h):
    """Missile streak down to a field, red impact burst."""
    # field
    fy = oy + int(h * 0.68)
    cv.fill_rect(ox, fy, w, h - int(h * 0.68), (120, 160, 110))
    cv.hline(ox, ox + w - 1, fy, INK, 2)
    # little tree for scale
    tx = ox + int(w * 0.78)
    cv.vline(tx, fy - 14, fy, INK, 2)
    cv.fill_circle(tx, fy - 18, 6, GREEN)
    # missile streak from upper right
    hx, hy = ox + int(w * 0.34), fy - 2
    cv.line(ox + int(w * 0.92), oy + int(h * 0.10), hx + 8, hy - 8, INK, 2)
    cv.fill_poly([(hx + 8, hy - 8), (hx + 16, hy - 14),
                  (hx + 18, hy - 4)], INK)
    # impact burst at the ground
    cv.star(hx, hy, 10, RED, 2)
    cv.fill_circle(hx, hy, 3, YELLOW)


def pic_vehicle(cv, ox, oy, w, h):
    """Armoured vehicle on a road, palm tree at the edge."""
    gy = oy + int(h * 0.72)
    cv.hline(ox, ox + w - 1, gy, INK, 2)
    # palm tree, right side
    px = ox + int(w * 0.86)
    cv.line(px, gy, px + 4, gy - 22, INK, 2)
    for dx, dy in ((-10, -26), (10, -28), (-14, -18), (12, -16)):
        cv.line(px + 4, gy - 22, px + 4 + dx, gy - 22 + dy, GREEN, 2)
    # vehicle body, turret, barrel, wheels
    bx, by = ox + int(w * 0.10), oy + int(h * 0.44)
    bw, bh = int(w * 0.58), int(h * 0.26)
    cv.fill_rect(bx, by, bw, bh, INK)
    cv.fill_rect(bx + int(bw * 0.25), by - 10, int(bw * 0.35), 10, INK)
    cv.line(bx + int(bw * 0.60), by - 5, bx + bw + 14, by - 8, INK, 3)
    for i in range(3):
        cv.fill_circle(bx + 12 + i * 22, gy - 3, 6, INK)
        cv.fill_circle(bx + 12 + i * 22, gy - 3, 2, PAPER)


def pic_strike(cv, ox, oy, w, h):
    """Three marchers, one holding a placard."""
    # placard on a stick, top right (clear of the red tag)
    sx = ox + int(w * 0.74)
    cv.vline(sx, oy + int(h * 0.12), oy + int(h * 0.62), INK, 2)
    pw = cv.text_width("SCIOPERO", 1) + 8
    cv.fill_rect(sx - pw // 2, oy + int(h * 0.06), pw, 13, PAPER)
    cv.hline(sx - pw // 2, sx + pw // 2 - 1, oy + int(h * 0.06), INK, 1)
    cv.hline(sx - pw // 2, sx + pw // 2 - 1, oy + int(h * 0.06) + 12, INK, 1)
    cv.vline(sx - pw // 2, oy + int(h * 0.06), oy + int(h * 0.06) + 12, INK, 1)
    cv.vline(sx + pw // 2 - 1, oy + int(h * 0.06), oy + int(h * 0.06) + 12,
             INK, 1)
    cv.text(sx - pw // 2 + 4, oy + int(h * 0.06) + 3, "SCIOPERO", 1, INK)
    # three figures
    by = oy + int(h * 0.78)
    for i, (fx, col) in enumerate(((0.16, INK), (0.38, RED), (0.58, INK))):
        hx = ox + int(w * fx)
        cv.fill_circle(hx, oy + int(h * 0.52), 7, col)
        cv.fill_poly([(hx - 12, by), (hx + 12, by),
                      (hx + 7, oy + int(h * 0.60)),
                      (hx - 7, oy + int(h * 0.60))], col)


def pic_rising(cv, ox, oy, w, h):
    """Rising sun, ascending bars, red up-arrow."""
    cv.fill_circle(ox + int(w * 0.30), oy + int(h * 0.38),
                   int(h * 0.13), RED)
    # ascending bars
    bw = int(w * 0.11)
    bx0 = ox + int(w * 0.38)
    for i, bh in enumerate((0.28, 0.44, 0.60)):
        bhpx = int(h * bh)
        cv.fill_rect(bx0 + i * (bw + 8), oy + int(h * 0.80) - bhpx,
                     bw, bhpx, INK)
    # red up arrow over the bars
    x0, y0 = ox + int(w * 0.36), oy + int(h * 0.62)
    x1, y1 = ox + int(w * 0.88), oy + int(h * 0.16)
    cv.line(x0, y0, x1, y1, RED, 3)
    cv.fill_poly([(x1, y1), (x1 - 12, y1), (x1, y1 + 12)], RED)


def pic_court(cv, ox, oy, w, h):
    """Courthouse: pediment, three columns, base."""
    # pediment, shifted right so the red tag clears its peak
    cv.fill_poly([(ox + int(w * 0.28), oy + int(h * 0.34)),
                  (ox + int(w * 0.95), oy + int(h * 0.34)),
                  (ox + int(w * 0.62), oy + int(h * 0.10))], INK)
    # columns
    for i in range(3):
        cx = ox + int(w * (0.36 + i * 0.26))
        cv.fill_rect(cx - 5, oy + int(h * 0.38), 10, int(h * 0.32), INK)
    # base
    cv.fill_rect(ox + int(w * 0.26), oy + int(h * 0.72),
                 int(w * 0.71), 6, INK)
    cv.fill_rect(ox + int(w * 0.22), oy + int(h * 0.80),
                 int(w * 0.79), 4, INK)


def pic_derrick(cv, ox, oy, w, h):
    """Oil derrick against a low sun, with a drop of crude."""
    cv.fill_circle(ox + int(w * 0.80), oy + int(h * 0.22),
                   int(h * 0.12), YELLOW)
    # A-frame
    ax = ox + int(w * 0.30)
    top = oy + int(h * 0.10)
    base = oy + int(h * 0.78)
    cv.line(ax - 26, base, ax, top, INK, 3)
    cv.line(ax + 26, base, ax, top, INK, 3)
    for fy in (0.30, 0.50, 0.68):
        yy = oy + int(h * fy)
        cv.hline(ax - 18, ax + 18, yy, INK, 2)
    cv.hline(ox, ox + w - 1, base, INK, 2)
    # crude drop
    dx, dy = ox + int(w * 0.72), oy + int(h * 0.62)
    cv.fill_circle(dx, dy, 6, INK)
    cv.fill_poly([(dx - 6, dy - 2), (dx + 6, dy - 2), (dx, dy - 12)], INK)


def pic_ballot(cv, ox, oy, w, h):
    """Ballot box with a paper in the slot and a red tick."""
    bx, by = ox + int(w * 0.22), oy + int(h * 0.38)
    bw, bh = int(w * 0.56), int(h * 0.42)
    # paper sticking out of the slot
    cv.fill_rect(bx + bw // 2 - 9, by - 18, 18, 20, PAPER)
    cv.hline(bx + bw // 2 - 9, bx + bw // 2 + 8, by - 18, INK, 1)
    cv.hline(bx + bw // 2 - 9, bx + bw // 2 + 8, by + 1, INK, 1)
    cv.vline(bx + bw // 2 - 9, by - 18, by + 1, INK, 1)
    cv.vline(bx + bw // 2 + 8, by - 18, by + 1, INK, 1)
    cv.hline(bx + bw // 2 - 5, bx + bw // 2 + 4, by - 12, INK, 1)
    cv.hline(bx + bw // 2 - 5, bx + bw // 2 + 4, by - 7, INK, 1)
    # box
    cv.fill_rect(bx, by, bw, bh, INK)
    cv.fill_rect(bx + bw // 2 - 14, by + 2, 28, 3, PAPER)
    # red tick on the front
    cv.line(bx + 10, by + bh // 2, bx + 18, by + bh // 2 + 8, RED, 3)
    cv.line(bx + 18, by + bh // 2 + 8, bx + 34, by + bh // 2 - 10, RED, 3)
    # "3" badge
    cv.fill_circle(ox + int(w * 0.84), oy + int(h * 0.20), 9, RED)
    cv.text(ox + int(w * 0.84) - 3, oy + int(h * 0.20) - 3, "3", 1, PAPER)


def pic_cricket(cv, ox, oy, w, h):
    """Stumps, a bat and a red ball on a green strip."""
    # green strip at the bottom
    gy = oy + int(h * 0.68)
    cv.fill_rect(ox, gy, w, h - int(h * 0.68), (150, 190, 140))
    # stumps
    sx = ox + int(w * 0.18)
    for i in range(3):
        cv.vline(sx + i * 7, oy + int(h * 0.30), gy, INK, 3)
    cv.hline(sx, sx + 14, oy + int(h * 0.30), INK, 2)
    # bat, diagonal
    cv.line(ox + int(w * 0.55), oy + int(h * 0.12),
            ox + int(w * 0.78), oy + int(h * 0.62), (200, 170, 110), 7)
    # ball
    cv.fill_circle(ox + int(w * 0.86), oy + int(h * 0.70), 7, RED)


# ------------------------------------------------------------------- map ----
# Rough world map as (start, end) land spans per row, 48 columns x 18 rows.
MAP_SPANS = {
    1: [(3, 10), (17, 20), (32, 46)],
    2: [(2, 11), (17, 21), (24, 27), (31, 46)],
    3: [(2, 12), (23, 27), (30, 46)],
    4: [(2, 11), (24, 26), (30, 45)],
    5: [(3, 10), (24, 26), (31, 44)],
    6: [(4, 9), (25, 30), (32, 42)],
    7: [(5, 8), (24, 31), (33, 40)],
    8: [(6, 8), (25, 31), (35, 38)],
    9: [(7, 8), (26, 30), (36, 37)],
    10: [(8, 9), (10, 14), (27, 30)],
    11: [(10, 15), (27, 29)],
    12: [(11, 15), (28, 29)],
    13: [(12, 14), (28, 28), (39, 44)],
    14: [(12, 14), (38, 44)],
    15: [(13, 14), (39, 43)],
    16: [(13, 13)],
}
# story number -> (map col, map row, label dx, label dy)
MAP_DOTS = [
    (1, 26, 3, 8, -4), (2, 36, 7, 8, -4), (3, 41, 6, 8, -4),
    (4, 24, 3, -16, -4), (5, 28, 5, 8, 5), (6, 25, 2, 8, -11),
    (7, 30, 5, 8, -4), (8, 25, 4, -8, 8), (9, 44, 5, 8, -11),
    (10, 42, 4, 8, -11), (11, 29, 10, 8, -4), (12, 7, 9, -14, -4),
    (13, 46, 16, 8, -4),
]


def draw_map(cv, ox, oy, cell=5):
    for row, spans in MAP_SPANS.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cv.fill_rect(ox + c * cell, oy + row * cell,
                             cell, cell, LAND)
    for num, col, row, dx, dy in MAP_DOTS:
        px = ox + col * cell + cell // 2
        py = oy + row * cell + cell // 2
        cv.fill_circle(px, py, 3, RED)
        cv.text(px + dx, py + dy, str(num), 1, RED)

# -------------------------------------------------------------- layout ----
MARGIN = 36
RIGHT = W - MARGIN  # 988

STATS = [
    ("3", "BRIDGES OVER THE DNIPRO", "DAMAGED IN KYIV"),
    ("300,000+", "PEOPLE MOVED TO SHELTERS", "BEFORE AKVAN"),
    ("-6.2%", "TAIWAN'S SHARE INDEX,", "FRIDAY'S CLOSE"),
    ("100,000", "YOUTH VISAS A YEAR IN THE", "UK-EU DEAL"),
    ("2.3%", "JAPAN CONSUMER INFLATION", "IN OCTOBER"),
    ("118", "RUNS BY GLENN PHILLIPS", "AGAINST INDIA"),
]

REGIONS = [
    ("EUROPE", 8, (36, 64, 120)),
    ("ASIA", 8, RED),
    ("MIDDLE EAST", 3, (150, 100, 20)),
    ("AFRICA", 5, GREEN),
    ("AMERICAS", 4, (90, 60, 140)),
    ("OCEANIA", 3, (20, 120, 120)),
    ("GLOBAL", 4, (70, 70, 70)),
]

TOP3 = [
    dict(pic=pic_kyiv, tag="KYIV", tag2="3 BRIDGES HIT",
         cap="OFFICIALS' COUNT",
         kicker="1 KYIV, UKRAINE - WAR",
         head="RUSSIAN MISSILES HIT THREE KYIV BRIDGES",
         body="AN OVERNIGHT BARRAGE OF ABOUT 110 MISSILES AND 400 DRONES "
              "KILLED AT LEAST NINE PEOPLE ACROSS UKRAINE AND CUT POWER "
              "AND WATER IN THE CAPITAL. (KYIV INDEPENDENT, BBC)"),
    dict(pic=pic_cyclone, tag="CYCLONE AKVAN", tag2="LANDFALL - 8 AM",
         cap="WEATHER OFFICE",
         kicker="2 ODISHA, INDIA - CYCLONE",
         head="CYCLONE AKVAN COMES ASHORE IN EASTERN INDIA",
         body="THE STORM CROSSED THE COAST NEAR GOPALPUR FROM ABOUT 8 AM "
              "AFTER MORE THAN 300,000 PEOPLE WERE MOVED TO SHELTERS. "
              "NO DEATHS WERE REPORTED. (IMD, DECCAN HERALD)"),
    dict(pic=pic_selloff, tag="AI SELL-OFF", tag2="ASIA, FRIDAY'S CLOSE",
         cap="CLOSING PRICES",
         kicker="3 TAIPEI - SEOUL - TOKYO - MARKETS",
         head="AI SELL-OFF SINKS ASIA'S STOCK MARKETS",
         body="TAIWAN'S INDEX FELL 6.2% TO END ITS WORST WEEK SINCE 1991. "
              "SEOUL LOST 5.2% AND TOKYO 5.1% AS CHIPMAKERS LED THE "
              "SLIDE. (AL JAZEERA, ANADOLU)"),
]

MID5 = [
    dict(pic=pic_flags, tag="UK-EU DEAL", cap="AGREED - REUTERS",
         kicker="4 BRUSSELS - DIPLOMACY",
         head="UK AND EU SEAL A 'RESET' DEAL",
         body="FOOD TRADE, YOUTH VISAS, CARBON LINK."),
    dict(pic=pic_globe, tag="COP31: NO DEAL", cap="ONGOING - UN NEWS",
         kicker="5 ANTALYA - CLIMATE",
         head="COP31 REACHES ITS LAST DAY WITH NO DEAL",
         body="THE DRAFT TEXT LEAVES OUT FOSSIL FUELS."),
    dict(pic=pic_poland, tag="POLAND: MISSILE",
         cap="MINISTER SAYS - REUTERS",
         kicker="6 EASTERN POLAND - SECURITY",
         head="RUSSIAN CRUISE MISSILE LANDS IN POLAND",
         body="IT FELL IN A FIELD; TWO AIRPORTS PAUSED."),
    dict(pic=pic_vehicle, tag="IRAQ: ARMY IN", cap="WITNESSED - REUTERS",
         kicker="7 CENTRAL IRAQ - SECURITY",
         head="IRAQI ARMY ENTERS A MILITIA STRONGHOLD",
         body="TROOPS DEPLOY TO JURF AL-SAKHAR."),
    dict(pic=pic_strike, tag="ITALY: STRIKE", cap="REPORTED - REUTERS",
         kicker="8 ITALY - LABOUR",
         head="GENERAL STRIKE OVER ITALY'S BUDGET",
         body="WORKERS AND STUDENTS MARCH."),
]

BOT5 = [
    dict(pic=pic_rising, tag="JAPAN: +2.3%",
         cap="OFFICIAL DATA - REUTERS",
         kicker="9 TOKYO - ECONOMY",
         head="JAPAN'S INFLATION PICKS UP TO 2.3%",
         body="A DECEMBER RATE RISE STAYS IN VIEW."),
    dict(pic=pic_court, tag="SEOUL: IMPEACH",
         cap="DECISION - KOREA HERALD",
         kicker="10 SEOUL - POLITICS",
         head="KOREA'S RULING PARTY TO IMPEACH TOP JUDGE",
         body="IT FOLLOWS AN OVERTURNED CONVICTION."),
    dict(pic=pic_derrick, tag="KENYA: OIL",
         cap="CEREMONY HELD - ALLAFRICA",
         kicker="11 TURKANA, KENYA - ENERGY",
         head="KENYA STARTS DRILLING ITS FIRST OIL WELL",
         body="FIRST CRUDE IS DUE ON 1 DECEMBER."),
    dict(pic=pic_ballot, tag="BUKELE: 3RD BID", cap="FILED - AP",
         kicker="12 SAN SALVADOR - POLITICS",
         head="BUKELE FILES TO RUN FOR A THIRD TERM",
         body="THE VOTE IS ON 28 FEBRUARY 2027."),
    dict(pic=pic_cricket, tag="PHILLIPS: 118", cap="SCORECARD - ICC",
         kicker="13 WELLINGTON - CRICKET",
         head="PHILLIPS HITS 118 AGAINST INDIA",
         body="HUNDREDS V INDIA IN ALL THREE FORMATS."),
]

ALSO_LEFT = [
    "14 LVIV - A STRIKE ON A RAILWAY STATION KILLS TWO (BBC)",
    "15 MOSCOW - RUSSIA DECLARES ESTONIA'S BORDER CLOSURE (REUTERS)",
    "16 BERLIN - SCHOOL PUPILS STRIKE AGAINST MILITARY SERVICE "
    "(AL JAZEERA)",
    "17 LONDON - GENERAL SAYS UK RUNS CYBER ATTACKS ABROAD (SKY NEWS)",
    "18 BEIJING - CHINA HOLDS ITS LOAN RATES FOR AN 18TH MONTH (XINHUA)",
    "19 TOKYO - SOFTBANK SHARES FALL MORE THAN 14% IN A DAY (AL JAZEERA)",
    "20 SEOUL - KOSPI INDEX ENDS THE WEEK 7.9% LOWER (ANADOLU)",
    "21 GANJAM - 209 MM OF RAIN FALLS AS AKVAN CROSSES ODISHA (PTI)",
    "22 LEBANON - ISRAELI AIR STRIKES HIT THE SOUTH AND THE EAST "
    "(ANADOLU)",
    "23 YEMEN - GUNMEN FIRE ON A CARGO SHIP OFF THE COAST (UKMTO)",
    "24 ABUJA - COURT BARS NEW EVIDENCE AGAINST TINUBU (CHANNELS TV)",
]

ALSO_RIGHT = [
    "25 KAMPALA - POLICE TOLD TO ENFORCE EBOLA BAN ON RALLIES (ALLAFRICA)",
    "26 MALAWI - FUEL CRISIS BRINGS NIGHT-LONG PETROL QUEUES (AL JAZEERA)",
    "27 AFRICA - AFDB SAYS 22 COUNTRIES ARE IN DEBT DISTRESS (ALLAFRICA)",
    "28 LAS VEGAS - RUSSELL FASTEST IN WET GRAND PRIX PRACTICE "
    "(AUTOSPORT)",
    "29 NEW YORK - NASDAQ FUTURES FALL 1.6% BEFORE THE BELL "
    "(24/7 WALL ST)",
    "30 WASHINGTON - DEMOCRATS QUERY LAW FIRM'S FREE WORK (AL JAZEERA)",
    "31 WELLINGTON - NICHOLLS MAKES 175 IN A STAND OF 216 (ICC)",
    "32 SYDNEY - AUSTRALIAN SHARES FALL 1.8% IN THE SELL-OFF (REUTERS)",
    "33 ANTALYA - PANAMA ASKS COP31 TO CAP WORLD OIL OUTPUT (ANADOLU)",
    "34 ANTALYA - EU OFFICIAL CALLS THE CLIMATE DRAFT UNACCEPTABLE (RTE)",
    "35 TURIN - ATP BACKS A PLAN TO LIFT PLAYER PAY PAST $350M (ANADOLU)",
]

DATE_CHECK = ("LEFT OUT AS THURSDAY 19 NOVEMBER'S NEWS: THE WORLD COURT'S "
              "RULING ON MYANMAR, THE THREE-LEADER DECLARATION IN SHENZHEN, "
              "TONGA'S DROUGHT EMERGENCY AND THE MIGRANT BOAT LOST OFF "
              "SENEGAL. NOT YET SHOWN: BEPICOLOMBO'S ENTRY INTO ORBIT ROUND "
              "MERCURY AND ANY FINAL COP31 TEXT.")


def draw_list_col(cv, x, y, items, w=336):
    for s in items:
        lines = cv.wrap(s, 1, w)
        for li, line in enumerate(lines):
            cv.text(x, y, line, 1, GRAY)
            if li == 0:
                cv.text(x, y, line.split(' ')[0], 1, RED)
            y += 9
        y += 2
    return y


def draw():
    cv = Canvas(W, H, PAPER)

    # page frame
    cv.hline(12, 1011, 12, INK, 2)
    cv.hline(12, 1011, 1010, INK, 2)
    cv.vline(12, 12, 1010, INK, 2)
    cv.vline(1011, 12, 1010, INK, 2)

    # ---- kicker + masthead ----
    cv.text(MARGIN, 24, "THE WORLD IN ONE DAY", 1, RED)
    cv.text_right(RIGHT, 24,
                  "35 STORIES - 7 REGIONS - EVERY ONE DATED "
                  "FRIDAY 20 NOVEMBER 2026", 1, INK)
    cv.text_centred(W // 2, 36, "FRIDAY 20 NOVEMBER 2026", 6, INK)
    cv.text_centred(W // 2, 84,
                    "RUSSIAN MISSILES HIT KYIV'S BRIDGES - CYCLONE AKVAN "
                    "STRIKES INDIA - AN AI SELL-OFF SINKS ASIA'S MARKETS - "
                    "UK AND EU SEAL A DEAL", 1, INK)
    cv.hline(MARGIN, RIGHT, 96, INK, 3)
    cv.hline(MARGIN, RIGHT, 101, INK, 1)

    # ---- stat strip ----
    col_w = 952 // 6
    for i, (num, l1, l2) in enumerate(STATS):
        x = MARGIN + i * col_w
        if i > 0:
            cv.vline(x - 4, 106, 150, RED, 2)
        cv.text(x + 2, 108, num, 3, INK)
        cv.text(x + 2, 134, l1, 1, GRAY)
        cv.text(x + 2, 143, l2, 1, GRAY)

    # ---- region bar ----
    total = sum(c for _, c, _ in REGIONS)
    widths = [952 * c // total for _, c, _ in REGIONS]
    widths[-1] = 952 - sum(widths[:-1])
    x = MARGIN
    for (name, count, col), wseg in zip(REGIONS, widths):
        cv.fill_rect(x, 156, wseg, 18, col)
        cv.text_centred(x + wseg // 2, 161, "%s %d" % (name, count), 1,
                        PAPER)
        x += wseg

    # ---- top 3 stories ----
    top_x = [MARGIN, 359, 682]
    top_w = 306
    for (sx, story) in zip(top_x, TOP3):
        pic_box(cv, sx, 180, top_w, 104)
        story['pic'](cv, sx + 1, 181, top_w - 2, 102)
        tag(cv, sx + 5, 185, story['tag'])
        tag_white(cv, sx + 5, 202, story['tag2'])
        caption_strip(cv, sx + 1, 180 + 104 - 13, top_w - 2, story['cap'])
        cv.text(sx, 290, story['kicker'], 1, RED)
        y = 300
        for line in cv.wrap(story['head'], 2, top_w):
            cv.text(sx, y, line, 2, INK)
            y += 16
        y = 336
        for line in cv.wrap(story['body'], 1, top_w):
            cv.text(sx, y, line, 1, GRAY)
            y += 9
    cv.hline(MARGIN, RIGHT, 378, INK, 1)

    # ---- five-story rows (middle + bottom) ----
    def five_row(y0, stories):
        xs = [MARGIN, 229, 422, 615, 808]
        for sx, story in zip(xs, stories):
            pic_box(cv, sx, y0, 180, 82)
            story['pic'](cv, sx + 1, y0 + 1, 178, 80)
            tag(cv, sx + 5, y0 + 5, story['tag'])
            caption_strip(cv, sx + 1, y0 + 82 - 13, 178, story['cap'])
            cv.text(sx, y0 + 88, story['kicker'], 1, RED)
            y = y0 + 98
            for line in cv.wrap(story['head'], 1, 180):
                cv.text(sx, y, line, 1, INK)
                y += 9
            y = y0 + 120
            for line in cv.wrap(story['body'], 1, 180):
                cv.text(sx, y, line, 1, GRAY)
                y += 9

    five_row(386, MID5)
    cv.hline(MARGIN, RIGHT, 530, INK, 1)
    five_row(538, BOT5)
    cv.hline(MARGIN, RIGHT, 682, INK, 1)

    # ---- map + also list ----
    cv.text(MARGIN, 690, "WHERE IT HAPPENED", 1, RED)
    cv.text(300, 690, "ALSO ON FRIDAY 20 NOVEMBER - 22 MORE STORIES", 2, INK)
    pic_box(cv, MARGIN, 700, 250, 150)
    draw_map(cv, MARGIN + 5, 705)
    for i, line in enumerate(cv.wrap(
            "EACH NUMBER IS THAT STORY WITH THAT NUMBER ON THIS PAGE.",
            1, 250)):
        cv.text(MARGIN, 856 + i * 9, line, 1, GRAY)
    draw_list_col(cv, 300, 708, ALSO_LEFT)
    draw_list_col(cv, 652, 708, ALSO_RIGHT)

    # ---- date check ----
    cv.fill_rect(MARGIN, 925, 952, 42, PAPER)
    cv.hline(MARGIN, RIGHT, 925, RED, 2)
    cv.hline(MARGIN, RIGHT, 966, RED, 2)
    cv.vline(MARGIN, 925, 966, RED, 2)
    cv.vline(RIGHT, 925, 966, RED, 2)
    cv.text(MARGIN + 8, 930, "DATE CHECK", 1, RED)
    y = 941
    for line in cv.wrap(DATE_CHECK, 1, 920):
        cv.text(MARGIN + 8, y, line, 1, INK)
        y += 9

    # ---- footer ----
    cv.text(MARGIN, 975,
            "EVERY STORY HERE HAPPENED, OR WAS FIRST REPORTED, ON FRIDAY "
            "20 NOVEMBER 2026. OFFICIALS' COUNTS ARE ATTRIBUTED.", 1, GRAY)
    cv.text_right(RIGHT, 975, "SOURCES NAMED BESIDE EACH STORY", 1, GRAY)
    cv.text_centred(W // 2, 985,
                    "ALL PICTURES ARE DRAWN BY THE PROGRAM - "
                    "NO PHOTOGRAPHS", 1, GRAY)
    return cv


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(outdir, exist_ok=True)
    except OSError:
        outdir = "."
    path = os.path.join(outdir, "entry.png")
    cv = draw()
    png = write_png(path, cv)
    print("path:  ", path)
    print("sha256:", hashlib.sha256(png).hexdigest())
    print("bytes: ", len(png))
    print("size:  ", cv.w, "x", cv.h)


if __name__ == "__main__":
    main()
