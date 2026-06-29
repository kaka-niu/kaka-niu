"""
kaka 个人信息轮播 GIF — 基于 real profile 数据重新生成
3 页自动循环，每页停留 5 秒

页面1：我是谁（基础身份）
页面2：技术栈（核心能力）
页面3：项目亮点 & 特质

输出：kaka-carousel.gif
"""

from PIL import Image, ImageDraw, ImageFont
import os, textwrap

# ── 配置 ────────────────────────────────────────
W, H = 520, 380          # 加高防文字溢出
DURATION = 5000           # 每页停 5 秒

# ── 配色（GitHub Dark） ──────────────────────────
BG_TOP    = (0x0D, 0x11, 0x17)
BG_BOT    = (0x16, 0x1B, 0x22)
BORDER    = (0x30, 0x36, 0x3D)
BLUE      = (0x58, 0xA6, 0xFF)
LIGHT_BL  = (0x79, 0xC0, 0xFF)
GREEN     = (0x3F, 0xB9, 0x50)
PINK      = (0xF7, 0x78, 0xBA)
YELLOW    = (0xE0, 0xB0, 0x50)
PURPLE    = (0xBB, 0x9A, 0xF7)
ORANGE    = (0xFF, 0xA6, 0x57)
CYAN      = (0x7D, 0xC2, 0xFF)
DIM       = (0x6E, 0x76, 0x8E)
VAL       = (0xC0, 0xCA, 0xF5)
WHITE     = (0xE6, 0xED, 0xF3)

# ── 字体 ─────────────────────────────────────────
FP = "C:/Windows/Fonts/msyh.ttc"
FPE = "C:/Windows/Fonts/seguiemj.ttf"  # Emoji 专用字体
try:
    f14b = ImageFont.truetype(FP, 15)   # 粗体标题
    f13  = ImageFont.truetype(FP, 13)   # 正常
    f12  = ImageFont.truetype(FP, 12)   # 小字
    f11  = ImageFont.truetype(FP, 11)   # 更小
    femoji = ImageFont.truetype(FPE, 15)
except Exception:
    f14b = f13 = f12 = f11 = ImageFont.load_default()
    femoji = f14b

# ── 工具函数 ─────────────────────────────────────
def wrap_text(text, font, max_width):
    """返回按像素宽度折行的文本列表"""
    lines = []
    for raw_line in text.split('\n'):
        if not raw_line.strip():
            lines.append('')
            continue
        # 逐字符测量，在 max_width 处断行
        current = ''
        for ch in raw_line:
            test = current + ch
            bbox = draw_text_size(test, font)
            if bbox[0] > max_width and current:
                lines.append(current)
                current = ch
            else:
                current = test
        if current:
            lines.append(current)
    return lines or ['']

def draw_text_size(text, font):
    """返回文本的 (宽, 高)"""
    bbox = font.getbbox(text)
    return (bbox[2] - bbox[0], bbox[3] - bbox[1])

def draw_multiline(draw, x, y, lines, font, color, line_h=20):
    """绘制多行文字，返回下一行 y 坐标"""
    cy = y
    for line in lines:
        if line:
            draw.text((x, cy), line, fill=color, font=font)
        cy += line_h
    return cy

def draw_section(draw, y, emoji, text, color):
    """绘制带 emoji 图标的章节标题（emoji 用专用字体），返回下一个 y"""
    draw.text((35, y), emoji, fill=color, font=femoji)
    draw.text((58, y), text, fill=color, font=f14b)
    return y + 24

def draw_bullet(draw, y, text, font, color):
    """绘制带圆点 bullet 的行，返回下一行 y"""
    # 画一个小圆点代替字符 ·
    cx, cy = 46, y + (draw_text_size(text[0] if text else "A", font)[1]) // 2
    draw.ellipse([cx-2, cy-2, cx+2, cy+2], fill=DIM)
    lines = wrap_text(text, font, W - 78)
    return draw_multiline(draw, 56, y, lines, font, color, 19)

def draw_panda(draw, x, y, size=14):
    """用 PIL 原生图形画一只迷你熊猫，不依赖 emoji 字体"""
    s = size
    # 熊猫耳朵（黑色半圆）
    ear_r = s // 4
    draw.ellipse([x - s//2 + 1, y - s//3 - ear_r//2, x - s//2 + 1 + ear_r*2, y - s//3 + ear_r//2], fill=(30,30,35))
    draw.ellipse([x + s//2 - ear_r*2 - 1, y - s//3 - ear_r//2, x + s//2 - 1, y - s//3 + ear_r//2], fill=(30,30,35))
    # 白色圆脸
    face_r = s // 2
    draw.ellipse([x - face_r, y - face_r//2, x + face_r, y + face_r + face_r//2], fill=WHITE)
    # 黑眼圈（椭圆）
    draw.ellipse([x - face_r + 2, y, x - face_r//2 + 4, y + s//3], fill=(25,25,28))
    draw.ellipse([x + face_r//2 - 4, y, x + face_r - 2, y + s//3], fill=(25,25,28))
    # 黑眼睛（小圆点）
    draw.ellipse([x - face_r + 5, y + 3, x - face_r//2 + 6, y + 7], fill=(20,20,22))
    draw.ellipse([x + face_r//2 - 5, y + 3, x + face_r - 6, y + 7], fill=(20,20,22))
    # 小黑鼻子
    draw.ellipse([x - 3, y + s//3 - 2, x + 3, y + s//3 + 4], fill=(25,25,28))
    # 微笑弧线
    draw.arc([x - 4, y + s//3, x + 4, y + s//3 + 7], start=200, end=-20, fill=(80,80,85), width=1)

# ── 背景绘制 ─────────────────────────────────────
def draw_bg(draw):
    """渐变背景 + 圆角边框 + 标题栏"""
    # 渐变填充
    for i in range(H):
        t = i / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line([(10, i), (W-10, i)], fill=(r,g,b))

    # 边框
    draw.rounded_rectangle([8, 8, W-8, H-8], radius=14, outline=BORDER, width=2)

    # 标题栏底色
    draw.rounded_rectangle([8, 8, W-8, 52], radius=14, fill=(0x1F,0x6F,0xEB,30))

    # 标题文字（带 emoji）
    title = "Would you like me"
    tw = draw_text_size(title, f14b)[0]
    draw.text(((W-tw)/2 - 22, 33), "👋", fill=BLUE, font=femoji)
    draw.text(((W-tw)/2 + 4, 33), title, fill=BLUE, font=f14b)

def draw_dots(draw, cur, total):
    """底部圆点分页指示器"""
    gap = 16
    total_w = (total - 1) * gap
    sx = (W - total_w) // 2
    cy = H - 28
    for i in range(total):
        cx = sx + i * gap
        r = 5 if i == cur else 4
        c = BLUE if i == cur else DIM
        draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=c)
    # 页码
    pt = f"{cur+1}/{total}"
    pw = draw_text_size(pt, f11)[0]
    draw.text(((W-pw)/2, H-18), pt, fill=DIM, font=f11)


# ═════════════ 页面定义 ══════════════

def page_whoami(draw):
    """Page 1: 我是谁"""
    y = 68

    # section: 基本信息
    y = draw_section(draw, y, "👤", "身份", PINK)
    rows = [
        ("location",  "老子蜀道山",         BLUE, True),   # True = 后面画熊猫
        ("status",    "伏特骇客", GREEN, False),
        ("passion",   "Python · API逆向 · Serverless", VAL, False),
        ("fun_fact",  "能用脚本搞定的，绝不手动点两次", YELLOW, False),
    ]
    for lbl, val, vc, has_icon in rows:
        lw = draw_text_size(lbl, f13)[0]
        draw.text((48, y), lbl, fill=BLUE, font=f13)
        draw.text((48 + lw + 6, y), ":", fill=DIM, font=f13)
        vx = 62 + lw + 6
        draw.text((vx, y), val, fill=vc, font=f13)
        if has_icon:
            vw = draw_text_size(val, f13)[0]
            draw_panda(draw, vx + vw + 5, y + 1, size=14)
        y += 24

    y += 8
    # section: 一句话定位
    draw.line([(35, y), (W-35, y)], fill=BORDER, width=1);  y += 12
    bio_lines = wrap_text(
        "电子信息专业，目前一枚正在进阶的电工。热爱用代码偷懒，"
        "从自动化脚本到API逆向，从边缘计算到AI验证码识别——"
        "能用脚本搞定的事，绝不手动点两次。",
        f12, W - 80
    )
    draw_multiline(draw, 40, y, bio_lines, f12, DIM, 20)


def page_tech(draw):
    """Page 2: 技术栈"""
    y = 68

    sections = [
        ("💻", "编程语言", PINK, [
            "Python  ——  自动化、爬虫、数据处理、脚本开发",
            "TypeScript / JS  ——  前端交互、Node.js",
            "HTML / CSS",
        ]),
        ("⚡", "核心能力", CYAN, [
            "HTTP 协议分析 · API 接口逆向 · 加密参数破解",
            "AI 验证码识别（孪生网络 Siamese Network）",
            "Cloudflare Workers / KV 边缘计算",
            "VLESS / Trojan 代理协议 · Clash 订阅转换",
        ]),
        ("🛠️", "工程化", GREEN, [
            "Git 版本控制 · GitHub Actions CI/CD",
            "PyArmor 代码混淆 · PowerShell / Linux 部署",
            "Jekyll 博客 · PWA 离线支持",
        ]),
    ]
    for emoji, title, tc, items in sections:
        y = draw_section(draw, y, emoji, title, tc)
        for item in items:
            y = draw_bullet(draw, y, item, f12, VAL)
        y += 4


def page_projects(draw):
    """Page 3: 项目 & 特质"""
    y = 66

    # projects
    y = draw_section(draw, y, "🚀", "核心项目", PURPLE)

    proj_title = ["★  高可用自动化签到系统"]
    y = draw_multiline(draw, 42, y, proj_title, f12, ORANGE, 19)
    proj_desc = wrap_text(
        "独立开发增强版签到工具。突破环境检测限制，"
        "引入孪生网络 AI 识别复杂验证码，CI/CD 云端定时触发实现 7×24h 运行。",
        f11, W - 78
    )
    y = draw_multiline(draw, 48, y, proj_desc, f11, DIM, 18);  y += 6

    proj2_title = ["★  Cloudflare 边缘计算应用"]
    y = draw_multiline(draw, 42, y, proj2_title, f12, ORANGE, 19)
    proj2_desc = wrap_text(
        "Workers 动态路由、API 代理转发、VLESS 订阅一键转 Clash/Singbox 格式。",
        f11, W - 78
    )
    y = draw_multiline(draw, 48, y, proj2_desc, f11, DIM, 18);  y += 8

    # strengths
    draw.line([(35, y), (W-35, y)], fill=BORDER, width=1);  y += 10
    y = draw_section(draw, y, "✨", "个人特质", YELLOW)

    traits = [
        "极客精神：不局限于课本，主动研究开源源码攻克技术难点",
        "产品+技术思维：需求对接 → 逻辑梳理 → 方案输出 → 代码交付",
        "工程规范意识：代码混淆、CI/CD 流水线，超越同龄人交付标准",
    ]
    for t in traits:
        y = draw_bullet(draw, y, t, f11, VAL)


# ═════════════ 主程序 ══════════════

def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "kaka-carousel.gif")
    pages = [page_whoami, page_tech, page_projects]
    frames = []

    for idx, drawer in enumerate(pages):
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        draw_bg(d)
        drawer(d)
        draw_dots(d, idx, len(pages))

        frame = Image.new("RGB", (W, H), BG_TOP)
        frame.paste(img, (0,0), img)
        frames.append(frame)

    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=DURATION,
        loop=0,
        disposal=2,
    )

    size_kb = os.path.getsize(out) / 1024
    print(f"[OK] Generated: {out}")
    print(f"     Size: {W}x{H}, Frames: {len(frames)}, "
          f"{DURATION}ms/page, {size_kb:.0f}KB, Loop forever")

if __name__ == "__main__":
    main()
