#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""建设银行龙集采平台采集脚本（L1 直连层，2026-10-10 上线）

零模型 token：Playwright 渲染 hash 路由 → 栏目列表抽取 → 代码关键词预筛 →
输出 monitor/new_items_ccb_YYYYMMDD_HHMM.json（schema 与 source_monitor 输出一致，
后续走 dedup_filter 去重，与千里马订阅候选同一流程）。

栏目：供应商征集(#/ccbgyszj) / 招标专区(#/ccbbidzbzq) / 采购动态(#/ccbpurcgdt)
L1 失效纪律：连续抓取失败 3 天须在汇报中报失效（降级/维修）。
"""
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ql_subscribe_fetch import TITLE_EXCLUDE  # 复用预筛排除词表

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "monitor"

CHANNELS = [
    ("供应商征集", "#/ccbgyszj", "360"),
    ("招标专区", "#/ccbbidzbzq", None),
    ("采购动态", "#/ccbpurcgdt", None),
]

# 阶段词：已过阶段直接丢（在招的征集/招标/磋商/谈判/询价保留）
STAGE_DROP = re.compile(
    r"结果公示|结果公告|中标|成交公告|废标|流标|终止|更正公告|变更公告|候选人公示|"

    r"合同公告|验收")
# 正向词：IT/业务相关才保留
POSITIVE = re.compile(
    r"数据|系统|平台|软件|智能|大模型|AI|财富|理财|资管|信创|外包|开发|测试|云|"
    r"数据库|监管|报送|风控|营销|客户|渠道|APP|中台|数字|科技|运维|人力|投顾|"
    r"养老金|托管|估值|TA|直销|直销银行|钱包|支付|接口|数据服务|资讯")
# 建行特有噪声：银医合作、现金押运清分等后勤外包（正向词"外包/系统"会误放）
CCB_NOISE = re.compile(
    r"医院|医疗|医技|病案|守押|押运|清分|整点|体检|敬老|观影|广告|宣传|"
    r"房屋租赁|迁址|装修|消防改造|外墙|搬迁|食材|物业|绿化")

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

EXTRACT_JS = """(channel) => {
  const out = [];
  const lis = document.querySelectorAll('li');
  for (const li of lis) {
    const a = li.querySelector('a');
    if (!a) continue;
    const t = (li.innerText || '').replace(/\\s+/g, ' ').trim();
    if (!t || t.length < 15) continue;
    const mDl = t.match(/截止时间：(\\d{4}-\\d{2}-\\d{2})/);
    const mDate = t.match(/(\\d{4}-\\d{2}-\\d{2})/);
    let title = t.split(/ \\d{4}-\\d{2}-\\d{2}/)[0].replace(/^\\d+\\s*/, '').trim();
    out.push({title, pubdate: mDate ? mDate[1] : '', deadline: mDl ? mDl[1] : '', channel});
  }
  return out.slice(0, 15);
}"""


def prescreen(title):
    if STAGE_DROP.search(title):
        return False
    if CCB_NOISE.search(title):
        return False
    for kw in TITLE_EXCLUDE:
        if kw in title:
            return False
    return bool(POSITIVE.search(title))


def resolve_url(page, index):
    """点击第 index 条列表项，从路由读出详情 id，返回后还原列表。"""
    try:
        cur = page.url
        page.evaluate(f"""() => {{
          const lis = [...document.querySelectorAll('li')].filter(
            li => li.querySelector('a') && (li.innerText||'').trim().length > 15);
          if (lis[{index}]) lis[{index}].querySelector('a').click();
        }}""")
        time.sleep(3)
        u = page.url
        page.goto(cur, timeout=60000)
        time.sleep(4)
        if 'id=' in u:
            return u
    except Exception:
        pass
    return None


def main():
    from playwright.sync_api import sync_playwright
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_ccb_{run_at}.json"
    result = {"run_at": run_at, "sources": [], "new_items": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(user_agent=UA).new_page()
        for name, route, pId in CHANNELS:
            status, total, kept = "ok", 0, []
            try:
                page.goto(f'https://ibuy.ccb.com/cms/index.html{route}', timeout=60000)
                time.sleep(8)
                items = page.evaluate(EXTRACT_JS, name)
                total = len(items)
                for idx, it in enumerate(items):
                    if not prescreen(it['title']):
                        continue
                    kept.append((idx, it))
                # 只为 keep 项解析详情 URL（点击法，最多 5 条）
                for n, (idx, it) in enumerate(kept[:5]):
                    it['url'] = resolve_url(page, idx) or (
                        f'https://ibuy.ccb.com/cms/index.html{route}')
                    it['source'] = '建设银行集采平台'
                    it['date'] = it.pop('pubdate', '') or it.get('deadline', '')
                    it['channel'] = name
                    result["new_items"].append(it)
                    time.sleep(1)
            except Exception as e:
                status = f"error: {str(e)[:80]}"
            result["sources"].append({"name": f"龙集采-{name}", "mode": "fetch",
                                      "status": status, "total_items": total,
                                      "new_count": len(kept)})
        browser.close()
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f"saved {out_path}")
    for s in result["sources"]:
        print(f"  {s['name']}: {s['status']} 共{s['total_items']}条 keep{s['new_count']}")
    for it in result["new_items"]:
        print(" KEEP:", it['title'][:55], '| 截止', it.get('deadline', ''))


if __name__ == '__main__':
    main()
