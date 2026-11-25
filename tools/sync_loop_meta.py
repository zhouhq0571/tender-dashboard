#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-23 meta 自愈脚本（11-23 双显示不一致事故固化，教训通则"规则必须代码化"）。

事故：决策管线上板 7 项后 latest_meta.json 未同步（仍 v439/74/candidates=10），
decide.html 构建时与晨报消费同一 stale meta → 两边数字双双失真。

本脚本从唯一事实源派生 meta 字段，任何消费 meta 的 UI 构建/部署前先跑一遍即可：
- version/total/date/timePeriod ← index.html tender-data JSON（板上事实）
- candidates ← pending_candidates.json status=待确认 条数（台账事实）
- added（今日纳入）← pending 中 decision_date==今天 的纳入条目，回查板上最终值
  （deadline/tags/rec/budget 取上板后值，遵守 2026-09-30 规则 O-晨报字段红线）

挂载点（已有）：
- build_decide_page.py 构建前自动调用（decide 页永远读到自愈后 meta）
- safe_deploy.sh 部署前自动调用（兜底所有 meta 消费方）
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

BIDDING = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
META = BIDDING / "reports" / "latest_meta.json"
PENDING = BIDDING / "pending_candidates.json"


def board_facts():
    html = (BIDDING / "index.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
    d = json.loads(m.group(1))
    return d.get("version"), len(d.get("projects", [])), d.get("date"), d.get("timePeriod"), d.get("projects", [])


def main():
    version, total, date, time_period, projects = board_facts()
    pend = json.loads(PENDING.read_text(encoding="utf-8"))
    candidates = sum(1 for c in pend if str(c.get("status", "待确认")) in ("待确认", "None", ""))

    today = datetime.now().strftime("%Y-%m-%d")
    meta = json.loads(META.read_text(encoding="utf-8")) if META.exists() else {}

    added = []
    for c in pend:
        if c.get("status") == "纳入" and c.get("decision_date") == today:
            # 回查板上最终值（公司+项目前缀匹配），匹配失败退回台账值
            hit = next((p for p in projects
                        if p["company"] == c["company"] and p["project"].startswith(c["project"][:15])), None)
            src = hit or c
            added.append({
                "company": c["company"],
                "project": c["project"],
                "budget": (hit or {}).get("budget", c.get("budget", "-")),
                "deadline": src.get("deadline", c.get("deadline", "")),
                "tags": src.get("tags", c.get("tags", [])) if isinstance(src.get("tags"), list) else c.get("tags", []),
            })

    changed = []
    for key, val in [("version", version), ("total", total), ("date", date),
                     ("timePeriod", time_period), ("candidates", candidates)]:
        if meta.get(key) != val:
            changed.append(f"{key}: {meta.get(key)} → {val}")
            meta[key] = val
    if added:
        meta["added"] = added
        changed.append(f"added: {len(added)} 条今日纳入")
    elif meta.get("date") == date and not meta.get("added"):
        pass  # 保持自动化写入的 added

    META.write_text(json.dumps(meta, ensure_ascii=False, indent=1), encoding="utf-8")
    if changed:
        print("meta 自愈:" + "；".join(changed))
    else:
        print(f"meta 无需自愈（{version}/{total}/candidates={candidates}）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
