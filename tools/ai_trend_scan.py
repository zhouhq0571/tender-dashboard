#!/usr/bin/env python3
"""大模型/智能体主线扫描（零模型 token，2026-10-24 立规）

用途：从在板 index.html 结构化提取「大模型/智能体/智算/AI平台」主线项目，
输出 Markdown 对比表（默认仅打印；--save 追加落盘 archive/ 便于周度复盘重跑）。

口径：tags 含「大模型应用」或 项目名/概况命中 智能体|大模型|智算|AI平台|人工智能平台。
排序：在招按截止日期升序；已截止单列。

用法：
    python3 tools/ai_trend_scan.py            # 打印到 stdout
    python3 tools/ai_trend_scan.py --save     # 打印 + 追加落盘 archive/ai_trend_scan_<date>.md
"""
import argparse
import datetime
import json
import re
from pathlib import Path

WS = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
INDEX = WS / "index.html"
PATTERN = re.compile(r"智能体|大模型|智算|AI平台|人工智能平台")


def load_projects():
    html = INDEX.read_text(encoding="utf-8")
    m = re.search(
        r'<script type="application/json" id="tender-data">(.*?)</script>',
        html, re.DOTALL)
    if not m:
        raise SystemExit("❌ index.html 中找不到 tender-data JSON")
    return json.loads(m.group(1))["projects"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true", help="追加落盘 archive/")
    args = ap.parse_args()

    projects = load_projects()
    hits = [
        p for p in projects
        if "大模型应用" in p.get("tags", [])
        or PATTERN.search(p["project"] + " " + p.get("overview", ""))
    ]
    active = sorted(
        (p for p in hits if "已截止" not in p.get("rec", "")),
        key=lambda p: p["deadline"])
    closed = [p for p in hits if "已截止" in p.get("rec", "")]
    today = datetime.date.today().isoformat()

    lines = []
    lines.append(f"# 大模型/智能体主线扫描 · {today}")
    lines.append("")
    lines.append(
        f"在板命中 {len(hits)} 条（在招 {len(active)} / 已截止 {len(closed)}）"
        f"｜口径：tags 含「大模型应用」或名称/概况命中 智能体|大模型|智算|AI平台")
    lines.append("")
    lines.append("| id | 机构 | 项目 | 截止 | 预算 | 建议 | 上板日期 |")
    lines.append("|---|---|---|---|---|---|---|")
    for p in active:
        budget = (p.get("budget") or "-").replace("万元", "万")
        rec = (p.get("rec") or "").split()[-1]
        lines.append(
            f"| {p['id']} | {p['company']} | {p['project'][:30]} "
            f"| {p['deadline'][:10]} | {budget} | {rec} | {p.get('date', '')} |")
    if closed:
        lines.append("")
        lines.append(f"已截止 {len(closed)} 条："
                     + "、".join(f"{p['company']}({p['id']})" for p in closed))
    out = "\n".join(lines)
    print(out)

    if args.save:
        dest = WS / "archive" / f"ai_trend_scan_{today}.md"
        dest.parent.mkdir(exist_ok=True)
        dest.write_text(out + "\n", encoding="utf-8")
        print(f"\n✅ 已落盘 {dest}")


if __name__ == "__main__":
    main()
