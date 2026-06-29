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
try:
    f14b = ImageFont.truetype(FP, 15)   # 粗体标题
    f13  = ImageFont.truetype(FP, 13)   # 正常
    f12  = ImageFont.truetype(FP, 12)   # 小字
    f11  = ImageFont.truetype(FP, 11)   # 更小
except Exception:
    f14b = f13 = f12 = f11 = ImageFont.load_default()

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

    # 标题文字
    title = "Would you like me"
    tw = draw_text_size(title, f14b)[0]
    draw.text(((W-tw)/2, 33), title, fill=BLUE, font=f14b)

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
    draw.text((35, y), "▸ 身份", fill=PINK, font=f14b);  y += 26
    rows = [
        ("location",  "四川 ·宜宾",         BLUE),
        ("status",    "嵌入式云平台 / 自动化开发者", GREEN),
        ("passion",   "Python · API逆向 · Serverless", VAL),
        ("fun_fact",  "能用脚本搞定的，绝不手动点两次", YELLOW),
    ]
    for lbl, val, vc in rows:
        lw = draw_text_size(lbl, f13)[0]
        draw.text((48, y), lbl, fill=BLUE, font=f13)
        draw.text((48 + lw + 6, y), ":", fill=DIM, font=f13)
        draw.text((62 + lw + 6, y), val, fill=vc, font=f13)
        y += 24

    y += 8
    # section: 一句话定位
    draw.line([(35, y), (W-35, y)], fill=BORDER, width=1);  y += 12
    bio_lines = wrap_text(
        "热爱通过技术解决实际问题。从自动化签到到边缘计算部署，"
        "从API逆向到AI验证码识别——能用代码搞定的事，绝不手动点两次。",
        f12, W - 80
    )
    draw_multiline(draw, 40, y, bio_lines, f12, DIM, 20)


def page_tech(draw):
    """Page 2: 技术栈"""
    y = 68

    sections = [
        ("▸ 编程语言", PINK, [
            "Python  ——  自动化、爬虫、数据处理、脚本开发",
            "TypeScript / JS  ——  前端交互、Node.js",
            "HTML / CSS",
        ]),
        ("▸ 核心能力", CYAN, [
            "HTTP 协议分析 · API 接口逆向 · 加密参数破解",
            "AI 验证码识别（孪生网络 Siamese Network）",
            "Cloudflare Workers / KV 边缘计算",
            "VLESS / Trojan 代理协议 · Clash 订阅转换",
        ]),
        ("▸ 工程化", GREEN, [
            "Git 版本控制 · GitHub Actions CI/CD",
            "PyArmor 代码混淆 · PowerShell / Linux 部署",
            "Jekyll 博客 · PWA 离线支持",
        ]),
    ]
    for title, tc, items in sections:
        draw.text((35, y), title, fill=tc, font=f14b);  y += 24
        for item in items:
            lines = wrap_text("· " + item, f12, W - 75)
            y = draw_multiline(draw, 45, y, lines, f12, VAL, 19)
        y += 4


def page_projects(draw):
    """Page 3: 项目 & 特质"""
    y = 66

    # projects
    draw.text((35, y), "▸ 核心项目", fill=PURPLE, font=f14b);  y += 24

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
    draw.text((35, y), "▸ 个人特质", fill=YELLOW, font=f14b);  y += 22

    traits = [
        "极客精神：不局限于课本，主动研究开源源码攻克技术难点",
        "产品+技术思维：需求对接 → 逻辑梳理 → 方案输出 → 代码交付",
        "工程规范意识：代码混淆、CI/CD 流水线，超越同龄人交付标准",
    ]
    for t in traits:
        lines = wrap_text("· " + t, f11, W - 72)
        y = draw_multiline(draw, 42, y, lines, f11, VAL, 18)


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
