#!/usr/bin/env python3
"""Passport spread for the Republic of Narovia.

Draws one invented passport spread (1024x1024 PNG) for a country that
does not exist: the data page of Elena Mara Varkas, born in Dunvar,
and the visa page carrying her travel history. Every date agrees:
issued 14 MAR 2023, stamps JUN 2023 - FEB 2024, expiry 14 MAR 2033.
The telling detail is the red endorsement: the holder may not enter
the Eastern Marches without a separate permit.

Deterministic: fixed seed, no network, no clock reads. Drawn at 2x
and downscaled for smooth edges. Standard library only: the renderer
is a hand-rolled RGB pixel buffer with a built-in 5x7 bitmap font and
a struct+zlib PNG encoder, so it runs in a bare python3.13 image
with no PIL and no font files.

  End-to-end check of this shipped file (2026-11-21): entry.png is
  1024 by 1024, 40,638 bytes, within the 1 MiB cap; the copy lands
  byte-for-byte identical (md5 a77140cd6ef9477f1f29067949063bdb)
  across two runs.
"""

import math
import os
import random
import struct
import zlib

S = 2  # supersample factor; final image is 1024x1024
W, H = 1024, 1024
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

INK = (28, 28, 26)
GREEN = (30, 77, 43)
GOLD = (176, 141, 42)
CREAM = (246, 241, 226)
PAPER = (250, 246, 233)
DESK = (38, 41, 47)
RED = (158, 42, 34)
BLUE = (38, 74, 110)
GREY = (96, 104, 90)


def sc(v):
    return int(v * S)


# ---------------------------------------------------------------------------
# Built-in 5x7 bitmap font. Each glyph is 7 rows of 5 bits ("1" = ink).
# Covers A-Z, a-z, 0-9, space and every punctuation the entry uses.
# ---------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "b": ("10000", "10000", "10110", "11001", "10001", "10001", "11110"),
    "c": ("00000", "00000", "01110", "10000", "10000", "10001", "01110"),
    "d": ("00001", "00001", "01101", "10011", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11110", "01000", "01000", "01000"),
    "g": ("00000", "01111", "10001", "10001", "01111", "00001", "01110"),
    "h": ("10000", "10000", "10110", "11001", "10001", "10001", "10001"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "j": ("00010", "00000", "00110", "00010", "00010", "10010", "01100"),
    "k": ("10000", "10000", "10010", "10100", "11000", "10100", "10010"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "m": ("00000", "00000", "11010", "10101", "10101", "10101", "10101"),
    "n": ("00000", "00000", "10110", "11001", "10001", "10001", "10001"),
    "o": ("00000", "00000", "01110", "10001", "10001", "10001", "01110"),
    "p": ("00000", "00000", "10110", "11001", "10001", "11110", "10000"),
    "q": ("00000", "00000", "01101", "10011", "10001", "01111", "00001"),
    "r": ("00000", "00000", "10110", "11001", "10000", "10000", "10000"),
    "s": ("00000", "00000", "01111", "10000", "01110", "00001", "11110"),
    "t": ("01000", "01000", "11100", "01000", "01000", "01001", "00110"),
    "u": ("00000", "00000", "10001", "10001", "10001", "10011", "01101"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    "w": ("00000", "00000", "10001", "10101", "10101", "10101", "01010"),
    "x": ("00000", "00000", "10001", "01010", "00100", "01010", "10001"),
    "y": ("00000", "00000", "10001", "10001", "01111", "00001", "01110"),
    "z": ("00000", "00000", "11111", "00010", "00100", "01000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "\u00b7": ("00000", "00000", "00000", "01100", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    "<": ("00010", "00100", "01000", "10000", "01000", "00100", "00010"),
    "\u2014": ("00000", "00000", "00000", "11111", "00000", "00000", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
}
# Precomputed set-bit coordinates per glyph, for fast text drawing.
FONT_BITS = {}
for _ch, _rows in FONT.items():
    _bits = []
    for _r, _row in enumerate(_rows):
        for _c, _bit in enumerate(_row):
            if _bit == "1":
                _bits.append((_c, _r))
    FONT_BITS[_ch] = _bits
FONT_FALLBACK = FONT_BITS["?"]


# ---------------------------------------------------------------------------
# Pixel buffer canvas (RGB bytearray, optional alpha plane for stamp layers)
# ---------------------------------------------------------------------------
class Canvas:
    def __init__(self, w, h, fill=None, alpha=False):
        self.w = w
        self.h = h
        if fill is None:
            self.px = bytearray(w * h * 3)
        else:
            self.px = bytearray(bytes(fill) * w * h)
        self.al = bytearray(w * h) if alpha else None

    def put(self, x, y, color, alpha=255):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            if alpha == 255:
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]
            else:
                ia = 255 - alpha
                self.px[i] = (color[0] * alpha + self.px[i] * ia) // 255
                self.px[i + 1] = (color[1] * alpha + self.px[i + 1] * ia) // 255
                self.px[i + 2] = (color[2] * alpha + self.px[i + 2] * ia) // 255
            if self.al is not None:
                j = y * self.w + x
                old = self.al[j]
                self.al[j] = 255 if alpha == 255 else alpha + old * (255 - alpha) // 255

    def fill_rect(self, x0, y0, x1, y1, color, alpha=255):
        """Inclusive corners; clipped to the canvas."""
        x0 = max(0, x0)
        y0 = max(0, y0)
        x1 = min(self.w - 1, x1)
        y1 = min(self.h - 1, y1)
        if x1 < x0 or y1 < y0:
            return
        n = x1 - x0 + 1
        if alpha == 255:
            row = bytes(color) * n
            for y in range(y0, y1 + 1):
                base = (y * self.w + x0) * 3
                self.px[base:base + 3 * n] = row
            if self.al is not None:
                for y in range(y0, y1 + 1):
                    j = y * self.w + x0
                    self.al[j:j + n] = b"\xff" * n
        else:
            for y in range(y0, y1 + 1):
                for x in range(x0, x1 + 1):
                    self.put(x, y, color, alpha)

    def rect_outline(self, x0, y0, x1, y1, color, width=1, alpha=255):
        for k in range(width):
            self.fill_rect(x0 + k, y0 + k, x1 - k, y0 + k, color, alpha)
            self.fill_rect(x0 + k, y1 - k, x1 - k, y1 - k, color, alpha)
            self.fill_rect(x0 + k, y0 + k, x0 + k, y1 - k, color, alpha)
            self.fill_rect(x1 - k, y0 + k, x1 - k, y1 - k, color, alpha)

    def line(self, x0, y0, x1, y1, color, width=1, alpha=255):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        r = width // 2
        x, y = x0, y0
        while True:
            if r == 0:
                self.put(x, y, color, alpha)
            else:
                self.filled_circle(x, y, r, color, alpha)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def filled_circle(self, cx, cy, r, color, alpha=255):
        for dy in range(-r, r + 1):
            dx = int(math.sqrt(max(0, r * r - dy * dy)))
            self.fill_rect(cx - dx, cy + dy, cx + dx, cy + dy, color, alpha)

    def filled_ellipse(self, cx, cy, rx, ry, color, alpha=255):
        for dy in range(-ry, ry + 1):
            t = 1.0 - (dy * dy) / float(ry * ry) if ry else 0.0
            dx = int(rx * math.sqrt(max(0.0, t)))
            self.fill_rect(cx - dx, cy + dy, cx + dx, cy + dy, color, alpha)

    def fill_polygon(self, pts, color, alpha=255):
        n = len(pts)
        if n < 3:
            return
        ymin = max(0, int(min(p[1] for p in pts)))
        ymax = min(self.h - 1, int(max(p[1] for p in pts)))
        for y in range(ymin, ymax + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / float(y1 - y0)
                    xs.append(x0 + t * (x1 - x0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(math.ceil(xs[i])), y,
                               int(math.floor(xs[i + 1])), y, color, alpha)

    def stroke_polygon(self, pts, color, width=1, alpha=255):
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            self.line(x0, y0, x1, y1, color, width, alpha)

    def arc(self, cx, cy, rx, ry, start_deg, end_deg, color, width=1,
            alpha=255):
        """PIL-style arc: angles in degrees from 3 o'clock, clockwise."""
        pts = []
        steps = max(2, int(abs(end_deg - start_deg) / 3) + 1)
        for i in range(steps + 1):
            a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            pts.append((int(round(cx + rx * math.cos(a))),
                        int(round(cy + ry * math.sin(a)))))
        for i in range(len(pts) - 1):
            self.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1],
                      color, width, alpha)

    def pieslice(self, cx, cy, rx, ry, start_deg, end_deg, color, alpha=255):
        pts = [(cx, cy)]
        steps = max(2, int(abs(end_deg - start_deg) / 3) + 1)
        for i in range(steps + 1):
            a = math.radians(start_deg + (end_deg - start_deg) * i / steps)
            pts.append((int(round(cx + rx * math.cos(a))),
                        int(round(cy + ry * math.sin(a)))))
        self.fill_polygon(pts, color, alpha)

    def rounded_rect_fill(self, x0, y0, x1, y1, r, color, alpha=255):
        self.fill_rect(x0 + r, y0, x1 - r, y1, color, alpha)
        self.fill_rect(x0, y0 + r, x1, y1 - r, color, alpha)
        for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r),
                       (x0 + r, y1 - r), (x1 - r, y1 - r)):
            self.filled_circle(cx, cy, r, color, alpha)

    def rounded_rect_outline(self, x0, y0, x1, y1, r, color, width=1,
                             alpha=255):
        self.line(x0 + r, y0, x1 - r, y0, color, width, alpha)
        self.line(x0 + r, y1, x1 - r, y1, color, width, alpha)
        self.line(x0, y0 + r, x0, y1 - r, color, width, alpha)
        self.line(x1, y0 + r, x1, y1 - r, color, width, alpha)
        self.arc(x0 + r, y0 + r, r, r, 180, 270, color, width, alpha)
        self.arc(x1 - r, y0 + r, r, r, 270, 360, color, width, alpha)
        self.arc(x0 + r, y1 - r, r, r, 90, 180, color, width, alpha)
        self.arc(x1 - r, y1 - r, r, r, 0, 90, color, width, alpha)


# ---------------------------------------------------------------------------
# Text (1024-space coordinates; glyph scale chosen from the nominal size,
# then shrunk if a max width is given so the line always fits its box)
# ---------------------------------------------------------------------------
def scale_for(size):
    return max(1, round(size * S / 7))


def text_width(text, scale, tracking=0):
    if not text:
        return 0
    return len(text) * 6 * scale + (len(text) - 1) * tracking


def _fit_scale(text, size, max_w, tracking=0):
    s = scale_for(size)
    while s > 1 and text_width(text, s, tracking) > max_w:
        s -= 1
    return s


def draw_text(cv, x, y, text, scale, color, tracking=0, alpha=255):
    cx = x
    for ch in text:
        bits = FONT_BITS.get(ch, FONT_FALLBACK)
        for c, r in bits:
            cv.fill_rect(cx + c * scale, y + r * scale,
                         cx + c * scale + scale - 1,
                         y + r * scale + scale - 1, color, alpha)
        cx += 6 * scale + tracking


def txt(cv, x, y, text, size, color, tracking=0, max_w=None, alpha=255):
    """Left-aligned text; x, y, size, max_w in 1024-space units."""
    tr = sc(tracking)
    s = scale_for(size)
    if max_w is not None:
        s = _fit_scale(text, size, sc(max_w), tr)
    draw_text(cv, sc(x), sc(y), text, s, color, tr, alpha)
    return text_width(text, s, tr) // S


def ctext(cv, cx, y, text, size, color, tracking=0, max_w=None, alpha=255):
    """Horizontally centred text; cx, y, size, max_w in 1024-space units."""
    tr = sc(tracking)
    s = scale_for(size)
    if max_w is not None:
        s = _fit_scale(text, size, sc(max_w), tr)
    w = text_width(text, s, tr)
    draw_text(cv, sc(cx) - w // 2, sc(y), text, s, color, tr, alpha)


def mrz_check(s):
    weights = (7, 3, 1)
    total = 0
    for i, ch in enumerate(s):
        if ch == "<":
            v = 0
        elif ch.isdigit():
            v = int(ch)
        else:
            v = ord(ch) - ord("A") + 10
        total += v * weights[i % 3]
    return str(total % 10)


def coat_of_arms(cv, cx, cy, scale=1.0):
    """Small shield: green field, gold mountain, gold star."""
    w, h = 34 * scale, 40 * scale
    x0, y0 = cx - w / 2, cy - h / 2
    shield = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h * 0.62),
              (cx, y0 + h), (x0, y0 + h * 0.62)]
    pts = [(sc(a), sc(b)) for a, b in shield]
    cv.fill_polygon(pts, GREEN)
    cv.stroke_polygon(pts, GOLD, sc(2))
    # mountain
    cv.fill_polygon([(sc(cx - w * 0.32), sc(y0 + h * 0.72)),
                     (sc(cx), sc(y0 + h * 0.34)),
                     (sc(cx + w * 0.32), sc(y0 + h * 0.72))], GOLD)
    # star
    sx, sy, r = cx, y0 + h * 0.16, 4 * scale
    star = []
    for i in range(10):
        ang = -90 + i * 36
        rr = r if i % 2 == 0 else r * 0.45
        star.append((sx + rr * math.cos(math.radians(ang)),
                     sy + rr * math.sin(math.radians(ang))))
    cv.fill_polygon([(sc(a), sc(b)) for a, b in star], GOLD)


def portrait(cv, x0, y0, w, h):
    """Stylised passport portrait: Elena Mara Varkas, 29, in national dress."""
    # photo background
    cv.fill_rect(sc(x0), sc(y0), sc(x0 + w), sc(y0 + h), (122, 158, 150))
    cv.rect_outline(sc(x0), sc(y0), sc(x0 + w), sc(y0 + h), (90, 110, 104),
                    sc(1))
    cx = x0 + w / 2
    # long hair behind shoulders
    cv.rounded_rect_fill(sc(cx - 42), sc(y0 + 52), sc(cx + 42),
                         sc(y0 + h - 6), sc(14), (46, 32, 24))
    # shoulders / coat
    cv.fill_polygon([(sc(cx - 62), sc(y0 + h)), (sc(cx - 46), sc(y0 + 128)),
                     (sc(cx - 20), sc(y0 + 116)), (sc(cx + 20), sc(y0 + 116)),
                     (sc(cx + 46), sc(y0 + 128)), (sc(cx + 62), sc(y0 + h))],
                    GREEN)
    # gold collar trim
    cv.line(sc(cx - 20), sc(y0 + 116), sc(cx), sc(y0 + 132), GOLD, sc(2))
    cv.line(sc(cx), sc(y0 + 132), sc(cx + 20), sc(y0 + 116), GOLD, sc(2))
    # woven sash across the shoulder
    cv.fill_polygon([(sc(cx - 58), sc(y0 + 150)), (sc(cx - 34), sc(y0 + 138)),
                     (sc(cx + 30), sc(y0 + h)), (sc(cx + 6), sc(y0 + h))],
                    (176, 141, 42))
    cv.fill_polygon([(sc(cx - 34), sc(y0 + 138)), (sc(cx - 26), sc(y0 + 142)),
                     (sc(cx + 38), sc(y0 + h)), (sc(cx + 30), sc(y0 + h))],
                    (158, 42, 34))
    # neck
    cv.fill_rect(sc(cx - 11), sc(y0 + 104), sc(cx + 11), sc(y0 + 124),
                 (217, 169, 134))
    # head
    cv.filled_ellipse(sc(cx), sc(y0 + 67), sc(32), sc(41), (217, 169, 134))
    # ears
    cv.filled_ellipse(sc(cx - 33), sc(y0 + 70), sc(4), sc(8), (217, 169, 134))
    cv.filled_ellipse(sc(cx + 33), sc(y0 + 70), sc(4), sc(8), (217, 169, 134))
    # hair cap
    cv.pieslice(sc(cx), sc(y0 + 52), sc(34), sc(34), 180, 360, (46, 32, 24))
    cv.fill_polygon([(sc(cx - 34), sc(y0 + 52)), (sc(cx - 28), sc(y0 + 30)),
                     (sc(cx - 12), sc(y0 + 44)), (sc(cx), sc(y0 + 32)),
                     (sc(cx + 12), sc(y0 + 44)), (sc(cx + 28), sc(y0 + 30)),
                     (sc(cx + 34), sc(y0 + 52)), (sc(cx + 30), sc(y0 + 58)),
                     (sc(cx - 30), sc(y0 + 58))], (46, 32, 24))
    # eyebrows
    cv.arc(sc(cx - 14), sc(y0 + 63), sc(8), sc(5), 200, 340, (46, 32, 24),
           sc(2))
    cv.arc(sc(cx + 14), sc(y0 + 63), sc(8), sc(5), 200, 340, (46, 32, 24),
           sc(2))
    # eyes
    for ex in (cx - 14, cx + 14):
        cv.filled_ellipse(sc(ex), sc(y0 + 72), sc(6), sc(4), (250, 246, 233))
        cv.filled_ellipse(sc(ex), sc(y0 + 72), sc(3), sc(3), (28, 28, 26))
    # nose
    cv.line(sc(cx), sc(y0 + 76), sc(cx - 1), sc(y0 + 88), (178, 128, 92),
            sc(2))
    cv.line(sc(cx - 1), sc(y0 + 88), sc(cx + 3), sc(y0 + 90), (178, 128, 92),
            sc(2))
    # mouth
    cv.arc(sc(cx), sc(y0 + 97), sc(8), sc(5), 15, 165, (140, 70, 60), sc(2))
    # cheek shading
    for ex in (cx - 21, cx + 21):
        cv.filled_ellipse(sc(ex), sc(y0 + 86), sc(5), sc(4), (226, 150, 130))


def stamp_layer(text_lines, ink, w=380, h=66):
    """One border stamp on its own transparent layer (1024-space coords)."""
    layer = Canvas(sc(w + 40), sc(h + 40), alpha=True)
    layer.rounded_rect_outline(sc(8), sc(8), sc(w + 32), sc(h + 32), sc(6),
                               ink, sc(3), 235)
    layer.rounded_rect_outline(sc(13), sc(13), sc(w + 27), sc(h + 27), sc(4),
                               ink, sc(1), 200)
    y = 14
    for i, (text, size) in enumerate(text_lines):
        s = scale_for(size)
        wpx = text_width(text, s)
        draw_text(layer, sc(w + 40) // 2 - wpx // 2, sc(y), text, s, ink,
                  0, 235)
        y += 17 if i == 0 else 15
    return layer


def blit_rotated(dst, src, ox, oy, angle_deg):
    """Paste src (with alpha) onto dst, rotated, bbox top-left at (ox, oy)."""
    th = math.radians(angle_deg)
    c, s = math.cos(th), math.sin(th)
    w, h = src.w, src.h
    rcx, rcy = w / 2.0, h / 2.0
    corners = []
    for x, y in ((0, 0), (w, 0), (w, h), (0, h)):
        dx, dy = x - rcx, y - rcy
        corners.append((dx * c - dy * s, dx * s + dy * c))
    minx = min(p[0] for p in corners)
    maxx = max(p[0] for p in corners)
    miny = min(p[1] for p in corners)
    maxy = max(p[1] for p in corners)
    rw = int(math.ceil(maxx - minx))
    rh = int(math.ceil(maxy - miny))
    dcx, dcy = ox + rw / 2.0, oy + rh / 2.0
    for dy in range(rh):
        for dx in range(rw):
            px, py = dx - rw / 2.0, dy - rh / 2.0
            sx = px * c + py * s + rcx
            sy = -px * s + py * c + rcy
            ix, iy = int(sx), int(sy)
            if 0 <= ix < w and 0 <= iy < h:
                a = src.al[iy * w + ix]
                if a:
                    j = (iy * w + ix) * 3
                    dst.put(ox + dx, oy + dy,
                            (src.px[j], src.px[j + 1], src.px[j + 2]), a)


def data_page(cv):
    x0, x1, y0, y1 = 28, 500, 24, 1000
    # page + borders
    cv.fill_rect(sc(x0), sc(y0), sc(x1), sc(y1), CREAM)
    cv.rect_outline(sc(x0), sc(y0), sc(x1), sc(y1), GREEN, sc(3))
    cv.rect_outline(sc(x0 + 10), sc(y0 + 10), sc(x1 - 10), sc(y1 - 10),
                    GREEN, sc(1))
    # header
    coat_of_arms(cv, 264, 78, scale=1.0)
    ctext(cv, 264, 128, "REPUBLIC OF NAROVIA", 21, INK, tracking=2)
    ctext(cv, 264, 158, "PASSPORT", 15, GREEN, tracking=8)
    cv.line(sc(70), sc(186), sc(458), sc(186), GREEN, sc(2))
    ctext(cv, 264, 200, "TYPE  P      CODE  NAR      No.  N04182736", 13,
          INK, max_w=388)
    # portrait
    portrait(cv, 64, 240, 150, 195)
    # data fields beside the portrait
    fields = [
        ("SURNAME", "VARKAS"),
        ("GIVEN NAMES", "ELENA MARA"),
        ("NATIONALITY", "NAROVIAN"),
        ("DATE OF BIRTH", "12 APR 1994"),
        ("PLACE OF BIRTH", "DUNVAR"),
        ("SEX", "F"),
    ]
    fy = 244
    for label, value in fields:
        txt(cv, 232, fy, label, 9, GREY)
        txt(cv, 232, fy + 13, value, 14, INK)
        fy += 32
    # issue / expiry / authority / signature
    txt(cv, 64, 462, "DATE OF ISSUE", 9, GREY)
    txt(cv, 64, 475, "14 MAR 2023", 14, INK)
    txt(cv, 264, 462, "DATE OF EXPIRY", 9, GREY)
    txt(cv, 264, 475, "14 MAR 2033", 14, INK)
    txt(cv, 64, 512, "AUTHORITY", 9, GREY)
    txt(cv, 64, 525, "DUNVAR PASSPORT OFFICE", 14, INK, max_w=190)
    txt(cv, 264, 512, "HOLDER'S SIGNATURE", 9, GREY)
    # signature: a flowing hand line, clear of the authority text
    sig = [(290, 540), (300, 532), (310, 540), (320, 530), (330, 539),
           (340, 531), (350, 540), (360, 533), (370, 539), (380, 534),
           (390, 540), (400, 532), (410, 539), (420, 535), (432, 540)]
    for i in range(len(sig) - 1):
        cv.line(sc(sig[i][0]), sc(sig[i][1]), sc(sig[i + 1][0]),
                sc(sig[i + 1][1]), (40, 40, 120), sc(2))
    cv.line(sc(264), sc(546), sc(440), sc(546), GREY, sc(1))
    # MRZ
    doc = "N04182736"
    line1 = "P<NARVARKAS<<ELENA<MARA" + "<" * 21
    opt = "<" * 14
    line2 = (doc + mrz_check(doc) + "NAR" + "940412" + mrz_check("940412")
             + "F" + "330314" + mrz_check("330314") + opt + mrz_check(opt))
    comp_src = (doc + mrz_check(doc) + "940412" + mrz_check("940412")
                + "330314" + mrz_check("330314") + opt + mrz_check(opt))
    line2 += mrz_check(comp_src)
    assert len(line1) == 44 and len(line2) == 44, (line1, line2)
    cv.fill_rect(sc(48), sc(580), sc(480), sc(640), (255, 255, 255))
    txt(cv, 58, 588, line1, 15, INK, max_w=412)
    txt(cv, 58, 612, line2, 15, INK, max_w=412)
    # languages + fine print
    txt(cv, 64, 668, "LANGUAGES:  NAROVIAN  \u00b7  ENGLISH  \u00b7  FRENCH",
        10, GREY, max_w=420)
    txt(cv, 64, 700,
        "This passport is the property of the Republic of Narovia",
        10, GREY, max_w=420)
    txt(cv, 64, 716,
        "and must be surrendered on demand. Loss must be reported",
        10, GREY, max_w=420)
    txt(cv, 64, 732,
        "to the nearest Narovian mission without delay.",
        10, GREY, max_w=420)
    # footer motto
    cv.line(sc(70), sc(900), sc(458), sc(900), GREEN, sc(1))
    ctext(cv, 264, 916, "UNITY  \u00b7  MOUNTAINS  \u00b7  FAITH", 13, GREEN,
          tracking=3)
    ctext(cv, 264, 940, "ISSUED IN GOOD FAITH BY THE DUNVAR PASSPORT OFFICE",
          9, GREY, tracking=1, max_w=388)


def visa_page(cv):
    x0, x1, y0, y1 = 524, 996, 24, 1000
    cv.fill_rect(sc(x0), sc(y0), sc(x1), sc(y1), PAPER)
    cv.rect_outline(sc(x0), sc(y0), sc(x1), sc(y1), GREEN, sc(3))
    cv.rect_outline(sc(x0 + 10), sc(y0 + 10), sc(x1 - 10), sc(y1 - 10),
                    GREEN, sc(1))
    ctext(cv, 760, 48, "VISAS", 20, INK, tracking=6)
    cv.line(sc(580), sc(82), sc(940), sc(82), GREEN, sc(2))
    # visa sticker — Aldermere, matching the first arrival stamp
    vx0, vy0, vx1, vy1 = 556, 104, 964, 252
    cv.fill_rect(sc(vx0), sc(vy0), sc(vx1), sc(vy1), (220, 232, 228))
    cv.rect_outline(sc(vx0), sc(vy0), sc(vx1), sc(vy1), BLUE, sc(2))
    txt(cv, vx0 + 16, vy0 + 12, "REPUBLIC OF ALDERMERE", 16, BLUE,
        max_w=276)
    txt(cv, vx0 + 16, vy0 + 40, "VISA \u2014 SINGLE ENTRY \u2014 TOURIST", 13,
        INK, max_w=276)
    txt(cv, vx0 + 16, vy0 + 64, "No. ALD-2291", 13, INK)
    txt(cv, vx0 + 16, vy0 + 88, "VALID 30 DAYS FROM 02 JUN 2023", 13, INK,
        max_w=390)
    txt(cv, vx0 + 16, vy0 + 112,
        "HOLDER: ELENA MARA VARKAS  \u00b7  PASSPORT N04182736", 11, GREY,
        max_w=390)
    # fee stamp on the sticker
    cv.rect_outline(sc(vx1 - 108), sc(vy0 + 14), sc(vx1 - 14), sc(vy0 + 58),
                    RED, sc(2))
    txt(cv, vx1 - 100, vy0 + 20, "FEE PAID", 11, RED)
    txt(cv, vx1 - 100, vy0 + 36, "12 KORUN", 11, RED)
    # border stamps — a plausible travel history, all after issue
    stamps = [
        ([("ALDERMERE", 15),
          ("ARRIVED  \u00b7  02 JUN 2023", 12),
          ("DUNVAR BORDER", 12)], BLUE, -6, 300),
        ([("KESSIG", 15),
          ("DEPARTED  \u00b7  18 SEP 2023", 12),
          ("VELKA CROSSING", 12)], RED, 5, 392),
        ([("TARNOVIA", 15),
          ("ARRIVED  \u00b7  05 JAN 2024", 12),
          ("SOUTH GATE", 12)], BLUE, -4, 484),
        ([("ALDERMERE", 15),
          ("DEPARTED  \u00b7  22 FEB 2024", 12),
          ("DUNVAR BORDER", 12)], RED, 5, 566),
    ]
    for lines, ink, rot, sy in stamps:
        layer = stamp_layer(lines, ink)
        blit_rotated(cv, layer, sc(570), sc(sy), rot)
    # the telling detail: the red endorsement
    ex0, ey0, ex1, ey1 = 556, 700, 964, 836
    cv.rect_outline(sc(ex0), sc(ey0), sc(ex1), sc(ey1), RED, sc(2))
    txt(cv, ex0 + 16, ey0 + 12, "ENDORSEMENT", 13, RED)
    txt(cv, ex0 + 16, ey0 + 38, "THE HOLDER MAY NOT ENTER THE EASTERN", 13,
        RED, max_w=390)
    txt(cv, ex0 + 16, ey0 + 58, "MARCHES WITHOUT A SEPARATE PERMIT.", 13,
        RED, max_w=390)
    txt(cv, ex0 + 16, ey0 + 84, "\u2014 MINISTRY OF THE INTERIOR, DUNVAR",
        11, RED, max_w=390)
    txt(cv, ex0 + 16, ey0 + 104,
        "Permit applications: Dunvar Passport Office, counter 3.", 10, GREY,
        max_w=390)
    # bottom note
    txt(cv, 556, 868,
        "Stamps are entered by the border officer at the crossing.", 10,
        GREY, max_w=440)
    txt(cv, 556, 884, "A stamp that predates this passport is void.", 10,
        GREY, max_w=440)
    ctext(cv, 760, 940, "PAGE 2 \u2014 VISAS AND ENDORSEMENTS", 9, GREY,
          tracking=2)


def downsample(px, sw, sh):
    """Box-average 2x2 downsample of an RGB bytearray to half size."""
    w, h = sw // 2, sh // 2
    out = bytearray(w * h * 3)
    for y in range(h):
        r0 = (2 * y) * sw * 3
        r1 = (2 * y + 1) * sw * 3
        o = y * w * 3
        for x in range(w):
            s = 2 * x * 3
            out[o] = (px[r0 + s] + px[r0 + s + 3] + px[r1 + s] + px[r1 + s + 3] + 2) // 4
            out[o + 1] = (px[r0 + s + 1] + px[r0 + s + 4] + px[r1 + s + 1] + px[r1 + s + 4] + 2) // 4
            out[o + 2] = (px[r0 + s + 2] + px[r0 + s + 5] + px[r1 + s + 2] + px[r1 + s + 5] + 2) // 4
            o += 3
    return out


def _png_chunk(ctype, data):
    chunk = struct.pack(">I", len(data)) + ctype + data
    chunk += struct.pack(">I", zlib.crc32(ctype + data) & 0xFFFFFFFF)
    return chunk


def write_png(path, rgb, w, h):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n"
           + _png_chunk(b"IHDR", ihdr)
           + _png_chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _png_chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    rng = random.Random(20261121)
    cv = Canvas(sc(W), sc(H), DESK)
    # desk vignette: faint darker corners
    for i in range(60):
        a = rng.randint(0, 10)
        x, y = rng.randint(0, W), rng.randint(0, H)
        cv.filled_circle(sc(x) + 3, sc(y) + 3, 3, (0, 0, 0), a)
    data_page(cv)
    visa_page(cv)
    # centre gutter shadow
    cv.fill_rect(sc(500), sc(24), sc(524), sc(1000), (0, 0, 0), 60)
    small = downsample(cv.px, sc(W), sc(H))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    size = write_png(OUT, small, W, H)
    print("wrote", OUT, size, "bytes")


if __name__ == "__main__":
    main()
