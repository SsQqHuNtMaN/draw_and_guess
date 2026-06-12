from PIL import Image, ImageDraw, ImageFont
import csv
import os
from pathlib import Path

# ======================
# 基础配置
# ======================

CSV_PATH = "bingo_items.csv"
OUTPUT_PATH = "底力Ultra音游社Bingo.png"

TITLE = "底力Ultra音游社Bingo"
SUBTITLE_1 = "五个连成一线你就是Ultra群资深群友！"
SUBTITLE_2 = "（然后你也差不多没救了）"

W, H = 1400, 1750
BG_COLOR = "white"
TEXT_COLOR = "black"
LINE_COLOR = "black"

GRID_LEFT = 70
GRID_TOP = 350
GRID_RIGHT = W - 70
GRID_BOTTOM = H - 70

ROWS = 5
COLS = 5
CELL_W = (GRID_RIGHT - GRID_LEFT) // COLS
CELL_H = (GRID_BOTTOM - GRID_TOP) // ROWS


# ======================
# 读取 CSV
# ======================

def load_bingo_items(csv_path):
    """
    CSV 格式：
    row,col,text
    1,1,按照全国\n音游地图\n填报志愿

    注意：
    - row 和 col 从 1 开始
    - text 里的 \\n 会被自动转成真正换行
    """
    items = [["" for _ in range(COLS)] for _ in range(ROWS)]

    with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        required_cols = {"row", "col", "text"}
        if not required_cols.issubset(reader.fieldnames or []):
            raise ValueError("CSV 必须包含 row、col、text 三列")

        for line_no, row in enumerate(reader, start=2):
            try:
                r = int(row["row"])
                c = int(row["col"])
            except ValueError:
                raise ValueError(f"第 {line_no} 行 row/col 必须是数字")

            if not (1 <= r <= ROWS and 1 <= c <= COLS):
                raise ValueError(f"第 {line_no} 行 row/col 超出 1-5 范围")

            text = row["text"].replace("\\n", "\n")
            items[r - 1][c - 1] = text

    missing = []
    for r in range(ROWS):
        for c in range(COLS):
            if not items[r][c].strip():
                missing.append((r + 1, c + 1))

    if missing:
        raise ValueError(f"CSV 中存在空格子：{missing}")

    return items


# ======================
# 字体加载
# ======================

def load_font(size, bold=False):
    """
    自动尝试加载常见中文字体。
    Windows 推荐：微软雅黑 / 黑体
    macOS 推荐：苹方
    Linux 推荐：Noto Sans CJK
    """
    if bold:
        font_candidates = [
            "C:/Windows/Fonts/msyhbd.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Medium.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]
    else:
        font_candidates = [
            "C:/Windows/Fonts/msyh.ttc",
            "C:/Windows/Fonts/simhei.ttf",
            "/System/Library/Fonts/PingFang.ttc",
            "/System/Library/Fonts/STHeiti Light.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        ]

    for path in font_candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


title_font = load_font(100, bold=True)
subtitle_font = load_font(48, bold=True)
cell_font = load_font(42, bold=False)
cell_font_small = load_font(34, bold=False)
center_font = load_font(45, bold=True)


# ======================
# 绘图函数
# ======================

def draw_centered_multiline_text(draw, box, text, font, fill="black", spacing=8):
    left, top, right, bottom = box
    bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing, align="center")
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x = left + (right - left - text_w) / 2
    y = top + (bottom - top - text_h) / 2

    draw.multiline_text(
        (x, y),
        text,
        font=font,
        fill=fill,
        spacing=spacing,
        align="center"
    )


def choose_font_for_cell(text, is_center=False):
    if is_center:
        return center_font

    plain_len = len(text.replace("\n", ""))
    line_count = text.count("\n") + 1

    if plain_len >= 22 or line_count >= 4:
        return cell_font_small

    return cell_font


def draw_centered_single_line(draw, y, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    draw.text(((W - text_w) / 2, y), text, font=font, fill=TEXT_COLOR)


# ======================
# 主程序
# ======================

def main():
    bingo_items = load_bingo_items(CSV_PATH)

    img = Image.new("RGB", (W, H), BG_COLOR)
    draw = ImageDraw.Draw(img)

    # 标题与副标题
    draw_centered_single_line(draw, 35, TITLE, title_font)
    draw_centered_single_line(draw, 165, SUBTITLE_1, subtitle_font)
    draw_centered_single_line(draw, 230, SUBTITLE_2, subtitle_font)

    # 表格线
    line_width = 3

    for i in range(COLS + 1):
        x = GRID_LEFT + i * CELL_W
        draw.line((x, GRID_TOP, x, GRID_BOTTOM), fill=LINE_COLOR, width=line_width)

    for j in range(ROWS + 1):
        y = GRID_TOP + j * CELL_H
        draw.line((GRID_LEFT, y, GRID_RIGHT, y), fill=LINE_COLOR, width=line_width)

    # 单元格文字
    for r in range(ROWS):
        for c in range(COLS):
            left = GRID_LEFT + c * CELL_W
            top = GRID_TOP + r * CELL_H
            right = left + CELL_W
            bottom = top + CELL_H

            text = bingo_items[r][c]
            is_center = (r == 2 and c == 2)
            font = choose_font_for_cell(text, is_center=is_center)

            padding = 16
            text_box = (
                left + padding,
                top + padding,
                right - padding,
                bottom - padding
            )

            draw_centered_multiline_text(
                draw,
                text_box,
                text,
                font,
                fill=TEXT_COLOR,
                spacing=10 if not is_center else 12
            )

    img.save(OUTPUT_PATH, quality=95)
    print(f"已生成：{OUTPUT_PATH}")


if __name__ == "__main__":
    main()
