#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-23 晨报·决策一体 Widget 联动刷新（11-23 "侧栏仍显示10项待确认"事故固化）。

事故：该 Widget（widget_8fb97907）workspace/index.html 内嵌数据由 05:47 主任务烘焙，
决策管线（对话裁决）执行后不刷新它 → 侧栏永久停留凌晨快照，与 decide.html/台账脱节。

本脚本以与 decide.html 完全同源的数据（decision_core.build_data + index.html + meta）
重烘焙 Widget 的 4 处动态点：
  ① dz-meta 看板行（版本/日期/时段/总数 ← index.html 板上事实）
  ② stats 三卡（新上板 ← meta.added 条数；候选待确认 ← 台账待确认数；过期删除 ← meta.removed_count）
  ③ 需确认 N 项 badge
  ④ cand-data JSON（候选表数据，与 decide.html 同一份）
凡替换均带 assert，缺锚点即报错退出，禁止静默写坏。

挂载：build_decide_page.py main() 末尾自动调用（决策页与晨报 Widget 同源同刻刷新）；
05:47 主任务仍按原路径刷新，两者数据同源不会打架。
"""
import json
import re
import sys
from pathlib import Path

BIDDING = Path("/Users/zhouhq/Documents/kimi/workspace/bidding-daily")
WIDGET_HTML = Path("/Users/zhouhq/Library/Application Support/kimi-desktop/daimon-share/daimon/agents/main/blueprint/widgets/widget_8fb97907-f189-4d86-9e4f-f177f5079ec8/workspace/index.html")
sys.path.insert(0, str(BIDDING))


def main():
    import decision_core
    data = decision_core.build_data()          # 与 decide.html 同一份候选数据
    items = data["items"]

    html_src = (BIDDING / "index.html").read_text(encoding="utf-8")
    mj = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html_src, re.S)
    board = json.loads(mj.group(1))
    version, total, bdate, tperiod = board.get("version"), len(board.get("projects", [])), board.get("date"), board.get("timePeriod")

    meta = json.loads((BIDDING / "reports" / "latest_meta.json").read_text(encoding="utf-8"))
    n_added = len(meta.get("added", []) or [])
    n_removed = meta.get("removed_count", 0)
    n_pending = len(items)

    html = WIDGET_HTML.read_text(encoding="utf-8")

    # ① 看板行
    pat = r'<span class="dz-meta">看板 v\d+ · [^<]*? · 共 \d+ 项</span>'
    assert re.search(pat, html), "锚点① dz-meta 未命中"
    html = re.sub(pat, f'<span class="dz-meta">看板 {version} · {bdate} {tperiod} · 共 {total} 项</span>', html)

    # ② stats 三卡（结构：新上板 / 候选待确认 / 过期删除 依次）
    pat = r'(<div class="stat"><div class="v">)\+?\d+(</div><div class="k">新上板</div>)'
    assert re.search(pat, html), "锚点②a 新上板未命中"
    html = re.sub(pat, rf'\g<1>+{n_added}\g<2>', html)
    pat = r'(class="stat stat-link" href="#dz-decision"><div class="v">)\d+(</div><div class="k">候选待确认)'
    assert re.search(pat, html), "锚点②b 候选待确认未命中"
    html = re.sub(pat, rf'\g<1>{n_pending}\g<2>', html)
    pat = r'(<div class="stat"><div class="v">)-\d+(</div><div class="k">过期删除</div>)'
    assert re.search(pat, html), "锚点②c 过期删除未命中"
    html = re.sub(pat, rf'\g<1>-{n_removed}\g<2>', html)

    # ③ badge（2026-11-25 起 cron 重构版 Widget 可能无此行，命中才改，不命中跳过）
    pat = r'<span class="badge warn">需确认 \d+ 项</span>'
    if re.search(pat, html):
        html = re.sub(pat, f'<span class="badge warn">需确认 {n_pending} 项</span>', html)

    # ④ cand-data（与 decide.html 同源 JSON）
    pat = r'(<script type="application/json" id="cand-data">).*?(</script>)'
    assert re.search(pat, html, re.S), "锚点④ cand-data 未命中"
    payload = decision_core.data_json(data)
    html = re.sub(pat, lambda m: m.group(1) + payload + m.group(2), html, flags=re.S)

    WIDGET_HTML.write_text(html, encoding="utf-8")
    print(f"晨报 Widget 已重烘焙：{version}/{total} · 待确认 {n_pending} · 新上板 +{n_added} · 过期 -{n_removed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
