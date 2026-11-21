#!/usr/bin/env python3
"""THE WORLD TODAY -- front page for Friday 20 November 2026.

Draws a 1024x1024 newspaper front page procedurally with Python 3 stdlib
only (struct + zlib for the PNG encoder, a hand-defined 5x7 bitmap font,
and geometric pictograms). No network, no external files, no randomness:
two runs produce byte-identical output.

Writes $MAKEFUN_OUTPUT_DIR/entry.png (fallback /output).

Stories (all verified against live reporting on 21 Nov 2026; see README):
  LEAD  ICJ rules Myanmar committed genocide against the Rohingya --
        first time the World Court has held a state responsible for
        genocide (ruling 9-6, reparations ordered).
  2     Trump, Xi and Putin hold the first trilateral summit in
        Shenzhen and sign a four-point Declaration toward Peace.
  3     Russian overnight strikes hit three Kyiv bridges:
        at least 8 killed, 28 injured.
  4     Markets slide: S&P 500 down 2%, sixth day in a row;
        Nikkei down about 5%; Anthropic debuts +17%.
  5     Houthi missile hits the PIF Tower in Riyadh:
        windows blown out on 7-8 floors, no injuries.
  ALSO  GTA 6: est. $2.36 billion in first-day sales (Sensor Tower).
"""
import hashlib
import os
import struct
import zlib

W = H = 1024

PAPER = (250, 246, 236)   # warm newsprint
INK = (17, 17, 17)        # near-black
GRAY = (74, 74, 74)       # body text
RED = (176, 30, 30)       # accent: date, kickers, alert marks
PANEL = (238, 232, 214)   # light tint for pictogram boxes

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
# Every icon is drawn from geometric primitives in code -- no images.

def pic_scales(cv, ox, oy, s):
    """Scales of justice, centred in a box of side s at (ox, oy)."""
    cx = ox + s // 2
    top = oy + 14
    # finial + post + base
    cv.fill_circle(cx, top, 5, INK)
    cv.fill_rect(cx - 2, top + 4, 5, 96, INK)
    cv.fill_rect(cx - 26, top + 100, 52, 6, INK)
    cv.fill_rect(cx - 36, top + 106, 72, 5, INK)
    # beam
    beam_y = top + 18
    cv.fill_rect(cx - 52, beam_y, 104, 4, INK)
    cv.fill_circle(cx - 52, beam_y + 2, 4, INK)
    cv.fill_circle(cx + 52, beam_y + 2, 4, INK)
    # two pans
    for sgn in (-1, 1):
        px = cx + sgn * 52
        cv.line(px, beam_y + 4, px - 20, beam_y + 42, INK, 2)
        cv.line(px, beam_y + 4, px, beam_y + 44, INK, 2)
        cv.line(px, beam_y + 4, px + 20, beam_y + 42, INK, 2)
        cv.fill_poly([(px - 22, beam_y + 40), (px + 22, beam_y + 40),
                      (px, beam_y + 62)], RED)
        cv.hline(px - 22, px + 22, beam_y + 40, INK, 3)


def pic_summit(cv, ox, oy, s):
    """Three leaders at a table with a document."""
    # heads
    for hx, hy in ((ox + 24, oy + 28), (ox + 52, oy + 22), (ox + 80, oy + 28)):
        cv.fill_circle(hx, hy, 9, INK)
    # bodies (trapezoids)
    cv.fill_poly([(ox + 12, oy + 68), (ox + 36, oy + 68),
                  (ox + 32, oy + 40), (ox + 16, oy + 40)], INK)
    cv.fill_poly([(ox + 40, oy + 68), (ox + 64, oy + 68),
                  (ox + 60, oy + 34), (ox + 44, oy + 34)], RED)
    cv.fill_poly([(ox + 68, oy + 68), (ox + 92, oy + 68),
                  (ox + 88, oy + 40), (ox + 72, oy + 40)], INK)
    # document on the table
    cv.fill_rect(ox + 45, oy + 62, 14, 10, PAPER)
    cv.hline(ox + 45, ox + 59, oy + 62, INK, 1)
    cv.hline(ox + 45, ox + 59, oy + 71, INK, 1)
    cv.vline(ox + 45, oy + 62, oy + 71, INK, 1)
    cv.vline(ox + 59, oy + 62, oy + 71, INK, 1)
    cv.hline(ox + 48, ox + 56, oy + 66, INK, 1)
    # table
    cv.fill_rect(ox + 6, oy + 74, 92, 4, INK)
    cv.vline(ox + 12, oy + 78, oy + 96, INK, 3)
    cv.vline(ox + 89, oy + 78, oy + 96, INK, 3)


def pic_bridge(cv, ox, oy, s):
    """Arched bridge over water, with a red strike burst above it."""
    # burst above the deck
    cv.star(ox + 52, oy + 18, 11, RED, 2)
    # arched deck
    cv.line(ox + 8, oy + 46, ox + 52, oy + 38, INK, 4)
    cv.line(ox + 52, oy + 38, ox + 96, oy + 46, INK, 4)
    # supports down to the water
    for sx in (ox + 26, ox + 52, ox + 78):
        cv.vline(sx, oy + 42, oy + 76, INK, 4)
    # water waves
    for wy in (oy + 84, oy + 93):
        x = ox + 8
        up = True
        while x < ox + 96:
            nx = min(x + 8, ox + 96)
            cv.line(x, wy, nx, wy - 3 if up else wy + 3, INK, 2)
            x = nx
            up = not up


def pic_chart(cv, ox, oy, s):
    """Falling bars with a red down-trend arrow."""
    # axes
    cv.vline(ox + 14, oy + 14, oy + 88, INK, 3)
    cv.hline(ox + 14, ox + 92, oy + 88, INK, 3)
    # descending bars
    for bx, bh in ((ox + 26, 50), (ox + 46, 38), (ox + 66, 26)):
        cv.fill_rect(bx, oy + 86 - bh, 12, bh, INK)
    # red trend line with arrowhead
    cv.line(ox + 22, oy + 24, ox + 46, oy + 40, RED, 3)
    cv.line(ox + 46, oy + 40, ox + 70, oy + 56, RED, 3)
    cv.line(ox + 70, oy + 56, ox + 90, oy + 74, RED, 3)
    cv.fill_poly([(ox + 90, oy + 74), (ox + 78, oy + 72),
                  (ox + 86, oy + 82)], RED)


def pic_tower(cv, ox, oy, s):
    """Tall tower with a missile streak and a red impact burst."""
    # missile streak from upper right
    cv.line(ox + 98, oy + 8, ox + 44, oy + 26, INK, 2)
    cv.fill_poly([(ox + 44, oy + 26), (ox + 54, oy + 20),
                  (ox + 56, oy + 30)], INK)
    # impact burst at the tower's top corner
    cv.star(ox + 36, oy + 26, 11, RED, 2)
    # tower body with lit windows
    cv.fill_rect(ox + 40, oy + 30, 32, 68, INK)
    for r in range(8):
        for c in range(3):
            cv.fill_rect(ox + 45 + c * 9, oy + 36 + r * 8, 4, 5, PAPER)
    # ground line
    cv.hline(ox + 8, ox + 96, oy + 98, INK, 2)


def pic_gamepad(cv, ox, oy):
    """Small game controller for the ALSO strip."""
    cv.fill_rect(ox, oy, 28, 16, PANEL)
    cv.hline(ox, ox + 27, oy, INK, 1)
    cv.hline(ox, ox + 27, oy + 15, INK, 1)
    cv.vline(ox, oy, oy + 15, INK, 1)
    cv.vline(ox + 27, oy, oy + 15, INK, 1)
    # d-pad
    cv.fill_rect(ox + 4, oy + 6, 3, 7, INK)
    cv.fill_rect(ox + 2, oy + 8, 7, 3, INK)
    # buttons
    cv.fill_circle(ox + 20, oy + 6, 2, RED)
    cv.fill_circle(ox + 24, oy + 10, 2, INK)


# -------------------------------------------------------------- layout ----
MARGIN = 36
RIGHT = W - MARGIN  # 988

ROWS = [
    (pic_summit,
     ["TRUMP, XI AND PUTIN SIGN", "PEACE DECLARATION"],
     ["FIRST THREE-WAY SUMMIT IN SHENZHEN",
      "FOUR POINTS: UN, OIL, COURTS, NUCLEAR RISK"]),
    (pic_bridge,
     ["RUSSIAN STRIKES HIT THREE", "KYIV BRIDGES"],
     ["AT LEAST 8 KILLED, 28 INJURED",
      "THREE BRIDGES OVER THE DNIPRO HIT"]),
    (pic_chart,
     ["MARKETS SLIDE AS", "ANTHROPIC DEBUTS"],
     ["S&P 500 DOWN 2%, SIXTH DAY IN A ROW",
      "NIKKEI DOWN ABOUT 5%; ANTHROPIC +17%"]),
    (pic_tower,
     ["HOUTHI MISSILE HITS PIF", "TOWER IN RIYADH"],
     ["WINDOWS BLOWN OUT ON 7-8 FLOORS",
      "NO INJURIES REPORTED IN RIYADH"]),
]


def draw():
    cv = Canvas(W, H, PAPER)

    # page frame
    cv.hline(12, 1011, 12, INK, 2)
    cv.hline(12, 1011, 1010, INK, 2)
    cv.vline(12, 12, 1010, INK, 2)
    cv.vline(1011, 12, 1010, INK, 2)

    # ---- masthead ----
    cv.text_centred(W // 2, 30, "THE WORLD TODAY", 10, INK)
    cv.hline(MARGIN, RIGHT, 110, INK, 3)
    cv.hline(MARGIN, RIGHT, 116, INK, 1)
    cv.text_centred(W // 2, 126, "FRIDAY 20 NOVEMBER 2026", 4, RED)
    cv.hline(MARGIN, RIGHT, 164, INK, 2)

    # ---- lead story ----
    lead_y = 178
    cv.fill_rect(MARGIN, lead_y, 150, 150, PANEL)
    cv.hline(MARGIN, MARGIN + 149, lead_y, INK, 1)
    cv.hline(MARGIN, MARGIN + 149, lead_y + 149, INK, 1)
    cv.vline(MARGIN, lead_y, lead_y + 149, INK, 1)
    cv.vline(MARGIN + 149, lead_y, lead_y + 149, INK, 1)
    pic_scales(cv, MARGIN, lead_y, 150)
    cv.vline(196, lead_y, lead_y + 214, INK, 1)
    tx = 206
    cv.text(tx, lead_y + 4, "THE HAGUE - WORLD COURT", 2, RED)
    for i, line in enumerate(["WORLD COURT FINDS MYANMAR",
                              "GUILTY OF GENOCIDE"]):
        cv.text(tx, lead_y + 28 + i * 45, line, 5, INK)
    for i, line in enumerate(["FIRST TIME THE WORLD COURT HAS HELD",
                              "A STATE RESPONSIBLE FOR GENOCIDE",
                              "RULING 9-6; REPARATIONS ORDERED"]):
        cv.text(tx, lead_y + 122 + i * 27, line, 3, GRAY)

    # ---- divider + section label ----
    cv.hline(MARGIN, RIGHT, 404, INK, 3)
    cv.hline(MARGIN, RIGHT, 409, INK, 1)
    cv.text_centred(W // 2, 418, "MORE TOP STORIES", 2, RED)

    # ---- four story rows ----
    row_y = 440
    for idx, (pic, head, facts) in enumerate(ROWS):
        cv.fill_rect(MARGIN, row_y + 6, 104, 104, PANEL)
        cv.hline(MARGIN, MARGIN + 103, row_y + 6, INK, 1)
        cv.hline(MARGIN, MARGIN + 103, row_y + 109, INK, 1)
        cv.vline(MARGIN, row_y + 6, row_y + 109, INK, 1)
        cv.vline(MARGIN + 103, row_y + 6, row_y + 109, INK, 1)
        pic(cv, MARGIN, row_y + 6, 104)
        cv.vline(152, row_y + 6, row_y + 110, INK, 1)
        for i, line in enumerate(head):
            cv.text(168, row_y + 4 + i * 34, line, 4, INK)
        for i, line in enumerate(facts):
            cv.text(168, row_y + 74 + i * 24, line, 3, GRAY)
        if idx < len(ROWS) - 1:
            cv.hline(MARGIN, RIGHT, row_y + 119, INK, 1)
        row_y += 122

    # ---- ALSO strip ----
    pic_gamepad(cv, MARGIN, 932)
    x = cv.text(72, 936, "ALSO: ", 2, RED)
    cv.text(x, 936, "GTA 6 - EST. $2.36 BILLION IN FIRST-DAY SALES "
                    "(SENSOR TOWER)", 2, INK)

    # ---- footer ----
    cv.hline(MARGIN, RIGHT, 962, INK, 1)
    cv.text_centred(W // 2, 974,
                    "SOURCES: JUST SECURITY EARLY EDITION - ONETURN - "
                    "OPENCHRONICLE - 20 NOV 2026", 2, GRAY)
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
