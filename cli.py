"""FlowMate CLI — 命令行快速操作，无需打开 Chat 界面

用法：
  python cli.py sync              同步全部平台投递
  python cli.py sync --boss        只同步 Boss
  python cli.py sync --recommend   同步全部推荐
  python cli.py export             导出全部 Excel
  python cli.py export --delivery  只导出投递
  python cli.py report             生成今日日报
  python cli.py status             查看当前配置
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from skills import (
    sync_all_applications, sync_all_recommends,
    sync_boss_applications, sync_boss_recommends,
    sync_zhaopin_applications, sync_zhaopin_recommends,
    sync_liepin_applications, sync_liepin_recommends,
    generate_daily_report,
)
from settings import show_settings


def cmd_sync(args):
    """同步数据"""
    if "--boss" in args:
        print(sync_boss_applications())
    elif "--zhaopin" in args:
        print(sync_zhaopin_applications())
    elif "--liepin" in args:
        print(sync_liepin_applications())
    elif "--recommend" in args or "--rec" in args:
        if "--boss" in args:
            print(sync_boss_recommends())
        elif "--zhaopin" in args:
            print(sync_zhaopin_recommends())
        elif "--liepin" in args:
            print(sync_liepin_recommends())
        else:
            print(sync_all_recommends())
    else:
        print(sync_all_applications())


def cmd_export(args):
    """导出 Excel"""
    if "--delivery" in args or "-d" in args:
        from skills import export_all_delivery
        print(export_all_delivery())
    elif "--recommend" in args or "--rec" in args or "-r" in args:
        from skills import export_all_recommends_excel
        print(export_all_recommends_excel())
    elif "--boss" in args:
        from skills import export_boss_excel
        print(export_boss_excel())
    elif "--zhaopin" in args:
        from skills import export_zhaopin_to_excel
        print(export_zhaopin_to_excel())
    elif "--liepin" in args:
        from skills import export_liepin_to_excel
        print(export_liepin_to_excel())
    else:
        from skills import export_all_excel
        print(export_all_excel())


def cmd_report(args):
    """生成日报"""
    date = None
    for a in args:
        if a.startswith("--date="):
            date = a.split("=", 1)[1]
    print(generate_daily_report(date=date))


def cmd_status(args):
    """查看配置"""
    print(show_settings())


def cmd_summary(args):
    """求职汇总"""
    from skills import boss_job_summary
    print(boss_job_summary())


def cmd_chart(args):
    """生成图表"""
    from charts import chart_all, chart_daily_trend, chart_status_pie, chart_platform_compare

    if "--trend" in args or "-t" in args:
        days = 14
        for a in args:
            if a.startswith("--days="):
                days = int(a.split("=", 1)[1])
        print(chart_daily_trend(days))
    elif "--pie" in args or "-p" in args:
        print(chart_status_pie())
    elif "--compare" in args or "-c" in args:
        print(chart_platform_compare())
    else:
        print(chart_all())


COMMANDS = {
    "sync": cmd_sync,
    "s": cmd_sync,
    "export": cmd_export,
    "e": cmd_export,
    "report": cmd_report,
    "r": cmd_report,
    "status": cmd_status,
    "st": cmd_status,
    "summary": cmd_summary,
    "sm": cmd_summary,
    "chart": cmd_chart,
}


def main():
    if len(sys.argv) < 2:
        print("FlowMate CLI")
        print("  python cli.py sync              同步全部投递")
        print("  python cli.py sync --recommend   同步全部推荐")
        print("  python cli.py sync --boss        只同步Boss")
        print("  python cli.py sync --zhaopin     只同步智联")
        print("  python cli.py sync --liepin      只同步猎聘")
        print("  python cli.py export             导出全部Excel")
        print("  python cli.py export --delivery  只导出投递")
        print("  python cli.py export --recommend 只导出推荐")
        print("  python cli.py export --boss      只导出Boss")
        print("  python cli.py report             生成今日日报")
        print("  python cli.py report --date=2026-02-20  指定日期日报")
        print("  python cli.py status             查看配置")
        print("  python cli.py summary            求职汇总")
        print("  python cli.py chart              全部图表")
        print("  python cli.py chart --trend      投递趋势")
        print("  python cli.py chart --pie        状态分布")
        print("  python cli.py chart --compare    平台对比")
        return

    cmd = sys.argv[1]
    args = sys.argv[2:]
    fn = COMMANDS.get(cmd)
    if fn:
        fn(args)
    else:
        print(f"未知命令: {cmd}")
        print(f"可用: {', '.join(COMMANDS.keys())}")


if __name__ == "__main__":
    main()
