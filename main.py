#!/usr/bin/env python3
"""news-image-20261119: draw the world news of Thursday 19 November 2026
as a one-page newspaper front page (1024x1024 PNG).

Pure Python 3 standard library only: no network, no fonts on disk, no
randomness, no clock. The image is drawn from a small embedded 5x7 bitmap
font and flat vector shapes, so two runs write byte-identical output.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""

import os
import struct
import zlib
from binascii import crc32

# ---------------------------------------------------------------- font
# 5x7 bitmap font. Each glyph is 7 rows of 5 pixels, '#' = ink, '.' = blank.
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
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
    '•': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}

# ---------------------------------------------------------------- canvas
W, H = 1024, 1024
PAPER = (246, 241, 231)
NAVY = (22, 35, 63)
RED = (192, 57, 43)
AMBER = (233, 163, 25)
INK = (26, 26, 26)
WHITE = (255, 255, 255)
GREY = (216, 210, 196)
GREEN = (39, 120, 70)
BLUE = (41, 98, 168)


class Canvas:
    def __init__(self, w=W, h=H, bg=PAPER):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            i = (yy * self.w + x) * 3
            self.px[i:i + w * 3] = bytes(c) * w

    def frame(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                for b in range(t):
                    self.set(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, fill=True):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            if fill:
                self.rect(cx - dx, yy, dx * 2 + 1, 1, c)
            else:
                self.set(cx - dx, yy, c)
                self.set(cx + dx, yy, c)

    def poly(self, pts, c):
        # scanline fill of a simple polygon
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, max(1, int(xs[i + 1]) - int(xs[i])), 1, c)

    # -- text -------------------------------------------------------------
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c):
        for ci, ch in enumerate(s):
            # the font holds capitals only: lowercase renders as capitals
            g = FONT.get(ch.upper() if 'a' <= ch <= 'z' else ch, FONT[' '])
            ox = x + ci * 6 * scale
            for row in range(7):
                bits = g[row]
                for col in range(5):
                    if bits[col] == '1':
                        self.rect(ox + col * scale, y + row * scale,
                                  scale, scale, c)
        return self.text_w(s, scale)

    def text_c(self, cx, y, s, scale, c):
        self.text(cx - self.text_w(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, maxw):
        words, lines, cur = s.split(' '), [], ''
        for w in words:
            t = (cur + ' ' + w).strip()
            if self.text_w(t, scale) <= maxw or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines


def png_bytes(cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        return out + struct.pack('>I', crc32(tag + data) & 0xffffffff)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))

# ---------------------------------------------------------------- icons
# Small flat pictograms, drawn from rectangles, circles, lines and polygons.

def icon_scales(cv, x, y, s=1):
    # scales of justice (ICJ / The Hague)
    cv.line(x + 28 * s, y + 4 * s, x + 28 * s, y + 46 * s, NAVY, 3 * s)
    cv.line(x + 6 * s, y + 10 * s, x + 50 * s, y + 10 * s, NAVY, 3 * s)
    cv.line(x + 6 * s, y + 10 * s, x + 6 * s, y + 24 * s, NAVY, 2 * s)
    cv.line(x + 50 * s, y + 10 * s, x + 50 * s, y + 24 * s, NAVY, 2 * s)
    cv.poly([(x + 0 * s, y + 24 * s), (x + 12 * s, y + 24 * s),
             (x + 6 * s, y + 34 * s)], NAVY)
    cv.poly([(x + 44 * s, y + 24 * s), (x + 56 * s, y + 24 * s),
             (x + 50 * s, y + 34 * s)], NAVY)
    cv.rect(x + 18 * s, y + 46 * s, 20 * s, 4 * s, NAVY)


def icon_bridge(cv, x, y, s=1):
    # suspension bridge over water (Crimea Bridge / Ukraine)
    cv.rect(x + 6 * s, y + 6 * s, 5 * s, 30 * s, NAVY)
    cv.rect(x + 45 * s, y + 6 * s, 5 * s, 30 * s, NAVY)
    cv.line(x + 8 * s, y + 6 * s, x + 28 * s, y + 24 * s, NAVY, 2 * s)
    cv.line(x + 48 * s, y + 6 * s, x + 28 * s, y + 24 * s, NAVY, 2 * s)
    cv.rect(x + 0 * s, y + 24 * s, 56 * s, 4 * s, NAVY)
    cv.line(x + 2 * s, y + 40 * s, x + 20 * s, y + 40 * s, BLUE, 2 * s)
    cv.line(x + 24 * s, y + 46 * s, x + 44 * s, y + 46 * s, BLUE, 2 * s)
    cv.line(x + 36 * s, y + 40 * s, x + 54 * s, y + 40 * s, BLUE, 2 * s)


def icon_flame(cv, x, y, s=1):
    # flame (Iran strikes / Bangladesh unrest)
    cv.poly([(x + 28 * s, y + 2 * s), (x + 40 * s, y + 18 * s),
             (x + 48 * s, y + 34 * s), (x + 38 * s, y + 50 * s),
             (x + 18 * s, y + 50 * s), (x + 8 * s, y + 34 * s),
             (x + 16 * s, y + 18 * s)], RED)
    cv.poly([(x + 28 * s, y + 22 * s), (x + 35 * s, y + 32 * s),
             (x + 33 * s, y + 44 * s), (x + 23 * s, y + 44 * s),
             (x + 21 * s, y + 32 * s)], AMBER)


def icon_globe(cv, x, y, s=1):
    # globe with a leaf (COP31 climate talks)
    cv.circle(x + 26 * s, y + 26 * s, 22 * s, NAVY, fill=False)
    cv.circle(x + 26 * s, y + 26 * s, 22 * s, NAVY, fill=False)
    cv.line(x + 26 * s, y + 4 * s, x + 26 * s, y + 48 * s, NAVY, 2 * s)
    cv.line(x + 4 * s, y + 26 * s, x + 48 * s, y + 26 * s, NAVY, 2 * s)
    cv.poly([(x + 34 * s, y + 34 * s), (x + 52 * s, y + 30 * s),
             (x + 54 * s, y + 44 * s), (x + 38 * s, y + 48 * s)], GREEN)


def icon_dome(cv, x, y, s=1):
    # capitol dome (US House / Jeffries)
    cv.poly([(x + 10 * s, y + 22 * s), (x + 28 * s, y + 4 * s),
             (x + 46 * s, y + 22 * s)], NAVY)
    cv.rect(x + 26 * s, y + 0 * s, 4 * s, 6 * s, NAVY)
    cv.rect(x + 6 * s, y + 22 * s, 44 * s, 4 * s, NAVY)
    for cx in (10, 20, 30, 40):
        cv.rect(x + cx * s, y + 26 * s, 4 * s, 18 * s, NAVY)
    cv.rect(x + 4 * s, y + 44 * s, 48 * s, 4 * s, NAVY)


def icon_flags(cv, x, y, w, h):
    # three flags side by side: USA, China, Russia (Shenzhen summit)
    fw = w // 3
    # USA: red/white stripes + blue canton
    for i in range(7):
        cv.rect(x, y + i * h // 7, fw, h // 7 + 1,
                RED if i % 2 == 0 else WHITE)
    cv.rect(x, y, fw * 2 // 5, h * 4 // 7, NAVY)
    for r in range(3):
        for c in range(3):
            cv.circle(x + 6 + c * 9, y + 8 + r * 11, 2, WHITE)
    # China: red field, yellow stars
    cv.rect(x + fw, y, fw, h, RED)
    cv.circle(x + fw + 18, y + 16, 7, AMBER)
    for sx, sy in ((52, 10), (62, 18), (62, 30), (52, 38)):
        cv.circle(x + fw + sx, y + sy, 3, AMBER)
    # Russia: white / blue / red horizontal
    cv.rect(x + 2 * fw, y, fw, h // 3 + 1, WHITE)
    cv.rect(x + 2 * fw, y + h // 3, fw, h // 3 + 1, BLUE)
    cv.rect(x + 2 * fw, y + 2 * h // 3, fw, h // 3 + 1, RED)
    # outlines so the white stripe reads against the white panel
    for fx in (x, x + fw, x + 2 * fw):
        cv.frame(fx, y, fw, h, NAVY, 2)


# ---------------------------------------------------------------- mini icons
# 24x24 pictograms for region headers (rects, circles and polygons only).

def mini_sun(cv, x, y):
    cv.circle(x + 12, y + 12, 6, AMBER)
    cv.rect(x + 11, y + 1, 2, 4, AMBER)
    cv.rect(x + 11, y + 19, 2, 4, AMBER)
    cv.rect(x + 1, y + 11, 4, 2, AMBER)
    cv.rect(x + 19, y + 11, 4, 2, AMBER)


def mini_flame(cv, x, y):
    cv.poly([(x + 12, y + 1), (x + 18, y + 10), (x + 21, y + 18),
             (x + 16, y + 23), (x + 8, y + 23), (x + 3, y + 18),
             (x + 6, y + 10)], RED)
    cv.poly([(x + 12, y + 11), (x + 16, y + 16), (x + 14, y + 21),
             (x + 10, y + 21), (x + 8, y + 16)], AMBER)


def mini_bridge(cv, x, y):
    cv.rect(x + 3, y + 3, 3, 15, NAVY)
    cv.rect(x + 18, y + 3, 3, 15, NAVY)
    cv.rect(x + 1, y + 12, 22, 3, NAVY)
    cv.rect(x + 1, y + 19, 8, 2, BLUE)
    cv.rect(x + 13, y + 19, 10, 2, BLUE)


def mini_dome(cv, x, y):
    cv.poly([(x + 4, y + 12), (x + 12, y + 3), (x + 20, y + 12)], NAVY)
    cv.rect(x + 11, y + 1, 2, 3, NAVY)
    cv.rect(x + 3, y + 12, 18, 2, NAVY)
    for cx in (5, 10, 15):
        cv.rect(x + cx, y + 14, 2, 7, NAVY)
    cv.rect(x + 2, y + 21, 20, 2, NAVY)


def mini_globe(cv, x, y):
    cv.circle(x + 12, y + 12, 10, NAVY, fill=False)
    cv.rect(x + 11, y + 2, 2, 20, NAVY)
    cv.rect(x + 2, y + 11, 20, 2, NAVY)
    cv.poly([(x + 15, y + 15), (x + 22, y + 13),
             (x + 23, y + 20), (x + 17, y + 22)], GREEN)


def mini_rocket(cv, x, y):
    cv.poly([(x + 12, y + 1), (x + 18, y + 12), (x + 6, y + 12)], NAVY)
    cv.rect(x + 9, y + 12, 6, 6, NAVY)
    cv.poly([(x + 12, y + 18), (x + 15, y + 23), (x + 9, y + 23)], RED)


def mini_chart(cv, x, y):
    cv.rect(x + 3, y + 13, 4, 10, NAVY)
    cv.rect(x + 10, y + 8, 4, 15, RED)
    cv.rect(x + 17, y + 3, 4, 20, GREEN)


# ---------------------------------------------------------------- stories
# 40 stories, every one dated 19 November 2026 (it happened, or was first
# reported, that day), in 7 regions. Story 1 is the lead hero; stories 2-40
# run as numbered briefs below it.
GROUPS = [
    ("ASIA-PACIFIC", mini_sun, [
        "IAEA: N. Korea grew uranium enrichment",
        "Lee renews dialogue call to Pyongyang",
        "Bangladesh turmoil: Yunus home torched",
        "Cyclone Akvan nears India; 50,000 flee",
        "S. Korea tightens exam AI rules",
        "Shenzhou-24: first Pakistani astronaut",
    ]),
    ("MIDDLE EAST", mini_flame, [
        "Iran hits Gulf states after Qeshm",
        "Kuwait repels first Iranian attack",
        "Trump: Iran exploring chemical arms",
        "Hormuz crisis tops energy threats",
        "NSA outage hits Mideast intel links",
        "Iran turns to China and Russia for cover",
    ]),
    ("EUROPE", mini_bridge, [
        "Ukraine hits Crimea Bridge a third time",
        "EU proposes EUR 45bn loan to Ukraine",
        "EU approves Indonesia trade pact",
        "ICJ rules on Rohingya genocide case",
        "COP31 deadlock persists in Antalya",
        "Chelsea beat PSG 1-0 in Champions League",
    ]),
    ("AMERICAS", mini_dome, [
        "Jeffries set to be first Black Speaker",
        "US loses measles elimination status",
        "Waymo pulls driverless taxis off freeways",
        "Trump seals Greenland military deal",
        "US, Venezuela sign military pact",
        "Van Gogh sells for $190.4M, a record",
    ]),
    ("AFRICA", mini_globe, [
        "Ebola vaccines to be trialled in DR Congo",
        "Uganda landslide victims turn to UN",
        "Somalia crisis deepens amid reforms",
        "Kenya drought deepens milk shortage",
        "UN: many women lack sexual consent rights",
    ]),
    ("SCIENCE & SPACE", mini_rocket, [
        "Voyager 1 reaches one light-day from Earth",
        "Webb confirms rare star merger",
        "Antarctic blue whales up tenfold",
        "COP31 AI pledge spurned by US tech",
        "Alzheimer's studies show advance",
    ]),
    ("MARKETS, TECH & SPORT", mini_chart, [
        "Anthropic IPO priced at $83 a share",
        "AI worries hit stocks; Hang Seng falls 2.78%",
        "Brent crude holds near $89 as Hormuz bites",
        "GTA VI goes on sale after 13-year wait",
        "England win ODI series, Duckett 133",
    ]),
]

# columns: (group indexes, x) — three columns across the page
COLUMNS = [
    ([0, 1], 24),
    ([2, 3], 354),
    ([4, 5, 6], 684),
]


# ---------------------------------------------------------------- layout
def draw():
    cv = Canvas()
    # masthead
    cv.rect(24, 20, 976, 88, NAVY)
    cv.text_c(512, 32, "THE WORLD IN ONE DAY", 5, WHITE)
    cv.text_c(512, 76, "THURSDAY, 19 NOVEMBER 2026", 3, AMBER)
    cv.rect(24, 108, 976, 5, RED)
    cv.text_c(512, 120, "40 STORIES  •  7 REGIONS  •  EVERY STORY DATED "
                         "19 NOVEMBER 2026", 2, RED)

    # lead hero: Shenzhen summit (story 1)
    cv.rect(24, 144, 976, 128, WHITE)
    cv.frame(24, 144, 976, 128, NAVY, 3)
    icon_flags(cv, 40, 158, 192, 100)
    cv.text(252, 158, "SHENZHEN  •  APEC SUMMIT", 2, RED)
    cv.text(252, 184, "TRUMP, XI AND PUTIN", 4, INK)
    cv.text(252, 216, "MEET IN SHENZHEN", 4, INK)
    cv.text(252, 250, "First three-way summit: nuclear arms, Ukraine, "
                      "Iran", 2, INK)

    # numbered briefs in three columns (stories 2-40); each column's
    # frame hugs its own content height
    n = 2
    for gidxs, cx in COLUMNS:
        y = 296
        for gi in gidxs:
            name, icon, stories = GROUPS[gi]
            icon(cv, cx + 16, y)
            cv.text(cx + 48, y + 5, name, 2, RED)
            y += 30
            for s in stories:
                lines = cv.wrap(s, 2, 262)
                cv.text(cx + 16, y, "%02d" % n, 2, RED)
                for i, ln in enumerate(lines):
                    cv.text(cx + 52, y + i * 16, ln, 2, INK)
                y += len(lines) * 16 + 4
                n += 1
            y += 2
        cv.frame(cx, 284, 314, y - 284 + 10, GREY, 1)

    # footer: date-check
    cv.rect(24, 962, 976, 34, NAVY)
    cv.text_c(512, 972, "DATE-CHECK: EVERY STORY HAPPENED OR WAS FIRST "
                        "REPORTED ON 19 NOV 2026", 2, WHITE)
    return cv


def main():
    outdir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(draw())
    with open(os.path.join(outdir, 'entry.png'), 'wb') as f:
        f.write(data)


if __name__ == '__main__':
    main()
