"""FlowMate 数据可视化 — 零依赖 ASCII 图表"""

from datetime import date, timedelta
from collections import Counter, defaultdict

from storage import _load_jobs

BAR_CHARS = "▁▂▃▄▅▆▇█"


def _daily_counts(days: int = 14) -> dict:
    """获取最近 N 天每天的投递数量"""
    jobs = _load_jobs()
    today = date.today()
    counts = defaultdict(lambda: defaultdict(int))

    for j in jobs:
        d = j.get("date", "")
        if not d:
            continue
        try:
            job_date = date.fromisoformat(d)
            if (today - job_date).days <= days:
                platform = j.get("platform", "其他")
                counts[d][platform] += 1
        except ValueError:
            pass

    result = {}
    for i in range(days, -1, -1):
        d = (today - timedelta(days=i)).isoformat()
        result[d] = dict(counts.get(d, {}))
    return result


def chart_daily_trend(days: int = 14) -> str:
    """每日投递趋势折线图（ASCII）"""
    data = _daily_counts(days)
    if not data:
        return "暂无投递数据。先说「同步投递」拉取。"

    all_vals = []
    for platforms in data.values():
        all_vals.append(sum(platforms.values()))
    if not all_vals or max(all_vals) == 0:
        return "暂无投递数据。"

    mx = max(all_vals)
    lines = [f"## 📈 每日投递趋势（近{days}天）", "", "```"]

    max_bar_len = 30
    for d, platforms in data.items():
        total = sum(platforms.values())
        bar_len = int(total / mx * max_bar_len) if mx > 0 else 0
        bar = "█" * bar_len
        day_name = ["一", "二", "三", "四", "五", "六", "日"][date.fromisoformat(d).weekday()]
        lines.append(f"  {d[-5:]} 周{day_name} {bar} {total}")

    lines.append("```")
    return "\n".join(lines)


def chart_status_pie() -> str:
    """投递状态分布饼图（ASCII）"""
    jobs = _load_jobs()
    if not jobs:
        return "暂无投递数据。"

    today = date.today().isoformat()
    recent = [j for j in jobs if j.get("date") == today]
    if not recent:
        # Use all data if nothing today
        recent = jobs

    status_count = Counter(j.get("status", "") for j in recent)
    total = sum(status_count.values())

    lines = [f"## 🍩 投递状态分布（{len(recent)} 条）", ""]

    status_icons = {
        "沟通过": "💬", "已投递": "📤", "面试": "🎯", "感兴趣": "⭐",
        "智联-已投递": "📤", "智联-收藏": "⭐", "智联-推荐": "📋",
        "猎聘-已投递": "📤", "猎聘-已查看": "👁", "猎聘-面试": "🎯", "猎聘-收藏": "⭐", "猎聘-推荐": "📋",
        "每日推荐": "📋", "不合适": "❌",
    }

    for status, count in status_count.most_common():
        pct = count / total * 100 if total > 0 else 0
        bar_len = int(pct / 2)
        bar = "█" * bar_len
        icon = status_icons.get(status, "")
        lines.append(f"  {icon} {status:12s} {bar} {count}条 ({pct:.0f}%)")

    return "\n".join(lines)


def chart_platform_compare() -> str:
    """平台对比柱状图（ASCII）"""
    jobs = _load_jobs()
    if not jobs:
        return "暂无投递数据。"

    by_platform = defaultdict(lambda: defaultdict(int))
    for j in jobs:
        platform = j.get("platform", "其他")
        status = j.get("status", "")
        by_platform[platform][status] += 1

    lines = ["## 📊 平台对比", ""]

    all_platforms = sorted(by_platform.keys())
    # Get max count for scaling
    max_total = max(sum(s.values()) for s in by_platform.values())

    for platform in all_platforms:
        statuses = by_platform[platform]
        total = sum(statuses.values())
        bar_len = int(total / max_total * 25) if max_total > 0 else 0
        bar = "█" * bar_len
        detail = " | ".join(f"{k[-3:]}:{v}" for k, v in sorted(statuses.items(), key=lambda x: -x[1])[:3])
        lines.append(f"  {platform:10s} {bar} {total:4d}条  ({detail})")

    return "\n".join(lines)


def chart_all() -> str:
    """一次性输出全部图表"""
    return "\n\n".join([
        chart_daily_trend(14),
        chart_status_pie(),
        chart_platform_compare(),
    ])
