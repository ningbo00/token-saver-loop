"""Render the README workflow demo GIF.

The HTML source in docs/assets/demo-loop-animation.html is the web animation.
This script draws matching frames directly with Pillow so rendering does not
depend on a browser being installed.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets" / "token-saver-loop-demo.gif"
WIDTH = 980
HEIGHT = 440
FRAME_COUNT = 36
FRAME_MS = 90


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path("C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


TITLE = font(30, True)
SUBTITLE = font(16)
CARD_TITLE = font(21, True)
BODY = font(15)
BODY_SMALL = font(14)
LABEL = font(16, True)


def lerp(a: int, b: int, t: float) -> int:
    return round(a + (b - a) * t)


def mix(c1: str, c2: str, t: float) -> str:
    c1 = c1.lstrip("#")
    c2 = c2.lstrip("#")
    parts = []
    for i in range(0, 6, 2):
        parts.append(lerp(int(c1[i : i + 2], 16), int(c2[i : i + 2], 16), t))
    return "#%02x%02x%02x" % tuple(parts)


def rounded(draw: ImageDraw.ImageDraw, xy: tuple[int, int, int, int], radius: int, fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)


def arrow(draw: ImageDraw.ImageDraw, x1: int, y: int, x2: int, color: str, width: int = 4) -> None:
    draw.line((x1, y, x2 - 12, y), fill=color, width=width)
    draw.polygon([(x2 - 12, y - 8), (x2 + 2, y), (x2 - 12, y + 8)], fill=color)


def card(draw: ImageDraw.ImageDraw, x: int, y: int, title: str, lines: list[str], fill: str, stroke: str, active: float) -> None:
    lift = round(-5 * active)
    bright_fill = mix(fill, "#ffffff", 0.10 * active)
    xy = (x, y + lift, x + 250, y + lift + 142)
    rounded(draw, xy, 12, bright_fill, stroke, 2)
    draw.text((x + 22, y + lift + 28), title, fill="#ffffff", font=CARD_TITLE)
    for index, line in enumerate(lines):
        draw.text((x + 22, y + lift + 63 + index * 26), line, fill="#f8fafc", font=BODY)


def active_for(frame: int, center: float, spread: float = 4.0) -> float:
    distance = min(abs(frame - center), abs(frame + FRAME_COUNT - center), abs(frame - FRAME_COUNT - center))
    return max(0.0, 1.0 - distance / spread)


def frame_image(i: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), "#0b1220")
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        t = y / HEIGHT
        color = mix("#0b1220", "#111827", t)
        draw.line((0, y, WIDTH, y), fill=color)

    rounded(draw, (26, 26, 954, 414), 16, "#0f172a", "#334155", 1)
    draw.text((56, 36), "Token Saver Loop", fill="#ffffff", font=TITLE)
    draw.text(
        (56, 85),
        "Keep premium models focused on judgment. Move execution noise into bounded worker rounds.",
        fill="#dbeafe",
        font=SUBTITLE,
    )

    card(
        draw,
        56,
        142,
        "Reviewer model",
        ["Plans one small round", "Sets scope and tests", "Owns final acceptance"],
        "#1e3a8a",
        "#93c5fd",
        active_for(i, 3),
    )
    arrow(draw, 318, 213, 354, "#e5e7eb")
    card(
        draw,
        365,
        142,
        "Worker model",
        ["Executes bounded task", "Runs commands and tests", "Writes compact evidence"],
        "#166534",
        "#86efac",
        active_for(i, 12),
    )
    arrow(draw, 627, 213, 663, "#e5e7eb")
    card(
        draw,
        674,
        142,
        "Reviewer verdict",
        ["PASS: accept and continue", "FIX: retry same tier", "STOP: human decision"],
        "#581c87",
        "#d8b4fe",
        active_for(i, 21),
    )

    loop_active = active_for(i, 30, 8)
    loop_color = mix("#b45309", "#fbbf24", loop_active)
    draw.line((800, 297, 800, 333, 181, 333, 181, 302), fill=loop_color, width=5, joint="curve")
    draw.polygon([(181, 294), (172, 306), (190, 306)], fill=loop_color)
    rounded(draw, (416, 313, 564, 353), 20, "#451a03", loop_color, 2)
    draw.text((446, 323), "next round", fill="#ffffff", font=LABEL)

    rounded(draw, (56, 366, 924, 396), 8, "#020617", "#475569", 1)
    draw.text(
        (78, 374),
        "The expensive model reviews compact evidence each loop, not the whole execution transcript.",
        fill="#e5e7eb",
        font=BODY_SMALL,
    )

    return img


def main() -> None:
    frames = [frame_image(i) for i in range(FRAME_COUNT)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        OUT,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
    )
    print(OUT)


if __name__ == "__main__":
    main()
