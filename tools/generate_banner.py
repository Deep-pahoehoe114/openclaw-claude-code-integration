#!/usr/bin/env python3
"""Generate a bilingual GitHub banner for OECK."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
PNG_PATH = ASSETS / "oeck-github-banner.png"
PHILOSOPHY_PATH = ASSETS / "oeck-visual-philosophy.md"

WIDTH = 1280
HEIGHT = 640


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        f"/System/Library/Fonts/Supplemental/{name}",
        f"/System/Library/Fonts/{name}",
        f"/Library/Fonts/{name}",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(HEIGHT):
        t = y / HEIGHT
        r = int(17 + (43 - 17) * t)
        g = int(28 + (47 - 28) * t)
        b = int(33 + (58 - 33) * t)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))


def add_mesh_orbs(base: Image.Image) -> None:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    orbs = [
        ((220, 170), 320, (255, 129, 72, 110)),
        ((1030, 130), 260, (63, 200, 219, 95)),
        ((960, 470), 360, (255, 209, 102, 60)),
        ((180, 520), 260, (109, 76, 255, 50)),
    ]
    for center, radius, color in orbs:
        x, y = center
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(48))
    base.alpha_composite(overlay)


def add_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, WIDTH, 48):
        alpha = 22 if x % 192 else 38
        draw.line((x, 0, x, HEIGHT), fill=(255, 255, 255, alpha), width=1)
    for y in range(0, HEIGHT, 48):
        alpha = 18 if y % 192 else 30
        draw.line((0, y, WIDTH, y), fill=(255, 255, 255, alpha), width=1)


def add_topographic_lines(draw: ImageDraw.ImageDraw) -> None:
    for offset in range(7):
        points = []
        for x in range(-20, WIDTH + 20, 18):
            wave = math.sin((x / 145.0) + offset * 0.65) * (18 + offset * 5)
            drift = math.cos((x / 320.0) - offset * 0.4) * 9
            y = 90 + offset * 42 + wave + drift
            points.append((x, y))
        draw.line(points, fill=(255, 255, 255, 36), width=2)

    for offset in range(6):
        points = []
        for x in range(-20, WIDTH + 20, 16):
            wave = math.sin((x / 120.0) + offset * 0.82) * (16 + offset * 4)
            drift = math.cos((x / 270.0) + offset * 0.5) * 13
            y = 430 + offset * 24 + wave + drift
            points.append((x, y))
        draw.line(points, fill=(106, 217, 227, 30), width=2)


def add_architecture_nodes(draw: ImageDraw.ImageDraw) -> None:
    nodes = [
        ((136, 530), "Content"),
        ((306, 446), "Runtime"),
        ((484, 524), "Policy"),
        ((676, 416), "Adapters"),
        ((906, 512), "Checks"),
        ((1112, 414), "Bundles"),
    ]
    for idx, ((x, y), label) in enumerate(nodes):
        next_node = nodes[idx + 1][0] if idx + 1 < len(nodes) else None
        if next_node:
            draw.line((x, y, next_node[0], next_node[1]), fill=(255, 255, 255, 55), width=3)
            draw.line((x, y, next_node[0], next_node[1]), fill=(63, 200, 219, 35), width=7)
        draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill=(255, 211, 138, 255))
        draw.ellipse((x - 20, y - 20, x + 20, y + 20), outline=(255, 255, 255, 55), width=2)
        draw.text((x + 18, y - 11), label, fill=(222, 233, 237, 210), font=load_font("Avenir Next.ttc", 22))


def add_badge(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, fill: tuple[int, int, int, int]) -> None:
    font = load_font("Avenir Next.ttc", 22)
    left, top = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0] + 34
    height = bbox[3] - bbox[1] + 18
    draw.rounded_rectangle((left, top, left + width, top + height), radius=16, fill=fill, outline=(255, 255, 255, 42), width=1)
    draw.text((left + 17, top + 8), text, fill=(249, 250, 251, 255), font=font)


def add_mode_chip(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str) -> int:
    font = load_font("Avenir Next.ttc", 18)
    left, top = xy
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0] + 26
    height = bbox[3] - bbox[1] + 14
    draw.rounded_rectangle(
        (left, top, left + width, top + height),
        radius=14,
        fill=(12, 22, 31, 214),
        outline=(255, 255, 255, 42),
        width=1,
    )
    draw.text((left + 13, top + 6), text, fill=(235, 239, 241, 248), font=font)
    return width


def write_philosophy() -> None:
    text = """# Signal Atlas

Signal Atlas is a visual philosophy for software infrastructure that should feel less like a banner and more like an engineered artifact. Space is treated as a control surface: dense in a few deliberate regions, quiet everywhere else. The composition should look meticulously crafted, with every interval tuned until the graphic reads as a confident product signal rather than a decorative splash.

Color behaves like routed energy. Warm ember tones indicate governance and decisive intervention; cool cyan fields imply compatibility, context flow, and runtime continuity. These two systems should stay in productive tension, calibrated with painstaking attention so the image feels stable, technical, and deeply intentional rather than loud.

Geometry should suggest maps, traces, and layered protocols. Lines drift like topographic telemetry, while nodes and capsules imply host targets, policy checkpoints, and distribution surfaces. Every curve and connector should look labored over by someone operating at master level, with no casual ornament and no accidental complexity.

Typography is sparse and architectural. The title carries authority, the supporting labels behave like instrumentation, and bilingual text is used as a precision accent instead of exposition. The final work should feel like the result of deep expertise: meticulously crafted, restrained, and unmistakably product-grade.

The overall mood is optimistic without becoming soft. It should read as a compatibility kit that brings order to multiple hosts, not as a chaotic hacker collage. Negative space, layering, and pacing must all communicate control. The finished banner should look like it took countless hours of refinement and that every visual decision received painstaking care.
"""
    PHILOSOPHY_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    write_philosophy()

    image = Image.new("RGBA", (WIDTH, HEIGHT), (14, 18, 24, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    draw_gradient(draw)
    add_mesh_orbs(image)
    draw = ImageDraw.Draw(image, "RGBA")
    add_grid(draw)
    add_topographic_lines(draw)

    left_panel = [(54, 68), (676, 68), (618, 572), (54, 572)]
    right_panel = [(734, 86), (1228, 86), (1228, 572), (804, 572)]
    draw.polygon(left_panel, fill=(8, 12, 18, 122), outline=(255, 255, 255, 36))
    draw.polygon(right_panel, fill=(8, 12, 18, 112), outline=(255, 255, 255, 30))

    eyebrow_font = load_font("Avenir Next.ttc", 24)
    title_font = load_font("BigCaslon.ttf", 58)
    sub_font = load_font("Avenir Next.ttc", 28)
    cn_font = load_font("Hiragino Sans GB.ttc", 24)

    draw.text((92, 104), "OPENCLAW ENHANCEMENT & COMPATIBILITY KIT", fill=(255, 206, 160, 255), font=eyebrow_font)
    draw.text((92, 154), "Governance, compatibility,\nand runtime enhancement.", fill=(248, 248, 246, 255), font=title_font, spacing=4)
    draw.text((95, 325), "统一策略 · 统一上下文 · 统一分发 · 统一观测 · 统一适配器", fill=(202, 227, 230, 228), font=cn_font)
    draw.text((95, 366), "For OpenClaw / Claude / Codex", fill=(231, 236, 238, 230), font=sub_font)

    add_badge(draw, (92, 446), "OpenClaw Native Plugin", (255, 132, 81, 112))
    add_badge(draw, (92, 500), "Claude Bundle", (63, 200, 219, 104))
    add_badge(draw, (295, 500), "Codex Bundle", (72, 119, 255, 96))

    add_architecture_nodes(draw)

    draw.rounded_rectangle((820, 150, 1176, 252), radius=30, fill=(10, 17, 24, 214), outline=(255, 255, 255, 58), width=2)
    draw.text((850, 176), "Mode Profiles", fill=(255, 209, 169, 255), font=load_font("Avenir Next.ttc", 24))
    mode_rows = [("ask", "plan", "build"), ("debug", "review", "auto")]
    chip_y = 208
    for row in mode_rows:
        chip_x = 850
        for label in row:
            chip_x += add_mode_chip(draw, (chip_x, chip_y), label) + 12
        chip_y += 36

    draw.rounded_rectangle((828, 274, 1182, 338), radius=22, fill=(7, 14, 20, 178), outline=(63, 200, 219, 102), width=2)
    draw.multiline_text(
        (850, 289),
        "Local-first by default.\nOptional adapters via feature flags.",
        fill=(217, 234, 238, 236),
        font=load_font("Avenir Next.ttc", 20),
        spacing=4,
    )

    footer_font = load_font("Avenir Next.ttc", 20)
    draw.text((858, 544), "Banner + GitHub social preview asset", fill=(228, 231, 232, 185), font=footer_font)

    image = image.convert("RGB")
    image.save(PNG_PATH, quality=95)
    print(PNG_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
