"""
GitHub Bio 自动更新脚本
========================
根据当前时间（北京时间）自动切换 GitHub Bio 内容：
  - 早晨 (6:00-11:59)  ☀️ 早安状态
  - 白天 (12:00-17:59) 💻 摸鱼/写码状态
  - 傍晚 (18:00-20:59) 🌆 下班状态
  - 深夜 (21:00-5:59)  🌙 夜间状态

使用方式：
  1. 设置环境变量 GITHUB_TOKEN（在 GitHub Settings > Developer settings > Personal access tokens 生成）
  2. 直接运行：python update_bio.py
  3. 或配合 GitHub Actions 自动运行（见 update-bio.yml）

权限要求：Token 需要 `user` scope
"""

import os
import requests
from datetime import datetime, timezone, timedelta

# ── 配置区 ──────────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")   # 从环境变量读取，不要硬编码！
GITHUB_API   = "https://api.github.com"

# 北京时间 = UTC+8
CST = timezone(timedelta(hours=8))

# Bio 时间段配置（根据喜好自由修改）
BIO_SCHEDULE = [
    # (开始小时, 结束小时, bio 内容)
    (6,  11, "☀️ 早起写代码 | 🍳 早饭还没吃 | Python & 自动化"),
    (12, 17, "💻 Coding... | ☕ Coffee Time | 🤖 搞自动化"),
    (18, 20, "🌆 下班了 | 🎮 摸鱼时间 | 📚 学点新东西"),
    (21, 29, "🌙 深夜码农 | 💤 困但睡不着 | 🔥 Bug 消灭中"),  # 21-23 + 0-5
]

def get_current_bio() -> str:
    """根据北京时间返回对应 Bio"""
    now_hour = datetime.now(CST).hour
    for start, end, bio in BIO_SCHEDULE:
        # 处理跨午夜情况（21-29 意味着 21:00 ~ 次日5:59）
        if end > 24:
            if now_hour >= start or now_hour < (end - 24):
                return bio
        else:
            if start <= now_hour <= end:
                return bio
    return "💻 kaka-niu | 学生 | Python 爱好者"  # 兜底

def update_bio(new_bio: str) -> bool:
    """
    调用 GitHub PATCH /user 接口更新 Bio
    返回 True 表示成功，False 表示失败
    """
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN 未设置，请设置环境变量后重试")
        return False

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    payload = {"bio": new_bio}

    resp = requests.patch(f"{GITHUB_API}/user", json=payload, headers=headers)

    if resp.status_code == 200:
        print(f"[OK] Bio 更新成功 → {new_bio}")
        return True
    else:
        print(f"[ERROR] 更新失败，HTTP {resp.status_code}: {resp.text}")
        return False

def get_current_profile() -> dict:
    """获取当前个人资料（可选，用于调试确认）"""
    if not GITHUB_TOKEN:
        return {}
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }
    resp = requests.get(f"{GITHUB_API}/user", headers=headers)
    return resp.json() if resp.status_code == 200 else {}

# ── 进阶功能：批量更新其他资料字段 ─────────────────────────────────────────
def update_profile(**kwargs) -> bool:
    """
    批量更新个人资料
    可用字段：name, bio, blog, location, email, hireable, twitter_username
    示例：update_profile(bio="新 Bio", location="四川·资阳")
    """
    if not GITHUB_TOKEN:
        print("[ERROR] GITHUB_TOKEN 未设置")
        return False

    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.patch(f"{GITHUB_API}/user", json=kwargs, headers=headers)

    if resp.status_code == 200:
        updated = resp.json()
        print(f"[OK] 资料更新成功")
        print(f"     Name     : {updated.get('name')}")
        print(f"     Bio      : {updated.get('bio')}")
        print(f"     Location : {updated.get('location')}")
        print(f"     Blog     : {updated.get('blog')}")
        return True
    else:
        print(f"[ERROR] 更新失败: {resp.status_code} → {resp.text}")
        return False


# ── 主入口 ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    now = datetime.now(CST)
    print(f"[INFO] 当前北京时间: {now.strftime('%Y-%m-%d %H:%M:%S')} (周{now.weekday()+1})")

    # 获取应该设置的 Bio
    bio = get_current_bio()
    print(f"[INFO] 目标 Bio: {bio}")

    # 更新
    success = update_bio(bio)

    if success:
        # 验证确认
        profile = get_current_profile()
        print(f"[INFO] 当前 Bio 确认: {profile.get('bio', '(获取失败)')}")

    # ── 示例：一次性更新完整资料（取消注释即可使用）──
    # update_profile(
    #     name="kaka",
    #     bio=bio,
    #     location="四川 · 资阳",
    #     blog="",           # 你的博客或网站
    # )
