# -*- coding: utf-8 -*-
"""千里马 VIP 列表搜索 v2（复用登录流程，单会话多关键词）
用法: python3 ql_vip_search.py "关键词1" "关键词2" ...
输出: /tmp/ql_vip_search.json
"""
import sys, time, json, re
from urllib.parse import quote
from playwright.sync_api import sync_playwright

USER = 'chaxun032322'
PASS = 'Chaxun!2026'
CLOSE_OVERLAY_JS = """(()=>{
  document.querySelectorAll('.btn-image-bg').forEach(e=>e.style.display='none');
  document.querySelectorAll('div').forEach(e=>{
    const cs=getComputedStyle(e);
    if((cs.position==='fixed'||cs.position==='absolute') && parseInt(cs.zIndex||'0')>=100
       && e.offsetWidth>200 && e.offsetHeight>200 && !e.querySelector('#log')) e.style.pointerEvents='none';
  });
})()"""

def login(page):
    page.goto('https://www.qianlima.com/', timeout=60000)
    time.sleep(3)
    page.evaluate(CLOSE_OVERLAY_JS)
    page.evaluate("document.querySelector('#loginBottomLink').click()")
    time.sleep(1.5)
    page.evaluate("document.querySelector('#log').click()")
    time.sleep(1.5)
    page.locator('input:visible[placeholder*="用户名"]').first.fill(USER, timeout=8000)
    page.locator('input:visible[type="password"]').first.fill(PASS, timeout=8000)
    page.locator('div.regist-foot:visible, button:visible:has-text("登录")').last.click(timeout=8000)
    time.sleep(5)

def extract(page):
    return page.evaluate("""(()=>{
      const out=[];
      document.querySelectorAll('a[href*="bid-"]').forEach(a=>{
        const t=(a.innerText||a.textContent||'').trim().replace(/\\s+/g,' ');
        if(t.length>8) out.push({title:t.slice(0,90), url:a.href.split('?')[0]});
      });
      // 去重
      const seen=new Set(); const r=[];
      for(const o of out){ if(!seen.has(o.url)){seen.add(o.url); r.push(o);} }
      return r.slice(0,30);
    })()""")

def main():
    kws = sys.argv[1:] or ['银行 系统']
    results = {}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
        ).new_page()
        login(page)
        for kw in kws:
            url = f'https://search.qianlima.com/?q={quote(kw)}'
            try:
                page.goto(url, timeout=45000)
                time.sleep(5)
                txt = page.inner_text('body')
                if 'Verification Required' in txt:
                    time.sleep(25)
                    page.goto(url, timeout=45000)
                    time.sleep(5)
                items = extract(page)
                results[kw] = {'count': len(items), 'items': items}
            except Exception as e:
                results[kw] = {'error': str(e)[:150]}
            time.sleep(6)
        browser.close()
    json.dump(results, open('/tmp/ql_vip_search.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    for kw, r in results.items():
        print(f'## {kw}: {r.get("count", "ERR")}')
        for it in r.get('items', [])[:15]:
            print('  ', it['title'], '|', it['url'])

if __name__ == '__main__':
    main()
