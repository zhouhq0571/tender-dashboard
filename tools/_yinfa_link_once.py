# -*- coding: utf-8 -*-
"""一次性：千里马VIP搜「银法智管」公告详情链接+联系方式，落盘 /tmp/yinfa_result.json"""
import sys, time, json, re, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ql_vip_fetch import new_logged_in_context, extract_contact
from playwright.sync_api import sync_playwright

KW = "银法智管"
OUT = "/tmp/yinfa_result.json"

with sync_playwright() as pw:
    ctx, _fresh = new_logged_in_context(pw)
    page = ctx.new_page()
    url = f'https://search.qianlima.com/?q={KW}'
    page.goto(url, timeout=60000)
    time.sleep(6)
    txt = page.inner_text('body')
    if 'Verification Required' in txt:
        time.sleep(25)
        page.goto(url, timeout=60000)
        time.sleep(6)
    hits = page.evaluate("""(()=>{
      const out=[];
      document.querySelectorAll('a[href*="bid-"]').forEach(a=>{
        const t=(a.innerText||a.textContent||'').trim().replace(/\\s+/g,' ');
        if(t.length>8) out.push({title:t.slice(0,120), url:a.href.split('?')[0]});
      });
      return out.slice(0,15);
    })""")
    print(json.dumps(hits, ensure_ascii=False, indent=1))
    result = None
    for h in hits:
        if '银法智管' in h['title']:
            page.goto(h['url'], timeout=60000)
            time.sleep(6)
            txt = page.inner_text('body')
            if 'Verification Required' in txt:
                time.sleep(25)
                page.goto(h['url'], timeout=60000)
                time.sleep(6)
                txt = page.inner_text('body')
            c = extract_contact(txt)
            result = {"url": h['url'], "title": h['title'], "contact": c,
                      "snippet": txt[:1500]}
            break
    json.dump(result, open(OUT, 'w'), ensure_ascii=False, indent=1)
    print("RESULT:", json.dumps(result, ensure_ascii=False)[:600] if result else None)
    ctx.browser.close()
