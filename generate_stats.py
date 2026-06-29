"""
GitHub Stats 卡片生成器
从 GitHub API 拉取数据，生成与 github-readme-stats 风格一致的 SVG 卡片
"""
import os, json, math, sys
from datetime import datetime
import requests

USER = os.environ.get("GH_USER", "kaka-niu")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HEADERS = {"Authorization": f"token {TOKEN}", "Accept": "application/vnd.github.v3+json"}

# ── 颜色主题 (tokyonight) ──
BG       = "#1a1b27"
TITLE_C  = "#70a5fd"
TEXT_C   = "#38bdae"
MUTED_C  = "#565f89"
BORDER_C = "#1a1b27"
ICON_COLORS = {
    "star":       "#e3b341",
    "commit":     "#9ece6a",
    "pr":         "#7aa2f7",
    "issue":      "#f7768e",
    "contrib":    "#bb9af7",
}

W = 460
H = 195

def api(url):
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code != 200:
        print(f"  [WARN] {url} → {r.status_code}")
        return {}
    return r.json()

def num(n):
    if n >= 1000:
        return f"{n/1000:.1f}k"
    return str(n)

def svg_card(title, items, output_path):
    rows = len(items)
    row_h = 36
    margin = 16
    inner_h = rows * row_h
    card_h = 60 + inner_h + margin

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{card_h}" viewBox="0 0 {W} {card_h}">
  <rect width="{W}" height="{card_h}" rx="8" fill="{BG}"/>
  <text x="20" y="36" font-family="Arial,sans-serif" font-size="14" fill="{MUTED_C}">{title}</text>
  <line x1="20" y1="44" x2="{W-20}" y2="44" stroke="{MUTED_C}" stroke-opacity="0.3"/>
'''
    for i, item in enumerate(items):
        y = 60 + i * row_h + 22
        icon = item.get("icon", "")
        label = item.get("label", "")
        value = item.get("value", "")
        icon_color = ICON_COLORS.get(icon, "#70a5fd")
        svg += f'  <text x="28" y="{y}" font-family="Arial,sans-serif" font-size="20" fill="{icon_color}">{_icon(icon)}</text>\n'
        svg += f'  <text x="56" y="{y}" font-family="Arial,sans-serif" font-size="14" fill="{TEXT_C}">{_esc(label)}</text>\n'
        svg += f'  <text x="{W-28}" y="{y}" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#c0caf5" text-anchor="end">{num(value)}</text>\n'

    svg += '</svg>'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)

def _icon(k):
    m = {"star":"★","commit":"●","pr":"◎","issue":"○","contrib":"◆"}
    return m.get(k, "●")

def _esc(s):
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

def lang_bar(name, pct, color, index):
    colors = ["#f7768e","#9ece6a","#7aa2f7","#e3b341","#bb9af7","#73daca","#ff9e64","#2ac3de"]
    c = colors[index % len(colors)]
    return f'  <rect x="24" y="{76+index*30}" width="{max(pct*3.8,1)}" height="14" rx="4" fill="{c}" opacity="0.8"/>\n' \
           f'  <text x="28" y="{87+index*30}" font-family="Arial,sans-serif" font-size="11" fill="#1a1b27">{_esc(name)}</text>\n' \
           f'  <text x="{W-24}" y="{87+index*30}" font-family="Arial,sans-serif" font-size="11" fill="#c0caf5" text-anchor="end">{pct:.1f}%</text>'

def generate_langs(top_langs):
    """简版语言条"""
    total = sum(top_langs.values())
    items = [(k, v/total*100) for k, v in sorted(top_langs.items(), key=lambda x:-x[1])[:6]]
    bar_h = 56 + len(items) * 30 + 16
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{bar_h}" viewBox="0 0 {W} {bar_h}">
  <rect width="{W}" height="{bar_h}" rx="8" fill="{BG}"/>
  <text x="20" y="36" font-family="Arial,sans-serif" font-size="14" fill="{MUTED_C}">📊 Top Languages</text>
  <line x1="20" y1="44" x2="{W-20}" y2="44" stroke="{MUTED_C}" stroke-opacity="0.3"/>
'''
    for i, (name, pct) in enumerate(items):
        svg += lang_bar(name, pct, None, i)
    svg += '</svg>'
    path = "assets/top-langs.svg"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"  ✅ {path}")

def generate_trophy(data):
    """生成奖杯卡片"""
    # 统计各项数据
    stars = data.get("stars", 0)
    commits = data.get("commits", 0)
    prs = data.get("prs", 0)
    issues = data.get("issues", 0)
    contrib = data.get("contrib", 0)

    items = [
        {"icon":"star","label":"Total Stars","value":stars},
        {"icon":"commit","label":"Total Commits","value":commits},
        {"icon":"pr","label":"Pull Requests","value":prs},
        {"icon":"issue","label":"Issues","value":issues},
        {"icon":"contrib","label":"Contributions","value":contrib},
    ]
    svg_card("🏆 GitHub Trophies", items, "assets/trophy.svg")

def main():
    print(f"📊 开始生成统计卡片 for {USER}...")
    os.makedirs("assets", exist_ok=True)

    # ── 1) 用户总览 ──
    user = api(f"https://api.github.com/users/{USER}")
    public_repos = user.get("public_repos", 0)
    followers = user.get("followers", 0)
    total_stars = 0
    total_forks = 0

    repos = api(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner")
    lang_count = {}
    for repo in repos:
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        lang = repo.get("language")
        if lang:
            lang_count[lang] = lang_count.get(lang, 0) + 1

    # ── 2) 搜索提交数 (近似) ──
    commit_search = api(f"https://api.github.com/search/commits?q=author:{USER}&per_page=1")
    total_commits = commit_search.get("total_count", 0)

    # ── 3) 搜索 PR 数 ──
    pr_search = api(f"https://api.github.com/search/issues?q=author:{USER}+type:pr&per_page=1")
    total_prs = pr_search.get("total_count", 0)

    # ── 4) 搜索 Issue 数 ──
    issue_search = api(f"https://api.github.com/search/issues?q=author:{USER}+type:issue&per_page=1")
    total_issues = issue_search.get("total_count", 0)

    stats = [
        {"icon":"star",   "label":"Total Stars","value":total_stars},
        {"icon":"commit", "label":"Total Commits","value":total_commits},
        {"icon":"pr",     "label":"Pull Requests","value":total_prs},
        {"icon":"issue",  "label":"Issues","value":total_issues},
    ]
    svg_card("📊 GitHub Stats", stats, "assets/stats.svg")

    # ── 语言 ──
    generate_langs(lang_count)

    # ── 奖杯 ──
    generate_trophy({
        "stars": total_stars,
        "commits": total_commits,
        "prs": total_prs,
        "issues": total_issues,
        "contrib": public_repos,
    })

    print("✅ 全部卡片生成完成!")

if __name__ == "__main__":
    main()
