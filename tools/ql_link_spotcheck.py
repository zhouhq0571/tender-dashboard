# -*- coding: utf-8 -*-
"""
千里马链接月度随机抽检（10%抽样、慢速、只读，严禁修改看板数据）
用法:
  python3 tools/ql_link_spotcheck.py            # 正常执行（playwright 慢速抓取）
  python3 tools/ql_link_spotcheck.py --dry-run  # 只输出抽样清单，不抓取
抽样: 以复盘月份(YYYYMM)为随机种子，从看板千里马来源项目中抽取 ceil(10%) 条
输出: reports/链接抽检-YYYYMM.md（错配清单 + 无法判定 + 正常三类）
规则: 仅当 fetch 成功且页面标题/正文中【招标单位】与【项目名关键词】均不出现 → 链接错配；
      fetch 失败/超时/419/403/验证码 → 无法判定（不算异常）。
"""
import sys, os, json, re, time, random, datetime
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/tools')

BASE = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily'
INDEX = os.path.join(BASE, 'index.html')
SAMPLE_RATE = 0.10

def load_ql_items():
    html = open(INDEX, encoding='utf-8').read()
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
    data = json.loads(m.group(1))
    items = data if isinstance(data, list) else (data.get('projects') or data.get('items'))
    out = []
    for x in items:
        blob = json.dumps(x, ensure_ascii=False)
        if 'qianlima.com' in blob or '千里马' in blob:
            out.append({'id': x.get('id'), 'company': x.get('company', ''),
                        'project': x.get('project', ''), 'url': x.get('url', '')})
    return out

def sample_items(items, ym):
    k = max(1, -(-len(items) * SAMPLE_RATE // 1))  # ceil(10%)
    k = int(-(-len(items) * SAMPLE_RATE // 1))
    rng = random.Random(ym)
    return rng.sample(items, k)

def main():
    dry = '--dry-run' in sys.argv
    now = datetime.datetime.now()
    ym = now.strftime('%Y%m')
    items = load_ql_items()
    picks = sample_items(items, ym)
    print(f'千里马来源项目 {len(items)} 条，按 10% 抽检 {len(picks)} 条（种子 {ym}）')
    if dry:
        for p in picks:
            print(' ', p['id'], p['company'], p['project'][:30], p['url'])
        return

    from playwright.sync_api import sync_playwright
    from ql_vip_fetch import login
    from ql_link_audit import fetch_page, aliases_for, keywords_for

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
        ).new_page()
        login(page)
        for it in picks:
            r = fetch_page(page, it['url'])
            rec = dict(it)
            if r['status'] != 'ok':
                rec['verdict'] = '无法判定'
                rec['reason'] = r.get('reason', '')[:100]
            else:
                text = r['title'] + '\n' + r['text']
                comp_hit = any(a in text for a in aliases_for(it['company']))
                kw_hit = any(k in text for k in keywords_for(it['project']))
                rec['page_title'] = r['title'][:80]
                rec['verdict'] = '链接错配' if (not comp_hit and not kw_hit) else '正常'
            results.append(rec)
            print(json.dumps({'id': rec['id'], 'verdict': rec['verdict']}, ensure_ascii=False))
            time.sleep(3)
        browser.close()

    bad = [r for r in results if r['verdict'] == '链接错配']
    unk = [r for r in results if r['verdict'] == '无法判定']
    ok = [r for r in results if r['verdict'] == '正常']
    lines = [f'# 千里马链接抽检报告（{ym}）',
             f'抽样口径：看板千里马来源 {len(items)} 条，随机抽检 10% 共 {len(results)} 条（种子 {ym}）',
             f'结果：正常 {len(ok)} / 链接错配 {len(bad)} / 无法判定 {len(unk)}（反爬、验证码、超时计入无法判定，不算异常）', '']
    if bad:
        lines.append('## 链接错配清单（只上报，未改动任何数据）')
        for r in bad:
            lines.append(f"- id={r['id']} {r['company']}｜{r['project']}\n  看板URL: {r['url']}\n  页面实际标题: {r.get('page_title','')}")
        lines.append('')
    if unk:
        lines.append('## 无法判定')
        for r in unk:
            lines.append(f"- id={r['id']} {r['company']}｜{r['project'][:30]}｜{r.get('reason','')}")
    os.makedirs(os.path.join(BASE, 'reports'), exist_ok=True)
    out = os.path.join(BASE, 'reports', f'链接抽检-{ym}.md')
    open(out, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
    print('REPORT=' + out)
    print(f'SUMMARY 正常{len(ok)} 错配{len(bad)} 无法判定{len(unk)}')

if __name__ == '__main__':
    main()
