#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sweep_candidates.py — 零模型多路采集编排器（2026-11-09 立规）

背景：周老师要求每日晨报候选 ≥10 条有效在招（「否则再这么下去你就废了」），
同时坚持 token 最小化/人工干预最小化。本编排器把"多通道采集+归一化+查重"
全部压在脚本层（零模型），模型只读最终短名单补详情：

  依次执行各通道采集脚本（子进程，单个超时受限，失败不致命）
  → 按各通道落盘格式归一化为统一条目
  → 管道送 dedup_filter.py（全库指纹 + 在板查重 + seen 库，一处判定不重复造轮子）
  → 短名单落盘 monitor/sweep_shortlist_<ts>.json

用法: python3 tools/sweep_candidates.py [--window N] [--no-vipsearch]
输出: 一行 JSON 汇总（各通道 raw/kept/fresh + 短名单路径），短名单文件供主任务读取。
"""
import json, os, sys, glob, subprocess, time, argparse
from datetime import datetime

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bidding-daily/
REPO = BASE
TOOLS = os.path.join(BASE, 'tools')
MON = os.path.join(BASE, 'monitor')

# (名称, 命令模板, 落盘 glob, 归一化来源键)
CHANNELS = [
    ("vip_tb",   [sys.executable, "vip_subscribe_tabbit.py", "2"],     "subscribe_items_tabbit_*.json", "keep"),
    ("kc",       [sys.executable, "kc_bid_fetch.py", "{window}"],      "new_items_kc_*.json",     "new_items"),
    ("qlsub",    [sys.executable, "ql_subscribe_fetch.py", "{window}"],"subscribe_items_*.json",  "keep"),
    ("l1bank",   [sys.executable, "l1_bank_fetch.py"],                 "new_items_l1bank_*.json", "new_items"),
    ("ccb",      [sys.executable, "ccb_ibuy_fetch.py"],                "new_items_ccb_*.json",    "new_items"),
    ("lcy",      [sys.executable, "lcy_fallback_kc.py"],               "new_items_lcykc_*.json",  "new_items"),
    ("lecaiyun", [sys.executable, "lecaiyun_fetch.py"],               "new_items_lecaiyun_*.json","new_items"),
    ("sdicc",    [sys.executable, "sdicc_fetch.py"],                  "new_items_sdicc_*.json",  "new_items"),  # 2026-11-19 国投平台L1直连（采购单位=国投泰康信托，4公开接口）
    ("sm",       [sys.executable, "source_monitor.py", "--tiers", "S,A"], "new_items_20*.json",    "new_items"),
    ("qlsearch", [sys.executable, "ql_vip_search.py", "{keywords}"],   "new_items_qlsearch_*.json","new_items"),
]


TIMEOUTS = {"vip_tb": 420}  # vip_tb 含 90s 人工滑块等待窗，最坏约 360s


def run_channel(name, cmd, pattern, run_start):
    """跑一个通道，返回 (状态, 本run产出的文件列表, stdout末行)。"""
    try:
        r = subprocess.run(cmd, cwd=TOOLS, capture_output=True, text=True,
                           timeout=TIMEOUTS.get(name, 300), env={**os.environ})
        status = "ok" if r.returncode == 0 else f"rc{r.returncode}"
        tail = (r.stdout or "").strip().splitlines()
        tail = tail[-1][:120] if tail else ""
    except subprocess.TimeoutExpired:
        status, tail = "timeout", ""
    except Exception as e:
        status, tail = f"err:{str(e)[:60]}", ""
    files = [f for f in glob.glob(os.path.join(MON, pattern))
             if os.path.getmtime(f) >= run_start - 2]
    return status, sorted(files), tail


def normalize(path, key, origin):
    """归一化各通道条目为统一六字段+origin。"""
    try:
        data = json.load(open(path, encoding='utf-8'))
    except Exception:
        return []
    items = data.get(key)
    if isinstance(items, dict):
        tmp = []
        for v in items.values():
            tmp.extend(v if isinstance(v, list) else [v])
        items = tmp
    if not isinstance(items, list):
        return []
    out = []
    for it in items:
        if not isinstance(it, dict):
            continue
        t = it.get('title') or it.get('project') or ''
        u = it.get('url') or it.get('link') or ''
        if not t or not u:
            continue
        out.append({
            "title": ' '.join(str(t).split()),
            "url": str(u).strip(),
            "date": it.get('date') or it.get('pubdate') or '',
            "deadline": it.get('deadline') or '',
            "contact": it.get('contact') or '',
            "source": it.get('source') or origin,
            "origin": origin,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--window', type=int, default=0, help='日期窗口天数（0=自动：周一4，其余3）')
    ap.add_argument('--no-vipsearch', action='store_true', help='跳过千里马主动泛词搜索')
    ap.add_argument('--only', default='', help='只跑指定通道（逗号分隔，如 kc,sm,qlsearch；调试/单通道重跑用）')
    args = ap.parse_args()

    window = args.window or (4 if datetime.now().weekday() == 0 else 3)
    run_start = time.time()
    run_at = datetime.now().strftime('%Y%m%d_%H%M')

    # 主动搜索关键词：按星期取轮动词表（tools/vip_search_words.json）
    keywords = []
    if not args.no_vipsearch:
        try:
            rot = json.load(open(os.path.join(TOOLS, 'vip_search_words.json'), encoding='utf-8'))
            keywords = rot['rotation'][datetime.now().weekday() % len(rot['rotation'])]
        except Exception:
            keywords = ["银行 系统", "信托 系统", "大模型 银行"]

    merged, summary = [], {}
    only = set(x.strip() for x in args.only.split(',') if x.strip())
    for name, cmd_t, pattern, key in CHANNELS:
        if only and name not in only:
            summary[name] = {"status": "skipped(--only)"}
            continue
        if name == "qlsearch" and args.no_vipsearch:
            summary[name] = {"status": "skipped"}
            continue
        cmd = [c.format(window=window, keywords=" ".join(f'"{k}"' for k in keywords))
               for c in cmd_t]
        status, files, tail = run_channel(name, cmd, pattern, run_start)
        items = []
        for f in files:
            items.extend(normalize(f, key, name))
        summary[name] = {"status": status, "files": len(files), "kept": len(items), "tail": tail}
        merged.extend(items)

    # 跨通道按 URL/标题先去一次重（dedup_filter 内部还有指纹+板上+seen 三道）
    uniq, seen_k = [], set()
    for it in merged:
        k = it['url'].split('#')[0].rstrip('/').lower() or it['title'][:40]
        if k in seen_k:
            continue
        seen_k.add(k)
        uniq.append(it)

    # dedup_filter：stdin 进、stdout 出（内部登记 seen 库）
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "dedup_filter.py")],
                       input=json.dumps(uniq, ensure_ascii=False),
                       capture_output=True, text=True, timeout=180, cwd=TOOLS)
    fresh = json.loads(r.stdout) if r.returncode == 0 and r.stdout.strip() else []

    # 2026-11-20 机构范围硬检接入采集管线（步骤2.5条件1代码化，00:09 事故固化）：
    # 上游各通道含保险/证券/基金等非银信机构公告，送审前先按 config.company_board_scope 剔除，
    # 剔除数计入 channels 摘要便于每日核对；宽口径需求走周报通道。
    sys.path.insert(0, REPO)
    from config import company_board_scope
    in_scope, scope_out = [], []
    for it in fresh:
        v, why = company_board_scope(it.get('title', ''))
        (in_scope if v != 'block' else scope_out).append(it)
    summary["_scope_gate"] = {"status": "ok", "kept": len(in_scope),
                              "blocked": len(scope_out)}
    fresh = in_scope

    out_path = os.path.join(MON, f'sweep_shortlist_{run_at}.json')
    json.dump({"run_at": run_at, "window": window, "channels": summary,
               "merged": len(merged), "pre_dedup": len(uniq), "fresh": len(fresh),
               "items": fresh}, open(out_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    brief = {k: (v.get('status'), v.get('kept')) for k, v in summary.items()}
    print(json.dumps({"sweep": brief, "merged": len(merged), "fresh": len(fresh),
                      "shortlist": os.path.basename(out_path)}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    sys.exit(main())
