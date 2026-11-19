#!/usr/bin/env python3
"""news-image-20261118: draw a one-day world-news poster for Wednesday,
18 November 2026, as a 1024x1024 PNG.

Python 3 standard library only. No network, no randomness, no timestamps:
running it twice writes byte-identical output.

The poster is drawn from scratch with a hand-made 5x7 bitmap font and a
hand-rolled PNG encoder. All facts on the poster come from news reports of
18 November 2026 (events announced 17 Nov US time and widely reported
18 Nov are framed as the news of 18 November, without mis-dating them).
"""

import os
import struct
import sys
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (245, 240, 230)   # warm newsprint
INK = (26, 26, 26)
NAVY = (22, 35, 63)
NAVY_LT = (38, 58, 96)
RED = (180, 35, 24)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
GREY = (110, 105, 95)
BORDER = (216, 210, 196)
SEA = (156, 195, 213)
LAND = (222, 205, 168)
LAND_DK = (205, 186, 145)
BLUE = (29, 78, 137)
GREEN = (46, 125, 50)
PURPLE = (91, 74, 138)
ORANGE = (192, 86, 33)

# ---------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 characters, '#' = ink, '.' = empty.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01111", "10000", "10000", "10111", "10001", "10001", "01110"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "11001", "10101", "10011", "10011", "10001"),
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
    '0': ("01110", "10011", "10101", "11001", "10001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00010", "00100", "01000", "11111"),
    '3': ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("01110", "10000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "00100", "00100", "00100"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00001", "01110"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "01100", "01000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '&': ("01100", "10010", "10010", "01000", "10101", "10010", "01101"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    ':': ("00000", "00000", "01100", "00000", "00000", "01100", "00000"),
    ';': ("00000", "00000", "01100", "00000", "01100", "01100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00010", "00100", "00000", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00001", "00010", "00100", "01000", "10000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "10101", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "01110", "00000", "01110", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    '~': ("00000", "00000", "01010", "10101", "00000", "00000", "00000"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}


def text_width(text, scale):
    """Pixel width of text at the given scale (glyph 5px + 1px gap)."""
    return len(text) * 6 * scale - scale if text else 0


def wrap(text, max_width, scale):
    """Word-wrap text into lines fitting max_width pixels at scale."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split(" ")
        cur = ""
        for word in words:
            trial = word if not cur else cur + " " + word
            if text_width(trial, scale) <= max_width:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def rect_border(self, x, y, w, h, color, t=1):
        self.fill_rect(x, y, w, t, color)
        self.fill_rect(x, y + h - t, w, t, color)
        self.fill_rect(x, y, t, h, color)
        self.fill_rect(x + w - t, y, t, h, color)

    def hline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, length, t, color)

    def vline(self, x, y, length, color, t=1):
        self.fill_rect(x, y, t, length, color)

    def fill_circle(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, color)

    def draw_star(self, cx, cy, r, color):
        # 8-spike marker: 4 straight + 4 diagonal lines through the centre.
        for dy in range(-r, r + 1):
            self.set(cx, cy + dy, color)
            self.set(cx + dy, cy, color)
            self.set(cx + dy, cy + dy, color)
            self.set(cx + dy, cy - dy, color)

    def draw_glyph(self, x, y, ch, scale, color):
        glyph = FONT.get(ch)
        if glyph is None:
            glyph = FONT['?']
        for row, bits in enumerate(glyph):
            for col, bit in enumerate(bits):
                if bit == '1':
                    self.fill_rect(x + col * scale, y + row * scale,
                                   scale, scale, color)

    def draw_text(self, x, y, text, scale, color):
        cx = x
        for ch in text:
            self.draw_glyph(cx, y, ch, scale, color)
            cx += 6 * scale
        return cx

    def draw_text_centered(self, cx, y, text, scale, color):
        x = cx - text_width(text, scale) // 2
        self.draw_text(x, y, text, scale, color)
        return x

    def draw_lines(self, x, y, lines, scale, color, leading=None):
        if leading is None:
            leading = 7 * scale + 6
        for line in lines:
            self.draw_text(x, y, line, scale, color)
            y += leading
        return y


# ---------------------------------------------------------------- PNG encode
def png_bytes(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)  # filter: none
        raw += canvas.px[y * stride:(y + 1) * stride]
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


# ---------------------------------------------------------------- poster
def build():
    c = Canvas(W, H, PAPER)

    # ---- masthead ------------------------------------------------------
    c.fill_rect(0, 0, W, 120, NAVY)
    c.fill_rect(0, 120, W, 6, GOLD)
    c.draw_text_centered(W // 2, 42, "WEDNESDAY, 18 NOVEMBER 2026", 5, WHITE)

    # ---- main story: war in the Gulf -----------------------------------
    c.draw_text(32, 152, "WAR IN THE GULF", 3, RED)
    c.hline(32, 188, 264, RED, 3)
    c.draw_text(32, 206, "US STRIKES IRAN", 4, INK)
    c.draw_text(32, 246, "AS TEHRAN HITS", 4, INK)
    c.draw_text(32, 286, "KUWAIT & BAHRAIN", 4, INK)

    main_facts = (
        "US HITS IRGC MISSILE SITES ON QESHM ISLAND, STRAIT OF "
        "HORMUZ, 17 NOV. KUWAIT AND BAHRAIN INTERCEPT IRANIAN DRONE "
        "ATTACKS, 18 NOV. WAR SINCE 28 FEB 2026. "
        "BRENT CRUDE $92.76 A BARREL."
    )
    lines = wrap(main_facts, 640, 2)
    c.draw_lines(32, 340, lines, 2, INK, leading=22)

    # ---- schematic map of the Gulf (right of the main story) -----------
    mx, my, mw, mh = 700, 150, 292, 268
    c.rect_border(mx, my, mw, mh, NAVY, 2)
    c.fill_rect(mx + 2, my + 2, mw - 4, mh - 4, SEA)
    # land: Iran (top) and Arabia (bottom)
    c.fill_rect(mx + 2, my + 2, mw - 4, 62, LAND)
    c.fill_rect(mx + 2, my + 168, mw - 4, mh - 170, LAND)
    # Qeshm island: small land strip in the sea near the strait
    c.fill_rect(mx + 150, my + 96, 92, 14, LAND_DK)
    # strait gap (right edge, sea cuts between the lands)
    c.fill_rect(mx + mw - 46, my + 64, 44, 104, SEA)
    c.draw_text(mx + 12, my + 12, "IRAN", 2, INK)
    c.draw_text(mx + 12, my + 178, "ARABIA", 2, INK)
    c.draw_text(mx + 12, my + 96, "PERSIAN GULF", 1, NAVY_LT)
    # strike / intercept markers
    c.draw_star(mx + 196, my + 103, 9, RED)
    c.draw_text(mx + 216, my + 99, "QESHM", 1, RED)
    c.draw_star(mx + 96, my + 128, 9, RED)
    c.draw_text(mx + 40, my + 144, "BAHRAIN", 1, RED)
    c.draw_star(mx + 62, my + 84, 9, RED)
    # KUWAIT label sits level with the star centre (was 15 px higher, where
    # its bottom edge came within ~2 px of the star's top spike).
    c.draw_text(mx + 8, my + 81, "KUWAIT", 1, RED)
    c.draw_text(mx + mw - 44, my + 120, "HORMUZ", 1, NAVY_LT)
    c.draw_text_centered(mx + mw // 2, my + mh + 10,
                         "THE GULF - SCHEMATIC MAP", 1, GREY)
    c.draw_text(32, 446, "AMERICA AND ISRAEL AT WAR WITH IRAN SINCE FEBRUARY.",
                1, GREY)

    c.hline(32, 472, W - 64, BORDER, 2)

    # ---- second story: APEC Shenzhen ------------------------------------
    c.draw_text(32, 494, "APEC SHENZHEN", 3, BLUE)
    c.hline(32, 530, 264, BLUE, 3)
    c.draw_text(32, 548, "XI MEETS PUTIN AHEAD OF FIRST-EVER", 3, INK)
    c.draw_text(32, 580, "TRUMP TRILATERAL", 3, INK)
    c.draw_text(32, 616,
                "FIRST TRILATERAL SUMMIT WITH TRUMP SET FOR 19 NOV IN SHENZHEN.",
                2, INK)

    c.hline(32, 650, W - 64, BORDER, 2)

    # ---- also on 18 November: five small panels ------------------------
    c.draw_text(16, 668, "ALSO ON 18 NOVEMBER", 2, NAVY)
    c.hline(16, 690, W - 32, NAVY, 2)

    panels = [
        # (label, fact, accent)
        ("KERCH BRIDGE DOWN",
         "ROAD ARCH TO CRIMEA DESTROYED. SPAN OF ABOUT 227 M COLLAPSES "
         "16-17 NOV; 2 KILLED.",
         RED),
        ("DEMOCRATS TAKE THE SENATE 56-44",
         "PELTOLA FLIPS ALASKA, ABOUT 50.1% TO 45.8% IN A RANKED-CHOICE "
         "VOTE.",
         BLUE),
        ("NVIDIA $115.8B",
         "RECORD QUARTER: REVENUE $115.8B, UP 103% YOY; Q4 GUIDANCE "
         "$130B.",
         GREEN),
        ("VOYAGER 1",
         "ONE LIGHT-DAY FROM EARTH AT 05:16 EST - ABOUT 16.1 BILLION "
         "MILES. A FIRST IN HISTORY.",
         PURPLE),
        ("CYCLONE AKVAN",
         "ANDHRA BRACES FOR LANDFALL AROUND 20 NOV; WINDS 120-130 KM/H.",
         ORANGE),
    ]

    # row 1: three panels; row 2: two wider panels
    row1 = [(16, 702, 320, 148), (344, 702, 320, 148), (672, 702, 320, 148)]
    row2 = [(16, 862, 488, 138), (520, 862, 488, 138)]
    slots = row1 + row2

    for (label, fact, accent), (px, py, pw, ph) in zip(panels, slots):
        c.fill_rect(px, py, pw, ph, WHITE)
        c.rect_border(px, py, pw, ph, BORDER, 1)
        c.fill_rect(px, py, pw, 8, accent)
        inner = pw - 32
        label_lines = wrap(label, inner, 2)
        y = py + 20
        for line in label_lines:
            c.draw_text(px + 16, y, line, 2, accent)
            y += 20
        y += 6
        fact_lines = wrap(fact, inner, 2)
        c.draw_lines(px + 16, y, fact_lines, 2, INK, leading=20)

    # ---- footer ---------------------------------------------------------
    c.draw_text_centered(W // 2, 1008,
                         "DRAWN BY CODE FROM REPORTS OF 18 NOVEMBER 2026",
                         1, GREY)
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    data = png_bytes(build())
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
