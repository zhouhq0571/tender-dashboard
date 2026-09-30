# -*- coding: utf-8 -*-
"""
千里马链接月度全量校验（慢速、只读，严禁修改看板数据）
用法: python3 tools/ql_link_audit.py <start_idx> <end_idx>
清单: /tmp/ql_check_list.json  结果追加: /tmp/ql_audit_result.jsonl
规则: 仅当 fetch 成功且页面标题/正文中【招标单位】与【项目名关键词】均不出现 → 链接错配；
      fetch 失败/超时/419/403/验证码 → 无法判定（不算异常）。
"""
import sys, time, json, re
sys.path.insert(0, '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/tools')
from playwright.sync_api import sync_playwright
from ql_vip_fetch import login, CLOSE_OVERLAY_JS

# 机构别名映射（看板简称 → 页面可能出现的写法）
ALIASES = {
    '中行江西分行': ['中国银行江西省分行', '中行江西', '江西省分行'],
    '国开行': ['国家开发银行', '国开行'],
    '光大理财': ['光大理财'],
    '宁银理财': ['宁银理财'],
    '龙湾农商': ['龙湾农商'],
    '黄河农商': ['黄河农商'],
    '吉林九台农商': ['九台农商'],
    '中国银行眉山分行': ['眉山分行', '中国银行眉山'],
    '工商银行苏州分行': ['工商银行苏州', '苏州分行', '中国工商银行'],
    '顺德农商': ['顺德农商'],
    '陕西信托': ['陕西省国际信托', '陕国投', '陕西信托'],
    '中信信托': ['中信信托'],
    '中核财务': ['中核财务'],
}
GENERIC = ['采购', '项目', '招标', '建设', '服务', '系统', '平台', '改造', '升级', '公示', '公告',
           '邀请', '磋商', '谈判', '询价', '单一来源', '征集', '供应商', '2026', '2025', '年度',
           '第一次', '第二次', '一期', '二期', '中标', '成交', '入围', '遴选', '比选', '的']

def aliases_for(company):
    out = [company]
    if company in ALIASES:
        out += ALIASES[company]
    return out

def keywords_for(project):
    """从项目名提取区分度关键词（去通用词，保留>=4字片段）"""
    # 去掉括号内公告类型说明
    name = re.sub(r'[（(][^）)]*(公示|公告|磋商|谈判|邀请|采购|重招|寻源)[^）)]*[）)]', '', project)
    # 按分隔符切片
    parts = re.split(r'[、，,\s/／\-—_（）()]+', name)
    kws = []
    for part in parts:
        part = part.strip('"\'""'' ')
        if len(part) >= 4:
            kws.append(part)  # 原样片段优先（页面通常含原词）
        p = part
        for g in GENERIC:
            p = p.replace(g, '')
        p = p.strip()
        if len(p) >= 4 and p not in kws:
            kws.append(p)
    if not kws:  # 兜底：整个项目名去通用词
        p = project
        for g in GENERIC:
            p = p.replace(g, '')
        kws = [p] if p else []
    return kws

def fetch_page(page, url):
    try:
        page.goto(url, timeout=60000)
        time.sleep(5)
        txt = page.inner_text('body')
        if 'Verification Required' in txt:
            time.sleep(25)
            page.goto(url, timeout=60000)
            time.sleep(5)
            txt = page.inner_text('body')
            if 'Verification Required' in txt:
                return {'status': '无法判定', 'reason': '验证码限流'}
        title = page.title()
        return {'status': 'ok', 'title': title, 'text': txt}
    except Exception as e:
        return {'status': '无法判定', 'reason': str(e)[:150]}

def main():
    start, end = int(sys.argv[1]), int(sys.argv[2])
    items = json.load(open('/tmp/ql_check_list.json', encoding='utf-8'))[start:end]
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36'
        ).new_page()
        login(page)
        for it in items:
            comp, proj, url = it['company'], it['project'], it['url']
            r = fetch_page(page, url)
            rec = {'id': it['id'], 'company': comp, 'project': proj, 'url': url}
            if r['status'] != 'ok':
                rec['verdict'] = '无法判定'
                rec['reason'] = r.get('reason', '')
            else:
                text = r['title'] + '\n' + r['text']
                comp_hit = any(a in text for a in aliases_for(comp))
                kws = keywords_for(proj)
                kw_hit = any(k in text for k in kws)
                rec['page_title'] = r['title'][:80]
                rec['company_hit'] = comp_hit
                rec['kw_hit'] = kw_hit
                rec['kws'] = kws
                rec['verdict'] = '链接错配' if (not comp_hit and not kw_hit) else '正常'
            print(json.dumps(rec, ensure_ascii=False))
            with open('/tmp/ql_audit_result.jsonl', 'a', encoding='utf-8') as f:
                f.write(json.dumps(rec, ensure_ascii=False) + '\n')
            time.sleep(3)
        browser.close()

if __name__ == '__main__':
    main()
