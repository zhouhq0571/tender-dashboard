#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""国投集团电子采购平台采集脚本（L1 直连层，2026-11-19 上线，L1 第 3 家）

零模型 token：urllib 直 POST 四个公开列表接口，按采购单位=国投泰康信托筛选：
  /cgxx/ggList        招标公告    → /cgxx/ggDetail?gcGuid=G&ggGuid=G
  /cgxx/preNoticeList 事前公示    → /cgxx/preNoticeDetail?guid=G&fromType=T
  /cgxx/zbhxrList     中标候选人  → /cgxx/zbhxrDetail?bdGuid=B&guid=G
  /cgxx/zbjgList      结果公告    → /cgxx/zbjgDetail?bdGuid=B&guid=G
（cgxxList 非招标公告栏目=登录墙，取不到；其事前公示先行覆盖，信号不丢）

预筛：TITLE_EXCLUDE 排除 + BIZ_INCLUDE 正向（复用 ql_subscribe_fetch 词表，
口径与订阅邮件管线一致）；近 15 天回看窗口。
输出：monitor/new_items_sdicc_YYYYMMDD_HHMM.json（schema 与 lecaiyun_fetch 一致：
new_items[]={title,pubdate,deadline,url,source,channel}，sources[]={name,mode,
status,total_items,new_count}），供 sweep_candidates 汇总走既有候选/上板管线。

L1 失效纪律：连续抓取失败 3 天须在汇报中报失效（降级/维修）。
"""
import json
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ql_subscribe_fetch import TITLE_EXCLUDE, BIZ_INCLUDE  # 复用订阅管线词表

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "monitor"

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

BUYER = '国投泰康信托'
LOOKBACK_DAYS = 15
MAX_PAGES = 3  # 每页 10 条；该平台该买方月产 1~3 条，3 页=30 条≈覆盖一年以上

ENDPOINTS = [
    {"key": "zbgg", "name": "国投平台-招标公告", "path": "/cgxx/ggList",
     "channel": "招标公告",
     "detail": lambda a, b: f"https://www.sdicc.com.cn/cgxx/ggDetail?gcGuid={b}&ggGuid={a}"},
    {"key": "sqgs", "name": "国投平台-事前公示", "path": "/cgxx/preNoticeList",
     "channel": "事前公示",
     "detail": lambda a, b: f"https://www.sdicc.com.cn/cgxx/preNoticeDetail?guid={a}&fromType={b}"},
    {"key": "hxr", "name": "国投平台-中标候选人", "path": "/cgxx/zbhxrList",
     "channel": "候选人公示",
     "detail": lambda a, b: f"https://www.sdicc.com.cn/cgxx/zbhxrDetail?bdGuid={a}&guid={b}"},
    {"key": "zbjg", "name": "国投平台-结果公告", "path": "/cgxx/zbjgList",
     "channel": "结果公告",
     "detail": lambda a, b: f"https://www.sdicc.com.cn/cgxx/zbjgDetail?bdGuid={a}&guid={b}"},
]

ROW_RE = re.compile(
    r"urlChange\('([0-9a-fA-F-]+)','([^']*)'\).*?"
    r"<td colspan=\"1\" rowspan=\"1\"><span[^>]*>([^<]{4,120})</span></td>.*?"
    r"(20\d{2}-\d{2}-\d{2})",
    re.S)
DATE_RE = re.compile(r"20\d{2}-\d{2}-\d{2}")


def prescreen(title):
    t = title.strip()
    if any(k in t for k in TITLE_EXCLUDE):
        return False
    return any(k in t for k in BIZ_INCLUDE)


def fetch_list(path, page_no):
    data = urllib.parse.urlencode(
        {"caiGouDanWei": BUYER, "currentPage": str(page_no)}).encode()
    req = urllib.request.Request(
        "https://www.sdicc.com.cn" + path, data=data,
        headers={"User-Agent": UA,
                 "Content-Type": "application/x-www-form-urlencoded"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.read().decode("utf-8", "ignore")


def parse_rows(html, ep):
    rows = []
    # 以 <tr onclick="urlChange(...)" 切分行，避免跨行误配
    for chunk in re.split(r"<tr onclick=\"urlChange\('",
                          html)[1:]:
        m_args = re.match(r"([0-9a-fA-F-]+)','([^']*)'\)", chunk)
        if not m_args:
            continue
        a, b = m_args.group(1), m_args.group(2)
        spans = re.findall(r"<span[^>]*>\s*([^<]{4,150}?)\s*</span>", chunk)
        if not spans:
            continue
        title = spans[0].strip()
        dm = DATE_RE.search(chunk)
        pub = dm.group(0) if dm else ""
        rows.append({"title": title, "pubdate": pub,
                     "url": ep["detail"](a, b), "channel": ep["channel"]})
    return rows


def main():
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_sdicc_{run_at}.json"
    result = {"run_at": run_at, "sources": [], "new_items": []}
    cutoff = (datetime.now() - timedelta(days=LOOKBACK_DAYS)).strftime('%Y-%m-%d')
    for ep in ENDPOINTS:
        status, total, kept = "ok", 0, []
        try:
            for pn in range(1, MAX_PAGES + 1):
                html = fetch_list(ep["path"], pn)
                rows = parse_rows(html, ep)
                total += len(rows)
                if not rows:
                    break
                last_date = rows[-1]["pubdate"]
                for r in rows:
                    if r["pubdate"] and r["pubdate"] < cutoff:
                        continue
                    if prescreen(r["title"]):
                        kept.append({**r, "deadline": "",
                                     "source": "国投集团电子采购平台"})
                # 列表按日期倒序：本页最旧已出窗即停翻
                if last_date and last_date < cutoff:
                    break
                time.sleep(1)
        except Exception as e:
            status = f"error: {str(e)[:80]}"
        result["sources"].append({"name": ep["name"], "mode": "fetch",
                                  "status": status, "total_items": total,
                                  "new_count": len(kept)})
        result["new_items"].extend(kept)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                        encoding='utf-8')
    print(f"saved {out_path}")
    for s in result["sources"]:
        print(f"  {s['name']}: {s['status']} 共{s['total_items']}条 keep{s['new_count']}")
    for it in result["new_items"]:
        print(f" KEEP: {it['pubdate']} [{it['channel']}] {it['title'][:55]}")
    return result


if __name__ == "__main__":
    main()
