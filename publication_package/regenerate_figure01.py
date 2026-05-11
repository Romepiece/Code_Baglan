from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "figures" / "figure01.png"

WIDTH = 2400
HEIGHT = 1800
BACKGROUND = "#ffffff"
BOX_FILL = "#ffffff"
OUTLINE = "#222222"
TEXT = "#111111"


def inset_box(box: tuple[int, int, int, int], pad_x: int, pad_y: int) -> tuple[int, int, int, int]:
    left, top, right, bottom = box
    return (left + pad_x, top + pad_y, right - pad_x, bottom - pad_y)


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    font_candidates = []
    if bold:
        font_candidates.extend(
            [
                r"C:\Windows\Fonts\timesbd.ttf",
                r"C:\Windows\Fonts\timesbi.ttf",
                r"C:\Windows\Fonts\arialbd.ttf",
            ]
        )
    else:
        font_candidates.extend(
            [
                r"C:\Windows\Fonts\times.ttf",
                r"C:\Windows\Fonts\timesi.ttf",
                r"C:\Windows\Fonts\arial.ttf",
            ]
        )

    for candidate in font_candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)

    return ImageFont.load_default()


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int, tuple[int, int, int, int]]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1], bbox


def draw_text(draw: ImageDraw.ImageDraw, x: int, y: int, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    width, height, bbox = text_size(draw, text, font)
    draw.text((x - bbox[0], y - bbox[1]), text, fill=TEXT, font=font)
    return width, height


def draw_centered_text(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    lines: list[tuple[str, ImageFont.ImageFont]],
    line_gap: int = 10,
    padding_x: int = 36,
    padding_y: int = 26,
    first_gap_extra: int = 0,
) -> None:
    left, top, right, bottom = box
    left += padding_x
    right -= padding_x
    top += padding_y
    bottom -= padding_y
    line_heights = []
    bboxes = []
    for text, font in lines:
        bbox = draw.textbbox((0, 0), text, font=font)
        bboxes.append(bbox)
        line_heights.append(bbox[3] - bbox[1])

    total_height = sum(line_heights) + line_gap * max(0, len(lines) - 1)
    current_y = top + ((bottom - top - total_height) // 2)

    for index, (text, font) in enumerate(lines):
        bbox = bboxes[index]
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = left + ((right - left - text_width) // 2)
        draw.text((x - bbox[0], current_y - bbox[1]), text, fill=TEXT, font=font)
        current_y += text_height
        if index < len(lines) - 1:
            current_y += line_gap
            if index == 0:
                current_y += first_gap_extra


def draw_multiline_left(draw: ImageDraw.ImageDraw, start: tuple[int, int], items: list[tuple[str, ImageFont.ImageFont]], line_gap: int = 22) -> None:
    x, y = start
    current_y = y
    for text, font in items:
        bbox = draw.textbbox((0, 0), text, font=font)
        draw.text((x - bbox[0], current_y - bbox[1]), text, fill=TEXT, font=font)
        current_y += (bbox[3] - bbox[1]) + line_gap


def draw_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rectangle(box, fill=BOX_FILL, outline=OUTLINE, width=5)


def draw_centered_title(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, font: ImageFont.ImageFont, top_y: int) -> int:
    left, _, right, _ = box
    width, height, _ = text_size(draw, text, font)
    x = left + ((right - left - width) // 2)
    draw_text(draw, x, top_y, text, font)
    return top_y + height


def draw_left_block(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], title: str, items: list[str], title_font: ImageFont.ImageFont, body_font: ImageFont.ImageFont) -> None:
    inner = inset_box(box, 45, 50)
    _, top, _, _ = inner
    current_y = draw_centered_title(draw, inner, title, title_font, top + 35) + 55
    draw_multiline_left(draw, (inner[0], current_y), [(item, body_font) for item in items], line_gap=28)


def draw_method_group(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    items: list[str],
    title_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
) -> None:
    left, top, right, bottom = box
    title_bottom = draw_centered_title(draw, box, title, title_font, top)
    body_x = left + 25
    current_y = title_bottom + 30
    for item in items:
        _, height = draw_text(draw, body_x, current_y, item, body_font)
        current_y += height + 20
        if current_y > bottom:
            break


def measure_method_group_height(
    draw: ImageDraw.ImageDraw,
    title: str,
    items: list[str],
    title_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
) -> int:
    _, title_height, _ = text_size(draw, title, title_font)
    body_height = 0
    for index, item in enumerate(items):
        _, item_height, _ = text_size(draw, item, body_font)
        body_height += item_height
        if index < len(items) - 1:
            body_height += 20
    return title_height + 30 + body_height


def draw_right_block(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    header: str,
    groups: list[tuple[str, list[str]]],
    header_font: ImageFont.ImageFont,
    title_font: ImageFont.ImageFont,
    body_font: ImageFont.ImageFont,
) -> None:
    inner = inset_box(box, 55, 42)
    header_bottom = draw_centered_title(draw, inner, header, header_font, inner[1] + 18)
    content_top = header_bottom + 52
    group_gap = 34
    group_heights = [measure_method_group_height(draw, title, items, title_font, body_font) for title, items in groups]
    total_height = sum(group_heights) + group_gap * (len(groups) - 1)
    available_height = inner[3] - 24 - content_top
    if total_height > available_height:
        group_gap = max(18, group_gap - ((total_height - available_height) // max(1, len(groups) - 1)) - 6)

    for index, (title, items) in enumerate(groups):
        group_top = content_top + sum(group_heights[:index]) + group_gap * index
        group_box = (inner[0], group_top, inner[2], group_top + group_heights[index])
        draw_method_group(draw, group_box, title, items, title_font, body_font)


def draw_arrow(draw: ImageDraw.ImageDraw, start: tuple[int, int], end: tuple[int, int], width: int = 8, head_len: int = 38, head_half: int = 20) -> None:
    x1, y1 = start
    x2, y2 = end
    draw.line((x1, y1, x2, y2), fill=OUTLINE, width=width)
    if x1 == x2 and y2 > y1:
        draw.polygon([(x2, y2), (x2 - head_half, y2 - head_len), (x2 + head_half, y2 - head_len)], fill=OUTLINE, outline=OUTLINE)
    elif y1 == y2 and x2 > x1:
        draw.polygon([(x2, y2), (x2 - head_len, y2 - head_half), (x2 - head_len, y2 + head_half)], fill=OUTLINE, outline=OUTLINE)


def main() -> None:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    top_box = (70, 70, 2330, 300)
    left_box = (135, 455, 1045, 1245)
    right_box = (1245, 355, 2335, 1300)
    bottom_box = (90, 1450, 2360, 1760)

    for box in (top_box, left_box, right_box, bottom_box):
        draw_box(draw, box)

    title_font = load_font(54, bold=False)
    subtitle_font = load_font(46, bold=False)
    header_font = load_font(52, bold=False)
    body_font = load_font(42, bold=False)
    bold_font = load_font(44, bold=True)
    result_font = load_font(64, bold=True)
    result_body_font = load_font(46, bold=False)

    draw_centered_text(
        draw,
        top_box,
        [
            ("PANEL DATA", title_font),
            ("20 regions of Kazakhstan, 2015-2024", subtitle_font),
            ("(175 observations, N=175)", subtitle_font),
        ],
        line_gap=12,
        padding_x=60,
        padding_y=34,
    )

    draw_left_block(
        draw,
        left_box,
        "PRELIMINARY ANALYSIS",
        [
            "• Logarithmic transformation log(1+x)",
            "• Handling of missing values",
            "• Descriptive statistics and correlation",
            "  analysis",
            "• Multicollinearity test (VIF)",
        ],
        header_font,
        body_font,
    )

    draw_right_block(
        draw,
        right_box,
        "BASIC METHODS",
        [
            ("Module 1 Econometrics", ["Pooled OLS and TWFE"]),
            ("Module 2 Clustering", ["k-means", "2 clusters"]),
            ("Module 3 Machine Learning", ["Random Forest", "Feature Imp", "PDP plots"]),
        ],
        header_font,
        bold_font,
        body_font,
    )

    draw_centered_text(
        draw,
        bottom_box,
        [
            ("Results", result_font),
            ("Integration of Findings", result_body_font),
            ("Causality", result_body_font),
            ("Heterogeneity", result_body_font),
            ("Prediction", result_body_font),
        ],
        line_gap=8,
        padding_x=60,
        padding_y=58,
        first_gap_extra=12,
    )

    draw_arrow(draw, (1200, 320), (1200, 470), width=8, head_len=48, head_half=28)
    draw_arrow(draw, (1045, 645), (1245, 645), width=8, head_len=46, head_half=24)
    draw_arrow(draw, (1045, 1010), (1245, 1010), width=8, head_len=46, head_half=24)
    draw_arrow(draw, (1200, 1305), (1200, 1445), width=8, head_len=48, head_half=28)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT, dpi=(300, 300))
    print(f"Saved {OUTPUT} ({WIDTH}x{HEIGHT})")


if __name__ == "__main__":
    main()