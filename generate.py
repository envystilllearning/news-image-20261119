#!/usr/bin/env python3
"""Draw the news-image-20261119 poster: one image summing up the world news
of Thursday 19 November 2026. Light-newspaper layout, 1024x1024 PNG.

Written fresh for this entry: data comes from the build brief and the
BUILD-REPORT claim list; the drawing code below is my own implementation.
Run: python3 generate.py  ->  entry.png (deterministic, same sha every run).
"""

import hashlib
import os
import sys
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

# ---------------------------------------------------------------- palette
PAPER = (247, 242, 231)
INK = (28, 25, 23)
MUTED = (107, 101, 92)
FAINT = (140, 133, 120)
RULE = (28, 25, 23)
RED = (168, 50, 38)
BLUE = (46, 74, 107)
GOLD = (176, 124, 22)
TEAL = (42, 110, 96)
LAND = (207, 200, 180)
LAND_EDGE = (143, 136, 117)
SEA = (233, 228, 214)
CARD_BG = (255, 253, 247)
STRIP_BG = (238, 231, 217)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

_font_cache = {}


def font(size, bold=False, serif=False):
    key = (size, bold, serif)
    if key not in _font_cache:
        path = SERIF_B if (serif and bold) else SERIF if serif else SANS_B if bold else SANS
        _font_cache[key] = ImageFont.truetype(path, size)
    return _font_cache[key]


def tw(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill=INK, leading=None, align="left", width=None):
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        lx = x
        if align == "center" and width is not None:
            lx = x + (width - draw.textlength(line, font=fnt)) / 2
        draw.text((lx, y), line, font=fnt, fill=fill)
        y += leading
    return y


def rule(draw, x0, y, x1, width=1, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def badge(draw, cx, cy, r, number, fill=BLUE, text_fill=(255, 255, 255)):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill, outline=(255, 255, 255), width=2)
    label = str(number)
    fnt = font(max(9, r), bold=True)
    w = draw.textlength(label, font=fnt)
    h = fnt.size
    draw.text((cx - w / 2, cy - h / 2 - 1), label, font=fnt, fill=text_fill)


# ------------------------------------------------------------------- data
# 39 verified stories. Regions: ASIA 18, N. AMERICA 10, EUROPE 6, WORLD 3,
# OCEANIA 2. Fields: Politics 10, Markets 15, Tech 3, World 6, Sport 3,
# Culture 2. Story 38 (ENISA) was removed: its report is from 10 November,
# not 19 November. Market briefs use 18 Nov closes as reported on the
# morning of 19 Nov (morning-paper convention).
FEATURES = [
    dict(n=1, kind="gta", region="WORLD", field="Culture",
         kicker="LEONIDA  •  THE BIGGEST LAUNCH OF THE YEAR",
         head="GTA VI IS HERE",
         body="Rolling midnight launch worldwide on PS5 and Xbox Series X|S, "
              "$79.99. New Zealand first; 16m+ pre-orders.",
         lon=167.0, lat=-45.0),
    dict(n=2, kind="shenzhen", region="ASIA", field="Politics",
         kicker="SHENZHEN  •  A FIRST",
         head="TRUMP, XI AND PUTIN MEET THREE-WAY",
         body="First-ever trilateral on the APEC sidelines; Iran and nuclear "
              "arms on the agenda, Ukraine off it.",
         lon=114.0, lat=22.5),
    dict(n=3, kind="hague", region="EUROPE", field="Politics",
         kicker="THE PEACE PALACE  •  THE HAGUE",
         head="WORLD COURT RULES ON MYANMAR",
         body="Judgment day in The Gambia v. Myanmar; 730,000+ displaced in "
              "2017; a first verdict possible.",
         lon=4.3, lat=52.1),
]

CARDS = [
    dict(n=4, kind="anthropic", region="N. AMERICA", field="Tech",
         head="ANTHROPIC DEBUTS AT $83",
         body="Priced above range at $83; $81.34bn offering; $26bn placement.",
         lon=-74.0, lat=40.7),
    dict(n=5, kind="voyager", region="N. AMERICA", field="Tech",
         head="VOYAGER 1: ONE LIGHT-DAY OUT",
         body="NASA confirms the milestone at 5:16 a.m. EST, 49 years after launch.",
         lon=-118.0, lat=34.0),
    dict(n=6, kind="cyclone", region="ASIA", field="World",
         head="CYCLONE AKVAN BEARS DOWN",
         body="Landfall due noon Friday; winds 90–100 km/h, red alerts in Odisha.",
         lon=86.0, lat=19.5),
    dict(n=7, kind="modi", region="ASIA", field="World",
         head="MODI MEETS THE ROYALS",
         body="The Prince and Princess of Wales in New Delhi, boosting UK–India ties.",
         lon=77.2, lat=28.6),
    dict(n=8, kind="defence", region="ASIA", field="Politics",
         head="INDIA AND JAPAN TALK DEFENCE",
         body="2+2 dialogue in Tokyo; Singh and Jaishankar review defence ties.",
         lon=139.7, lat=35.7),
    dict(n=9, kind="indigo", region="ASIA", field="Markets",
         head="INDIGO HALTS FOUR SAUDI ROUTES",
         body="Flights to Jeddah, Madinah, Riyadh and Dammam cancelled to 30 Nov.",
         lon=46.7, lat=24.6),
    dict(n=10, kind="berlin", region="EUROPE", field="Politics",
         head="THE COALITION MEETS IN BERLIN",
         body="Merz hosts five leaders plus NATO's Rutte; drone package for Kyiv.",
         lon=13.4, lat=52.5),
    dict(n=11, kind="cop", region="EUROPE", field="World",
         head="COP31'S FINAL STRETCH",
         body="Antalya talks seek fossil-fuel phase-out; $120bn a year by 2035.",
         lon=30.7, lat=36.9),
    dict(n=12, kind="alibaba", region="ASIA", field="Tech",
         head="ALIBABA REPORTS TODAY",
         body="September-quarter results before the US open; Qwen4-Max out Monday.",
         lon=120.2, lat=30.3),
    dict(n=13, kind="e1", region="ASIA", field="Politics",
         head="ISRAEL'S E1 DECISION DUE",
         body="Caretaker government to rule on E1; Australia, Britain imposed sanctions.",
         lon=35.2, lat=31.8),
]

BRIEFS = [
    (14, "Dow drops 561 (−1.11%) to 50,198", -74.0, 40.7),
    (15, "S&P falls a fifth day; Nasdaq +0.42%", -74.0, 40.7),
    (16, "Brent slides to $88.73 (−4.73%)", -0.1, 51.5),
    (17, "Gold extends slide to $3,738", -74.0, 40.7),
    (18, "Nikkei closes up 0.3% at 59,024", 139.7, 35.7),
    (19, "Nikkei opens higher; SoftBank +1.2%", 139.7, 35.7),
    (20, "FTSE 100 falls 1.3% to 10,551", -0.1, 51.5),
    (21, "US 10-year yield holds above 5%", -74.0, 40.7),
    (22, "Seoul delays open an hour for exam", 127.0, 37.5),
    (23, "UnitedHealth sinks 10% on clawback", -74.0, 40.7),
    (24, "Hong Kong stocks set to open lower", 114.2, 22.3),
    (25, "Kospi jumps 2% to 5,067 on chips", 127.0, 37.5),
    (26, "Nvidia gives back bounce, down 2.9%", -122.0, 37.4),
    (27, "Colts at Texans, Thursday night NFL", -95.4, 29.8),
    (28, "Bangladesh trail by 99 runs, day four", 90.4, 23.8),
    (29, "Sri Lanka–Pakistan Test, day two", 73.1, 33.6),
    (30, "Britain and EU haggle over summit text", 4.4, 50.8),
    (31, "APEC leaders wrap up in Shenzhen", 114.0, 22.5),
    (32, "Saudi Arabia braces for long Houthi fight", 46.7, 24.6),
    (33, "Canadian judge orders firms to disclose", -79.4, 43.7),
    (34, "Pakistan minister to attend SCO talks", 77.2, 28.6),
    (35, "India reviews rail readiness for Akvan", 77.2, 28.6),
    (36, "Telangana braces for rain to Saturday", 78.5, 17.4),
    (37, "KFC Australia's fake funeral for GTA", 151.2, -33.9),
    (39, "Logitech declares GTA “Game Day” off", 6.6, 46.5),
    (40, "New Zealand first to play GTA VI", 174.8, -41.3),
]

NUMBERS = [
    ("DOW", "−561", "−1.11%"),
    ("BRENT", "$88.73", "−4.73%"),
    ("GOLD", "$3,738", "sliding"),
    ("NIKKEI", "59,024", "+0.3%"),
    ("GTA VI", "$79.99", "16m+ pre-orders"),
    ("VOYAGER 1", "25.9bn km", "one light-day"),
]

DATE_CHECK = ("DATE CHECK — reported 17–18 Nov, not today: Pew Islam report · "
              "Jeffries nominated · Glastonbury 2027 · Brazil fiscal package · "
              "Gaza offensive · EU €45bn loan · Nvidia H200 halt · Carney–Xi thaw")

REGION_ORDER = ["ASIA", "N. AMERICA", "EUROPE", "WORLD", "OCEANIA"]
REGION_COLORS = {"ASIA": RED, "N. AMERICA": BLUE, "EUROPE": GOLD,
                 "WORLD": TEAL, "OCEANIA": (122, 90, 140)}
FIELD_ORDER = ["Politics", "Markets", "Tech", "World", "Sport", "Culture"]
FIELD_COLORS = {"Politics": RED, "Markets": BLUE, "Tech": GOLD,
                "World": TEAL, "Sport": (122, 90, 140), "Culture": (90, 110, 60)}

# ------------------------------------------------------- feature artwork
# Each feature panel gets a small drawn scene (PIL primitives only). The
# scenes are my own compositions for the three lead stories.


def sky_bands(draw, x, y, w, h, top, bottom):
    """Vertical gradient made of thin horizontal bands."""
    steps = max(1, h)
    for i in range(steps):
        t = i / steps
        col = tuple(int(top[c] + (bottom[c] - top[c]) * t) for c in range(3))
        draw.line([(x, y + i), (x + w, y + i)], fill=col)


def draw_palm(draw, x, y, s, lean=0):
    """A simple palm: curved trunk plus radiating fronds."""
    trunk_top = (x + lean, y - int(3.2 * s))
    draw.line([(x, y), trunk_top], fill=(30, 22, 18), width=max(2, s // 4))
    for k in range(-3, 4):
        ang = k * 0.45
        dx = int(2.6 * s * (1 if k >= 0 else -1) * (0.55 + 0.45 * abs(k) / 3.0))
        dy = int(-1.1 * s - 0.55 * s * (1 - abs(k) / 3.0))
        draw.line([trunk_top, (trunk_top[0] + dx, trunk_top[1] + dy)],
                  fill=(30, 22, 18), width=max(1, s // 6))


def draw_gta(draw, x, y, w, h):
    sky_bands(draw, x, y, w, h, (64, 32, 88), (235, 130, 70))
    draw.ellipse([x + w - 78, y + 12, x + w - 26, y + 64], fill=(255, 214, 130))
    draw_palm(draw, x + 26, y + h - 6, 12, lean=6)
    draw_palm(draw, x + w - 30, y + h - 6, 10, lean=-6)
    vi = font(56, bold=True, serif=True)
    label = "VI"
    vw = draw.textlength(label, font=vi)
    draw.text((x + (w - vw) / 2 + 2, y + 8), label, font=vi, fill=(60, 30, 10))
    draw.text((x + (w - vw) / 2, y + 6), label, font=vi, fill=(255, 200, 60))
    draw.line([(x + w / 2 - 34, y + h - 9), (x + w / 2 + 34, y + h - 9)],
              fill=(255, 200, 60), width=3)
    lf = font(11, bold=True)
    tag = "LEONIDA"
    twd = draw.textlength(tag, font=lf)
    draw.text((x + (w - twd) / 2, y + h - 24), tag, font=lf, fill=(255, 240, 210))


def draw_shenzhen(draw, x, y, w, h):
    sky_bands(draw, x, y, w, h, (214, 226, 238), (245, 238, 222))
    base = y + h
    towers = [(0, 43, 34), (34, 62, 40), (76, 36, 30), (108, 67, 44),
              (154, 49, 36), (192, 59, 42), (236, 41, 34), (272, 55, 38)]
    for tx, th, twd in towers:
        draw.rectangle([x + tx, base - th, x + tx + twd, base],
                       fill=(52, 66, 92), outline=(30, 40, 60))
        for wy in range(base - th + 8, base - 6, 10):
            for wx in range(x + tx + 5, x + tx + twd - 4, 9):
                draw.point((wx, wy), fill=(255, 220, 130))
    draw.rectangle([x + 108, base - 67 - 10, x + 152, base - 67],
                   fill=(52, 66, 92))
    # three small flags on poles, each anchored to a tower top
    for tx, th, col in [(34, 62, (168, 50, 38)), (108, 67, (200, 40, 30)),
                        (192, 59, (46, 74, 107))]:
        px = x + tx + 10
        pole_top = base - th - 14
        draw.line([(px, pole_top), (px, base - th)], fill=(28, 25, 23), width=2)
        draw.rectangle([px, pole_top - 12, px + 26, pole_top], fill=col)
    lf = font(11, bold=True)
    tag = "SHENZHEN"
    twd = draw.textlength(tag, font=lf)
    draw.rectangle([x + (w - twd) / 2 - 6, y + h - 24, x + (w + twd) / 2 + 6, y + h - 6],
                   fill=(28, 25, 23))
    draw.text((x + (w - twd) / 2, y + h - 22), tag, font=lf, fill=(255, 255, 255))


def draw_hague(draw, x, y, w, h):
    sky_bands(draw, x, y, w, h, (226, 232, 238), (245, 240, 228))
    base = y + h
    # palace: steps, columns, pediment
    for s in range(3):
        draw.rectangle([x + 30 + s * 8, base - 14 - s * 5, x + w - 30 - s * 8, base - 9 - s * 5],
                       fill=(120, 112, 96))
    for cx in range(x + 52, x + w - 52, 34):
        draw.rectangle([cx, base - 62, cx + 12, base - 28], fill=(232, 226, 210),
                       outline=(90, 84, 70))
    draw.rectangle([x + 40, base - 74, x + w - 40, base - 62], fill=(232, 226, 210),
                   outline=(90, 84, 70))
    draw.polygon([(x + 30, base - 74), (x + w // 2, base - 100), (x + w - 30, base - 74)],
                 fill=(176, 124, 22))
    # scales of justice, right side
    sx = x + w - 52
    draw.line([(sx, base - 96), (sx, base - 34)], fill=(28, 25, 23), width=2)
    draw.line([(sx - 26, base - 92), (sx + 26, base - 92)], fill=(28, 25, 23), width=2)
    draw.line([(sx - 26, base - 92), (sx - 36, base - 70)], fill=(28, 25, 23), width=1)
    draw.line([(sx - 26, base - 92), (sx - 16, base - 70)], fill=(28, 25, 23), width=1)
    draw.line([(sx + 26, base - 92), (sx + 16, base - 70)], fill=(28, 25, 23), width=1)
    draw.line([(sx + 26, base - 92), (sx + 36, base - 70)], fill=(28, 25, 23), width=1)
    draw.arc([sx - 40, base - 74, sx - 12, base - 62], 0, 180, fill=(28, 25, 23), width=2)
    draw.arc([sx + 12, base - 74, sx + 40, base - 62], 0, 180, fill=(28, 25, 23), width=2)
    lf = font(11, bold=True)
    tag = "THE HAGUE"
    twd = draw.textlength(tag, font=lf)
    draw.text((x + (w - twd) / 2, y + h - 22), tag, font=lf, fill=(28, 25, 23))


FEATURE_ART = {"gta": draw_gta, "shenzhen": draw_shenzhen, "hague": draw_hague}

# ---------------------------------------------------------- card artwork
# Small scenes for the ten cards, one per story, drawn with PIL primitives.


def draw_anthropic(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(28, 32, 48))
    bars = [8, 13, 11, 18, 24]
    bw = 12
    for i, bh in enumerate(bars):
        bx = x + 12 + i * (bw + 5)
        draw.rectangle([bx, y + h - 6 - bh, bx + bw, y + h - 6], fill=(255, 200, 60))
    f = font(22, bold=True)
    draw.text((x + w - 78, y + 4), "$83", font=f, fill=(255, 255, 255))


def draw_voyager(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(12, 14, 30))
    import random as _rnd
    rng = _rnd.Random(19)
    for _ in range(26):
        sx = x + rng.randint(2, w - 2)
        sy = y + rng.randint(2, h - 2)
        draw.point((sx, sy), fill=(255, 255, 255))
    cx, cy = x + w - 46, y + h // 2
    draw.line([(cx - 26, cy + 12), (cx, cy)], fill=(200, 210, 230), width=2)
    draw.polygon([(cx, cy - 8), (cx + 16, cy), (cx, cy + 8)], fill=(200, 210, 230))
    draw.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(255, 200, 60))
    f = font(9, bold=True)
    draw.text((x + 8, y + 5), "1 LIGHT-DAY", font=f, fill=(255, 220, 130))


def draw_cyclone(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 226, 238))
    cx, cy = x + w // 2, y + h // 2 - 2
    for r in (16, 11, 6):
        draw.arc([cx - r, cy - r, cx + r, cy + r], 200, 470, fill=(46, 74, 107), width=3)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(168, 50, 38))
    f = font(9, bold=True)
    draw.text((x + w - 78, y + h - 15), "90–100 KM/H", font=f, fill=(28, 25, 23))


def draw_modi(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 231, 217))
    # India: saffron / white / green bands
    draw.rectangle([x + 14, y + 8, x + 74, y + 16], fill=(255, 153, 51))
    draw.rectangle([x + 14, y + 16, x + 74, y + 24], fill=(255, 255, 255))
    draw.rectangle([x + 14, y + 24, x + 74, y + 32], fill=(19, 136, 8))
    # UK: simplified union jack
    draw.rectangle([x + w - 74, y + 8, x + w - 14, y + 32], fill=(36, 58, 120))
    draw.rectangle([x + w - 74, y + 17, x + w - 14, y + 23], fill=(255, 255, 255))
    draw.rectangle([x + w - 47, y + 8, x + w - 41, y + 32], fill=(255, 255, 255))
    draw.rectangle([x + w - 74, y + 19, x + w - 14, y + 21], fill=(200, 16, 46))
    draw.rectangle([x + w - 45, y + 8, x + w - 43, y + 32], fill=(200, 16, 46))
    f = font(9, bold=True)
    draw.text((x + w // 2 - 22, y + h - 14), "NEW DELHI", font=f, fill=(28, 25, 23))


def draw_defence(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 231, 217))
    draw.rectangle([x + 14, y + 8, x + 74, y + 16], fill=(255, 153, 51))
    draw.rectangle([x + 14, y + 16, x + 74, y + 24], fill=(255, 255, 255))
    draw.rectangle([x + 14, y + 24, x + 74, y + 32], fill=(19, 136, 8))
    draw.rectangle([x + w - 74, y + 8, x + w - 14, y + 32], fill=(255, 255, 255),
                   outline=(28, 25, 23))
    draw.ellipse([x + w - 56, y + 13, x + w - 32, y + 27], fill=(188, 0, 45))
    f = font(9, bold=True)
    draw.text((x + w // 2 - 16, y + h - 14), "TOKYO", font=f, fill=(28, 25, 23))


def draw_indigo(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(214, 226, 238))
    px, py = x + w // 2, y + 14
    draw.polygon([(px - 36, py), (px - 14, py - 5), (px + 6, py - 4), (px + 36, py - 8),
                  (px + 41, py - 6), (px + 14, py + 1), (px + 36, py + 7), (px + 32, py + 9),
                  (px - 4, py + 6), (px - 24, py + 7)],
                 fill=(28, 40, 80))
    f = font(9, bold=True)
    draw.text((x + 8, y + h - 13), "4 CITIES · TO 30 NOV", font=f, fill=(168, 50, 38))


def draw_berlin(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 231, 217))
    base = y + h - 4
    for cx in range(x + 30, x + w - 30, 26):
        draw.rectangle([cx, base - 26, cx + 9, base], fill=(90, 84, 70))
    draw.rectangle([x + 24, base - 34, x + w - 24, base - 26], fill=(120, 112, 96))
    draw.polygon([(x + 40, base - 34), (x + w // 2, base - 46), (x + w - 40, base - 34)],
                 fill=(120, 112, 96))
    f = font(9, bold=True)
    draw.text((x + 8, y + 4), "BERLIN", font=f, fill=(28, 25, 23))


def draw_cop(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 231, 217))
    tx = x + 26
    draw.rectangle([tx - 3, y + 6, tx + 3, y + h - 12], fill=(220, 220, 220),
                   outline=(28, 25, 23))
    draw.rectangle([tx - 3, y + 14, tx + 3, y + h - 12], fill=(168, 50, 38))
    draw.ellipse([tx - 8, y + h - 16, tx + 8, y + h - 2], fill=(168, 50, 38))
    f = font(11, bold=True)
    draw.text((x + 44, y + 6), "$120bn", font=f, fill=(28, 25, 23))
    f2 = font(9, bold=True)
    draw.text((x + 44, y + 22), "/YR BY 2035", font=f2, fill=(107, 101, 92))


def draw_alibaba(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(28, 32, 48))
    bars = [10, 16, 13, 22, 30]
    bw = 14
    for i, bh in enumerate(bars):
        bx = x + 12 + i * (bw + 6)
        col = (255, 140, 40) if i == len(bars) - 1 else (120, 140, 190)
        draw.rectangle([bx, y + h - 6 - bh, bx + bw, y + h - 6], fill=col)
    f = font(9, bold=True)
    draw.text((x + w - 96, y + 5), "QWEN4-MAX", font=f, fill=(255, 255, 255))


def draw_e1(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=(238, 231, 217))
    for i, (bx, by, s) in enumerate([(14, 14, 12), (32, 10, 10), (48, 16, 12),
                                     (66, 10, 9), (82, 15, 11)]):
        draw.rectangle([x + bx, y + by, x + bx + s, y + by + s], fill=(140, 130, 110),
                       outline=(90, 84, 70))
    px, py = x + w - 34, y + 10
    draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(168, 50, 38))
    draw.ellipse([px - 12, py - 12, px + 12, py + 12], outline=(168, 50, 38), width=2)
    f = font(9, bold=True)
    draw.text((x + 8, y + h - 15), "DECISION DUE TODAY", font=f, fill=(28, 25, 23))


CARD_ART = {"anthropic": draw_anthropic, "voyager": draw_voyager,
            "cyclone": draw_cyclone, "modi": draw_modi,
            "defence": draw_defence, "indigo": draw_indigo,
            "berlin": draw_berlin, "cop": draw_cop,
            "alibaba": draw_alibaba, "e1": draw_e1}

# ------------------------------------------------------------- world map
# Simplified continent outlines (lon, lat), drawn equirectangular.
CONTINENTS = {
    "N. America": [(-168, 66), (-150, 70), (-130, 71), (-115, 72), (-100, 73),
                   (-88, 70), (-80, 66), (-70, 62), (-60, 55), (-55, 47),
                   (-65, 44), (-75, 38), (-81, 31), (-84, 30), (-90, 21),
                   (-97, 16), (-105, 20), (-114, 28), (-124, 40), (-124, 49),
                   (-140, 60), (-155, 58), (-165, 60)],
    "S. America": [(-80, 10), (-76, 6), (-66, 2), (-58, -2), (-50, -4),
                   (-38, -6), (-36, -12), (-40, -20), (-48, -28), (-56, -35),
                   (-64, -42), (-70, -52), (-73, -44), (-73, -32), (-72, -20),
                   (-77, -8), (-81, -2), (-80, 6)],
    "Europe": [(-10, 36), (-9, 43), (-2, 48), (0, 50), (4, 53), (8, 57),
               (12, 55), (18, 56), (21, 60), (24, 64), (28, 68), (32, 70),
               (38, 66), (42, 60), (36, 55), (30, 52), (28, 46), (24, 42),
               (20, 40), (14, 38), (8, 38), (2, 37), (-4, 36)],
    "Africa": [(-17, 15), (-16, 24), (-10, 30), (-4, 35), (8, 37), (16, 33),
               (24, 32), (30, 31), (34, 28), (38, 22), (42, 15), (46, 11),
               (51, 12), (46, 4), (41, -2), (40, -10), (36, -18), (32, -26),
               (26, -33), (19, -35), (16, -30), (13, -20), (12, -8), (9, 0),
               (9, 5), (-6, 5), (-13, 8), (-17, 12)],
    "Asia": [(38, 70), (52, 72), (66, 72), (80, 73), (95, 76), (110, 77),
             (125, 75), (140, 72), (155, 70), (170, 68), (178, 65), (170, 60),
             (160, 58), (156, 51), (142, 46), (135, 40), (128, 34), (122, 30),
             (118, 24), (110, 20), (106, 10), (101, 8), (97, 12), (93, 18),
             (89, 22), (85, 19), (80, 14), (76, 9), (73, 16), (68, 22),
             (62, 25), (56, 27), (51, 29), (47, 30), (42, 34), (38, 38),
             (36, 44), (36, 52), (36, 62)],
    "Oceania": [(113, -22), (114, -30), (115, -34), (122, -34), (129, -32),
                (135, -35), (140, -38), (147, -39), (150, -37), (153, -32),
                (153, -27), (148, -20), (143, -15), (142, -11), (137, -12),
                (132, -12), (127, -14), (122, -17), (116, -20)],
}


def lonlat_to_xy(lon, lat, x, y, w, h):
    fx = (lon + 170.0) / 360.0
    fy = (78.0 - lat) / 136.0
    return x + fx * w, y + fy * h


def draw_map(draw, x, y, w, h):
    draw.rectangle([x, y, x + w, y + h], fill=SEA, outline=(180, 174, 158))
    for pts in CONTINENTS.values():
        xy = [lonlat_to_xy(lon, lat, x, y, w, h) for lon, lat in pts]
        draw.polygon(xy, fill=LAND, outline=LAND_EDGE)
    # brief dots first (under the numbered pins)
    for n, _head, lon, lat in BRIEFS:
        px, py = lonlat_to_xy(lon, lat, x, y, w, h)
        draw.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(90, 84, 70))
    for story in FEATURES + CARDS:
        px, py = lonlat_to_xy(story["lon"], story["lat"], x, y, w, h)
        badge(draw, px, py, 8, story["n"], fill=BLUE)

# ------------------------------------------------------------ layout
# Region / field for each brief (features and cards carry their own).
BRIEF_META = {
    14: ("N. AMERICA", "Markets"), 15: ("N. AMERICA", "Markets"),
    16: ("N. AMERICA", "Markets"), 17: ("WORLD", "Markets"),
    18: ("ASIA", "Markets"), 19: ("ASIA", "Markets"),
    20: ("EUROPE", "Markets"), 21: ("N. AMERICA", "Markets"),
    22: ("ASIA", "Markets"), 23: ("N. AMERICA", "Markets"),
    24: ("ASIA", "Markets"), 25: ("ASIA", "Markets"),
    26: ("N. AMERICA", "Markets"), 27: ("N. AMERICA", "Sport"),
    28: ("ASIA", "Sport"), 29: ("ASIA", "Sport"),
    30: ("EUROPE", "Politics"), 31: ("WORLD", "Politics"),
    32: ("ASIA", "Politics"), 33: ("N. AMERICA", "Politics"),
    34: ("ASIA", "Politics"), 35: ("ASIA", "World"),
    36: ("ASIA", "World"), 37: ("OCEANIA", "Culture"),
    39: ("EUROPE", "Markets"), 40: ("OCEANIA", "World"),
}

MARGIN = 16
RIGHT = W - MARGIN


def check_counts():
    regions = {r: 0 for r in REGION_ORDER}
    fields = {f: 0 for f in FIELD_ORDER}
    for s in FEATURES + CARDS:
        regions[s["region"]] += 1
        fields[s["field"]] += 1
    for n, _h, _lo, _la in BRIEFS:
        r, f = BRIEF_META[n]
        regions[r] += 1
        fields[f] += 1
    assert sum(regions.values()) == 39, regions
    assert sum(fields.values()) == 39, fields
    assert regions == {"ASIA": 18, "N. AMERICA": 10, "EUROPE": 6,
                       "WORLD": 3, "OCEANIA": 2}, regions
    assert fields == {"Politics": 10, "Markets": 15, "Tech": 3,
                      "World": 6, "Sport": 3, "Culture": 2}, fields
    assert len(BRIEFS) == 26
    assert [n for n, _, _, _ in BRIEFS] == [14, 15, 16, 17, 18, 19, 20, 21,
                                            22, 23, 24, 25, 26, 27, 28, 29,
                                            30, 31, 32, 33, 34, 35, 36, 37,
                                            39, 40]


def draw_masthead(draw):
    title = "THE WORLD IN ONE DAY"
    f = font(40, bold=True, serif=True)
    draw.text(((W - draw.textlength(title, font=f)) / 2, 8), title, font=f, fill=INK)
    date = "THURSDAY 19 NOVEMBER 2026"
    f2 = font(44, bold=True, serif=True)
    draw.text(((W - draw.textlength(date, font=f2)) / 2, 54), date, font=f2, fill=RED)
    sub = ("Everything on this page happened, or was first reported, "
           "on Thursday 19 November 2026.")
    f3 = font(13)
    draw.text(((W - draw.textlength(sub, font=f3)) / 2, 104), sub, font=f3, fill=MUTED)
    rule(draw, MARGIN, 124, RIGHT, width=3)
    rule(draw, MARGIN, 129, RIGHT, width=1)
    return 136


def draw_strip(draw, label, counts, colors, y):
    f_lab = font(10, bold=True)
    draw.text((MARGIN, y + 2), label, font=f_lab, fill=INK)
    total = sum(c for _, c in counts)
    bx, bw, bh = 112, RIGHT - 112, 16
    x = float(bx)
    for name, c in counts:
        seg = bw * c / total
        draw.rectangle([x, y, x + seg, y + bh], fill=colors[name])
        x += seg
    draw.rectangle([bx, y, bx + bw, y + bh], outline=INK, width=1)
    lx = bx
    f_leg = font(9)
    for name, c in counts:
        draw.rectangle([lx, y + 22, lx + 9, y + 31], fill=colors[name], outline=INK)
        txt = "%s %d" % (name, c)
        draw.text((lx + 13, y + 21), txt, font=f_leg, fill=INK)
        lx += 13 + draw.textlength(txt, font=f_leg) + 18
    return y + 38


def region_counts():
    regions = {r: 0 for r in REGION_ORDER}
    for s in FEATURES + CARDS:
        regions[s["region"]] += 1
    for n, _, _, _ in BRIEFS:
        regions[BRIEF_META[n][0]] += 1
    return [(r, regions[r]) for r in REGION_ORDER]


def field_counts():
    fields = {f: 0 for f in FIELD_ORDER}
    for s in FEATURES + CARDS:
        fields[s["field"]] += 1
    for n, _, _, _ in BRIEFS:
        fields[BRIEF_META[n][1]] += 1
    return [(f, fields[f]) for f in FIELD_ORDER]


def draw_numbers(draw, y):
    f_lab = font(10, bold=True)
    draw.text((MARGIN, y), "THE DAY IN NUMBERS", font=f_lab, fill=INK)
    rule(draw, MARGIN, y + 16, RIGHT, width=1)
    cell_w = (RIGHT - MARGIN) / 6.0
    for i, (lab, val, sub) in enumerate(NUMBERS):
        cx = MARGIN + i * cell_w
        draw.text((cx + 2, y + 22), val, font=font(16, bold=True, serif=True), fill=INK)
        draw.text((cx + 2, y + 44), lab, font=font(9, bold=True), fill=RED)
        draw.text((cx + 2, y + 56), sub, font=font(8), fill=MUTED)
        if i:
            draw.line([(cx, y + 22), (cx, y + 66)], fill=(210, 204, 190), width=1)
    return y + 68


def draw_features(draw, y):
    h = 180
    pw = 326
    for i, s in enumerate(FEATURES):
        x = MARGIN + i * (pw + 7)
        draw.rectangle([x, y, x + pw, y + h], fill=CARD_BG, outline=INK, width=1)
        FEATURE_ART[s["kind"]](draw, x + 1, y + 1, pw - 2, 96)
        badge(draw, x + 16, y + 110, 11, s["n"], fill=RED)
        draw.text((x + 32, y + 101), s["kicker"], font=font(9, bold=True), fill=RED)
        head_lines = wrap(draw, s["head"], font(15, bold=True, serif=True), pw - 16)
        assert len(head_lines) <= 2, (s["n"], head_lines)
        draw_lines(draw, head_lines, x + 8, y + 118, font(15, bold=True, serif=True),
                   leading=18)
        body_lines = wrap(draw, s["body"], font(10), pw - 16)
        assert len(body_lines) <= 2, (s["n"], body_lines)
        draw_lines(draw, body_lines, x + 8, y + 154, font(10), leading=13)
    return y + h


def draw_cards(draw, y):
    h = 100
    cw = 193
    step = 199
    for row in range(2):
        for col in range(5):
            s = CARDS[row * 5 + col]
            x = MARGIN + col * step
            yy = y + row * (h + 6)
            draw.rectangle([x, yy, x + cw, yy + h], fill=CARD_BG, outline=INK, width=1)
            CARD_ART[s["kind"]](draw, x + 1, yy + 1, cw - 2, 38)
            badge(draw, x + 13, yy + 53, 9, s["n"], fill=BLUE)
            head_lines = wrap(draw, s["head"], font(11, bold=True), cw - 32)
            assert len(head_lines) <= 2, (s["n"], head_lines)
            draw_lines(draw, head_lines, x + 27, yy + 42, font(11, bold=True),
                       leading=12)
            body_lines = wrap(draw, s["body"], font(9), cw - 12)
            assert len(body_lines) <= 2, (s["n"], body_lines)
            draw_lines(draw, body_lines, x + 6, yy + 69, font(9), leading=10)
    return y + 2 * h + 6


def draw_bottom(draw, y):
    # Left: world map. Right: ALSO list (2 columns x 13).
    rule(draw, MARGIN, y, RIGHT, width=1)
    y += 6
    f_lab = font(10, bold=True)
    draw.text((MARGIN, y), "WHERE IT HAPPENED", font=f_lab, fill=INK)
    draw.text((536, y), "ALSO — 26 MORE STORIES", font=f_lab, fill=INK)
    map_x, map_y, map_w, map_h = MARGIN, y + 20, 504, 190
    draw_map(draw, map_x, map_y, map_w, map_h)
    cap = ("Pins 1–13 mark the features and cards; "
           "dots mark the briefs 14–40.")
    cap_lines = wrap(draw, cap, font(9), map_w)
    draw_lines(draw, cap_lines, map_x, map_y + map_h + 6, font(9),
               fill=MUTED, leading=12)
    col_w = 230
    for ci in range(2):
        cx = 536 + ci * (col_w + 12)
        items = BRIEFS[ci * 13:(ci + 1) * 13]
        iy = map_y
        for n, head, _lo, _la in items:
            txt = "%d. %s" % (n, head)
            assert draw.textlength(txt, font=font(9)) <= col_w, txt
            draw.text((cx, iy), txt, font=font(9), fill=INK)
            iy += 16
    return y + 20 + map_h + 28


def draw_datecheck(draw, y):
    draw.rectangle([MARGIN, y, RIGHT, y + 40], fill=STRIP_BG, outline=INK, width=1)
    lines = wrap(draw, DATE_CHECK, font(9), RIGHT - MARGIN - 16)
    assert len(lines) <= 2, lines
    draw_lines(draw, lines, MARGIN + 8, y + 5, font(9), leading=12)
    return y + 46


def draw_footer(draw, y):
    f = font(8)
    line1 = ("Sources: Rockstar Support · PlayStation Blog · Reuters · AP · NASA · "
             "The Hindu · Le Monde · TradingView · MarketWatch · Inc.com · cricbuzz · "
             "Times of India · and others.")
    line2 = ("All stories happened or were first reported on Thursday 19 November 2026; "
             "market briefs use 18 Nov closes as reported on the morning of 19 Nov.")
    draw.text((MARGIN, y), line1, font=f, fill=MUTED)
    draw.text((MARGIN, y + 11), line2, font=f, fill=MUTED)
    return y + 26


def build():
    check_counts()
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)
    y = draw_masthead(draw)
    y = draw_strip(draw, "BY REGION", region_counts(), REGION_COLORS, y + 4)
    y = draw_strip(draw, "BY FIELD", field_counts(), FIELD_COLORS, y + 2)
    y = draw_numbers(draw, y + 4)
    y = draw_features(draw, y + 4)
    y = draw_cards(draw, y + 4)
    y = draw_bottom(draw, y + 8)
    y = draw_datecheck(draw, y + 6)
    y = draw_footer(draw, y + 4)
    assert y <= H - 4, y
    return img


def main():
    img = build()
    img.save(OUT, format="PNG")
    data = open(OUT, "rb").read()
    assert len(data) < 1048576, len(data)
    print("wrote %s %d bytes sha256 %s" % (OUT, len(data),
                                           hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
