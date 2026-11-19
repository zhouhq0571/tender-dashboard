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
import sys, time, json, re, os
from playwright.sync_api import sync_playwright

USER = 'chaxun032322'
PASS = 'Chaxun!2026'

# 2026-11-10：VIP 会话复用（storage_state 落盘 36h 内复用，超期或探针失败才重新登录）。
# 根因：主任务 sweep 内 subscribe+search 两次独立登录 + 详情补抓多次登录，
# 同一账号短时多次 headless 登录触发千里马滑块风控（"向右滑动完成验证"），
# 导致 11-10 晨 VIP 全通道异常（订阅0/搜索0）。三脚本共用本助手的单点修复。
VIP_STATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'monitor', '.vip_state.json')
UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')


def _state_fresh(path):
    return os.path.exists(path) and (time.time() - os.path.getmtime(path) < 36 * 3600)


def _probe_ok(ctx):
    """探针：state 能否免登访问 VIP 区且未触发滑块风控。
    2026-11-12 修复：探针从 vip.qianlima.com 首页改为 search.vip.qianlima.com——
    首页宽容度高会造成"探针通过但搜索子域登录态超时"的假阳性（今晨 qlsearch 因此全 0）。"""
    try:
        page = ctx.new_page()
        page.goto('https://search.qianlima.com/', timeout=30000)
        time.sleep(4)
        t = page.inner_text('body')[:3000]
        page.close()
        if '向右滑动' in t or '安全验证' in t:
            return False
        if '登录状态超时' in t or '重新登录' in t:
            return False
        return True
    except Exception:
        return False


def new_logged_in_context(p, state_path=None):
    """返回 (context, fresh_login: bool)。优先复用 storage_state，失败回退交互登录并落盘。"""
    sp = state_path or VIP_STATE
    if _state_fresh(sp):
        try:
            browser = p.chromium.launch(headless=True)
            ctx = browser.new_context(storage_state=sp, user_agent=UA)
            if _probe_ok(ctx):
                return ctx, False
            browser.close()
        except Exception:
            try:
                browser.close()
            except Exception:
                pass
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(user_agent=UA)
    login(ctx.new_page())
    try:
        os.makedirs(os.path.dirname(sp), exist_ok=True)
        ctx.storage_state(path=sp)
    except Exception:
        pass
    return ctx, True

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
    info['联系方式'] = extract_contact(txt)
    return info

def extract_contact(txt):
    """从公告全文中提取项目咨询/联系方式（2026-10-30 新增，上板硬规字段）
    只取公告正文，剔除千里马页面 chrome（招标联系人/代理联系人 脱敏模块、
    企业信息链接尾巴）。返回 '代理 X；联系人 Y；电话 Z；邮箱 W'，截断 120 字。"""
    parts = []
    def add(s):
        s = (s or '').strip(' ：:，,。;；\t\n ')
        if s and s not in parts and len(s) >= 2:
            parts.append(s)
    # 1) 招标代理机构（行首标签型与正文型通用）
    m = re.search(r'招标代理机构[：:\t\s]*([^\n\t，。；]{4,40})', txt)
    if m:
        raw = m.group(1)
        if '...' not in raw:  # 名称被截断（企业信息链接尾巴）则弃用
            name = re.sub(r'企业信息.*$', '', raw).strip(' .。')
            if len(name) >= 4 and '联系人' not in name and re.search(r'(公司|中心|院|事务所|集团)$', name):
                add('代理 ' + name)
    # 2) 联系人（正文型，值不得为 - / 空 / junk；分隔符不许跨行）
    m = re.search(r'联系[ \t]*人[：:\t ]*([^\n，。；电话邮箱\-]{2,15})', txt)
    if m and m.group(1).strip():
        v = m.group(1).strip()
        if v not in ('-', '查看更多') and not any(w in v for w in ['预约', '详见', '原文', '更多']):
            add('联系人 ' + v)
    # 3) 电话
    m = re.search(r'(?:联系电话|咨询电话|电[ \t]*话|手机)[ \t]*[：:]?[ \t]*([0-9][0-9\-+ ]{6,20})', txt)
    if m:
        add('电话 ' + m.group(1).strip())
    # 4) 邮箱
    m = re.search(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,})', txt)
    if m:
        add('邮箱 ' + m.group(1))
    return '；'.join(parts)[:120]

def main():
    bids = sys.argv[1:]
    if not bids:
        print('用法: python3 ql_vip_fetch.py bid1 bid2 ...')
        return
    results = []
    with sync_playwright() as p:
        ctx, fresh = new_logged_in_context(p)
        page = ctx.new_page()
        for bid in bids:
            try:
                info = fetch_bid(page, bid)
            except Exception as e:
                info = {'bid': bid, 'error': str(e)[:200]}
            results.append(info)
            print(json.dumps(info, ensure_ascii=False))
            time.sleep(3)
        ctx.browser.close()
    json.dump(results, open('/tmp/ql_vip_result.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('saved /tmp/ql_vip_result.json')

if __name__ == '__main__':
    main()
