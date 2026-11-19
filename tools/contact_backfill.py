# -*- coding: utf-8 -*-
"""
在板项目 contact 字段批量补全（2026-10-30，零模型，断点续跑）
================================================================
低成本机制：复用 ql_vip_fetch 的登录态与 extract_contact，从千里马公告
原文正则提取 项目咨询/联系方式，结构化回写 index.html 的 tender-data。

用法：python3 tools/contact_backfill.py [每批条数，默认10]
状态文件：/tmp/contact_backfill_state.json（已补 id -> contact，幂等续跑）
仅处理 url 为 qianlima.com 且在板 contact 为空的条目；其他来源另案。
"""
import json, re, sys, time, os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ql_vip_fetch import login, extract_contact

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, 'index.html')
STATE = '/tmp/contact_backfill_state.json'

def empty(c):
    c = str(c or '').strip()
    return c in ('', '-', '/', '无', '暂无')

def load_board():
    html = open(HTML, encoding='utf-8').read()
    m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
    return html, json.loads(m.group(1))

def save_board(html, data):
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    out = re.sub(r'(<script type="application/json" id="tender-data">).*?(</script>)',
                 lambda m: m.group(1) + new_json + m.group(2), html, count=1, flags=re.DOTALL)
    open(HTML, 'w', encoding='utf-8').write(out)

def main():
    batch = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    html, data = load_board()
    projects = data['projects']
    todo = [p for p in projects
            if empty(p.get('contact')) and 'qianlima.com' in str(p.get('url', ''))
            and str(p['id']) not in state]
    print(f'待补全 {len(todo)} 条（本批 {min(batch, len(todo))} 条）')
    if not todo:
        return
    from playwright.sync_api import sync_playwright
    done = 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
        ).new_page()
        login(page)
        for p in todo[:batch]:
            url = p['url']
            try:
                page.goto(url, timeout=60000)
                time.sleep(5)
                txt = page.inner_text('body')
                if 'Verification Required' in txt:
                    time.sleep(25)
                    page.goto(url, timeout=60000)
                    time.sleep(5)
                    txt = page.inner_text('body')
                contact = extract_contact(txt)
                if contact:
                    p['contact'] = contact
                    state[str(p['id'])] = contact
                    print(f"✅ id={p['id']} {p['company'][:12]} => {contact[:60]}")
                else:
                    state[str(p['id'])] = ''
                    print(f"⚠️ id={p['id']} {p['company'][:12]} 未提取到，跳过（留空）")
            except Exception as e:
                print(f"❌ id={p['id']} error: {str(e)[:120]}（不入 state，下批重试）")
            json.dump(state, open(STATE, 'w'), ensure_ascii=False, indent=1)
            done += 1
            if done < len(todo[:batch]):
                time.sleep(3)
        browser.close()
    save_board(html, data)
    filled = sum(1 for v in state.values() if v)
    print(f'本批完成 {done} 条；累计已补 {filled} 条，仍空 {len(todo) - done} 条待下批')

if __name__ == '__main__':
    main()
