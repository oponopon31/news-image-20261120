#!/usr/bin/env python3
"""THE WORLD IN ONE DAY -- front page for Friday 20 November 2026.

  v4 (21 Nov 2026): visual-richness upgrade -- detailed lead and
  thumbnail illustrations (gradients, hatching, stipple, skylines,
  candlesticks, spiral arms), heavy double-struck nameplate, shaded
  stat strip, graticule world map, tinted ALSO rows, fine deterministic
  newsprint grain over the whole page. All 51 stories and dates
  unchanged from v3.

Draws a 1024x1024 newspaper front page procedurally with Python 3 stdlib
only (struct + zlib for the PNG encoder, a hand-defined 5x7 bitmap font,
and geometric pictograms). No network, no external files, no randomness:
two runs produce byte-identical output.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (fallback /output).

Layout: 51 stories in 7 regions, every one dated Friday 20 November 2026.
  TOP     1 Kyiv bridges hit -- 2 Cyclone Akvan landfall -- 3 AI sell-off
  MID     4 UK-EU reset deal -- 5 COP31 no deal -- 6 missile in Poland --
          7 Iraqi army in -- 8 Italy general strike
  LOW     9 Japan inflation -- 10 Seoul impeach -- 11 Kenya first oil --
          12 Rikers closure plan -- 13 Phillips 118
  ALSO    14-51: two-column list of 38 more stories, one line each.
  DATE CHECK: stories deliberately left out because they are
  Thursday 19 November news -- the World Court's ruling on Myanmar,
  the three-leader declaration in Shenzhen, Tonga's drought emergency
  and the migrant boat lost off Senegal. Not yet shown: BepiColombo,
  which enters orbit round Mercury on 21 November (19:24 CET), and
  any final COP31 text -- none was adopted on 20 November.

  v2 (21 Nov 2026): three Thursday stories that v1 carried are out
  (Bukele's filing, the Uganda Ebola rally ban, the Democrats'
  law-firm query); Poland, Moscow, Lebanon, debt-distress and ASX
  items corrected; three 20-November-verified replacements in
  (Rikers plan, Congo Ebola schools, Davies cyber director). The
  ATP player-pay plan appears once, as a single item.

  v3 (21 Nov 2026): 16 more verified 20-November stories in as ALSO
  items 36-51 (Copenhagen expels a Russian attache; GTA VI $3.79bn
  day one; Riemann proof CLAIM; $7.25bn Roundup deal; Palisades fire
  conviction; Zecler beating sentences; Bayelsa boat; Haiti blast;
  Pentagon UFO files; Trump AI-centre tax threat; Pakistan Test win;
  India A thrash Nepal; Xi-Albanese turnaround; Indian rice high;
  ANC cities; Sydney car-bomb charge). Regions now EUROPE 10, ASIA 12,
  MIDDLE EAST 3, AFRICA 7, AMERICAS 11, OCEANIA 4, GLOBAL 4 (51 total).
  Redesign: nameplate "THE WORLD IN ONE DAY" is now the biggest thing
  on the page (scale 5, centred), dateline beneath it (scale 3), the
  51-story kicker above it; lead story #1 gets a wider column, a taller
  pictogram and a scale-3 headline; red section labels TOP STORIES and
  MORE FROM THE DAY; BY THE NUMBERS label and scale-4 stat numbers
  (uneven columns so 300,000+ fits); ALSO list reworked to single-line
  items, 19 per column, red numbers, tighter leading.

Facts follow the 35-story reference page for 20 November 2026; the
load-bearing claims were re-verified against live reporting on
21 Nov 2026: Akvan landfall near Gopalpur 07:30-08:30 IST 20 Nov,
300,000+ evacuated, no deaths (IMD); Taiex -6.23% on 20 Nov, worst
week since 1991, Nikkei -5.1%, KOSPI -5.2%, Hang Seng -1.9%
(Reuters/AP); two Russian missiles and a jet drone down in
south-eastern Poland on 20 Nov -- a Kh-101 near Nowy Lipowiec, a
second missile near Rudnik nad Sanem, drone debris at Molodycz --
no one hurt, only Rzeszow-Jasionka airport briefly suspended
(Polish defence ministry, Reuters); S&P/ASX 200 down 1.6% to
8,592.6 on 20 Nov (Dow Jones Newswires); Mamdani's Rikers plan
unveiled on Friday 20 Nov (Reuters, AP); Ebola reported in nearly
100 schools in eastern Congo, official data released Friday
(Anadolu); the White House announced Kirsten Davies as national
cyber director on Friday (Bloomberg). All drawings are original
geometric work in code.
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


# ------------------------------------------------------- v4 helpers ----
def grad_v(cv, x, y, w, h, c1, c2):
    """Vertical gradient in h bands (deterministic, stdlib only)."""
    for yy in range(h):
        t = yy / max(1, h - 1)
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        cv.hline(x, x + w - 1, y + yy, c)

def grad_h(cv, x, y, w, h, c1, c2):
    for xx in range(w):
        t = xx / max(1, w - 1)
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
        cv.vline(x + xx, y, y + h - 1, c)

def hatch_diag(cv, x, y, w, h, c, step=6):
    for k in range(-h, w + h, step):
        cv.line(x + k, y + h - 1, x + k + h, y, c, 1)

def stipple(cv, x, y, w, h, c, seed=7, density=3):
    """Deterministic pseudo-random dots inside a rect."""
    s = seed
    for yy in range(y, y + h, 2):
        for xx in range(x, x + w, 2):
            s = (s * 1103515245 + 12345) & 0x7FFFFFFF
            if s % 10 < density:
                cv.set(xx, yy, c)

def apply_grain(cv, amp=7):
    """Fine deterministic newsprint grain over the whole page.
    The single biggest PNG-size lever: per-pixel variation that
    zlib cannot collapse, at an amplitude that stays readable."""
    buf = cv.buf
    state = 987654321
    span = 2 * amp + 1
    for i in range(0, len(buf), 3):
        state = (state * 1664525 + 1013904223) & 0xFFFFFFFF
        d = (state >> 24) % span - amp
        if d:
            v = buf[i] + d
            buf[i] = 255 if v > 255 else (0 if v < 0 else v)
        d = ((state >> 16) & 0xFF) % span - amp
        if d:
            v = buf[i + 1] + d
            buf[i + 1] = 255 if v > 255 else (0 if v < 0 else v)
        d = ((state >> 8) & 0xFF) % span - amp
        if d:
            v = buf[i + 2] + d
            buf[i + 2] = 255 if v > 255 else (0 if v < 0 else v)

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
    grad_v(cv, ox, oy, w, h, (16, 26, 54), (38, 58, 96))
    # moon with halo
    mx, my = ox + int(w * 0.88), oy + int(h * 0.16)
    cv.fill_circle(mx, my, 11, (210, 210, 190))
    cv.fill_circle(mx, my, 7, (240, 238, 220))
    cv.fill_circle(mx - 2, my - 2, 2, (200, 200, 185))
    # many stars, some with cross sparkle
    for sx, sy in ((0.06, 0.12), (0.14, 0.07), (0.24, 0.18), (0.33, 0.08),
                   (0.44, 0.14), (0.55, 0.07), (0.66, 0.16), (0.76, 0.06),
                   (0.05, 0.30), (0.20, 0.28), (0.38, 0.26), (0.60, 0.28),
                   (0.82, 0.30), (0.94, 0.10), (0.48, 0.20), (0.70, 0.24)):
        px, py = ox + int(w * sx), oy + int(h * sy)
        cv.fill_rect(px, py, 2, 2, PAPER)
        if (int(sx * 100) + int(sy * 100)) % 3 == 0:
            cv.hline(px - 2, px + 3, py, PAPER, 1)
            cv.vline(px, py - 2, py + 3, PAPER, 1)
    # skyline: buildings with lit windows behind the bridge
    base = oy + int(h * 0.58)
    bx = ox + 4
    bi = 0
    while bx < ox + w - 8:
        bw = 14 + (bi * 7) % 18
        bh = 12 + (bi * 11) % 22
        cv.fill_rect(bx, base - bh, bw, bh, (10, 16, 34))
        cv.hline(bx, bx + bw - 1, base - bh, (90, 100, 130), 1)
        for wy in range(base - bh + 3, base - 2, 5):
            for wx in range(bx + 3, bx + bw - 3, 5):
                if (wx * 3 + wy * 7 + bi) % 5 < 2:
                    cv.fill_rect(wx, wy, 2, 2, (255, 205, 90))
        bx += bw + 3
        bi += 1
    # three dashed missile trails + missile dots
    for (tx0, tx1) in ((0.98, 0.62), (0.80, 0.45), (0.62, 0.30)):
        dashed(cv, ox + int(w * tx0), oy + 2,
               ox + int(w * tx1), oy + int(h * 0.55), PAPER)
        cv.fill_circle(ox + int(w * tx0) - 6, oy + 8, 2, YELLOW)
    # bridge deck, arches, cables, supports
    dy = base
    cv.hline(ox + 6, ox + w - 7, dy, (170, 170, 170), 4)
    cv.hline(ox + 6, ox + w - 7, dy + 4, (110, 110, 110), 1)
    cv.line(ox + int(w * 0.15), dy + 4, ox + w // 2, dy + 14,
            (150, 150, 150), 3)
    cv.line(ox + w // 2, dy + 14, ox + int(w * 0.85), dy + 4,
            (150, 150, 150), 3)
    for fx in (0.12, 0.28, 0.50, 0.72, 0.88):
        cv.vline(ox + int(w * fx), dy + 4, oy + int(h * 0.82),
                 (140, 140, 140), 3)
    for cx0 in (0.15, 0.35, 0.55, 0.75):
        cv.line(ox + int(w * cx0), dy, ox + int(w * (cx0 + 0.08)),
                dy - 12, (120, 120, 120), 1)
    # three blasts: glow rings + burst + smoke
    for bfx, bc in ((0.30, YELLOW), (0.66, RED), (0.84, YELLOW)):
        px, py = ox + int(w * bfx), dy - 6
        cv.fill_circle(px, py, 12, (200, 90, 20))
        cv.fill_circle(px, py, 8, (240, 140, 40))
        cv.star(px, py, 9, bc, 2)
        cv.fill_circle(px, py, 3, PAPER)
        cv.fill_circle(px - 8, py - 12, 4, (120, 120, 120))
        cv.fill_circle(px + 6, py - 14, 5, (100, 100, 100))
        cv.fill_circle(px + 12, py - 8, 3, (130, 130, 130))
        # reflection streak in the water below
        cv.vline(px, oy + int(h * 0.86), oy + h - 4, (240, 160, 60), 2)
    # water: gradient + ripples + reflections
    wy = oy + int(h * 0.84)
    grad_v(cv, ox, wy, w, h - int(h * 0.84), (46, 78, 130), (24, 48, 92))
    for wx in range(ox + 6, ox + w - 10, 14):
        cv.line(wx, wy + 5, wx + 7, wy + 2, (180, 200, 230), 1)
        cv.line(wx + 7, wy + 2, wx + 14, wy + 5, (180, 200, 230), 1)
        cv.line(wx + 3, wy + 12, wx + 10, wy + 10, (140, 170, 210), 1)


def pic_cyclone(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (86, 132, 190), (52, 96, 158))
    # wave dashes across the sea
    for wy in range(oy + 8, oy + h - 6, 12):
        for wx in range(ox + 4, ox + int(w * 0.80), 18):
            if (wx + wy) % 36 < 18:
                cv.hline(wx, wx + 8, wy, (150, 190, 230), 1)
    # cloud puffs top-left
    for cx0, cy0, r0 in ((0.10, 0.10, 7), (0.16, 0.08, 9), (0.22, 0.11, 6),
                         (0.70, 0.09, 6), (0.76, 0.12, 8)):
        cv.fill_circle(ox + int(w * cx0), oy + int(h * cy0), r0,
                       (225, 232, 240))
    # spiral: concentric offset rings + spiral arms + rain bands
    cx, cy = ox + int(w * 0.42), oy + int(h * 0.52)
    for i, r in enumerate((5, 10, 15, 20, 25, 30, 35)):
        cv.circle(cx - i * 2, cy - i, r, PAPER, 2)
        cv.circle(cx - i * 2, cy - i, r - 1, (190, 210, 235), 1)
    cv.fill_circle(cx, cy, 5, (240, 240, 235))
    cv.circle(cx, cy, 8, RED, 2)
    for k in range(12):
        a = 2 * math.pi * k / 12
        x0 = cx + int(10 * math.cos(a))
        y0 = cy + int(10 * math.sin(a))
        x1 = cx + int(34 * math.cos(a + 0.5))
        y1 = cy + int(34 * math.sin(a + 0.5))
        cv.line(x0, y0, x1, y1, (200, 220, 240), 1)
    # rain slashes, both flanks
    for rx, ry in ((0.05, 0.15), (0.11, 0.32), (0.03, 0.52), (0.09, 0.72),
                   (0.14, 0.88), (0.60, 0.82), (0.66, 0.68), (0.58, 0.20)):
        cv.line(ox + int(w * rx), oy + int(h * ry),
                ox + int(w * rx) + 7, oy + int(h * ry) + 9, PAPER, 2)
    # coast: land with fields, town dots, coastline
    lx0 = ox + int(w * 0.82)
    grad_v(cv, lx0, oy, w - int(w * 0.82), h, (214, 196, 152), (186, 166, 122))
    cv.line(lx0, oy, lx0 + 6, oy + h // 3, (120, 100, 60), 2)
    cv.line(lx0 + 6, oy + h // 3, lx0 - 2, oy + 2 * h // 3, (120, 100, 60), 2)
    cv.line(lx0 - 2, oy + 2 * h // 3, lx0 + 4, oy + h, (120, 100, 60), 2)
    for tx, ty in ((0.87, 0.20), (0.90, 0.38), (0.86, 0.60), (0.92, 0.78)):
        cv.fill_rect(ox + int(w * tx), oy + int(h * ty), 3, 3, (90, 70, 40))
    # dashed path + landfall marker + wind arrow
    lx, ly = ox + int(w * 0.80), oy + int(h * 0.45)
    dashed(cv, cx + 30, cy, lx - 4, ly, RED)
    cv.fill_circle(lx, ly, 5, RED)
    cv.circle(lx, ly, 9, PAPER, 2)
    cv.circle(lx, ly, 12, RED, 1)
    cv.line(lx - 16, ly + 14, lx - 6, ly + 14, PAPER, 2)
    cv.fill_poly([(lx - 6, ly + 14), (lx - 12, ly + 10),
                  (lx - 12, ly + 18)], PAPER)


def pic_selloff(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (30, 48, 84), (16, 28, 58))
    # faint grid
    for gy in range(oy + 10, oy + h - 8, 14):
        cv.hline(ox + 4, ox + int(w * 0.52), gy, (60, 80, 120), 1)
    for gx in range(ox + 8, ox + int(w * 0.52), 16):
        cv.vline(gx, oy + 6, oy + int(h * 0.82), (60, 80, 120), 1)
    # descending candlesticks, left half
    bw = int(w * 0.055)
    bx0 = ox + int(w * 0.05)
    tops = (0.18, 0.24, 0.32, 0.40, 0.48, 0.56)
    bots = (0.42, 0.50, 0.55, 0.62, 0.68, 0.74)
    for i, (t0, b0) in enumerate(zip(tops, bots)):
        x = bx0 + i * (bw + 5)
        cv.vline(x + bw // 2, oy + int(h * t0) - 4, oy + int(h * b0) + 4,
                 (200, 200, 200), 1)
        cv.fill_rect(x, oy + int(h * t0), bw, int(h * (b0 - t0)),
                     (214, 48, 48) if i % 2 == 0 else (220, 90, 70))
    # red down-trend line + arrowhead + shaded area beneath
    x0, y0 = ox + int(w * 0.05), oy + int(h * 0.12)
    x1, y1 = ox + int(w * 0.50), oy + int(h * 0.72)
    for yy in range(y0, y1):
        xx = x0 + (yy - y0) * (x1 - x0) // max(1, y1 - y0)
        cv.vline(xx, yy, oy + int(h * 0.80), (120, 30, 30), 1)
    cv.line(x0, y0, x1, y1, RED, 3)
    cv.line(x0, y0, x1, y1, (255, 120, 120), 1)
    cv.fill_poly([(x1, y1), (x1 - 12, y1 - 2), (x1 - 2, y1 - 12)], RED)
    # closing numbers with red down arrows and mini bars, right half
    nx = ox + int(w * 0.55)
    for i, (s, v) in enumerate((("TAIPEI -6.2%", 62), ("SEOUL -5.2%", 52),
                                ("TOKYO -5.1%", 51), ("HONG KONG -1.9%", 19))):
        yy = oy + 14 + i * 17
        cv.fill_rect(nx, yy + 2, v // 2, 5, RED)
        cv.fill_rect(nx, yy + 2, v // 4, 5, (255, 120, 120))
        cv.text(nx + 36, yy, s, 1, PAPER)
        cv.fill_poly([(nx + 32, yy + 2), (nx + 28, yy + 2),
                      (nx + 30, yy + 7)], RED)


def pic_flags(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (242, 236, 220), (228, 220, 200))
    stipple(cv, ox, oy, w, h, (200, 192, 170), seed=11, density=1)
    # flag poles + shadows
    ex, ey, ew, eh = ox + int(w * 0.06), oy + int(h * 0.18), \
        int(w * 0.40), int(h * 0.62)
    cv.vline(ex - 3, ey - 4, ey + eh + 4, INK, 2)
    cv.fill_circle(ex - 2, ey - 5, 2, YELLOW)
    ux, uy, uw, uh = ox + int(w * 0.54), oy + int(h * 0.18), \
        int(w * 0.40), int(h * 0.62)
    cv.vline(ux - 3, uy - 4, uy + uh + 4, INK, 2)
    cv.fill_circle(ux - 2, uy - 5, 2, YELLOW)
    cv.fill_rect(ex, ey + eh + 1, ew, 3, (180, 172, 150))
    cv.fill_rect(ux, uy + uh + 1, uw, 3, (180, 172, 150))
    # EU flag with shading + 12 stars
    grad_v(cv, ex, ey, ew, eh, (40, 84, 180), (24, 58, 140))
    ecx, ecy = ex + ew // 2, ey + eh // 2
    for k in range(12):
        a = 2 * math.pi * k / 12 - math.pi / 2
        px = int(ecx + (eh * 0.30) * math.cos(a))
        py = int(ecy + (eh * 0.30) * math.sin(a))
        cv.fill_circle(px, py, 2, YELLOW)
        cv.hline(px - 3, px + 3, py, YELLOW, 1)
        cv.vline(px, py - 3, py + 3, YELLOW, 1)
    # UK flag: blue field, saltire, white cross, red cross, shading
    grad_v(cv, ux, uy, uw, uh, (40, 84, 180), (24, 58, 140))
    cv.line(ux, uy, ux + uw, uy + uh, PAPER, 4)
    cv.line(ux + uw, uy, ux, uy + uh, PAPER, 4)
    cv.line(ux, uy, ux + uw, uy + uh, RED, 2)
    cv.line(ux + uw, uy, ux, uy + uh, RED, 2)
    cv.fill_rect(ux + uw // 2 - 5, uy, 10, uh, PAPER)
    cv.fill_rect(ux, uy + uh // 2 - 5, uw, 10, PAPER)
    cv.fill_rect(ux + uw // 2 - 2, uy, 4, uh, RED)
    cv.fill_rect(ux, uy + uh // 2 - 2, uw, 4, RED)
    cv.hline(ux, ux + uw - 1, uy + uh - 1, (120, 120, 120), 1)


def pic_globe(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (242, 236, 220), (226, 218, 198))
    stipple(cv, ox, oy, w, h, (200, 192, 170), seed=23, density=1)
    cx, cy = ox + w // 2, oy + int(h * 0.48)
    r = int(h * 0.30)
    # ocean disc + continents
    cv.fill_circle(cx, cy, r, (120, 170, 215))
    cv.fill_circle(cx - 6, cy - 8, 7, (90, 160, 100))
    cv.fill_circle(cx + 8, cy + 2, 6, (90, 160, 100))
    cv.fill_circle(cx - 2, cy + 10, 5, (110, 170, 110))
    cv.fill_circle(cx + 10, cy - 10, 4, (90, 160, 100))
    cv.circle(cx, cy, r, INK, 2)
    cv.vline(cx, cy - r, cy + r, INK, 1)
    cv.hline(cx - r, cx + r, cy, INK, 1)
    cv.line(cx - int(r * 0.7), cy - int(r * 0.7),
            cx - int(r * 0.7), cy + int(r * 0.7), INK, 1)
    cv.line(cx + int(r * 0.7), cy - int(r * 0.7),
            cx + int(r * 0.7), cy + int(r * 0.7), INK, 1)
    cv.hline(cx - int(r * 0.85), cx + int(r * 0.85),
             cy - int(r * 0.55), INK, 1)
    cv.hline(cx - int(r * 0.85), cx + int(r * 0.85),
             cy + int(r * 0.55), INK, 1)
    # red slash + small no-deal badge
    cv.line(cx - r - 4, cy + r + 4, cx + r + 4, cy - r - 4, RED, 4)
    cv.line(cx - r - 2, cy + r + 2, cx + r + 2, cy - r - 2,
            (255, 130, 130), 1)
    cv.fill_circle(cx + r - 2, cy - r + 2, 6, RED)
    cv.text(cx + r - 5, cy - r - 1, "X", 1, PAPER)


def pic_poland(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (170, 205, 235), (215, 228, 240))
    # clouds + distant treeline
    for cx0, cy0, r0 in ((0.14, 0.12, 6), (0.20, 0.10, 8), (0.68, 0.08, 7),
                         (0.76, 0.11, 9), (0.44, 0.06, 5)):
        cv.fill_circle(ox + int(w * cx0), oy + int(h * cy0), r0, PAPER)
    fy = oy + int(h * 0.68)
    cv.hline(ox, ox + w - 1, fy, (70, 110, 70), 2)
    for tx in range(ox + 2, ox + w - 4, 10):
        cv.fill_circle(tx, fy - 3, 3, (60, 100, 60))
    # furrowed field with alternating strips
    for i in range(6):
        yy = fy + 2 + i * 3
        col = (120, 160, 110) if i % 2 == 0 else (100, 140, 95)
        cv.hline(ox, ox + w - 1, yy, col, 2)
    for wx in range(ox + 4, ox + w - 6, 12):
        cv.vline(wx, fy + 2, oy + h - 2, (90, 130, 85), 1)
    # trees for scale
    for tx0, th0 in ((0.78, 14), (0.86, 10), (0.06, 9)):
        tx = ox + int(w * tx0)
        cv.vline(tx, fy - th0, fy, INK, 2)
        cv.fill_circle(tx, fy - th0 - 4, 6, GREEN)
        cv.fill_circle(tx - 4, fy - th0, 4, (60, 130, 70))
    # missile streak + body, smoke trail
    hx, hy = ox + int(w * 0.34), fy - 2
    for i in range(5):
        cv.fill_circle(ox + int(w * 0.92) - i * 12,
                       oy + int(h * 0.10) + i * 7, 2, (200, 200, 200))
    cv.line(ox + int(w * 0.92), oy + int(h * 0.10), hx + 8, hy - 8, INK, 2)
    cv.fill_poly([(hx + 8, hy - 8), (hx + 16, hy - 14),
                  (hx + 18, hy - 4)], INK)
    cv.fill_rect(hx + 4, hy - 12, 12, 4, INK)
    # three impact bursts with smoke and scorched ground
    for bx0, r0 in ((0.34, 10), (0.58, 6), (0.14, 6)):
        px = ox + int(w * bx0)
        cv.fill_circle(px, fy + 2, r0, (60, 50, 40))
        cv.star(px, fy - 2, r0, RED, 2)
        cv.fill_circle(px, fy - 2, 3, YELLOW)
        cv.fill_circle(px - 7, fy - 10, 4, (150, 150, 150))
        cv.fill_circle(px + 6, fy - 13, 5, (130, 130, 130))


def pic_vehicle(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (240, 222, 180), (226, 206, 160))
    stipple(cv, ox, oy, w, h, (200, 180, 140), seed=31, density=1)
    # sun + distant dunes + building
    cv.fill_circle(ox + int(w * 0.82), oy + int(h * 0.16),
                   int(h * 0.11), YELLOW)
    cv.fill_circle(ox + int(w * 0.82), oy + int(h * 0.16),
                   int(h * 0.07), (255, 220, 120))
    cv.fill_rect(ox + int(w * 0.04), oy + int(h * 0.52),
                 int(w * 0.14), int(h * 0.20), (150, 130, 100))
    for wy in range(oy + int(h * 0.56), oy + int(h * 0.68), 5):
        cv.fill_rect(ox + int(w * 0.06), wy, 3, 3, (60, 50, 30))
        cv.fill_rect(ox + int(w * 0.13), wy, 3, 3, (60, 50, 30))
    gy = oy + int(h * 0.72)
    cv.fill_rect(ox, gy, w, h - int(h * 0.72), (120, 110, 95))
    cv.hline(ox, ox + w - 1, gy, INK, 2)
    for dx in range(ox + 6, ox + w - 8, 18):
        cv.fill_rect(dx, gy + 5, 10, 2, PAPER)
    # palm tree
    px = ox + int(w * 0.90)
    cv.line(px, gy, px + 4, gy - 22, INK, 2)
    for dx, dy in ((-10, -26), (10, -28), (-14, -18), (12, -16), (0, -30)):
        cv.line(px + 4, gy - 22, px + 4 + dx, gy - 22 + dy, GREEN, 2)
    # vehicle: body, camo patches, turret, barrel, windows, wheels
    bx, by = ox + int(w * 0.10), oy + int(h * 0.44)
    bw, bh = int(w * 0.58), int(h * 0.26)
    cv.fill_rect(bx, by, bw, bh, (52, 62, 44))
    cv.fill_rect(bx + 8, by + 3, 18, 8, (90, 100, 60))
    cv.fill_rect(bx + bw - 26, by + 6, 16, 7, (90, 100, 60))
    cv.fill_rect(bx + int(bw * 0.25), by - 10, int(bw * 0.35), 10,
                 (52, 62, 44))
    cv.fill_rect(bx + int(bw * 0.30), by - 8, 8, 5, (150, 190, 220))
    cv.line(bx + int(bw * 0.60), by - 5, bx + bw + 14, by - 8, INK, 3)
    cv.fill_rect(bx, by + bh - 3, bw, 3, INK)
    for i in range(3):
        wx0 = bx + 12 + i * 22
        cv.fill_circle(wx0, gy - 3, 6, INK)
        cv.fill_circle(wx0, gy - 3, 2, PAPER)
        cv.vline(wx0, gy - 9, gy - 3, INK, 2)


def pic_strike(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (235, 228, 210), (220, 212, 192))
    # street buildings behind the march
    for bx0, bh0 in ((0.04, 0.30), (0.22, 0.22), (0.58, 0.26)):
        bx = ox + int(w * bx0)
        cv.fill_rect(bx, oy + int(h * 0.62) - int(h * bh0),
                     int(w * 0.14), int(h * bh0), (170, 160, 140))
        for wy in range(oy + int(h * 0.62) - int(h * bh0) + 4,
                        oy + int(h * 0.62) - 2, 6):
            cv.fill_rect(bx + 3, wy, 3, 3, (80, 70, 50))
            cv.fill_rect(bx + 12, wy, 3, 3, (80, 70, 50))
    # two placards on sticks
    for sx0, word in ((0.74, "SCIOPERO"), (0.30, "NO!")):
        sx = ox + int(w * sx0)
        cv.vline(sx, oy + int(h * 0.12), oy + int(h * 0.62), INK, 2)
        pw = cv.text_width(word, 1) + 8
        cv.fill_rect(sx - pw // 2, oy + int(h * 0.06), pw, 13, PAPER)
        cv.hline(sx - pw // 2, sx + pw // 2 - 1, oy + int(h * 0.06), INK, 1)
        cv.hline(sx - pw // 2, sx + pw // 2 - 1, oy + int(h * 0.06) + 12,
                 INK, 1)
        cv.vline(sx - pw // 2, oy + int(h * 0.06),
                 oy + int(h * 0.06) + 12, INK, 1)
        cv.vline(sx + pw // 2 - 1, oy + int(h * 0.06),
                 oy + int(h * 0.06) + 12, INK, 1)
        cv.text(sx - pw // 2 + 4, oy + int(h * 0.06) + 3, word, 1, INK)
    # ground + four marchers with arms
    by = oy + int(h * 0.78)
    cv.hline(ox, ox + w - 1, by, INK, 2)
    cv.hline(ox, ox + w - 1, by + 3, (150, 140, 120), 1)
    for i, (fx, col) in enumerate(((0.14, INK), (0.36, RED),
                                   (0.56, INK), (0.70, (60, 60, 60)))):
        hx = ox + int(w * fx)
        cv.fill_circle(hx, oy + int(h * 0.52), 7, col)
        cv.fill_poly([(hx - 12, by), (hx + 12, by),
                      (hx + 7, oy + int(h * 0.60)),
                      (hx - 7, oy + int(h * 0.60))], col)
        cv.line(hx + 6, oy + int(h * 0.62), hx + 14, oy + int(h * 0.52),
                col, 2)
        cv.line(hx - 10, by, hx - 14, by + 4, col, 2)
        cv.line(hx + 10, by, hx + 14, by + 4, col, 2)


def pic_rising(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (250, 238, 210), (240, 224, 190))
    # sun with rays
    sx, sy = ox + int(w * 0.26), oy + int(h * 0.36)
    for k in range(12):
        a = 2 * math.pi * k / 12
        cv.line(sx + int(14 * math.cos(a)), sy + int(14 * math.sin(a)),
                sx + int(20 * math.cos(a)), sy + int(20 * math.sin(a)),
                (230, 120, 60), 2)
    cv.fill_circle(sx, sy, 12, (230, 90, 50))
    cv.fill_circle(sx, sy, 8, RED)
    cv.fill_circle(sx - 3, sy - 3, 3, (255, 150, 100))
    # faint grid + ascending bars with tops
    for gy in range(oy + 10, oy + int(h * 0.82), 12):
        cv.hline(ox + int(w * 0.36), ox + w - 4, gy, (200, 190, 170), 1)
    bw = int(w * 0.11)
    bx0 = ox + int(w * 0.38)
    for i, bh in enumerate((0.28, 0.44, 0.60)):
        bhpx = int(h * bh)
        x = bx0 + i * (bw + 8)
        grad_v(cv, x, oy + int(h * 0.80) - bhpx, bw, bhpx,
               (70, 70, 70), INK)
        cv.hline(x, x + bw - 1, oy + int(h * 0.80) - bhpx, RED, 2)
    # red up arrow + dashed extension
    x0, y0 = ox + int(w * 0.36), oy + int(h * 0.62)
    x1, y1 = ox + int(w * 0.88), oy + int(h * 0.16)
    dashed(cv, x0, y0, x1, y1, (200, 100, 100))
    cv.line(x0, y0, x1, y1, RED, 3)
    cv.fill_poly([(x1, y1), (x1 - 12, y1), (x1, y1 + 12)], RED)
    cv.fill_circle(x0, y0, 3, RED)


def pic_court(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (238, 232, 216), (222, 214, 196))
    stipple(cv, ox, oy, w, h, (200, 192, 172), seed=41, density=1)
    # flag on the pediment
    fx = ox + int(w * 0.62)
    cv.vline(fx, oy + int(h * 0.02), oy + int(h * 0.10), INK, 2)
    cv.fill_poly([(fx, oy + int(h * 0.02)), (fx + 12, oy + int(h * 0.04)),
                  (fx, oy + int(h * 0.07))], RED)
    # pediment with round medallion
    cv.fill_poly([(ox + int(w * 0.28), oy + int(h * 0.34)),
                  (ox + int(w * 0.95), oy + int(h * 0.34)),
                  (ox + int(w * 0.62), oy + int(h * 0.10))], INK)
    cv.fill_circle(ox + int(w * 0.62), oy + int(h * 0.26), 5, PAPER)
    cv.fill_circle(ox + int(w * 0.62), oy + int(h * 0.26), 2, RED)
    # three fluted columns with capitals
    for i in range(3):
        cx = ox + int(w * (0.36 + i * 0.26))
        cv.fill_rect(cx - 7, oy + int(h * 0.36), 14, 4, INK)
        cv.fill_rect(cx - 5, oy + int(h * 0.38), 10, int(h * 0.32), INK)
        cv.vline(cx - 2, oy + int(h * 0.40), oy + int(h * 0.68), PAPER, 1)
        cv.vline(cx + 2, oy + int(h * 0.40), oy + int(h * 0.68), PAPER, 1)
        cv.fill_rect(cx - 7, oy + int(h * 0.68), 14, 4, INK)
    # steps
    cv.fill_rect(ox + int(w * 0.26), oy + int(h * 0.72),
                 int(w * 0.71), 6, INK)
    cv.fill_rect(ox + int(w * 0.22), oy + int(h * 0.80),
                 int(w * 0.79), 4, INK)
    cv.fill_rect(ox + int(w * 0.18), oy + int(h * 0.87),
                 int(w * 0.87), 3, (120, 112, 96))


def pic_derrick(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (250, 232, 190), (238, 210, 160))
    # low sun with rays + clouds
    sx, sy = ox + int(w * 0.80), oy + int(h * 0.22)
    for k in range(8):
        a = 2 * math.pi * k / 8
        cv.line(sx + int(12 * math.cos(a)), sy + int(12 * math.sin(a)),
                sx + int(17 * math.cos(a)), sy + int(17 * math.sin(a)),
                (230, 160, 60), 2)
    cv.fill_circle(sx, sy, 10, YELLOW)
    cv.fill_circle(sx, sy, 6, (255, 220, 120))
    for cx0, cy0, r0 in ((0.12, 0.14, 6), (0.18, 0.12, 8), (0.55, 0.08, 5)):
        cv.fill_circle(ox + int(w * cx0), oy + int(h * cy0), r0,
                       (245, 240, 225))
    # ground + scrub
    base = oy + int(h * 0.78)
    cv.fill_rect(ox, base, w, h - int(h * 0.78), (150, 130, 90))
    cv.hline(ox, ox + w - 1, base, INK, 2)
    for gx in range(ox + 6, ox + w - 8, 14):
        cv.line(gx, base + 4, gx + 3, base - 2, (90, 110, 60), 1)
    # A-frame with cross-bracing + crown + cable
    ax = ox + int(w * 0.30)
    top = oy + int(h * 0.10)
    cv.line(ax - 26, base, ax, top, INK, 3)
    cv.line(ax + 26, base, ax, top, INK, 3)
    for fy in (0.28, 0.44, 0.60):
        yy = oy + int(h * fy)
        cv.hline(ax - 18, ax + 18, yy, INK, 2)
    cv.line(ax - 18, oy + int(h * 0.28), ax + 18, oy + int(h * 0.44),
            INK, 1)
    cv.line(ax + 18, oy + int(h * 0.28), ax - 18, oy + int(h * 0.44),
            INK, 1)
    cv.fill_rect(ax - 4, top - 4, 8, 6, INK)
    cv.vline(ax, top + 2, oy + int(h * 0.30), INK, 1)
    cv.fill_rect(ax - 3, oy + int(h * 0.30), 6, 5, INK)
    # crude drop + puddle + barrel
    dx, dy = ox + int(w * 0.72), oy + int(h * 0.62)
    cv.fill_circle(dx, dy, 6, INK)
    cv.fill_poly([(dx - 6, dy - 2), (dx + 6, dy - 2), (dx, dy - 12)], INK)
    cv.fill_circle(dx + 2, dy - 2, 2, (90, 90, 90))
    cv.fill_circle(dx, base - 2, 9, (40, 35, 30))
    cv.fill_rect(ox + int(w * 0.52), base - 12, 12, 12, (90, 60, 30))
    cv.hline(ox + int(w * 0.52), ox + int(w * 0.52) + 11, base - 12,
             INK, 1)


def pic_rikers(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (190, 215, 235), (220, 230, 240))
    # clouds + gulls
    for cx0, cy0, r0 in ((0.14, 0.12, 6), (0.20, 0.10, 8), (0.70, 0.08, 6)):
        cv.fill_circle(ox + int(w * cx0), oy + int(h * cy0), r0, PAPER)
    for gx0, gy0 in ((0.45, 0.12), (0.55, 0.16)):
        gx, gy = ox + int(w * gx0), oy + int(h * gy0)
        cv.line(gx - 5, gy, gx, gy - 3, INK, 1)
        cv.line(gx, gy - 3, gx + 5, gy, INK, 1)
    # river with gradient + ripples + boat wake
    wy = oy + int(h * 0.70)
    grad_v(cv, ox, wy, w, h - int(h * 0.70), (70, 120, 175), (40, 85, 140))
    for wx in range(ox + 6, ox + w - 10, 14):
        cv.line(wx, wy + 5, wx + 7, wy + 2, PAPER, 1)
        cv.line(wx + 7, wy + 2, wx + 14, wy + 5, PAPER, 1)
        cv.line(wx + 3, wy + 11, wx + 10, wy + 9, (150, 190, 225), 1)
    cv.fill_rect(ox + int(w * 0.06), wy + 8, 16, 4, (90, 90, 90))
    cv.fill_rect(ox + int(w * 0.08), wy + 4, 6, 5, (70, 70, 70))
    # island mound + shore grass
    cv.fill_poly([(ox + int(w * 0.08), wy),
                  (ox + int(w * 0.92), wy),
                  (ox + int(w * 0.84), wy - 8),
                  (ox + int(w * 0.16), wy - 8)], LAND)
    for gx in range(ox + int(w * 0.12), ox + int(w * 0.88), 10):
        cv.line(gx, wy - 8, gx + 2, wy - 12, GREEN, 1)
    # jail block: roof, barred windows, door, watchtower
    bx, by = ox + int(w * 0.24), oy + int(h * 0.30)
    bw, bh = int(w * 0.52), int(h * 0.36)
    cv.fill_rect(bx, by, bw, bh, INK)
    cv.hline(bx - 4, bx + bw + 3, by - 2, INK, 2)
    cv.hline(bx - 4, bx + bw + 3, by - 5, (120, 120, 120), 1)
    for i in range(4):
        wx = bx + 8 + i * 20
        cv.fill_rect(wx, by + 7, 10, 10, PAPER)
        cv.vline(wx + 5, by + 7, by + 16, INK, 1)
        cv.hline(wx, wx + 9, by + 11, INK, 1)
    cv.fill_rect(bx + bw // 2 - 5, by + bh - 10, 10, 10, PAPER)
    cv.vline(bx + bw // 2, by + bh - 10, by + bh - 1, INK, 1)
    tx = ox + int(w * 0.84)
    cv.fill_rect(tx - 2, by + 4, 4, int(h * 0.30), INK)
    cv.fill_rect(tx - 8, by, 16, 8, INK)
    cv.fill_rect(tx - 6, by + 2, 4, 4, PAPER)
    cv.fill_rect(tx + 2, by + 2, 4, 4, PAPER)


def pic_cricket(cv, ox, oy, w, h):
    grad_v(cv, ox, oy, w, h, (180, 215, 235), (215, 232, 240))
    # clouds + crowd dots in the stand
    for cx0, cy0, r0 in ((0.12, 0.10, 6), (0.18, 0.08, 8), (0.55, 0.07, 5)):
        cv.fill_circle(ox + int(w * cx0), oy + int(h * cy0), r0, PAPER)
    cv.fill_rect(ox, oy + int(h * 0.22), w, 8, (120, 120, 120))
    for cx0 in range(ox + 6, ox + w - 6, 9):
        cv.fill_rect(cx0, oy + int(h * 0.23), 3, 3,
                     RED if (cx0 // 9) % 3 == 0 else
                     (BLUE if (cx0 // 9) % 3 == 1 else PAPER))
    # green outfield with mowing stripes + pitch
    gy = oy + int(h * 0.68)
    for i in range(6):
        col = (150, 190, 140) if i % 2 == 0 else (130, 175, 125)
        cv.fill_rect(ox + i * (w // 6), gy, w // 6 + 1,
                     h - int(h * 0.68), col)
    cv.fill_rect(ox + int(w * 0.30), oy + int(h * 0.30),
                 int(w * 0.40), gy - oy - int(h * 0.30), (215, 195, 160))
    cv.hline(ox, ox + w - 1, gy, (90, 130, 90), 1)
    # stumps + bails
    sx = ox + int(w * 0.18)
    for i in range(3):
        cv.vline(sx + i * 7, oy + int(h * 0.30), gy, INK, 3)
    cv.hline(sx, sx + 14, oy + int(h * 0.30), INK, 2)
    cv.fill_rect(sx + 1, oy + int(h * 0.30) - 3, 5, 2, YELLOW)
    cv.fill_rect(sx + 8, oy + int(h * 0.30) - 3, 5, 2, YELLOW)
    # bat with handle + grip lines, diagonal
    cv.line(ox + int(w * 0.55), oy + int(h * 0.12),
            ox + int(w * 0.78), oy + int(h * 0.62), (200, 170, 110), 7)
    cv.line(ox + int(w * 0.55), oy + int(h * 0.12),
            ox + int(w * 0.60), oy + int(h * 0.24), (120, 90, 50), 3)
    # ball with seam + motion dots, fielder silhouette
    bx0, by0 = ox + int(w * 0.86), oy + int(h * 0.70)
    cv.fill_circle(bx0, by0, 7, RED)
    cv.fill_circle(bx0 - 2, by0 - 2, 2, (255, 150, 150))
    cv.line(bx0 - 5, by0 - 5, bx0 + 5, by0 + 5, PAPER, 1)
    for dx0, dy0 in ((-14, -10), (-22, -16)):
        cv.fill_circle(bx0 + dx0, by0 + dy0, 1, RED)
    fx0 = ox + int(w * 0.44)
    cv.fill_circle(fx0, gy - 14, 4, INK)
    cv.fill_rect(fx0 - 3, gy - 10, 6, 10, INK)

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
    (10, 42, 4, 8, -11), (11, 29, 10, 8, -4), (12, 9, 4, -14, -4),
    (13, 46, 16, 8, -4),
]

def draw_map(cv, ox, oy, cell=5):
    # ocean tint + graticule
    cv.fill_rect(ox, oy, 48 * cell, 18 * cell, (214, 228, 238))
    for gx in range(0, 48, 6):
        cv.vline(ox + gx * cell, oy, oy + 18 * cell, (190, 205, 220), 1)
    for gy in range(0, 18, 6):
        cv.hline(ox, ox + 48 * cell, oy + gy * cell, (190, 205, 220), 1)
    for row, spans in MAP_SPANS.items():
        for c0, c1 in spans:
            for c in range(c0, c1 + 1):
                cv.fill_rect(ox + c * cell, oy + row * cell,
                             cell, cell, LAND)
                if (c * 7 + row * 3) % 4 == 0:
                    cv.set(ox + c * cell + 1, oy + row * cell + 1,
                           (170, 152, 112))
    # equator + tropics
    cv.hline(ox, ox + 48 * cell - 1, oy + 9 * cell, (150, 150, 150), 1)
    for num, col, row, dx, dy in MAP_DOTS:
        px = ox + col * cell + cell // 2
        py = oy + row * cell + cell // 2
        cv.fill_circle(px, py, 4, PAPER)
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
    ("EUROPE", 10, (36, 64, 120)),
    ("ASIA", 12, RED),
    ("MIDDLE EAST", 3, (150, 100, 20)),
    ("AFRICA", 7, GREEN),
    ("AMERICAS", 11, (90, 60, 140)),
    ("OCEANIA", 4, (20, 120, 120)),
    ("GLOBAL", 4, (70, 70, 70)),
]

TOP3 = [
    dict(pic=pic_kyiv, tag="KYIV", tag2="3 BRIDGES HIT",
         cap="OFFICIALS' COUNT", w=360, pic_h=108, head_scale=3,
         kicker="1 KYIV, UKRAINE - WAR",
         head="RUSSIAN MISSILES HIT THREE KYIV BRIDGES",
         body="AN OVERNIGHT BARRAGE OF ABOUT 110 MISSILES AND 400 DRONES "
              "KILLED AT LEAST NINE PEOPLE ACROSS UKRAINE AND CUT POWER "
              "AND WATER IN THE CAPITAL. (KYIV INDEPENDENT, BBC)"),
    dict(pic=pic_cyclone, tag="CYCLONE AKVAN", tag2="LANDFALL - 8 AM",
         cap="WEATHER OFFICE", w=278, pic_h=96, head_scale=2,
         kicker="2 ODISHA, INDIA - CYCLONE",
         head="CYCLONE AKVAN COMES ASHORE IN EASTERN INDIA",
         body="THE STORM CROSSED THE COAST NEAR GOPALPUR FROM ABOUT 8 AM "
              "AFTER MORE THAN 300,000 PEOPLE WERE MOVED TO SHELTERS. "
              "NO DEATHS WERE REPORTED. (IMD, DECCAN HERALD)"),
    dict(pic=pic_selloff, tag="AI SELL-OFF", tag2="ASIA, FRIDAY'S CLOSE",
         cap="CLOSING PRICES", w=278, pic_h=96, head_scale=2,
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
    dict(pic=pic_poland, tag="POLAND: 3 OBJECTS",
         cap="NOWY LIPOWIEC - REUTERS",
         kicker="6 EASTERN POLAND - SECURITY",
         head="RUSSIAN MISSILES AND DRONE LAND IN POLAND",
         body="THREE OBJECTS DOWN; ONLY RZESZOW AIRPORT PAUSED."),
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
    dict(pic=pic_rikers, tag="RIKERS: 2032", cap="PLAN OUT - REUTERS",
         kicker="12 NEW YORK - JUSTICE",
         head="MAMDANI UNVEILS PLAN TO CLOSE RIKERS BY 2032",
         body="FOUR BOROUGH JAILS TO REPLACE IT; INMATES CUT TO 4,100."),
    dict(pic=pic_cricket, tag="PHILLIPS: 118", cap="SCORECARD - ICC",
         kicker="13 WELLINGTON - CRICKET",
         head="PHILLIPS HITS 118 AGAINST INDIA",
         body="HUNDREDS V INDIA IN ALL THREE FORMATS."),
]

ALSO_LEFT = [
    "14 LVIV - RAILWAY STATION STRIKE KILLS TWO (BBC)",
    "15 MOSCOW - RUSSIA DENIES SABOTAGE (REUTERS)",
    "16 BERLIN - PUPILS STRIKE OVER ARMY SERVICE (AL JAZEERA)",
    "17 LONDON - UK RUNS CYBER ATTACKS ABROAD (SKY NEWS)",
    "18 BEIJING - CHINA HOLDS LOAN RATES, 18TH MONTH (XINHUA)",
    "19 TOKYO - SOFTBANK SHARES FALL OVER 14% (AL JAZEERA)",
    "20 SEOUL - KOSPI ENDS THE WEEK 7.9% LOWER (ANADOLU)",
    "21 GANJAM - 209 MM OF RAIN AS AKVAN CROSSES ODISHA (PTI)",
    "22 LEBANON - ISRAELI STRIKES HIT THREE TOWNS (NNA)",
    "23 YEMEN - GUNMEN FIRE ON A CARGO SHIP OFF COAST (UKMTO)",
    "24 ABUJA - COURT BARS EVIDENCE VS TINUBU (CHANNELS TV)",
    "25 CONGO - EBOLA IN NEARLY 100 EASTERN SCHOOLS (ANADOLU)",
    "26 MALAWI - FUEL CRISIS, NIGHT-LONG QUEUES (AL JAZEERA)",
    "27 AFRICA - 22 IN OR NEAR DEBT DISTRESS (ALLAFRICA)",
    "28 LAS VEGAS - RUSSELL FASTEST IN PRACTICE (AUTOSPORT)",
    "29 NEW YORK - NASDAQ FUTURES FALL 1.6% (24/7 WALL ST)",
    "30 WASHINGTON - DAVIES NAMED CYBER DIRECTOR (BLOOMBERG)",
    "31 WELLINGTON - NICHOLLS 175 IN A STAND OF 216 (ICC)",
    "32 SYDNEY - ASX 200 FALLS 1.6% TO 8,592.6 (REUTERS)",
]

ALSO_RIGHT = [
    "33 ANTALYA - PANAMA WANTS COP31 OIL OUTPUT CAP (ANADOLU)",
    "34 ANTALYA - EU CALLS CLIMATE DRAFT UNACCEPTABLE (RTE)",
    "35 TURIN - ATP TO LIFT PLAYER PAY PAST $350M (ANADOLU)",
    "36 COPENHAGEN - DENMARK EXPELS RUSSIAN ATTACHE (BBC)",
    "37 GTA VI SMASHES $3.79BN DAY-ONE RECORD (REUTERS)",
    "38 WASHINGTON - MATHEMATICIAN CLAIMS RIEMANN PROOF (AFP)",
    "39 ST LOUIS - $7.25BN ROUNDUP DEAL APPROVED (REUTERS)",
    "40 LOS ANGELES - MAN CONVICTED OVER PALISADES FIRE (BBC)",
    "41 PARIS - THREE POLICE JAILED OVER ZECLER BEATING (BBC)",
    "42 BAYELSA - FUNERAL BOAT CAPSIZES, 4 DEAD (AL JAZEERA)",
    "43 HAITI - TWO SALVADORAN SOLDIERS KILLED (AL JAZEERA)",
    "44 WASHINGTON - PENTAGON DECLASSIFIES UFO FOOTAGE (BBC)",
    "45 WASHINGTON - TRUMP THREATENS TAX ON AI CENTRES (BBC)",
    "46 PAKISTAN BEAT SRI LANKA TO SEAL TEST SERIES (REUTERS)",
    "47 DOHA - INDIA A THRASH NEPAL BY 306 RUNS (IANS)",
    "48 XI HAILS TURNAROUND IN CHINA-AUSTRALIA TIES (REUTERS)",
    "49 MUMBAI - RICE PRICES HIT 19-MONTH HIGH (REUTERS)",
    "50 JOHANNESBURG - ANC FIGHTS TO KEEP KEY CITIES (BBC)",
    "51 SYDNEY - MAN CHARGED OVER ALLEGED CAR-BOMB PLOT (ABC)",
]

DATE_CHECK = ("LEFT OUT AS THURSDAY 19 NOVEMBER'S NEWS: THE WORLD COURT'S "
              "RULING ON MYANMAR, THE THREE-LEADER DECLARATION IN SHENZHEN, "
              "TONGA'S DROUGHT AND THE MIGRANT BOAT OFF SENEGAL. "
              "NOT YET SHOWN: BEPICOLOMBO ENTERS ORBIT ROUND MERCURY ON 21 "
              "NOVEMBER, AND NO FINAL COP31 TEXT WAS ADOPTED ON 20 NOVEMBER.")


def draw_list_col(cv, x, y, items, w=336):
    # Single-line items only: every item is <= 56 chars, which fits
    # 336 px at scale 1 (6 px per char). Number in red, rest in gray.
    # Alternating row tint + hairline rules for density.
    y0 = y
    for i, s in enumerate(items):
        assert len(s) <= 56, s
        if i % 2 == 0:
            cv.fill_rect(x - 3, y - 2, w + 6, 11, (243, 238, 226))
        cv.hline(x - 3, x + w + 2, y + 10, (214, 206, 188), 1)
        cv.fill_rect(x - 3, y - 2, 2, 11, RED if i % 2 == 0 else (200, 120, 120))
        cv.text(x, y, s, 1, GRAY)
        cv.text(x, y, s.split(' ')[0], 1, RED)
        y += 12
    return y


def draw():
    cv = Canvas(W, H, PAPER)

    # page frame
    cv.hline(12, 1011, 12, INK, 2)
    cv.hline(12, 1011, 1010, INK, 2)
    cv.vline(12, 12, 1010, INK, 2)
    cv.vline(1011, 12, 1010, INK, 2)

    # ---- kicker + masthead: the paper's name is the biggest thing ----
    cv.text_centred(W // 2, 20,
                    "51 STORIES - 7 REGIONS - EVERY ONE DATED "
                    "FRIDAY 20 NOVEMBER 2026", 1, RED)
    # nameplate: grey shadow, then double-struck black for a heavy
    # serif-style weight, with diamond ornaments either side
    _mw = cv.text_width("THE WORLD IN ONE DAY", 5)
    _mx = W // 2 - _mw // 2
    cv.text(_mx + 3, 33, "THE WORLD IN ONE DAY", 5, (150, 145, 135))
    cv.text(_mx, 30, "THE WORLD IN ONE DAY", 5, INK)
    cv.text(_mx + 1, 30, "THE WORLD IN ONE DAY", 5, INK)
    for _dx in (-1, 1):
        _ox = W // 2 + _dx * (_mw // 2 + 26)
        cv.fill_poly([(_ox, 40), (_ox + 6, 47), (_ox, 54), (_ox - 6, 47)],
                     RED)
        cv.fill_poly([(_ox, 43), (_ox + 3, 47), (_ox, 51), (_ox - 3, 47)],
                     PAPER)
    cv.text_centred(W // 2, 68, "FRIDAY 20 NOVEMBER 2026", 3, RED)
    cv.text_centred(W // 2, 69, "FRIDAY 20 NOVEMBER 2026", 3, RED)
    cv.hline(MARGIN, RIGHT, 94, INK, 3)
    cv.hline(MARGIN, RIGHT, 99, INK, 1)

    # ---- stat strip: BY THE NUMBERS label, scale-4 numbers ----
    # Uneven columns: each column is as wide as its longest line needs
    # (number at scale 4, or its two label lines), so 300,000+ fits.
    cv.fill_rect(MARGIN, 102, 952, 66, (244, 239, 228))
    cv.hline(MARGIN, RIGHT, 102, RED, 1)
    cv.hline(MARGIN, RIGHT, 167, INK, 1)
    for _sx in range(MARGIN, RIGHT, 24):
        cv.set(_sx, 104, (220, 214, 200))
    cv.text(MARGIN, 106, "BY THE NUMBERS", 1, RED)
    cv.hline(MARGIN + 91, RIGHT, 109, RED, 1)
    stat_w = [153, 198, 134, 174, 153, 140]
    x = MARGIN
    for (num, l1, l2), wseg in zip(STATS, stat_w):
        if x > MARGIN:
            cv.vline(x - 4, 120, 164, RED, 2)
        cv.text(x + 2, 120, num, 4, INK)
        cv.text(x + 2, 150, l1, 1, GRAY)
        cv.text(x + 2, 159, l2, 1, GRAY)
        x += wseg

    # ---- region bar ----
    total = sum(c for _, c, _ in REGIONS)
    widths = [952 * c // total for _, c, _ in REGIONS]
    widths[-1] = 952 - sum(widths[:-1])
    x = MARGIN
    for (name, count, col), wseg in zip(REGIONS, widths):
        cv.fill_rect(x, 172, wseg, 18, col)
        cv.text_centred(x + wseg // 2, 177, "%s %d" % (name, count), 1,
                        PAPER)
        x += wseg

    # ---- top 3 stories: lead (#1) is wider, taller, scale-3 head ----
    cv.text(MARGIN, 196, "TOP STORIES", 1, RED)
    cv.hline(MARGIN + 73, RIGHT, 199, RED, 1)
    top_x = [MARGIN, 414, 710]
    for (sx, story) in zip(top_x, TOP3):
        w = story['w']
        ph = story['pic_h']
        hs = story['head_scale']
        pic_box(cv, sx, 208, w, ph)
        story['pic'](cv, sx + 1, 209, w - 2, ph - 2)
        tag(cv, sx + 5, 213, story['tag'])
        tag_white(cv, sx + 5, 230, story['tag2'])
        caption_strip(cv, sx + 1, 208 + ph - 13, w - 2, story['cap'])
        cv.text(sx, 208 + ph + 6, story['kicker'], 1, RED)
        y = 208 + ph + 16
        for line in cv.wrap(story['head'], hs, w):
            cv.text(sx, y, line, hs, INK)
            y += 7 * hs + 2
        y += 6
        for line in cv.wrap(story['body'], 1, w):
            cv.text(sx, y, line, 1, GRAY)
            y += 9
    cv.hline(MARGIN, RIGHT, 417, INK, 1)

    # ---- five-story rows (middle + bottom), compressed pictograms ----
    def five_row(y0, stories):
        xs = [MARGIN, 229, 422, 615, 808]
        for sx, story in zip(xs, stories):
            pic_box(cv, sx, y0, 180, 60)
            story['pic'](cv, sx + 1, y0 + 1, 178, 58)
            tag(cv, sx + 5, y0 + 5, story['tag'])
            caption_strip(cv, sx + 1, y0 + 60 - 13, 178, story['cap'])
            cv.text(sx, y0 + 66, story['kicker'], 1, RED)
            y = y0 + 76
            for line in cv.wrap(story['head'], 1, 180):
                cv.text(sx, y, line, 1, INK)
                y += 9
            y = y0 + 96
            for line in cv.wrap(story['body'], 1, 180):
                cv.text(sx, y, line, 1, GRAY)
                y += 9

    cv.text(MARGIN, 423, "MORE FROM THE DAY", 1, RED)
    cv.hline(MARGIN + 115, RIGHT, 426, RED, 1)
    five_row(436, MID5)
    cv.hline(MARGIN, RIGHT, 556, INK, 1)
    five_row(562, BOT5)
    cv.hline(MARGIN, RIGHT, 680, INK, 1)

    # ---- map + also list ----
    cv.text(MARGIN, 686, "WHERE IT HAPPENED", 1, RED)
    cv.text(300, 686, "ALSO ON FRIDAY 20 NOVEMBER - 38 MORE STORIES", 2, INK)
    pic_box(cv, MARGIN, 694, 250, 150)
    draw_map(cv, MARGIN + 5, 699)
    for i, line in enumerate(cv.wrap(
            "EACH NUMBER IS THAT STORY WITH THAT NUMBER ON THIS PAGE.",
            1, 250)):
        cv.text(MARGIN, 850 + i * 9, line, 1, GRAY)
    draw_list_col(cv, 300, 700, ALSO_LEFT)
    draw_list_col(cv, 652, 700, ALSO_RIGHT)

    # ---- date check ----
    cv.fill_rect(MARGIN, 925, 952, 42, (253, 238, 232))
    hatch_diag(cv, MARGIN + 2, 927, 952 - 4, 38, (245, 228, 220), step=14)
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
    # v4: fine newsprint grain over the finished page (see apply_grain)
    apply_grain(cv, 7)
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
