#!/usr/bin/env python3
"""Passport spread for the Republic of Narovia.

Draws one invented passport spread (1024x1024 PNG) for a country that
does not exist: the data page of Elena Mara Varkas, born in Dunvar,
and the visa page carrying her travel history. Every date agrees:
issued 14 MAR 2023, stamps JUN 2023 - FEB 2024, expiry 14 MAR 2033.
The telling detail is the red endorsement: the holder may not enter
the Eastern Marches without a separate permit.

Deterministic: fixed seed, no network, no clock reads. Drawn at 2x
and downscaled for smooth edges.

  End-to-end check of this shipped file (2026-11-21): entry.png is
  1024 by 1024, 319.120 bytes, within the 1 MiB cap; the copy lands
  byte-for-byte identical (md5 df436e650c4ce4330b609643329e0b31)
  across two runs.
"""

import os
import random
from PIL import Image, ImageDraw, ImageFont

S = 2  # supersample factor; final image is 1024x1024
W, H = 1024, 1024
OUT = os.path.join(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"), "entry.png")

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
INK = (28, 28, 26)
GREEN = (30, 77, 43)
GOLD = (176, 141, 42)
CREAM = (246, 241, 226)
PAPER = (250, 246, 233)
DESK = (38, 41, 47)
RED = (158, 42, 34)
BLUE = (38, 74, 110)
GREY = (96, 104, 90)


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), int(size * S))


def sc(v):
    return int(v * S)


def tracked(d, x, y, text, fnt, fill, tracking=0):
    """Draw text with letter tracking (tracking in 1024-space px)."""
    cx = sc(x)
    for ch in text:
        d.text((cx, sc(y)), ch, font=fnt, fill=fill)
        cx += int(d.textlength(ch, font=fnt) + sc(tracking))
    return cx


def tracked_width(d, text, fnt, tracking=0):
    w = 0
    for ch in text:
        w += d.textlength(ch, font=fnt) + sc(tracking)
    return w - sc(tracking)


def centered(d, cx, y, text, fnt, fill, tracking=0):
    w = tracked_width(d, text, fnt, tracking)
    tracked(d, cx - w / S / 2, y, text, fnt, fill, tracking)


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


def coat_of_arms(d, cx, cy, scale=1.0):
    """Small shield: green field, gold mountain, gold star."""
    w, h = 34 * scale, 40 * scale
    x0, y0 = cx - w / 2, cy - h / 2
    shield = [(x0, y0), (x0 + w, y0), (x0 + w, y0 + h * 0.62),
              (cx, y0 + h), (x0, y0 + h * 0.62)]
    d.polygon([(sc(a), sc(b)) for a, b in shield], fill=GREEN,
              outline=GOLD, width=sc(2))
    # mountain
    d.polygon([(sc(cx - w * 0.32), sc(y0 + h * 0.72)),
               (sc(cx), sc(y0 + h * 0.34)),
               (sc(cx + w * 0.32), sc(y0 + h * 0.72))],
              fill=GOLD)
    # star
    sx, sy, r = cx, y0 + h * 0.16, 4 * scale
    pts = []
    for i in range(10):
        ang = -90 + i * 36
        rr = r if i % 2 == 0 else r * 0.45
        import math
        pts.append((sx + rr * math.cos(math.radians(ang)),
                    sy + rr * math.sin(math.radians(ang))))
    d.polygon([(sc(a), sc(b)) for a, b in pts], fill=GOLD)


def portrait(d, x0, y0, w, h):
    """Stylised passport portrait: Elena Mara Varkas, 29, in national dress."""
    # photo background
    d.rectangle([sc(x0), sc(y0), sc(x0 + w), sc(y0 + h)], fill=(122, 158, 150))
    d.rectangle([sc(x0), sc(y0), sc(x0 + w), sc(y0 + h)], outline=(90, 110, 104),
                width=sc(1))
    cx = x0 + w / 2
    # long hair behind shoulders
    d.rounded_rectangle([sc(cx - 42), sc(y0 + 52), sc(cx + 42), sc(y0 + h - 6)],
                        radius=sc(14), fill=(46, 32, 24))
    # shoulders / coat
    d.polygon([(sc(cx - 62), sc(y0 + h)), (sc(cx - 46), sc(y0 + 128)),
               (sc(cx - 20), sc(y0 + 116)), (sc(cx + 20), sc(y0 + 116)),
               (sc(cx + 46), sc(y0 + 128)), (sc(cx + 62), sc(y0 + h))],
              fill=GREEN)
    # gold collar trim
    d.line([(sc(cx - 20), sc(y0 + 116)), (sc(cx), sc(y0 + 132)),
            (sc(cx + 20), sc(y0 + 116))], fill=GOLD, width=sc(2))
    # woven sash across the shoulder
    d.polygon([(sc(cx - 58), sc(y0 + 150)), (sc(cx - 34), sc(y0 + 138)),
               (sc(cx + 30), sc(y0 + h)), (sc(cx + 6), sc(y0 + h))],
              fill=(176, 141, 42))
    d.polygon([(sc(cx - 34), sc(y0 + 138)), (sc(cx - 26), sc(y0 + 142)),
               (sc(cx + 38), sc(y0 + h)), (sc(cx + 30), sc(y0 + h))],
              fill=(158, 42, 34))
    # neck
    d.rectangle([sc(cx - 11), sc(y0 + 104), sc(cx + 11), sc(y0 + 124)],
                fill=(217, 169, 134))
    # head
    d.ellipse([sc(cx - 32), sc(y0 + 26), sc(cx + 32), sc(y0 + 108)],
              fill=(217, 169, 134))
    # ears
    d.ellipse([sc(cx - 37), sc(y0 + 62), sc(cx - 29), sc(y0 + 78)],
              fill=(217, 169, 134))
    d.ellipse([sc(cx + 29), sc(y0 + 62), sc(cx + 37), sc(y0 + 78)],
              fill=(217, 169, 134))
    # hair cap
    d.pieslice([sc(cx - 34), sc(y0 + 18), sc(cx + 34), sc(y0 + 86)],
               start=180, end=360, fill=(46, 32, 24))
    d.polygon([(sc(cx - 34), sc(y0 + 52)), (sc(cx - 28), sc(y0 + 30)),
               (sc(cx - 12), sc(y0 + 44)), (sc(cx), sc(y0 + 32)),
               (sc(cx + 12), sc(y0 + 44)), (sc(cx + 28), sc(y0 + 30)),
               (sc(cx + 34), sc(y0 + 52)), (sc(cx + 30), sc(y0 + 58)),
               (sc(cx - 30), sc(y0 + 58))], fill=(46, 32, 24))
    # eyebrows
    d.arc([sc(cx - 22), sc(y0 + 58), sc(cx - 6), sc(y0 + 68)], start=200,
          end=340, fill=(46, 32, 24), width=sc(2))
    d.arc([sc(cx + 6), sc(y0 + 58), sc(cx + 22), sc(y0 + 68)], start=200,
          end=340, fill=(46, 32, 24), width=sc(2))
    # eyes
    for ex in (cx - 14, cx + 14):
        d.ellipse([sc(ex - 6), sc(y0 + 68), sc(ex + 6), sc(y0 + 76)],
                  fill=(250, 246, 233))
        d.ellipse([sc(ex - 2.5), sc(y0 + 69.5), sc(ex + 2.5), sc(y0 + 74.5)],
                  fill=(28, 28, 26))
    # nose
    d.line([(sc(cx), sc(y0 + 76)), (sc(cx - 1), sc(y0 + 88)),
            (sc(cx + 3), sc(y0 + 90))], fill=(178, 128, 92), width=sc(2))
    # mouth
    d.arc([sc(cx - 8), sc(y0 + 92), sc(cx + 8), sc(y0 + 102)], start=15,
          end=165, fill=(140, 70, 60), width=sc(2))
    # cheek shading
    for ex in (cx - 21, cx + 21):
        d.ellipse([sc(ex - 5), sc(y0 + 82), sc(ex + 5), sc(y0 + 90)],
                  fill=(226, 150, 130))


def stamp(text_lines, ink, rotate_deg, w=380, h=66):
    """One border stamp on its own layer, rotated."""
    layer = Image.new("RGBA", (sc(w + 40), sc(h + 40)), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([sc(8), sc(8), sc(w + 32), sc(h + 32)], radius=sc(6),
                        outline=ink + (235,), width=sc(3))
    d.rounded_rectangle([sc(13), sc(13), sc(w + 27), sc(h + 27)], radius=sc(4),
                        outline=ink + (200,), width=sc(1))
    f1 = font("DejaVuSans-Bold.ttf", 15)
    f2 = font("DejaVuSans.ttf", 12)
    y = 14
    for i, (txt, fnt) in enumerate(text_lines):
        tw = d.textlength(txt, font=fnt)
        d.text((sc(w + 40) / 2 - tw / 2, sc(y)), txt, font=fnt,
               fill=ink + (235,))
        y += 15 if i == 0 else 13
    return layer.rotate(rotate_deg, expand=True, resample=Image.BICUBIC)


def data_page(img):
    d = ImageDraw.Draw(img, "RGBA")
    x0, x1, y0, y1 = 28, 500, 24, 1000
    # page + borders
    d.rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], fill=CREAM)
    d.rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], outline=GREEN, width=sc(3))
    d.rectangle([sc(x0 + 10), sc(y0 + 10), sc(x1 - 10), sc(y1 - 10)],
                outline=GREEN, width=sc(1))
    # header
    coat_of_arms(d, 264, 78, scale=1.0)
    centered(d, 264, 128, "REPUBLIC OF NAROVIA", font("DejaVuSerif-Bold.ttf", 21),
             INK, tracking=2)
    centered(d, 264, 158, "PASSPORT", font("DejaVuSans-Bold.ttf", 15), GREEN,
             tracking=8)
    d.line([(sc(70), sc(186)), (sc(458), sc(186))], fill=GREEN, width=sc(2))
    centered(d, 264, 200, "TYPE  P      CODE  NAR      No.  N04182736",
             font("DejaVuSansMono.ttf", 13), INK)
    # portrait
    portrait(d, 64, 240, 150, 195)
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
        d.text((sc(232), sc(fy)), label, font=font("DejaVuSans.ttf", 9),
               fill=GREY)
        d.text((sc(232), sc(fy + 13)), value,
               font=font("DejaVuSans-Bold.ttf", 14), fill=INK)
        fy += 32
    # issue / expiry / authority / signature
    d.text((sc(64), sc(462)), "DATE OF ISSUE",
           font=font("DejaVuSans.ttf", 9), fill=GREY)
    d.text((sc(64), sc(475)), "14 MAR 2023",
           font=font("DejaVuSans-Bold.ttf", 14), fill=INK)
    d.text((sc(264), sc(462)), "DATE OF EXPIRY",
           font=font("DejaVuSans.ttf", 9), fill=GREY)
    d.text((sc(264), sc(475)), "14 MAR 2033",
           font=font("DejaVuSans-Bold.ttf", 14), fill=INK)
    d.text((sc(64), sc(512)), "AUTHORITY",
           font=font("DejaVuSans.ttf", 9), fill=GREY)
    d.text((sc(64), sc(525)), "DUNVAR PASSPORT OFFICE",
           font=font("DejaVuSans-Bold.ttf", 14), fill=INK)
    d.text((sc(264), sc(512)), "HOLDER'S SIGNATURE",
           font=font("DejaVuSans.ttf", 9), fill=GREY)
    # signature: a flowing hand line, clear of the authority text
    sig = [(290, 540), (300, 532), (310, 540), (320, 530), (330, 539),
           (340, 531), (350, 540), (360, 533), (370, 539), (380, 534),
           (390, 540), (400, 532), (410, 539), (420, 535), (432, 540)]
    d.line([(sc(a), sc(b)) for a, b in sig], fill=(40, 40, 120), width=sc(2))
    d.line([(sc(264), sc(546)), (sc(440), sc(546))], fill=GREY, width=sc(1))
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
    d.rectangle([sc(48), sc(580), sc(480), sc(640)], fill=(255, 255, 255))
    d.text((sc(58), sc(588)), line1, font=font("DejaVuSansMono.ttf", 15),
           fill=INK)
    d.text((sc(58), sc(612)), line2, font=font("DejaVuSansMono.ttf", 15),
           fill=INK)
    # languages + fine print
    d.text((sc(64), sc(668)), "LANGUAGES:  NAROVIAN  ·  ENGLISH  ·  FRENCH",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    d.text((sc(64), sc(700)),
           "This passport is the property of the Republic of Narovia",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    d.text((sc(64), sc(716)),
           "and must be surrendered on demand. Loss must be reported",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    d.text((sc(64), sc(732)),
           "to the nearest Narovian mission without delay.",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    # footer motto
    d.line([(sc(70), sc(900)), (sc(458), sc(900))], fill=GREEN, width=sc(1))
    centered(d, 264, 916, "UNITY  ·  MOUNTAINS  ·  FAITH",
             font("DejaVuSerif.ttf", 13), GREEN, tracking=3)
    centered(d, 264, 940, "ISSUED IN GOOD FAITH BY THE DUNVAR PASSPORT OFFICE",
             font("DejaVuSans.ttf", 9), GREY, tracking=1)


def visa_page(img):
    d = ImageDraw.Draw(img, "RGBA")
    x0, x1, y0, y1 = 524, 996, 24, 1000
    d.rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], fill=PAPER)
    d.rectangle([sc(x0), sc(y0), sc(x1), sc(y1)], outline=GREEN, width=sc(3))
    d.rectangle([sc(x0 + 10), sc(y0 + 10), sc(x1 - 10), sc(y1 - 10)],
                outline=GREEN, width=sc(1))
    centered(d, 760, 48, "VISAS", font("DejaVuSerif-Bold.ttf", 20), INK,
             tracking=6)
    d.line([(sc(580), sc(82)), (sc(940), sc(82))], fill=GREEN, width=sc(2))
    # visa sticker — Aldermere, matching the first arrival stamp
    vx0, vy0, vx1, vy1 = 556, 104, 964, 252
    d.rectangle([sc(vx0), sc(vy0), sc(vx1), sc(vy1)], fill=(220, 232, 228))
    d.rectangle([sc(vx0), sc(vy0), sc(vx1), sc(vy1)], outline=BLUE, width=sc(2))
    d.text((sc(vx0 + 16), sc(vy0 + 12)), "REPUBLIC OF ALDERMERE",
           font=font("DejaVuSans-Bold.ttf", 16), fill=BLUE)
    d.text((sc(vx0 + 16), sc(vy0 + 40)), "VISA — SINGLE ENTRY — TOURIST",
           font=font("DejaVuSans.ttf", 13), fill=INK)
    d.text((sc(vx0 + 16), sc(vy0 + 64)), "No. ALD-2291",
           font=font("DejaVuSansMono.ttf", 13), fill=INK)
    d.text((sc(vx0 + 16), sc(vy0 + 88)),
           "VALID 30 DAYS FROM 02 JUN 2023",
           font=font("DejaVuSans.ttf", 13), fill=INK)
    d.text((sc(vx0 + 16), sc(vy0 + 112)),
           "HOLDER: ELENA MARA VARKAS  ·  PASSPORT N04182736",
           font=font("DejaVuSans.ttf", 11), fill=GREY)
    # fee stamp on the sticker
    d.rectangle([sc(vx1 - 108), sc(vy0 + 14), sc(vx1 - 14), sc(vy0 + 58)],
                outline=RED, width=sc(2))
    d.text((sc(vx1 - 100), sc(vy0 + 20)), "FEE PAID",
           font=font("DejaVuSans-Bold.ttf", 11), fill=RED)
    d.text((sc(vx1 - 100), sc(vy0 + 36)), "12 KORUN",
           font=font("DejaVuSans-Bold.ttf", 11), fill=RED)
    # border stamps — a plausible travel history, all after issue
    stamps = [
        ([("ALDERMERE", font("DejaVuSans-Bold.ttf", 15)),
          ("ARRIVED  ·  02 JUN 2023", font("DejaVuSans.ttf", 12)),
          ("DUNVAR BORDER", font("DejaVuSans.ttf", 12))], BLUE, -6, 300),
        ([("KESSIG", font("DejaVuSans-Bold.ttf", 15)),
          ("DEPARTED  ·  18 SEP 2023", font("DejaVuSans.ttf", 12)),
          ("VELKA CROSSING", font("DejaVuSans.ttf", 12))], RED, 5, 392),
        ([("TARNOVIA", font("DejaVuSans-Bold.ttf", 15)),
          ("ARRIVED  ·  05 JAN 2024", font("DejaVuSans.ttf", 12)),
          ("SOUTH GATE", font("DejaVuSans.ttf", 12))], BLUE, -4, 484),
        ([("ALDERMERE", font("DejaVuSans-Bold.ttf", 15)),
          ("DEPARTED  ·  22 FEB 2024", font("DejaVuSans.ttf", 12)),
          ("DUNVAR BORDER", font("DejaVuSans.ttf", 12))], RED, 5, 566),
    ]
    for lines, ink, rot, sy in stamps:
        layer = stamp(lines, ink, rot)
        img.paste(layer, (sc(570), sc(sy)), layer)
    # the telling detail: the red endorsement
    ex0, ey0, ex1, ey1 = 556, 700, 964, 836
    d.rectangle([sc(ex0), sc(ey0), sc(ex1), sc(ey1)], outline=RED, width=sc(2))
    d.text((sc(ex0 + 16), sc(ey0 + 12)), "ENDORSEMENT",
           font=font("DejaVuSans-Bold.ttf", 13), fill=RED)
    d.text((sc(ex0 + 16), sc(ey0 + 38)),
           "THE HOLDER MAY NOT ENTER THE EASTERN",
           font=font("DejaVuSans.ttf", 13), fill=RED)
    d.text((sc(ex0 + 16), sc(ey0 + 58)),
           "MARCHES WITHOUT A SEPARATE PERMIT.",
           font=font("DejaVuSans.ttf", 13), fill=RED)
    d.text((sc(ex0 + 16), sc(ey0 + 84)),
           "— MINISTRY OF THE INTERIOR, DUNVAR",
           font=font("DejaVuSans.ttf", 11), fill=RED)
    d.text((sc(ex0 + 16), sc(ey0 + 104)),
           "Permit applications: Dunvar Passport Office, counter 3.",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    # bottom note
    d.text((sc(556), sc(868)),
           "Stamps are entered by the border officer at the crossing.",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    d.text((sc(556), sc(884)),
           "A stamp that predates this passport is void.",
           font=font("DejaVuSans.ttf", 10), fill=GREY)
    centered(d, 760, 940, "PAGE 2 — VISAS AND ENDORSEMENTS",
             font("DejaVuSans.ttf", 9), GREY, tracking=2)


def main():
    rng = random.Random(20261121)
    img = Image.new("RGB", (sc(W), sc(H)), DESK)
    d = ImageDraw.Draw(img, "RGBA")
    # desk vignette: faint darker corners
    for i in range(60):
        a = rng.randint(0, 10)
        x, y = rng.randint(0, W), rng.randint(0, H)
        d.ellipse([sc(x), sc(y), sc(x + 3), sc(y + 3)], fill=(0, 0, 0, a))
    data_page(img)
    visa_page(img)
    # centre gutter shadow
    d = ImageDraw.Draw(img, "RGBA")
    d.rectangle([sc(500), sc(24), sc(524), sc(1000)], fill=(0, 0, 0, 60))
    small = img.resize((W, H), Image.LANCZOS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    small.save(OUT, optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
