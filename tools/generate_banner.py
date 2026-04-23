#!/usr/bin/env python3
"""Generate Chinese-first GitHub marketing assets for OECK."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "docs" / "assets"
PHILOSOPHY_PATH = ASSETS / "oeck-visual-philosophy.md"

SCALE = 2


def px(value: int) -> int:
    return int(value * SCALE)


def load_font(candidates: list[tuple[str, int | None]], size: int) -> ImageFont.FreeTypeFont:
    roots = [
        Path("/System/Library/Fonts"),
        Path("/System/Library/Fonts/Supplemental"),
        Path("/Library/Fonts"),
    ]
    for name, index in candidates:
        for root in roots:
            path = root / name
            if path.exists():
                kwargs = {"size": px(size)}
                if index is not None:
                    kwargs["index"] = index
                return ImageFont.truetype(str(path), **kwargs)
    return ImageFont.load_default()


FONT_CN_DISPLAY = [("Hiragino Sans GB.ttc", 0)]
FONT_UI = [("Avenir Next.ttc", 0), ("HelveticaNeue.ttc", 0)]
FONT_NUMBER = [("DIN Condensed Bold.ttf", None), ("Arial Black.ttf", None)]


def make_canvas(width: int, height: int) -> Image.Image:
    canvas = Image.new("RGBA", (px(width), px(height)), (6, 10, 16, 255))
    pixels = canvas.load()
    for y in range(canvas.size[1]):
        t = y / max(canvas.size[1] - 1, 1)
        top = (7, 10, 16)
        bottom = (17, 24, 38)
        row = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        for x in range(canvas.size[0]):
            pixels[x, y] = (*row, 255)
    return canvas


def add_noise(base: Image.Image, alpha: int = 16) -> None:
    noise = Image.effect_noise(base.size, 10).convert("L")
    texture = ImageOps.colorize(noise, black=(8, 11, 18), white=(32, 38, 46)).convert("RGBA")
    texture.putalpha(alpha)
    base.alpha_composite(texture)


def add_glow(base: Image.Image, box: tuple[int, int, int, int], color: tuple[int, int, int, int], blur: int) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.ellipse(tuple(px(v) for v in box), fill=color)
    overlay = overlay.filter(ImageFilter.GaussianBlur(px(blur)))
    base.alpha_composite(overlay)


def add_gradient_bar(base: Image.Image, box: tuple[int, int, int, int], left: tuple[int, int, int], right: tuple[int, int, int]) -> None:
    x0, y0, x1, y1 = [px(v) for v in box]
    bar = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(bar)
    width = max(x1 - x0, 1)
    for index in range(width):
        t = index / max(width - 1, 1)
        color = tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3))
        draw.line((x0 + index, y0, x0 + index, y1), fill=(*color, 255), width=1)
    bar = bar.filter(ImageFilter.GaussianBlur(px(2)))
    base.alpha_composite(bar)


def draw_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: tuple[int, int, int, int], outline: tuple[int, int, int, int], radius: int, width: int = 2) -> None:
    draw.rounded_rectangle(tuple(px(v) for v in box), radius=px(radius), fill=fill, outline=outline, width=px(width))


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> str:
    lines: list[str] = []
    current = ""
    for char in text:
        candidate = current + char
        if draw.textbbox((0, 0), candidate, font=font)[2] <= px(max_width):
            current = candidate
            continue
        if current:
            lines.append(current)
        current = char
    if current:
        lines.append(current)
    return "\n".join(lines)


def draw_chip(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, outline: tuple[int, int, int], fill_alpha: int = 188, text_fill: tuple[int, int, int, int] = (245, 248, 250, 252), font_size: int = 20) -> int:
    font = load_font(FONT_CN_DISPLAY + FONT_UI, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    width = bbox[2] - bbox[0] + px(28)
    height = bbox[3] - bbox[1] + px(16)
    left, top = px(xy[0]), px(xy[1])
    draw.rounded_rectangle((left, top, left + width, top + height), radius=px(18), fill=(10, 17, 24, fill_alpha), outline=(*outline, 255), width=px(2))
    draw.text((left + px(14), top + px(8)), text, font=font, fill=text_fill)
    return int(width / SCALE)


def add_hero_graphic(base: Image.Image) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    draw.rounded_rectangle((px(1018), px(90), px(1506), px(690)), radius=px(54), fill=(10, 18, 25, 198), outline=(163, 234, 242, 126), width=px(2))
    draw.rounded_rectangle((px(1082), px(144), px(1450), px(638)), radius=px(40), fill=(14, 34, 42, 218), outline=(73, 213, 229, 86), width=px(1))
    for x in range(1048, 1502, 58):
        draw.line((px(x), px(116), px(x), px(664)), fill=(166, 230, 239, 26), width=px(1))
    for y in range(126, 676, 58):
        draw.line((px(982), px(y), px(1520), px(y)), fill=(166, 230, 239, 26), width=px(1))
    overlay = overlay.filter(ImageFilter.GaussianBlur(px(0)))
    base.alpha_composite(overlay)

    add_gradient_bar(base, (842, 592, 1256, 632), (255, 122, 70), (65, 208, 230))
    slash = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(slash)
    draw.polygon((px(838), px(626), px(1208), px(364), px(1284), px(364), px(912), px(626)), fill=(255, 124, 71, 238))
    draw.polygon((px(862), px(650), px(1232), px(388), px(1272), px(388), px(902), px(650)), fill=(255, 223, 196, 108))
    slash = slash.filter(ImageFilter.GaussianBlur(px(8)))
    base.alpha_composite(slash)


def add_highlights_background(base: Image.Image) -> None:
    add_glow(base, (-180, 420, 560, 1280), (255, 125, 78, 72), 90)
    add_glow(base, (1050, -220, 1760, 520), (56, 205, 228, 82), 100)
    for start, end in [((92, 178), (1510, 178)), ((92, 844), (1510, 844))]:
        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        draw.line((px(start[0]), px(start[1]), px(end[0]), px(end[1])), fill=(255, 255, 255, 22), width=px(1))
        base.alpha_composite(overlay)


def save_asset(base: Image.Image, path: Path, width: int, height: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    final = base.resize((width, height), Image.Resampling.LANCZOS).convert("RGB")
    final.save(path, optimize=True, quality=96)


def render_hero() -> None:
    width = 1600
    height = 780
    image = make_canvas(width, height)
    add_glow(image, (-180, 420, 680, 1260), (255, 126, 82, 82), 92)
    add_glow(image, (990, -180, 1820, 620), (51, 205, 229, 88), 108)
    add_noise(image)
    add_hero_graphic(image)

    draw = ImageDraw.Draw(image, "RGBA")
    label_font = load_font(FONT_CN_DISPLAY, 24)
    eyebrow_font = load_font(FONT_CN_DISPLAY + FONT_UI, 22)
    title_font = load_font(FONT_CN_DISPLAY, 84)
    subtitle_font = load_font(FONT_CN_DISPLAY, 26)
    card_title_font = load_font(FONT_CN_DISPLAY, 26)
    card_body_font = load_font(FONT_CN_DISPLAY, 18)
    number_font = load_font(FONT_NUMBER, 40)

    draw.text((px(88), px(76)), "面向 OpenClaw / Claude / Codex", font=label_font, fill=(255, 209, 180, 252))
    draw.text((px(88), px(118)), "治理 · 兼容 · 运行时增强", font=eyebrow_font, fill=(168, 226, 233, 236))
    draw.multiline_text((px(88), px(176)), "OpenClaw\n增强与兼容套件", font=title_font, fill=(246, 248, 250, 255), spacing=px(8))
    draw.multiline_text(
        (px(92), px(414)),
        "把零散 skills 升级为统一治理、统一上下文、统一分发、\n统一观测的产品层。",
        font=subtitle_font,
        fill=(205, 223, 228, 238),
        spacing=px(8),
    )
    draw.multiline_text(
        (px(92), px(492)),
        "支持 OpenClaw 原生插件、Claude Bundle、Codex Bundle，\n并保留本地优先运行方式。",
        font=subtitle_font,
        fill=(167, 216, 224, 228),
        spacing=px(8),
    )

    for idx, (title, desc, accent) in enumerate(
        [
            ("统一策略", "模式系统、审批边界、命令风险评分统一收口", (255, 124, 71)),
            ("统一上下文", "Resolver、MemoryProvider、RuleStore 统一抽象", (59, 201, 221)),
            ("统一分发", "同一份 canonical metadata 生成多宿主产物", (88, 124, 255)),
            ("统一观测", "TraceExporter 与可选 observability adapter 接轨", (90, 220, 187)),
        ]
    ):
        x0 = 1046
        y0 = 140 + idx * 124
        draw_panel(draw, (x0, y0, 1470, y0 + 94), (8, 14, 21, 204), (*accent, 120), 24, width=1)
        draw.text((px(x0 + 22), px(y0 + 18)), f"{idx + 1:02d}", font=number_font, fill=(*accent, 255))
        draw.text((px(x0 + 96), px(y0 + 18)), title, font=card_title_font, fill=(245, 248, 250, 250))
        draw.multiline_text((px(x0 + 96), px(y0 + 54)), wrap_text(draw, desc, card_body_font, 320), font=card_body_font, fill=(186, 219, 225, 235), spacing=px(5))

    chip_y = 620
    chip_x = 88
    for text, color in [
        ("本地优先", (255, 124, 71)),
        ("三宿主分发", (59, 201, 221)),
        ("模式系统", (88, 124, 255)),
        ("工程闭环", (90, 220, 187)),
        ("可选适配器", (255, 208, 142)),
    ]:
        chip_x += draw_chip(draw, (chip_x, chip_y), text, color, font_size=19) + 14

    save_asset(image, ASSETS / "oeck-github-banner.png", width, height)


def render_highlights() -> None:
    width = 1600
    height = 980
    image = make_canvas(width, height)
    add_highlights_background(image)
    add_noise(image, alpha=14)
    draw = ImageDraw.Draw(image, "RGBA")

    title_font = load_font(FONT_CN_DISPLAY, 56)
    subtitle_font = load_font(FONT_CN_DISPLAY, 24)
    card_title_font = load_font(FONT_CN_DISPLAY, 28)
    card_body_font = load_font(FONT_CN_DISPLAY, 18)
    number_font = load_font(FONT_NUMBER, 42)

    draw.text((px(92), px(86)), "产品亮点", font=title_font, fill=(246, 248, 250, 255))
    draw.text((px(92), px(158)), "不是继续堆技能，而是把技能、策略、上下文、分发和观测统一成一个产品面。", font=subtitle_font, fill=(184, 219, 226, 236))

    cards = [
        ("01", "统一策略", "把模式系统、权限评分、规则优化和审批边界收束到同一套策略引擎。"),
        ("02", "统一上下文", "用 WorkspaceResolver、SessionResolver、MemoryProvider 抹平宿主差异。"),
        ("03", "统一分发", "从同一份 canonical metadata 生成 OpenClaw、Claude、Codex 三种产物。"),
        ("04", "统一观测", "默认结构化 trace 导出，未来可按 adapter 接 Langfuse、Opik 等系统。"),
        ("05", "本地可跑", "默认不依赖外部凭证，远程沙箱、时序记忆、lossless context 都是可选项。"),
        ("06", "兼容迁移", "保留既有 skills，并通过 shim 和 resolver 封装移除旧宿主硬编码。"),
    ]

    for idx, (code, title, desc) in enumerate(cards):
        row = idx // 3
        col = idx % 3
        x0 = 92 + col * 472
        y0 = 248 + row * 274
        accent = [(255, 124, 71), (59, 201, 221), (88, 124, 255), (90, 220, 187), (255, 208, 142), (168, 120, 255)][idx]
        draw_panel(draw, (x0, y0, x0 + 420, y0 + 214), (8, 14, 21, 212), (*accent, 120), 26, width=1)
        draw.line((px(x0 + 26), px(y0 + 80), px(x0 + 394), px(y0 + 80)), fill=(*accent, 130), width=px(2))
        draw.text((px(x0 + 24), px(y0 + 18)), code, font=number_font, fill=(*accent, 255))
        draw.text((px(x0 + 122), px(y0 + 24)), title, font=card_title_font, fill=(246, 248, 250, 250))
        draw.multiline_text((px(x0 + 26), px(y0 + 108)), wrap_text(draw, desc, card_body_font, 352), font=card_body_font, fill=(188, 218, 224, 236), spacing=px(8))

    save_asset(image, ASSETS / "oeck-highlights-zh.png", width, height)


def render_modes() -> None:
    width = 1600
    height = 960
    image = make_canvas(width, height)
    add_glow(image, (-160, 360, 620, 1180), (255, 126, 82, 68), 84)
    add_glow(image, (1060, -180, 1840, 680), (54, 205, 228, 86), 96)
    add_noise(image, alpha=14)
    draw = ImageDraw.Draw(image, "RGBA")

    title_font = load_font(FONT_CN_DISPLAY, 54)
    subtitle_font = load_font(FONT_CN_DISPLAY, 23)
    mode_name_font = load_font(FONT_UI, 24)
    mode_body_font = load_font(FONT_CN_DISPLAY, 17)
    flow_title_font = load_font(FONT_CN_DISPLAY, 30)
    flow_body_font = load_font(FONT_CN_DISPLAY, 18)

    draw.text((px(92), px(86)), "模式系统与工程闭环", font=title_font, fill=(246, 248, 250, 255))
    draw.text((px(92), px(154)), "从 ask 到 auto，不只是权限切换，还把检查、验证、smoke test、CI 串成一个闭环。", font=subtitle_font, fill=(183, 217, 224, 236))

    modes = [
        ("ASK", "只读解答", "只读、禁网、严格审批，适合查阅和解释。"),
        ("PLAN", "规划模式", "做方案、查结构、给边界，执行受控。"),
        ("BUILD", "开发模式", "默认实现模式，允许修改并带验证。"),
        ("DEBUG", "诊断模式", "强调 trace、复现、测试与根因定位。"),
        ("REVIEW", "审查模式", "只读 review/checks，聚焦风险和回归。"),
        ("AUTO", "自动模式", "由 profile 与 sandbox provider 决定自动化边界。"),
    ]

    for idx, (name, title, desc) in enumerate(modes):
        row = idx // 2
        col = idx % 2
        x0 = 92 + col * 344
        y0 = 246 + row * 184
        accent = [(255, 124, 71), (59, 201, 221), (88, 124, 255), (90, 220, 187), (255, 208, 142), (168, 120, 255)][idx]
        draw_panel(draw, (x0, y0, x0 + 300, y0 + 144), (8, 14, 21, 214), (*accent, 116), 24, width=1)
        draw.text((px(x0 + 24), px(y0 + 22)), name, font=mode_name_font, fill=(*accent, 255))
        draw.text((px(x0 + 24), px(y0 + 60)), title, font=load_font(FONT_CN_DISPLAY, 24), fill=(246, 248, 250, 252))
        draw.multiline_text((px(x0 + 24), px(y0 + 96)), desc, font=mode_body_font, fill=(188, 218, 224, 236), spacing=px(6))

    flow_box = (850, 234, 1506, 812)
    draw_panel(draw, flow_box, (9, 16, 24, 210), (170, 232, 240, 96), 28, width=1)
    draw.text((px(904), px(264)), "Post-edit Validation Pipeline", font=flow_title_font, fill=(246, 248, 250, 248))
    draw.text((px(904), px(310)), "本地开发、review、CI 复用同一套检查链路。", font=flow_body_font, fill=(186, 219, 225, 235))

    steps = [
        ("01", "修改代码", "编辑实现与配置"),
        ("02", "运行 checks", "markdown checks + review runner"),
        ("03", "post-edit validation", "compile / lint / targeted validation"),
        ("04", "smoke test", "检查脚本、manifest、产物是否可跑"),
        ("05", "CI 复用", "同一套校验直接进 GitHub Actions"),
    ]
    for idx, (code, title, desc) in enumerate(steps):
        x = 902
        y = 408 + idx * 78
        accent = [(255, 124, 71), (255, 208, 142), (59, 201, 221), (90, 220, 187), (88, 124, 255)][idx]
        draw.ellipse((px(x - 26), px(y - 26), px(x + 26), px(y + 26)), fill=(10, 16, 23, 214), outline=(*accent, 255), width=px(3))
        draw.text((px(x - 15), px(y - 15)), code, font=load_font(FONT_NUMBER, 18), fill=(*accent, 255))
        if idx < len(steps) - 1:
            draw.line((px(x), px(y + 26), px(x), px(y + 52)), fill=(*accent, 155), width=px(3))
        draw.text((px(x + 54), px(y - 18)), title, font=load_font(FONT_CN_DISPLAY, 21), fill=(246, 248, 250, 250))
        draw.text((px(x + 54), px(y + 18)), desc, font=load_font(FONT_CN_DISPLAY, 15), fill=(188, 218, 224, 234))

    save_asset(image, ASSETS / "oeck-modes-zh.png", width, height)


def render_distribution() -> None:
    width = 1600
    height = 980
    image = make_canvas(width, height)
    add_glow(image, (-180, 520, 620, 1280), (255, 126, 82, 70), 88)
    add_glow(image, (980, -220, 1800, 660), (53, 205, 229, 84), 102)
    add_noise(image, alpha=14)
    draw = ImageDraw.Draw(image, "RGBA")

    title_font = load_font(FONT_CN_DISPLAY, 56)
    subtitle_font = load_font(FONT_CN_DISPLAY, 23)
    card_title_font = load_font(FONT_CN_DISPLAY, 28)
    card_body_font = load_font(FONT_CN_DISPLAY, 18)
    section_font = load_font(FONT_CN_DISPLAY, 26)
    small_ui_font = load_font(FONT_UI, 20)

    draw.text((px(92), px(86)), "三宿主分发与可选适配器", font=title_font, fill=(246, 248, 250, 255))
    draw.text((px(92), px(158)), "一份 canonical metadata，生成多宿主插件与 bundle；外部能力全部通过 adapter 与 feature flags 接入。", font=subtitle_font, fill=(183, 217, 224, 236))

    draw.text((px(92), px(248)), "分发目标", font=section_font, fill=(245, 248, 250, 248))
    dist_cards = [
        ("OpenClaw 原生插件", "openclaw.plugin.json", "适合 OpenClaw 原生插件安装路径。", (255, 124, 71)),
        ("Claude Bundle", ".claude-plugin/plugin.json", "带命令、设置与 bundle 元数据。", (59, 201, 221)),
        ("Codex Bundle", ".codex-plugin/plugin.json", "带 hook 包与 post-edit validation 入口。", (88, 124, 255)),
    ]
    for idx, (title, path, desc, accent) in enumerate(dist_cards):
        x0 = 92
        y0 = 292 + idx * 190
        draw_panel(draw, (x0, y0, 612, y0 + 150), (8, 14, 21, 214), (*accent, 120), 26, width=1)
        draw.text((px(x0 + 28), px(y0 + 24)), title, font=card_title_font, fill=(246, 248, 250, 250))
        draw.text((px(x0 + 28), px(y0 + 68)), path, font=small_ui_font, fill=(*accent, 255))
        draw.text((px(x0 + 28), px(y0 + 104)), desc, font=card_body_font, fill=(188, 218, 224, 234))

    center_x = 790
    draw.text((px(center_x - 110), px(276)), "统一事实源", font=section_font, fill=(245, 248, 250, 248))
    draw_panel(draw, (648, 334, 934, 458), (10, 18, 26, 208), (255, 208, 142, 112), 26, width=1)
    draw.text((px(680), px(366)), "metadata/canonical.json", font=load_font(FONT_UI, 22), fill=(255, 208, 142, 255))
    draw.text((px(680), px(406)), "由同一份 metadata 生成 README 清单、manifest、bundle。", font=card_body_font, fill=(188, 218, 224, 234))
    for y in (392, 582, 772):
        draw.line((px(934), px(396), px(1010), px(y)), fill=(255, 208, 142, 128), width=px(3))

    draw.text((px(1044), px(248)), "可选适配器", font=section_font, fill=(245, 248, 250, 248))
    adapters = [
        ("lossless-context", "给 smart-compact / memory-compaction 提供可选无损上下文后端。"),
        ("observability", "默认结构化事件导出，可选接 Opik，未来可接 Langfuse。"),
        ("temporal-memory", "先提供接口与本地 stub，不强依赖图数据库。"),
        ("remote-sandbox", "先定义 provider 接口与网络策略，不强依赖云账号。"),
    ]
    for idx, (name, desc) in enumerate(adapters):
        y0 = 292 + idx * 148
        accent = [(59, 201, 221), (90, 220, 187), (168, 120, 255), (255, 124, 71)][idx]
        draw_panel(draw, (1042, y0, 1508, y0 + 116), (8, 14, 21, 214), (*accent, 110), 24, width=1)
        draw.text((px(1070), px(y0 + 22)), name, font=small_ui_font, fill=(*accent, 255))
        draw.multiline_text((px(1070), px(y0 + 56)), wrap_text(draw, desc, card_body_font, 370), font=card_body_font, fill=(188, 218, 224, 234), spacing=px(6))

    chip_y = 872
    chip_x = 92
    for text, color in [
        ("默认本地可跑", (255, 124, 71)),
        ("外部能力可选开启", (59, 201, 221)),
        ("同一份 metadata 统一生成", (255, 208, 142)),
    ]:
        chip_x += draw_chip(draw, (chip_x, chip_y), text, color, font_size=18) + 14

    save_asset(image, ASSETS / "oeck-distribution-zh.png", width, height)


def write_philosophy() -> None:
    text = """# Monolithic Signal（整体信号）

Monolithic Signal 的目标不是把很多元素堆在一张图里，而是让产品价值像一个整体物体那样被看见。画面必须先建立一个强主视觉，再让其余信息作为支撑层次出现。第一眼应该先读到产品定位，而不是先看到装饰或局部技巧。最终成品必须显得经过大量推敲，像一张被反复打磨过的产品海报，而不是功能截图拼贴。

色彩只保留两种主要能量：偏暖的橙色负责表达治理、分发、决策和介入感；偏冷的青色负责表达上下文、运行时、兼容性和持续流动。深色背景提供足够的压缩感，让亮色像被控制过的能量一样释放出来。整体必须克制、精确、昂贵，体现出产品成熟度，而不是炫技。

构图要强调“大形优先”。每张图都只允许一个最强图形关系：主标题与产品柱体、六宫格亮点、模式卡片与验证链路、分发目标与适配器矩阵。其余细节都服务于这个主关系，不能抢戏。观者应当在几秒内知道这张图讲什么，再在停留时继续读到第二层信息。

文字全部承担视觉功能，而不只是说明功能。中文是主语言，字形需要有明确的重量、节奏和留白。标题负责冲击力，副标题负责定位，标签和芯片负责记忆点。每一个字距、边距、卡片厚度、线条密度都要显得经过耐心校准，体现出“这是一个真正被设计过的产品页面”。

整套素材必须像同一个系统的不同切面，而不是各自独立的海报。颜色、圆角、描边、阴影、排版密度都要统一，让 README 上的多张图片连起来形成一条完整叙事线：它是什么、亮点是什么、怎么运行、怎么分发。成品必须看起来专业、稳、清楚，而且有产品冲击力。
"""
    PHILOSOPHY_PATH.write_text(text, encoding="utf-8")


def main() -> int:
    ASSETS.mkdir(parents=True, exist_ok=True)
    write_philosophy()
    render_hero()
    render_highlights()
    render_modes()
    render_distribution()
    print(ASSETS / "oeck-github-banner.png")
    print(ASSETS / "oeck-highlights-zh.png")
    print(ASSETS / "oeck-modes-zh.png")
    print(ASSETS / "oeck-distribution-zh.png")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
