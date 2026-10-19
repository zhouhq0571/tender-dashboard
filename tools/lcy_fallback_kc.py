#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""乐采云 WAF 兜底通道（2026-10-19 上线，用户批准）

背景：乐采云 2026-10-17/18 升级阿里云 WAF v2.0.1，lecaiyun_fetch.py 无头采集被拦
（实测持续拦截，挑战脚本需真实浏览器环境，短期内不可解）。乐采云是浙江政采电子
交易平台，标的多为浙江区域金融机构（浙江农信系统/泰隆/民泰/稠州及各城商行）。
其公告快查均有收录，故用快查标准 API 定向补漏。

策略（每日 ≤3 次 API 调用）：
  A. tender_names="浙江"（命中浙江稠州/泰隆/民泰/浙江农信及各"浙江"冠名银行），
     15 天回看窗口（与 lecaiyun_fetch 的 LOOKBACK_DAYS=15 对齐）
  B. 浙江无"浙江"冠名的城商行 8 家轮转（每日 1 家，8 天一轮；15 天窗口保证不漏）
  仅当最近一次 lecaiyun 采集为 waf_blocked/error 时才执行（自给自足判断，不依赖人工）；
  若乐采云恢复则输出 skipped，不消耗额度。

口径：type=招标、报名未截止；预筛词表复用 kc_bid_fetch（ORGK+IT+排除词+阶段词）。
输出：monitor/new_items_lcykc_*.json（source=快查，channel=乐采云兜底，走同一 dedup 管线）。
"""
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from kc_bid_fetch import api_call, prescreen, ORG_POS, IT_POS  # noqa: E402

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "monitor"
LOOKBACK_DAYS = 15
MAX_PAGES = 3          # 单查询最多翻页数（API 调用上限 = A×页数 + B×页数）
WINDOW = LOOKBACK_DAYS * 86400

# 浙江无"浙江"冠名的城商行（其余浙江系银行由关键词"浙江"覆盖）
ZJ_CITY_BANKS = ["湖州银行", "杭州银行", "宁波银行", "温州银行",
                 "嘉兴银行", "绍兴银行", "金华银行", "台州银行"]

EM = re.compile(r'<[^>]+>')
# 机构"类型"词（区别于 kc ORG_POS 里的省份词——"新疆"等省份词会把援疆/政企项目放进来）
FIN_TYPE = re.compile(
    r'银行|信托|理财子|理财|农商|信用社|证券|基金|消费金融|金融租赁|资产管理公司|'
    r'AIC|金融资产管理|村镇银行')


def latest_lecaiyun_status():
    files = sorted(OUT_DIR.glob("new_items_lecaiyun_*.json"))
    if not files:
        return "no_run"
    try:
        d = json.loads(files[-1].read_text())
        return (d.get("sources") or [{}])[0].get("status", "unknown")
    except Exception:
        return "unknown"


def search(tender_names, start, now):
    """单机构关键词查询，按发布时间倒序翻页至窗口外/页数上限。返回 items 列表。"""
    items = []
    for page in range(1, MAX_PAGES + 1):
        payload = {"type": "招标", "pub_time": start, "pub_time_1": now,
                   "registration_deadline_time": now,
                   "page": page, "page_size": 50, "orders": "pub_time desc",
                   "tender_names": tender_names}
        r = api_call(payload)
        batch = (r.get('data') or {}).get('list') or r.get('list') or []
        items.extend(batch)
        if len(batch) < 50:
            break
        last_ts = batch[-1].get('pub_time') or 0
        if last_ts and last_ts < start:
            break
        time.sleep(0.5)
    return items


def norm_buyer(it):
    hl = it.get('highlight') or {}
    b = hl.get('tender_names')
    if isinstance(b, list) and b:
        return EM.sub('', str(b[0]))
    return EM.sub('', str(it.get('tender_names') or ''))


def main():
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_lcykc_{run_at}.json"
    result = {"run_at": run_at, "sources": [], "new_items": []}

    st = latest_lecaiyun_status()
    if st not in ("waf_blocked",) and not str(st).startswith("error"):
        result["sources"].append(
            {"name": "乐采云兜底-快查", "mode": "api",
             "status": f"skipped: lecaiyun={st}", "total_items": 0,
             "new_count": 0})
        out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                            encoding='utf-8')
        print(f"saved {out_path}\n  skipped（乐采云状态 {st}，未消耗快查额度）")
        return

    now = int(time.time())
    start = now - WINDOW
    day_index = datetime.now().timetuple().tm_yday
    rotation = ZJ_CITY_BANKS[day_index % len(ZJ_CITY_BANKS)]
    queries = [("浙江", "A-浙江冠名机构"), (rotation, f"B-轮转城商行:{rotation}")]

    total, kept = 0, []
    seen_titles = set()
    for tn, label in queries:
        status, n_kept = "ok", 0
        try:
            items = search(tn, start, now)
            total += len(items)
            for it in items:
                title = EM.sub('', str(it.get('title') or '')).strip()
                buyer = norm_buyer(it)
                # 兜底通道加码硬闸：招标主体必须在金融机构词表内
                # （"浙江"模糊匹配会带进援疆/政采等非金融主体，kc 预筛拦不住）
                if not title or title in seen_titles:
                    continue
                if not (FIN_TYPE.search(buyer) or FIN_TYPE.search(title)):
                    continue
                if not prescreen(title, buyer):
                    continue
                seen_titles.add(title)
                ts = it.get('registration_deadline_time') or 0
                kept.append({
                    "title": title if buyer in title else f"{title}（{buyer}）",
                    "date": datetime.fromtimestamp(
                        it.get('pub_time') or now).strftime('%Y-%m-%d'),
                    "deadline": datetime.fromtimestamp(ts).strftime(
                        '%Y-%m-%d') if ts else "",
                    "url": it.get('url') or it.get('notice_url') or
                           "https://www.kuaicha365.com/",
                    "source": "快查",
                    "channel": f"乐采云兜底-{label}",
                })
                n_kept += 1
        except Exception as e:
            status = f"error: {str(e)[:80]}"
        result["sources"].append({"name": f"乐采云兜底-{label}",
                                  "mode": "api", "status": status,
                                  "total_items": len(items) if 'items' in dir() else 0,
                                  "new_count": n_kept})
        time.sleep(0.5)

    result["new_items"] = kept
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                        encoding='utf-8')
    print(f"saved {out_path}")
    for s in result["sources"]:
        print(f"  {s['name']}: {s['status']} 共{s['total_items']}条 "
              f"keep{s['new_count']}")
    for it in kept:
        print(" KEEP:", it['title'][:60], '| 截止', it.get('deadline', ''),
              '|', it.get('date', ''))


if __name__ == '__main__':
    main()
