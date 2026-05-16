from datetime import date, timedelta
from collections import Counter

import storage

# ---- OpenAI Function Definitions ----

FUNCTION_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_work_record",
            "description": "添加一条工作记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "日期，格式 YYYY-MM-DD，默认今天",
                    },
                    "description": {
                        "type": "string",
                        "description": "工作内容描述",
                    },
                    "time_spent": {
                        "type": "number",
                        "description": "花费时间，单位小时",
                    },
                    "category": {
                        "type": "string",
                        "description": "分类，如：开发、会议、文档、学习、运维等",
                    },
                },
                "required": ["description", "time_spent", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_records_by_date",
            "description": "按日期列出工作记录，不指定日期则列出全部",
            "parameters": {
                "type": "object",
                "properties": {
                    "date": {
                        "type": "string",
                        "description": "日期，格式 YYYY-MM-DD，不填则返回所有记录",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "summarize_records",
            "description": "汇总指定日期范围内的工作记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "开始日期 YYYY-MM-DD",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期 YYYY-MM-DD",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "generate_weekly_report",
            "description": "生成周报，默认最近一周",
            "parameters": {
                "type": "object",
                "properties": {
                    "end_date": {
                        "type": "string",
                        "description": "周报截止日期 YYYY-MM-DD，默认今天",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_time_allocation",
            "description": "分析指定日期范围内的时间分配情况",
            "parameters": {
                "type": "object",
                "properties": {
                    "start_date": {
                        "type": "string",
                        "description": "开始日期 YYYY-MM-DD",
                    },
                    "end_date": {
                        "type": "string",
                        "description": "结束日期 YYYY-MM-DD",
                    },
                },
                "required": ["start_date", "end_date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "give_suggestions",
            "description": "基于近期工作记录给出优化建议",
            "parameters": {
                "type": "object",
                "properties": {
                    "days": {
                        "type": "integer",
                        "description": "分析最近多少天的数据，默认14天",
                    },
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_keywords",
            "description": "按关键词搜索工作记录",
            "parameters": {
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "string",
                        "description": "搜索关键词，多个关键词用逗号分隔",
                    },
                },
                "required": ["keywords"],
            },
        },
    },
]


# ---- Skill Implementations ----

def add_work_record(date_str: str = None, description: str = "", time_spent: float = 0, category: str = "") -> str:
    if not date_str:
        date_str = date.today().isoformat()
    record = storage.add_record(date_str, description, time_spent, category)
    return f"已添加记录 #{record['id']}: {record['date']} | {record['category']} | {record['time_spent']}h | {record['description']}"


def list_records_by_date(date_str: str = None) -> str:
    records = storage.list_by_date(date_str)
    if not records:
        return f"没有找到记录" + (f"（{date_str}）" if date_str else "")
    total_time = sum(r["time_spent"] for r in records)
    lines = [f"共 {len(records)} 条记录，总用时 {total_time:.1f}h："]
    for r in records:
        lines.append(f"  #{r['id']} [{r['date']}] {r['category']} | {r['time_spent']}h | {r['description']}")
    return "\n".join(lines)


def summarize_records(start_date: str, end_date: str) -> str:
    records = storage.list_by_date_range(start_date, end_date)
    if not records:
        return f"{start_date} ~ {end_date} 期间没有工作记录"

    total_time = sum(r["time_spent"] for r in records)
    by_category = Counter()
    for r in records:
        by_category[r["category"]] += r["time_spent"]

    lines = [
        f"汇总 {start_date} ~ {end_date}：",
        f"共 {len(records)} 条记录，总用时 {total_time:.1f}h",
        "",
        "按分类统计：",
    ]
    for cat, t in by_category.most_common():
        pct = t / total_time * 100 if total_time > 0 else 0
        lines.append(f"  {cat}: {t:.1f}h ({pct:.0f}%)")

    return "\n".join(lines)


def generate_weekly_report(end_date: str = None) -> str:
    if not end_date:
        end_date_str = date.today().isoformat()
    else:
        end_date_str = end_date
    end = date.fromisoformat(end_date_str)
    start = end - timedelta(days=6)
    start_str = start.isoformat()

    records = storage.list_by_date_range(start_str, end_date_str)
    if not records:
        return f"本周（{start_str} ~ {end_date_str}）暂无工作记录"

    total_time = sum(r["time_spent"] for r in records)
    by_day = {}
    for r in records:
        by_day.setdefault(r["date"], []).append(r)

    lines = [f"周报（{start_str} ~ {end_date_str}）", f"总用时: {total_time:.1f}h", ""]
    for d in sorted(by_day):
        day_total = sum(r["time_spent"] for r in by_day[d])
        items = "；".join(f"{r['category']}({r['time_spent']}h)" for r in by_day[d])
        lines.append(f"{d} ({day_total:.1f}h): {items}")

    return "\n".join(lines)


def analyze_time_allocation(start_date: str, end_date: str) -> str:
    records = storage.list_by_date_range(start_date, end_date)
    if not records:
        return f"{start_date} ~ {end_date} 期间没有记录"

    total_time = sum(r["time_spent"] for r in records)
    days = len(set(r["date"] for r in records))
    working_days = max(days, 1)

    by_category = Counter()
    for r in records:
        by_category[r["category"]] += r["time_spent"]

    lines = [
        f"时间分配分析（{start_date} ~ {end_date}）",
        f"记录天数: {days} 天",
        f"总用时: {total_time:.1f}h",
        f"日均用时: {total_time / working_days:.1f}h/天",
        "",
        "分类占比：",
    ]
    for cat, t in by_category.most_common():
        pct = t / total_time * 100 if total_time > 0 else 0
        bar = "█" * int(pct / 5)
        lines.append(f"  {cat:8s} {bar} {t:.1f}h ({pct:.0f}%)")

    return "\n".join(lines)


def give_suggestions(days: int = 14) -> str:
    end = date.today()
    start = end - timedelta(days=days - 1)
    records = storage.list_by_date_range(start.isoformat(), end.isoformat())

    if not records:
        return f"最近 {days} 天暂无记录，建议开始记录工作内容以获得分析和建议。"

    total_time = sum(r["time_spent"] for r in records)
    working_days = len(set(r["date"] for r in records))
    avg_daily = total_time / max(working_days, 1)

    by_category = Counter()
    for r in records:
        by_category[r["category"]] += r["time_spent"]

    lines = [f"基于最近 {days} 天的分析：", ""]
    lines.append(f"日均工作时长: {avg_daily:.1f}h")

    if avg_daily > 10:
        lines.append("⚠ 日均工作时间较长，建议注意工作与休息平衡。")
    elif avg_daily < 4:
        lines.append("💡 日均工作时间偏少，可以考虑增加深度工作时间。")
    else:
        lines.append("✅ 日均工作时长合理。")

    lines.append("")
    top_cat = by_category.most_common(1)
    if top_cat:
        cat_name, cat_time = top_cat
        pct = cat_time / total_time * 100 if total_time > 0 else 0
        if pct > 60:
            lines.append(f"⚠ 「{cat_name}」占比过高（{pct:.0f}%），可能过于集中在单一类型工作上。")
        else:
            lines.append(f"📊 时间分配最多的类别是「{cat_name}」({pct:.0f}%)")

    # Check for gaps
    sorted_dates = sorted(set(r["date"] for r in records))
    gaps = 0
    for i in range(len(sorted_dates) - 1):
        d1 = date.fromisoformat(sorted_dates[i])
        d2 = date.fromisoformat(sorted_dates[i + 1])
        if (d2 - d1).days > 2:
            gaps += 1
    if gaps:
        lines.append(f"📝 有 {gaps} 段较长时间没有记录，建议保持记录的连续性。")

    return "\n".join(lines)


def search_by_keywords(keywords: str) -> str:
    records = storage.search_keywords(keywords)
    if not records:
        return f"未找到包含「{keywords}」的记录"

    lines = [f"搜索「{keywords}」，找到 {len(records)} 条记录："]
    for r in records:
        lines.append(f"  #{r['id']} [{r['date']}] {r['category']} | {r['time_spent']}h | {r['description']}")
    return "\n".join(lines)


# ---- Skill dispatcher ----

SKILL_MAP = {
    "add_work_record": add_work_record,
    "list_records_by_date": list_records_by_date,
    "summarize_records": summarize_records,
    "generate_weekly_report": generate_weekly_report,
    "analyze_time_allocation": analyze_time_allocation,
    "give_suggestions": give_suggestions,
    "search_by_keywords": search_by_keywords,
}


def execute_skill(name: str, arguments: dict) -> str:
    fn = SKILL_MAP.get(name)
    if not fn:
        return f"未知技能: {name}"
    return fn(**{k: v for k, v in arguments.items() if v is not None})
