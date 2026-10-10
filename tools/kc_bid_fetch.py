#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""快查开放平台 L0 采集脚本（2026-10-10 上线，官方 API 对接）

数据源：快查"招标中标公告筛选查询"（operation_get_yuqing_bidding_search_plus）
鉴权：open-authorization: Bearer <KUAICHA_API_KEY>（Key 存 .kc_apikey，600 权限，已 gitignore）
口径：type=招标、近3天（周一近4天由调用方控制 window_days 参数）、报名未截止、
     机构正向词（银行/信托/理财等）+ IT 业务正向词 + 复用 ql_subscribe_fetch 排除词表
输出：monitor/new_items_kc_YYYYMMDD_HHMM.json（与监控器同 schema，走 dedup_filter 同一流程）
额度纪律：每日查询组数 ≤6 组（每组 1 次 API 调用），额度异常时降组并写入汇报。
"""
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ql_subscribe_fetch import TITLE_EXCLUDE

BASE = Path(__file__).resolve().parent.parent
KEY_FILE = BASE / ".kc_apikey"
OUT_DIR = BASE / "monitor"
GATEWAY = "https://bizveris.kuaicha365.com"
TOOL_ID = "operation_get_yuqing_bidding_search_plus"

ORG_POS = re.compile(
    r"银行|信托|理财|农商|农信|农商行|信用社|邮储|工行|农行|中行|建行|交行|"
    r"招商|中信|光大|华夏|民生|兴业|浦发|广发|平安|浙商|渤海|恒丰|北京银行|"
    r"上海银行|南京银行|宁波银行|江苏银行|杭州银行|中原|齐鲁|河北|徽商|长沙|"
    r"成都|重庆银行|贵阳|云南|甘肃|青海|宁夏|新疆|内蒙古|吉林|黑龙江|辽宁|"
    r"大连|青岛|厦门|苏州|无锡|台州|温州|嘉兴|湖州|绍兴|金华|潍坊|威海|"
    r"日照|临沂|德州|烟台|济宁|泰安|枣庄|东营|滨州|聊城|菏泽")
IT_POS = re.compile(
    r"数据|数据库|系统|平台|软件|智能|大模型|AI|信创|开发|测试|外包|云|"
    r"中台|监管|报送|风控|估值|TA|直销|渠道|营销|投顾|托管|财富|资管|理财|"
    r"支付|接口|运维|安全|科技")
STAGE_DROP = re.compile(r"结果公示|结果公告|中标|成交公告|废标|流标|终止|更正|变更|候选人|合同公告")

# 每日查询组（title 关键词 × 机构词由预筛承担，控制 API 调用次数）
QUERY_GROUPS = [
    {"title": "数据", "tender_names": "银行"},
    {"title": "大模型", "tender_names": "银行"},
    {"title": "信创", "tender_names": "银行"},
]
# 2026-10-10 晚额度止血：账户 MCP 与 Skill 池仅剩 137 次，6组→3组（月耗约66次）。
# 迁移标准 API（独立额度）后恢复 6 组。


def api_call(payload):
    key = KEY_FILE.read_text().strip()
    req = urllib.request.Request(
        f"{GATEWAY}/api_route/gateway/{TOOL_ID}",
        data=json.dumps(payload).encode(),
        headers={
            "Content-Type": "application/json",
            "open-authorization": f"Bearer {key}",
        },
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def prescreen(title, buyer):
    if STAGE_DROP.search(title):
        return False
    if not ORG_POS.search(buyer or ''):
        return False
    if not IT_POS.search(title):
        return False
    for kw in TITLE_EXCLUDE:
        if kw in title:
            return False
    return True


def main(window_days=3):
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_kc_{run_at}.json"
    now = int(time.time())
    start = now - window_days * 86400
    result = {"run_at": run_at, "sources": [], "new_items": []}
    seen = set()
    for g in QUERY_GROUPS:
        payload = {
            "type": "招标",
            "pub_time": start,
            "pub_time_1": now,
            "registration_deadline_time": now,
            "page": 1,
            "page_size": 50,
            "orders": "pub_time desc",
        }
        payload.update({k: v for k, v in g.items() if v})
        name = f"快查-{g.get('title','')}×{g.get('tender_names','')}"
        status, total, kept = "ok", 0, 0
        try:
            r = api_call(payload)
            items = (r.get('data') or {}).get('list') or r.get('list') or []
            if isinstance(items, dict):
                items = items.get('list') or []
            total = len(items)
            em = re.compile(r'<[^>]+>')
            for it in items:
                title = em.sub('', str(it.get('title') or it.get('notice_title') or ''))
                hl = it.get('highlight') or {}
                buyer = ''
                if isinstance(hl.get('tender_names'), list) and hl['tender_names']:
                    buyer = em.sub('', str(hl['tender_names'][0]))
                if not buyer:
                    buyer = str(it.get('tender_names') or it.get('tender_name') or '')
                if not title or title in seen:
                    continue
                if not prescreen(title, buyer):
                    continue
                seen.add(title)
                kept += 1
                result["new_items"].append({
                    "title": f"{title}（{buyer}）" if buyer and buyer not in title else title,
                    "date": datetime.fromtimestamp(
                        it.get('pub_time') or it.get('index_time') or now
                    ).strftime('%Y-%m-%d'),
                    "deadline": datetime.fromtimestamp(it.get('registration_deadline_time') or now).strftime('%Y-%m-%d') if it.get('registration_deadline_time') else "",
                    "url": it.get('url') or it.get('notice_url') or
                           f"https://www.kuaicha365.com/",
                    "source": "快查",
                })
        except Exception as e:
            status = f"error: {str(e)[:80]}"
        result["sources"].append({"name": name, "mode": "api",
                                  "status": status, "total_items": total,
                                  "new_count": kept})
        time.sleep(1)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"saved {out_path}")
    for s in result["sources"]:
        print(f"  {s['name']}: {s['status']} 命中{s['total_items']} keep{s['new_count']}")
    for it in result["new_items"][:15]:
        print(" KEEP:", it['title'][:60], '|', it['deadline'])


if __name__ == '__main__':
    wd = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    main(wd)
