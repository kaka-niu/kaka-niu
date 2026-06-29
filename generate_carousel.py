"""
生成 kaka 个人信息轮播 GIF（3 页，自动循环）

页面1：基础信息（location, status, passion, fun_fact）- 标题 "Would you like me"
页面2：学习态度 & 方向
页面3：爱好 & 喜欢问什么 & 浏览偏好

输出：kaka-carousel.gif（500 x 300）
"""

from PIL import Image, ImageDraw, ImageFont
import math, os, textwrap

# ── 配置 ──────────────────────────────────────────
W, H = 500, 300           # GIF 尺寸
FPS = 0.25                 # 每页停留 4 秒（0.25 帧/秒）
FRAMES_PER_PAGE = 1       # 每页只有 1 帧（纯静态，无过渡动画的实际帧）
DURATION = 4000           # 每帧显示 4000ms

# GitHub Dark 配色
BG_TOP = (0x0D, 0x11, 0x17)
BG_BOT = (0x16, 0x1B, 0x22)
BORDER = (0x30, 0x36, 0x3D)
HEADER_BG = (0x1F, 0x6F, 0xEB, 25)  # 带 alpha
BLUE = (0x58, 0xA6, 0xFF)
LIGHT_BLUE = (0x79, 0xC0, 0xFF)
GREEN = (0x3F, 0xB9, 0x50)
PINK = (0xF7, 0x78, 0xBA)
YELLOW = (0xF0, 0xD0, 0x60)
PURPLE = (0xD2, 0xA8, 0xFF)
ORANGE = (0xFF, 0xA6, 0x57)
TEXT_DIM = (0x8B, 0x94, 0x9E)
VALUE_TEXT = (0xA5, 0xD6, 0xFF)
WHITE = (0xE6, 0xED, 0xF3)

# ── 字体 ──────────────────────────────────────────
# Windows 自带字体
FONT_PATH = "C:/Windows/Fonts/msyh.ttc"       # 微软雅黑（中文）
try:
    font_14 = ImageFont.truetype(FONT_PATH, 14)
    font_13 = ImageFont.truetype(FONT_PATH, 13)
    font_12 = ImageFont.truetype(FONT_PATH, 12)
    font_11 = ImageFont.truetype(FONT_PATH, 11)
    font_10 = ImageFont.truetype(FONT_PATH, 10)
    font_bold_14 = ImageFont.truetype(FONT_PATH, 14)
    font_bold_12 = ImageFont.truetype(FONT_PATH, 12)
except:
    font_14 = ImageFont.load_default()
    font_13 = font_14
    font_12 = font_14
    font_11 = font_14
    font_10 = font_14
    font_bold_14 = font_14
    font_bold_12 = font_14

# ── 绘制函数 ───────────────────────────────────────
def draw_card(draw):
    """绘制卡片背景和标题栏"""
    # 背景（从顶到底的渐变，用 3 个矩形模拟）
    for i in range(H):
        t = i / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line([(12, i), (W - 12, i)], fill=(r, g, b))

    # 圆角矩形边框
    draw.rounded_rectangle([10, 10, W - 10, H - 10], radius=12, outline=BORDER, width=2)

    # 标题栏
    draw.rounded_rectangle([10, 10, W - 10, 54], radius=12, fill=HEADER_BG)

    # 标题文字
    bbox = draw.textbbox((0, 0), "Would you like me", font=font_bold_14)
    tw = bbox[2] - bbox[0]
    draw.text(((W - tw) / 2, 35), "Would you like me", fill=BLUE, font=font_bold_14)

    # 页面指示箭头 (◀ 1/3 ▶)
    draw.text((30, H - 35), "◀", fill=TEXT_DIM, font=font_13)
    draw.text((W - 50, H - 35), "▶", fill=TEXT_DIM, font=font_13)

def draw_pagination(draw, current, total):
    """绘制分页圆点"""
    for i in range(total):
        cx = W // 2 + (i - 1) * 18
        cy = H - 30
        r = 5
        color = BLUE if i == current else BORDER
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)

    # 页码文字
    page_text = f"{current + 1} / {total}"
    bbox = draw.textbbox((0, 0), page_text, font=font_10)
    pw = bbox[2] - bbox[0]
    draw.text(((W - pw) / 2, H - 18), page_text, fill=TEXT_DIM, font=font_10)

def draw_page1(draw):
    """第1页：基础信息"""
    y_start = 75
    items = [
        ("location", "四川 · 宜宾", BLUE, VALUE_TEXT),
        ("status",   "刚入社会",     BLUE, GREEN),
        ("passion",  "自动化脚本 | Python | GitHub", BLUE, VALUE_TEXT),
        ("fun_fact", "能用脚本搞定的事，绝不手动点两次", BLUE, VALUE_TEXT),
    ]
    for i, (label, value, lbl_color, val_color) in enumerate(items):
        y = y_start + i * 42
        # 标签
        draw.text((50, y), label, fill=lbl_color, font=font_bold_12)
        # 冒号
        draw.text((155, y), ":", fill=TEXT_DIM, font=font_12)
        # 值
        draw.text((170, y), value, fill=val_color, font=font_12)

def draw_page2(draw):
    """第2页：学习态度 & 方向"""
    draw.text((45, 75), "· 学习态度", fill=PINK, font=font_bold_14)

    attitudes = [
        "能用代码解决的，绝不用鼠标点",
        "遇到问题先查文档，再 Google，最后问 AI",
        "喜欢折腾，不怕报错，只怕不报错",
    ]
    for i, text in enumerate(attitudes):
        draw.text((60, 105 + i * 28), "· " + text, fill=VALUE_TEXT, font=font_12)

    draw.text((45, 195), "· 学习方向", fill=PINK, font=font_bold_14)
    directions = [
        "Python 自动化 & 爬虫",
        "GitHub Actions & DevOps",
    ]
    for i, text in enumerate(directions):
        draw.text((60, 225 + i * 28), "· " + text, fill=VALUE_TEXT, font=font_12)

def draw_page3(draw):
    """第3页：爱好 & 提问 & 浏览"""
    draw.text((45, 75), "· 爱好", fill=PURPLE, font=font_bold_14)
    hobbies = [
        "写脚本解放双手，把重复的事交给代码",
        "折腾 GitHub 主页，研究各种花哨效果",
    ]
    for i, text in enumerate(hobbies):
        draw.text((60, 105 + i * 28), "· " + text, fill=VALUE_TEXT, font=font_12)

    draw.text((45, 170), "· 喜欢问", fill=PURPLE, font=font_bold_14)
    questions = [
        "「这个能不能用 Python 自动化？」",
        "「GitHub 这个效果是怎么做的？」",
    ]
    for i, text in enumerate(questions):
        draw.text((60, 200 + i * 28), "· " + text, fill=VALUE_TEXT, font=font_12)

    draw.text((45, 260), "· 浏览偏好", fill=PURPLE, font=font_bold_12)
    draw.text((155, 260), "技术博客 | GitHub Trending | 开源工具", fill=VALUE_TEXT, font=font_12)

# ── 主程序 ─────────────────────────────────────────
def main():
    out_path = os.path.join(os.path.dirname(__file__), "kaka-carousel.gif")

    frames = []
    page_drawers = [draw_page1, draw_page2, draw_page3]

    for page_idx, drawer in enumerate(page_drawers):
        # 每页生成一帧
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_card(draw)
        drawer(draw)
        draw_pagination(draw, page_idx, len(page_drawers))

        # 转 RGB
        frame = Image.new("RGB", (W, H), (13, 17, 23))
        frame.paste(img, (0, 0), img)
        frames.append(frame)

    # 保存 GIF
    frames[0].save(
        out_path,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION,
        loop=0,
        disposal=2,
    )
    print(f"[OK] Generated: {out_path}")
    print(f"     Size: {W}x{H}, Frames: {len(frames)}, Duration: {DURATION}ms, Loop: forever")

if __name__ == "__main__":
    main()
