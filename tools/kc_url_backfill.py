# -*- coding: utf-8 -*-
"""
快查来源条目 URL 修复（2026-10-30）：按项目名搜千里马 VIP 取 bid 链接
==================================================================
背景：快查 API 无详情页 URL（网页版招投标详情未公开），看板 9 条快查/建行集采
来源条目 url 落成了首页占位（https://www.kuaicha365.com/），导致 validate URL 重复
告警、链接不可点。本脚本零模型：项目名去噪 → 千里马 VIP 搜索 → 同项目命中取
bid 链接 → 顺手 fetch 详情页用 extract_contact 补 contact → 结构化回写 index.html。

用法：python3 tools/kc_url_backfill.py
"""
import json, re, sys, time, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ql_vip_fetch import login, extract_contact
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
KC_HOME = ('https://www.kuaicha365.com/', 'https://www.kuaicha365.com')

def is_placeholder(u):
    return str(u or '').strip().rstrip('/') in ('https://www.kuaicha365.com', 'http://www.kuaicha365.com')

def load_board():
    html = open(HTML, encoding='utf-8').read()
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
    return html, json.loads(m.group(1))

def save_board(html, data):
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    out = re.sub(r'(<script type="application/json" id="tender-data">).*?(</script>)',
                 lambda m: m.group(1) + new_json + m.group(2), html, count=1, flags=re.DOTALL)
    open(HTML, 'w', encoding='utf-8').write(out)

def keyword(project):
    """项目名去噪：去年份/书名号/尾缀，取前16字作搜索词"""
    s = re.sub(r'^[\[【][^\]】]*[\]】]', '', project)
    s = re.sub(r'20\d{2}[-—年至]', '', s)
    s = re.sub(r'(项目|采购|招标|供应商征集|征集调研|入围|服务)$', '', s.strip())
    return s.strip()[:16]

def search(page, kw):
    from urllib.parse import quote
    url = f'https://search.qianlima.com/?q={quote(kw)}'
    try:
        page.goto(url, timeout=60000)
        time.sleep(5)
        txt = page.inner_text('body')
        if 'Verification Required' in txt:
            time.sleep(25)
            page.goto(url, timeout=60000)
            time.sleep(5)
        return page.evaluate("""(()=>{
          const out=[];
          document.querySelectorAll('a[href*="bid-"]').forEach(a=>{
            const t=(a.innerText||a.textContent||'').trim().replace(/\\s+/g,' ');
            if(t.length>8) out.push({title:t.slice(0,90), url:a.href.split('?')[0]});
          });
          return out.slice(0,10);
        })""")
    except Exception:
        return []

def main():
    html, data = load_board()
    targets = [p for p in data['projects'] if is_placeholder(p.get('url'))]
    print(f'占位URL条目 {len(targets)} 条')
    if not targets:
        return
    with sync_playwright() as pw:
        b = pw.chromium.launch(headless=True)
        page = b.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
        ).new_page()
        login(page)
        for p in targets:
            kw = keyword(p['project'])
            hits = search(page, kw)
            # 命中判定：标题与项目名前8字重合
            core = re.sub(r'\W+', '', p['project'])[:8]
            hit = next((h for h in hits if core and core in re.sub(r'\W+', '', h['title'])), None)
            if not hit:
                print(f"⚠️ id={p['id']} [{p['company'][:10]}] 关键词「{kw}」未命中，保留占位")
                time.sleep(3)
                continue
            p['url'] = hit['url']
            note = f"url←千里马搜索（原快查占位）"
            # 顺手 fetch 详情补 contact
            try:
                page.goto(hit['url'], timeout=60000)
                time.sleep(5)
                txt = page.inner_text('body')
                if 'Verification Required' in txt:
                    time.sleep(25)
                    page.goto(hit['url'], timeout=60000)
                    time.sleep(5)
                    txt = page.inner_text('body')
                c = extract_contact(txt)
                if c and str(p.get('contact','')).strip() in ('','-'):
                    p['contact'] = c
                    note += '，contact已补'
            except Exception as e:
                note += f'，contact补取失败({str(e)[:40]})'
            print(f"✅ id={p['id']} [{p['company'][:10]}] {p['project'][:20]} => {hit['url']}（{note}）")
            time.sleep(3)
        b.close()
    save_board(html, data)
    left = [p['id'] for p in data['projects'] if is_placeholder(p.get('url'))]
    print(f'完成，仍占位 {len(left)} 条: {left}')

if __name__ == '__main__':
    main()
