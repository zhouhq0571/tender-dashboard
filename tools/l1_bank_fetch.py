#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""银行集采平台批量采集脚本（L1 直连层通用框架，2026-10-16 上线）

覆盖：邮储邮银易采 / 工银集采 / 中信金控共享 / 民生银行 / 北京银行集采 /
      浙商数智采购 / 交行智采（7家配置驱动）。
零模型 token：Playwright 渲染各家公告栏目 → DOM 抽取（每站可覆写）→ 标题清洗
（剥 【标签】/项目编号/状态词）→ 代码预筛（TITLE_EXCLUDE + 业务正向词 + 阶段词
+ 平台特有噪声）→ keep 项点击解析详情 URL（民生/交行/工银为 JS 路由，点击法）→
输出 monitor/new_items_l1bank_*.json（schema 与 ccb_ibuy_fetch/lecaiyun_fetch
一致，后续走 dedup_filter 同一条流程）。

待突破（登录墙，诚实记录不硬凑）：农银e采、平安慧采、中信信托 going-link
（租户接口返回空；中信信托标的主要经中信金控共享平台发布，已被本脚本覆盖）。

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

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

LOOKBACK_DAYS = 4

STAGE_DROP = re.compile(
    r'结果公示|结果公告|中标|成交公告|废标|流标|终止|更正公告|变更公告|候选人公示|'
    r'合同公告|验收|延期公告|预公示')

POSITIVE = re.compile(
    r'数据|系统|平台|软件|智能|大模型|AI|财富|理财|资管|信创|外包|开发|测试|云|'
    r'数据库|监管|报送|风控|营销|客户|渠道|APP|中台|数字|科技|运维|人力|投顾|'
    r'养老金|托管|估值|TA|直销|钱包|支付|接口|资讯|数字人民币|数币|认证|安全|'
    r'网络|存储|灾备|终端|机房')

# 平台特有噪声（在通用 TITLE_EXCLUDE 之外）
PLATFORM_NOISE = re.compile(
    r'体检|物业|餐饮|食堂|押运|清分|整点|守库|金库|现金|档案保管|档案管理业务|'
    r'装修|消防|搬迁|租赁|绿化|车辆|停车|LED显示屏|办公用品|家具|空调|'
    r'电梯|工作服|清洗|饮水机|直饮水|慰问|观影|采摘|露营|年会|活动服务|'
    r'消杀|绿化|点餐|食材|医疗|医院|银医|酒店|保安|巡逻|印刷|宣传|'
    r'施工图审查|工程施工|弱电工程|精装工程|机电|监理|勘察|造价|审计服务')

# 中信金控为集团共享平台：只保留银行/信托/金控本体条目，其余集团子公司噪声拦截
CFHC_SCOPE = re.compile(r'中信银行|中信金控|中信信托')

# 通用列表抽取：li 级（CMS，文本含日期）+ a 级（SPA），按去日期标题去重、优先带日期的
EXTRACT_JS = """() => {
  const out = [];
  const seen = new Map();
  const norm = t => (t||'').replace(/\\s+/g,' ').replace(/\\s*20\\d{2}-\\d{2}-\\d{2}.*$/,'')
      .replace(/\\s*(NEW|进行中|已结束|未开始)\\s*$/,'').trim();
  const push = (title, date, href) => {
    title = (title||'').replace(/\\s+/g,' ').trim();
    if (!title || title.length < 12) return;
    const key = norm(title);
    if (key.length < 10) return;
    const prev = seen.get(key);
    const rec = {title, pubdate: date || '', href: href || ''};
    if (prev) { if (!prev.pubdate && rec.pubdate) seen.set(key, rec); return; }
    seen.set(key, rec);
  };
  document.querySelectorAll('li').forEach(li => {
    const a = li.querySelector('a');
    if (!a) return;
    const t = (li.innerText || '').replace(/\\s+/g,' ').trim();
    if (t.length < 12 || t.length > 150) return;
    const m = t.match(/(20\\d{2}-\\d{2}-\\d{2})/);
    push(t.split(/\\s*20\\d{2}-\\d{2}-\\d{2}/)[0].trim(), m ? m[1] : '', a.href);
  });
  document.querySelectorAll('a').forEach(a => {
    const t = (a.innerText || '').replace(/\\s+/g,' ').trim();
    if (t.length >= 12 && t.length <= 90) push(t, '', a.href);
  });
  return [...seen.values()].slice(0, 40);
}"""

# 工银专属：div.cell 文本为 "{类别} {标题} 招标公告： {date} {time} 发布机构：{org}"
ICBC_EXTRACT_JS = """() => {
  const out = [];
  document.querySelectorAll('div.cell').forEach(c => {
    const t = (c.innerText || '').replace(/\\s+/g,' ').trim();
    if (t.length < 20) return;
    const m = t.match(/^(.*?)(?:招标公告|招募公告|采购结果|公示)：?\\s*(20\\d{2}-\\d{2}-\\d{2})/);
    if (!m) return;
    const title = m[1].replace(/^(物品类|服务类|工程类|权益类|其他类)\\s*/,'').trim();
    if (title.length >= 10) out.push({title, pubdate: m[2], href: ''});
  });
  return out.slice(0, 30);
}"""

# 点击解析详情 URL：按标题片段定位元素点击，读路由后返回
RESOLVE_JS = """(titlePrefix) => {
  const els = [...document.querySelectorAll('a,li,div')];
  const el = els.find(e => (e.innerText||'').replace(/\\s+/g,' ').includes(titlePrefix.slice(0,14)));
  if (el) { (el.closest('a')||el).click(); return true; }
  return false;
}"""

PLATFORMS = [
    {
        'name': '邮储邮银易采', 'source': '中国邮政储蓄银行邮银易采平台',
        'pages': [('招标公告', 'https://cg.psbc.com/cms/default/webfile/1ywgg2/index.html'),
                  ('采购公告', 'https://cg.psbc.com/cms/default/webfile/2ywgg1/index.html')],
    },
    {
        'name': '中信金控共享', 'source': '中信金控采购共享平台',
        'pages': [('采购公告', 'https://ebid.cfhc.citic/cms/default/webfile/ywgg1/index.html'),
                  ('供应商征集', 'https://ebid.cfhc.citic/cms/default/webfile/gyszj/index.html')],
        'scope': CFHC_SCOPE,
    },
    {
        'name': '北京银行集采', 'source': '北京银行集中采购管理平台',
        'pages': [('采购动态', 'https://login-cpm-xt.bankofbeijing.com.cn/cms/default/webfile/1ywgg1/index.html'),
                  ('招标计划', 'https://login-cpm-xt.bankofbeijing.com.cn/cms/default/webfile/gyszj/index.html')],
    },
    {
        'name': '浙商数智采购', 'source': '浙商银行数智采购平台',
        'pages': [('集中采购公告', 'https://ccgp.szcgpt.czbank.com/luban/category?parentId=700835&childrenCode=134-848230'),
                  ('非集中采购公告', 'https://ccgp.szcgpt.czbank.com/luban/category?parentId=700836&childrenCode=134-480225')],
    },
    {
        'name': '工银集采', 'source': '工银集采平台',
        'pages': [('招标公告', 'https://jc.icbc.com.cn/#/main')],
        'click_tab': 'text=招标公告', 'wait_after_tab': 6,
        'extract_js': ICBC_EXTRACT_JS, 'click_resolve': True,
    },
    {
        'name': '民生银行', 'source': '民生银行供应商管理系统',
        'pages': [('采购公告', 'https://pms.cmbc.com.cn/purchase/')],
        'click_resolve': True,
    },
    {
        'name': '交行智采', 'source': '交通银行智采平台',
        'pages': [('采购公告', 'https://bocom-gys.bankcomm.com/espuser/login')],
        'click_resolve': True,
    },
]


def clean_title(t):
    """剥图标字符/【标签】/类别词/项目编号/电话前缀/尾部状态词（可叠多个）"""
    t = re.sub('[\ue000-\uf8ff]', '', t)                 # PUA 图标字符
    t = re.sub(r'\s+(采购单位|发布机构|发布时间|发布日期|项目编号)[:：].*$', '', t)  # li 尾部元信息
    t = re.sub(r'^[\s【\[][^】\]]{1,12}[】\]]\s*', '', t)
    t = re.sub(r'^(物品类|服务类|工程类|权益类|其他类)\s*', '', t)
    t = re.sub(r'^[A-Z]{2,6}[-\[]?[\w\-\[\]（）()]*\s+', '', t)  # 项目编号前缀
    t = re.sub(r'^0\d{2,3}-?\d{7,8}\s*', '', t)                  # 电话前缀
    t = re.sub(r'(\s*(NEW|进行中|已结束|未开始))+\s*$', '', t)    # 尾部状态词可叠
    t = re.sub(r'\s+(公开招标|公开竞争性磋商|竞争性磋商|竞争性谈判|询价|单一来源)\s*$', '', t)  # 尾部方式词
    return t.strip()


def dedup_key(t):
    return clean_title(t)


def prescreen(title, scope=None):
    if STAGE_DROP.search(title):
        return False
    if PLATFORM_NOISE.search(title):
        return False
    if scope is not None and not scope.search(title):
        return False
    if not POSITIVE.search(title):
        return False
    for kw in TITLE_EXCLUDE:
        if kw in title:
            return False
    return True


def run_platform(page, cfg):
    """返回 (status, total, kept_list)"""
    scope = cfg.get('scope')
    kept, total = [], 0
    extract_js = cfg.get('extract_js', EXTRACT_JS)
    for channel, url in cfg['pages']:
        try:
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(6000)
            if cfg.get('click_tab'):
                try:
                    page.click(cfg['click_tab'], timeout=6000)
                    page.wait_for_timeout(cfg.get('wait_after_tab', 5) * 1000)
                except Exception:
                    pass
            items = page.evaluate(extract_js)
            total += len(items)
            cutoff = (datetime.now().timestamp() - LOOKBACK_DAYS * 86400)
            for it in items:
                if it.get('pubdate'):
                    try:
                        ts = datetime.strptime(it['pubdate'], '%Y-%m-%d').timestamp()
                        if ts < cutoff:
                            continue
                    except ValueError:
                        pass
                title = clean_title(it['title'])
                if not prescreen(title, scope):
                    continue
                kept.append({'title': title, 'pubdate': it.get('pubdate', ''),
                             'deadline': '', 'url': it.get('href', '') or url,
                             'source': cfg['source'], 'channel': channel})
        except Exception as e:
            return f'error: {str(e)[:70]}', total, kept
    # 点击解析详情 URL（SPA 路由站点，每平台最多 5 条）
    if cfg.get('click_resolve'):
        base_url = cfg['pages'][0][1]
        try:
            page.goto(base_url, timeout=60000, wait_until='domcontentloaded')
            page.wait_for_timeout(6000)
            if cfg.get('click_tab'):
                try:
                    page.click(cfg['click_tab'], timeout=6000)
                    page.wait_for_timeout(cfg.get('wait_after_tab', 5) * 1000)
                except Exception:
                    pass
            for it in kept[:5]:
                if it['url'].startswith(base_url) and 'id=' not in it['url'] \
                        and '/oaasres/' not in it['url']:
                    try:
                        ok = page.evaluate(RESOLVE_JS, it['title'])
                        if ok:
                            time.sleep(3)
                            u = page.url
                            page.go_back(timeout=60000)
                            page.wait_for_timeout(4)
                            if u != page.url and len(u) > len(base_url) + 3:
                                it['url'] = u
                    except Exception:
                        pass
                    time.sleep(1)
        except Exception:
            pass
    return 'ok', total, kept


def main():
    from playwright.sync_api import sync_playwright
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_l1bank_{run_at}.json"
    result = {"run_at": run_at, "sources": [], "new_items": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for cfg in PLATFORMS:
            ctx = browser.new_context(user_agent=UA)
            page = ctx.new_page()
            try:
                status, total, kept = run_platform(page, cfg)
            except Exception as e:
                status, total, kept = f'error: {str(e)[:70]}', 0, []
            # 平台内去重（同标题跨栏目重复）
            seen_t, dedup = set(), []
            for it in kept:
                k = dedup_key(it['title'])
                if k in seen_t:
                    continue
                seen_t.add(k)
                dedup.append(it)
            result["sources"].append({"name": cfg['name'], "mode": "fetch",
                                      "status": status, "total_items": total,
                                      "new_count": len(dedup)})
            result["new_items"].extend(dedup)
            print(f"  {cfg['name']}: {status} 共{total}条 keep{len(dedup)}")
            ctx.close()
        browser.close()
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                        encoding='utf-8')
    print(f"saved {out_path}")
    for it in result["new_items"]:
        print(" KEEP:", it['title'][:58], '|', it.get('pubdate', ''),
              '|', it['source'], '|', it['url'][:80])


if __name__ == '__main__':
    main()
