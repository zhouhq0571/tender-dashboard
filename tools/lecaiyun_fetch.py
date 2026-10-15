#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""乐采云平台采集脚本（L1 直连层，2026-10-15 上线，L1 第 2 家）

零模型 token：Playwright 过阿里云 WAF（acw_sc__v2）→ 页内 fetch 公告大厅
/announcement/lobby/queryPage（项目采购全量在招公告，含全文）→ 代码预筛
（金融机构 + 业务正向词 + 阶段/后勤噪声）→ 正文抽取投标截止 →
输出 monitor/new_items_lecaiyun_YYYYMMDD_HHMM.json（schema 与 ccb_ibuy_fetch 一致）。

背景：湖州银行 AI 大模型平台、数智化平台两标均经此平台交易；浙江区域
城商行/农商（湖州银行、温州银行、泰隆、稠州、杭州银行等）政采类标高频入口。

L1 失效纪律：连续抓取失败 3 天须在汇报中报失效（降级/维修）。
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ql_subscribe_fetch import TITLE_EXCLUDE  # 复用预筛排除词表

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "monitor"

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

# 项目采购-在招类公告（ lobbying 页首屏 tab1 的 types，公示/结果类不在此列）
TENDER_TYPES = ["3012", "3020", "2002", "3003", "3011", "3002", "3001",
                "3008", "2001", "10007", "10002", "10012", "20010",
                "200012", "200003", "200026", "200025", "200004", "200002",
                "200005", "200022", "200001", "200006", "200023", "200000",
                "20010", "20012", "20009"]
PAGES = 3          # 每天 3 页 ≈ 297 条，覆盖近 2-3 天新发
LOOKBACK_DAYS = 4  # 只保留近 N 天 releasedAt 的条目

# 金融机构（招标主体或项目对象须在范围内）
FINANCE = re.compile(
    r'银行|信托|理财|农商|信用社|金融|资产管理|证券|基金|消费金融|金融租赁|AIC')
# 业务正向词：IT/业务相关才保留
POSITIVE = re.compile(
    r'数据|系统|平台|软件|智能|大模型|AI|财富|理财|资管|信创|外包|开发|测试|云|'
    r'数据库|监管|报送|风控|营销|客户|渠道|APP|中台|数字|科技|运维|人力|投顾|'
    r'养老金|托管|估值|TA|直销|钱包|支付|接口|资讯|数字人民币|数币')
# 乐采云特有噪声（平台为全行业采购，后勤/工程/物资占比极高）
LCY_NOISE = re.compile(
    r'体检|物业|餐饮|年金|开户银行|资金专户|存款账户|恒温恒湿|金库|守押|押运|'
    r'清分|宣传|广告|装修|租赁|绿化|车辆|充电桩|停车|搬迁|食材|苗木|'
    r'电梯|空调|办公用品|家具|印刷|监控设备|门禁|档案|洗衣|票务|'
    r'医疗|医院|学院|学校|课时|教材|实训|病房|器械|药品')
# 阶段词：已过阶段直接丢
STAGE_DROP = re.compile(
    r'结果公示|结果公告|中标|成交公告|废标|流标|终止|更正公告|变更公告|候选人公示|'
    r'合同公告|验收|预公示')

DETAIL = 'https://sourcing-lcy.lecaiyun.com/luban/announcement/detail?encryptId='

FETCH_JS = """async ({types, pages}) => {
  const out = [];
  for (let pn = 1; pn <= pages; pn++) {
    const r = await fetch('/announcement/lobby/queryPage', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({district: null, districtCodeFProvince: '900099',
        announcementTypes: types, pageNo: pn, pageSize: 99})
    });
    const j = await r.json();
    const data = (j && j.result && j.result.data) || [];
    out.push(...data);
    if (data.length < 99) break;
  }
  return out;
}"""


def strip_html(s):
    return re.sub(r'<[^>]+>', '', s or '')


def extract_deadline(text):
    """从公告正文抽取投标/响应截止日（YYYY-MM-DD），取第一个匹配。"""
    pats = [
        (r'(?:投标|响应|报价|申请文件)[^\n。；]{0,12}?截止[^\n。；]{0,20}?'
         r'(\d{4})年(\d{1,2})月(\d{1,2})日', 3),
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日[^\n。；]{0,15}?(?:开标|截止)', 3),
        (r'(?:投标|响应|报价)[^\n。；]{0,10}?截止[^0-9]{0,10}(\d{4})-(\d{1,2})-(\d{1,2})', 3),
    ]
    for p, ngroups in pats:
        m = re.search(p, text)
        if m:
            if ngroups == 3:
                y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
                return f'{y}-{mo:02d}-{d:02d}'
    return ''


def prescreen(title):
    if STAGE_DROP.search(title):
        return False
    if LCY_NOISE.search(title):
        return False
    if not FINANCE.search(title):
        return False
    if not POSITIVE.search(title):
        return False
    for kw in TITLE_EXCLUDE:
        if kw in title:
            return False
    return True


def main():
    from playwright.sync_api import sync_playwright
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_lecaiyun_{run_at}.json"
    result = {"run_at": run_at, "sources": [], "new_items": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(user_agent=UA).new_page()
        status, total, kept = "ok", 0, []
        try:
            page.goto('https://sourcing-lcy.lecaiyun.com/luban/xmcg',
                      timeout=60000)
            page.wait_for_timeout(8000)  # 过 WAF +  Lobby 首屏加载
            items = page.evaluate(FETCH_JS, {"types": TENDER_TYPES,
                                             "pages": PAGES})
            total = len(items)
            cutoff = datetime.now().timestamp() - LOOKBACK_DAYS * 86400
            for it in items:
                ts = it.get('releasedAt') or it.get('createdAt') or 0
                if isinstance(ts, str):
                    try:
                        ts = datetime.fromisoformat(
                            ts.replace('Z', '+00:00')).timestamp()
                    except ValueError:
                        ts = 0
                if ts and ts < cutoff:
                    continue
                title = (it.get('title') or '').strip()
                if not prescreen(title):
                    continue
                text = strip_html(it.get('content', ''))
                kept.append({
                    'title': title,
                    'pubdate': datetime.fromtimestamp(
                        ts / 1000 if ts > 1e12 else ts).strftime('%Y-%m-%d')
                    if ts else '',
                    'deadline': extract_deadline(text),
                    'url': DETAIL + it.get('encryptId', ''),
                    'source': '乐采云平台',
                    'channel': it.get('announcementTypeName') or '',
                })
            for k in kept:
                result["new_items"].append(k)
        except Exception as e:
            status = f"error: {str(e)[:80]}"
        result["sources"].append({"name": "乐采云-项目采购公告",
                                  "mode": "fetch", "status": status,
                                  "total_items": total,
                                  "new_count": len(kept)})
        browser.close()
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                        encoding='utf-8')
    print(f"saved {out_path}")
    for s in result["sources"]:
        print(f"  {s['name']}: {s['status']} 共{s['total_items']}条 "
              f"keep{s['new_count']}")
    for it in result["new_items"]:
        print(" KEEP:", it['title'][:60], '| 截止', it.get('deadline', ''),
              '|', it.get('pubdate', ''))


if __name__ == '__main__':
    main()
