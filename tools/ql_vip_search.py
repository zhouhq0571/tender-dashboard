# -*- coding: utf-8 -*-
"""千里马 VIP 列表搜索 v2（复用登录流程，单会话多关键词）
用法: python3 ql_vip_search.py "关键词1" "关键词2" ...
输出: monitor/new_items_qlsearch_<ts>.json（预筛后结构化落盘，供 sweep_candidates 汇总；
      2026-11-09 改造——原 /tmp 落盘+大段 stdout 不利于零模型 sweep 管线，改为落盘+计数输出）
"""
import sys, time, json, re, os
from datetime import datetime
from urllib.parse import quote
from playwright.sync_api import sync_playwright
# 2026-11-10：共用 VIP 会话复用助手（防同账号多脚本独立登录触发滑块风控）
try:
    from ql_vip_fetch import new_logged_in_context
except ImportError:  # 直接以其他 cwd 运行时
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from ql_vip_fetch import new_logged_in_context

# 2026-11-09 预筛（与 kc_bid_fetch 同源词表思路）：只留"金融机构主体 × IT品类 × 在招阶段"
_STAGE_DROP = re.compile(r'结果公示|结果公告|中标|成交公告|废标|流标|终止|更正|变更|候选人|合同公告|成交结果|结果通知')
_ORG_POS = re.compile(r'银行|信托|理财|农商|农信|农商行|信用社|邮储|工行|农行|中行|建行|交行|招商|中信|光大|华夏|民生|兴业|浦发|广发|平安|浙商|渤海|恒丰|北京银行|上海银行|南京银行|宁波银行|江苏银行|杭州银行|徽商|贵阳|齐鲁|中原|长沙|成都|重庆银行|桂林|东莞|南海|顺德|华兴|新网|网商|微众|蓝海|众邦|亿联|苏宁')
_IT_POS = re.compile(r'系统|平台|软件|智能|大模型|AI|信创|开发|测试|外包|中台|监管|报送|风控|估值|TA|直销|渠道|营销|投顾|托管|财富|资管|数据|支付|接口|运维|安全|科技|清算|核算|终端|一体机|算力')

def prescreen(title):
    if not title or _STAGE_DROP.search(title):
        return False
    if not _ORG_POS.search(title):
        return False
    return bool(_IT_POS.search(title))

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
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    results = {}
    kept_all = []
    with sync_playwright() as p:
        ctx, _fresh = new_logged_in_context(p)
        page = ctx.new_page()
        page.goto('https://vip.qianlima.com/', timeout=60000)
        time.sleep(4)
        if page.locator('div.Captcha').count() > 0 or '向右滑动' in page.inner_text('body')[:3000]:
            print('VIP_CAPTCHA_BLOCKED 滑块风控未解，本通道今日跳过（冷却期勿反复探测）')
            ctx.browser.close()
            sys.exit(2)
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
                kept = [it for it in items if prescreen(it.get('title', ''))]
                results[kw] = {'count': len(items), 'kept': len(kept)}
                for it in kept:
                    it['keyword'] = kw
                    kept_all.append(it)
            except Exception as e:
                results[kw] = {'error': str(e)[:150]}
            time.sleep(6)
        ctx.browser.close()
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'monitor')
    out = os.path.join(base, f'new_items_qlsearch_{run_at}.json')
    json.dump({'run_at': run_at, 'keywords': kws, 'summary': results,
               'new_items': kept_all}, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    total_raw = sum(v.get('count', 0) for v in results.values())
    print(f'qlsearch: 关键词{len(kws)}组 原始{total_raw} 预筛保留{len(kept_all)} -> {out}')

if __name__ == '__main__':
    main()
