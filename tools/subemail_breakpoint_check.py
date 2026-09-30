# -*- coding: utf-8 -*-
"""邮件管线断点新鲜度检查（2026-09-23 新增，供招标看板月度健康自检调用）。

检查 金融要闻周报 两条邮件日更管线（12:13 标讯订阅 / 12:23 中标监控）：
1. state.json / win_state.json 的 last_success_at 距今是否超过 2 天
   （超过说明管线当前停滞，重新开机后将按动态窗口自动回补，但需人工知晓）；
2. daily_report.md 运行日志中同一管线相邻两次成功运行的间隔是否超过 2 天
   （超过即"曾中断 N 天"，动态窗口机制下重跑已自动回补，建议抽查该区间线索完整性）。

输出：首行 SUBEMAIL_BREAKPOINT: PASS|WARN，随后逐条明细。退出码 0=PASS，1=WARN。
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/Workspaces/金融要闻周报")
SUB = WS / "subemail_daily"
GAP_DAYS = 2  # 超过该间隔视为中断/停滞


def check_freshness(name, path):
    """返回 (状态行, 是否WARN)。"""
    if not path.exists():
        return f"{name}: WARN state 文件缺失（{path.name}），动态窗口断点无法回溯", True
    try:
        st = json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:
        return f"{name}: WARN state 文件解析失败（{e}）", True
    last = st.get("last_success_at")
    if not last:
        return f"{name}: WARN 无 last_success_at 字段（动态窗口未生效？）", True
    age = (datetime.now() - datetime.fromisoformat(last)).total_seconds() / 86400
    if age > GAP_DAYS:
        return (f"{name}: WARN 断点距今 {age:.1f} 天未推进，管线当前停滞"
                f"（恢复运行后将自动回补近 {min(60, int(age) + 1)} 天邮件）"), True
    return f"{name}: PASS 断点新鲜（{age:.1f} 天前推进）", False


def check_report_gaps():
    """解析 daily_report.md，找同一管线相邻运行间隔 > GAP_DAYS 的空窗。"""
    report = SUB / "daily_report.md"
    if not report.exists():
        return ["运行日志缺失（daily_report.md），无法检测历史中断"], True
    runs = {"订阅管线": [], "中标管线": []}
    for line in report.read_text(encoding="utf-8").splitlines():
        m = re.match(r"- (\d{4}-\d{2}-\d{2} \d{2}:\d{2}) (订阅管线|中标管线)：", line)
        if m:
            runs[m.group(2)].append(datetime.strptime(m.group(1), "%Y-%m-%d %H:%M"))
    out, warn = [], False
    for name, ts in runs.items():
        ts = sorted(set(ts))
        if len(ts) < 2:
            continue
        found = False
        for a, b in zip(ts, ts[1:]):
            gap = (b - a).total_seconds() / 86400
            if gap > GAP_DAYS:
                warn = True
                found = True
                out.append(f"{name}: WARN {a:%Y-%m-%d} ~ {b:%Y-%m-%d} 中断 {gap:.0f} 天"
                           f"（重跑已按动态窗口自动回补，建议抽查该区间线索完整性）")
        if not found:
            out.append(f"{name}: PASS 日志内无超过 {GAP_DAYS} 天的运行间隔（共 {len(ts)} 次记录）")
    return out, warn


def main():
    lines, warns = [], False
    for name, fn in (("标讯管线(12:13)", "state.json"), ("中标管线(12:23)", "win_state.json")):
        line, w = check_freshness(name, SUB / fn)
        lines.append(line)
        warns = warns or w
    gap_lines, w = check_report_gaps()
    lines.extend(gap_lines)
    warns = warns or w
    print(f"SUBEMAIL_BREAKPOINT: {'WARN' if warns else 'PASS'}")
    for line in lines:
        print(f"- {line}")
    return 1 if warns else 0


if __name__ == "__main__":
    sys.exit(main())
