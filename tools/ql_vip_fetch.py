# -*- coding: utf-8 -*-
"""
千里马招标网 VIP 抓取脚本（v2 修复版，2026-08-31）
=================================================
用途：登录千里马 VIP（账号 chaxun032322），批量抓取 bid 详情页的
      招标单位/招标估价/报名截止/投标截止等字段（登录后不脱敏）。

2026-08-31 特大故障根因与修复：
1. 千里马首页新增 Vue 推广浮层 div.btn-image-bg，遮挡登录弹层，
   导致对 #log（登录切换标签）的点击被拦截（intercepts pointer events）。
   修复：先隐藏 .btn-image-bg，并对高层级 fixed/absolute 元素禁用 pointer-events。
2. 登录弹层默认显示"注册"表单，需点击 span#log.regist-log 切换到账号密码表单。
3. 页面存在同名隐藏 input（WS_username 等），禁止用 input[name=username] 填充，
   必须用 :visible + placeholder 定位（请输入用户名 / 请输入密码）。
4. 连续抓取触发验证码限流（Verification Required），每次请求间隔 >=5 秒，
   遇限流等待 25 秒后重试一次。

用法：python3 ql_vip_fetch.py bid1 bid2 ...
输出：打印并保存 /tmp/ql_vip_result.json
"""
import sys, time, json, re
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

def fetch_bid(page, bid):
    url = f'https://www.qianlima.com/bid-{bid}.html'
    page.goto(url, timeout=60000)
    time.sleep(5)
    txt = page.inner_text('body')
    if 'Verification Required' in txt:
        time.sleep(25)
        page.goto(url, timeout=60000)
        time.sleep(5)
        txt = page.inner_text('body')
    info = {'bid': bid, 'masked': '点击查看' in txt}
    # 摘要信息表格：label\tvalue 或 label\nvalue
    for label in ['招标单位', '招标编号', '招标估价', '报名截止时间', '投标截止时间', '开标时间']:
        m = re.search(label + r'[\t\s\n]+([^\t\n]{1,60})', txt)
        if m:
            info[label] = m.group(1).strip()
    # 正文中的截止日期
    m2 = re.search(r'(?:投标截止|递交截止|响应文件递交截止|报价截止)[^\d\n]{0,25}(20\d{2}[\s年\-/\.]\d{1,2}[\s月\-/\.]\d{1,2}[日号]?(?:\s*\d{1,2}[:：时点]\d{0,2}分?)?)', txt)
    if m2:
        info['正文截止'] = m2.group(1).strip()
    # 信息来源（原始公告URL）
    m3 = re.search(r'信息来源：\s*(https?://[^\s]+)', txt)
    if m3:
        info['原始来源'] = m3.group(1).strip()
    return info

def main():
    bids = sys.argv[1:]
    if not bids:
        print('用法: python3 ql_vip_fetch.py bid1 bid2 ...')
        return
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
        ).new_page()
        login(page)
        for bid in bids:
            try:
                info = fetch_bid(page, bid)
            except Exception as e:
                info = {'bid': bid, 'error': str(e)[:200]}
            results.append(info)
            print(json.dumps(info, ensure_ascii=False))
            time.sleep(3)
        browser.close()
    json.dump(results, open('/tmp/ql_vip_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('saved /tmp/ql_vip_result.json')

if __name__ == '__main__':
    main()
