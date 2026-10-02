# -*- coding: utf-8 -*-
"""
信源指纹监测器 v1（2026-09-01）
================================
目标：把"补充信源清单"从文档变成低 token 的可执行监测能力。

原理：
- 纯 Python 抓取（不调模型、零 LLM token），只抓各信源的列表页；
- 用正则从列表页提取"标题+日期+链接"条目集合作为指纹；
- 与 source_fingerprints.json 中昨日指纹 diff，只输出【新增条目】；
- 每日定时任务先跑本脚本，仅把新增条目交给模型核实截止日期后再上报。

反 WAF 策略：检测到 412/403/挑战页 → 标记 waf_blocked，交给定时任务用
搜索引擎快照模式（site:域名 招标 after:昨天）补位，不再硬抓浪费 token。

用法：python3 source_monitor.py [--all] [--source 名称关键字]
输出：bidding-daily/monitor/new_items_YYYYMMDD_HHMM.json + 更新指纹库
"""
import json, re, os, sys, ssl, hashlib, argparse
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # bidding-daily/
FP_PATH = os.path.join(BASE, 'monitor', 'source_fingerprints.json')
OUT_DIR = os.path.join(BASE, 'monitor')

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36')

# 监测目标配置：mode=fetch（直连列表页）/ search（WAF 拦截，走搜索快照）
# tier=S 每日必监测；tier=A 抽查（默认也每日跑，直连零token）；B 级不进监测器，仅定向核查
SOURCES = [
    {"name": "中招联合招标采购平台", "mode": "fetch", "tier": "A",
     "urls": ["https://www.365trade.com.cn/zfwzb/index.jhtml",
              "https://www.365trade.com.cn/"],
     "note": "公告全文免登录，龙江银行ECIF/中信信托职业年金来源"},
    {"name": "移动支付网", "mode": "fetch", "tier": "S",
     "urls": ["https://www.mpaypass.com.cn/news/"],
     "note": "银行IT招标聚合媒体，免登录"},
    {"name": "甘肃经济信息网", "mode": "fetch", "tier": "A",
     "urls": ["https://www.gsei.com.cn/"],
     "note": "甘肃地区招标公告，免登录"},
    {"name": "阳光采购服务平台", "mode": "fetch", "tier": "A",
     "urls": ["http://www.ygcgfw.com/"],
     "note": "山东省属企业采购，免登录"},
    {"name": "九江银行招标采购", "mode": "fetch", "tier": "B",
     "urls": ["https://www.jycbank.com/jjccb/zbcg/"],
     "note": "详情页免登录可读"},
    {"name": "宁波国际投资咨询", "mode": "fetch", "tier": "A",
     "urls": ["https://www.nbgodo.com/"],
     "note": "宁银理财指定发布渠道"},
    {"name": "广西北部湾银行采购公告", "mode": "search", "tier": "B",
     "domain": "bankofbbg.com",
     "note": "瑞数WAF 412，直连不可行，仅搜索快照"},
    {"name": "四川采购网", "mode": "search", "tier": "A",
     "domain": "sc.chinamae.com",
     "note": "详情页403，仅搜索快照"},
    {"name": "苏州农商官网", "mode": "fetch", "tier": "B",
     "urls": ["https://www.szrcb.com/"],
     "note": "招标公告栏目"},
    {"name": "黄河农商银行官网", "mode": "fetch", "tier": "A",
     "urls": ["https://www.bankyellowriver.com/"],
     "note": "招标公告栏目"},
]

TENDER_KW = re.compile(r'招标|采购|磋商|征集|谈判|询价|竞价|中标|成交|公示|公告|候选人|供应商')
DATE_RE = re.compile(r'20\d{2}[\-年/]\d{1,2}[\-月/]\d{1,2}')
A_RE = re.compile(r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.S | re.I)
TAG_RE = re.compile(r'<[^>]+>')

CTX = ssl.create_default_context()
CTX.check_hostname = False
CTX.verify_mode = ssl.CERT_NONE


def fetch(url, timeout=25):
    req = Request(url, headers={
        'User-Agent': UA,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    })
    try:
        with urlopen(req, timeout=timeout, context=CTX) as r:
            raw = r.read()
            for enc in ('utf-8', 'gbk', 'gb18030'):
                try:
                    return r.status, raw.decode(enc)
                except UnicodeDecodeError:
                    continue
            return r.status, raw.decode('utf-8', errors='ignore')
    except HTTPError as e:
        body = ''
        try:
            body = e.read()[:2000].decode('utf-8', errors='ignore')
        except Exception:
            pass
        return e.code, body
    except (URLError, Exception) as e:  # noqa
        return -1, str(e)


def extract_items(html, base_url):
    """从列表页HTML提取 招标类条目：标题+日期+链接"""
    items = {}
    for m in A_RE.finditer(html):
        href, text = m.group(1), m.group(2)
        title = TAG_RE.sub('', text).strip()
        title = re.sub(r'\s+', ' ', title)
        if len(title) < 10 or not TENDER_KW.search(title):
            continue
        # 在该链接后面 300 字符内找日期
        tail = html[m.end():m.end() + 300]
        dm = DATE_RE.search(tail)
        date = dm.group(0) if dm else ''
        if href.startswith('/'):
            from urllib.parse import urlparse
            pu = urlparse(base_url)
            href = f'{pu.scheme}://{pu.netloc}{href}'
        elif not href.startswith('http'):
            continue
        key = hashlib.md5(title.encode()).hexdigest()[:12]
        items[key] = {'title': title, 'date': date, 'url': href}
    return items


def is_waf(status, body):
    if status in (412, 403, 503):
        return True
    if status == -1:
        return False
    markers = ['BsOatOKjxZbd', 'Verification Required', 'challenge', '安全验证', '访问验证']
    return any(k in body for k in markers) and len(body) < 5000


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--source', default='', help='只跑名称含该关键字的信源')
    ap.add_argument('--tiers', default='S,A', help='只跑指定层级，逗号分隔，如 S 或 S,A')
    args = ap.parse_args()
    tiers = set(t.strip() for t in args.tiers.split(',') if t.strip())

    os.makedirs(OUT_DIR, exist_ok=True)
    fp = {}
    if os.path.exists(FP_PATH):
        with open(FP_PATH, encoding='utf-8') as f:
            fp = json.load(f)

    now = datetime.now()
    report = {'run_at': now.strftime('%Y-%m-%d %H:%M:%S'), 'sources': [], 'new_items': []}

    for src in SOURCES:
        if args.source and args.source not in src['name']:
            continue
        if src.get('tier', 'B') not in tiers:
            continue
        name = src['name']
        state = fp.get(name, {'keys': [], 'hits': 0, 'runs': 0, 'last_status': ''})
        state['runs'] = state.get('runs', 0) + 1
        entry = {'name': name, 'mode': src['mode']}

        if src['mode'] == 'search':
            entry['status'] = 'search_mode'
            entry['note'] = src.get('note', '')
            state['last_status'] = 'search_mode'
            report['sources'].append(entry)
            fp[name] = state
            continue

        status, body, used_url = -1, '', ''
        for url in src['urls']:
            status, body = fetch(url)
            used_url = url
            if status == 200 and len(body) > 3000:
                break

        if is_waf(status, body):
            entry['status'] = 'waf_blocked'
            entry['http'] = status
            entry['action'] = '转搜索引擎快照模式（site:%s after:昨日）' % src.get('domain', used_url)
            state['last_status'] = 'waf_blocked'
        elif status != 200:
            entry['status'] = f'fetch_failed:{status}'
            state['last_status'] = entry['status']
        else:
            items = extract_items(body, used_url)
            new_keys = [k for k in items if k not in state.get('keys', [])]
            first_run = not state.get('keys')
            entry['status'] = 'ok'
            entry['total_items'] = len(items)
            entry['new_count'] = 0 if first_run else len(new_keys)
            if first_run:
                entry['note'] = '首次运行，仅建立指纹基线，不输出新增'
            else:
                for k in new_keys:
                    it = items[k]
                    it['source'] = name
                    report['new_items'].append(it)
                if new_keys:
                    state['hits'] = state.get('hits', 0) + len(new_keys)
            # 指纹滚动更新（保留本次全量）
            state['keys'] = list(items.keys())
            state['last_status'] = 'ok'
            state['last_ok'] = now.strftime('%Y-%m-%d %H:%M:%S')

        report['sources'].append(entry)
        fp[name] = state

    with open(FP_PATH, 'w', encoding='utf-8') as f:
        json.dump(fp, f, ensure_ascii=False, indent=1)

    out_file = os.path.join(OUT_DIR, 'new_items_%s.json' % now.strftime('%Y%m%d_%H%M'))
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=1)

    # 控制台摘要
    print('=== 信源指纹监测 %s ===' % report['run_at'])
    for s in report['sources']:
        line = f"[{s['status']:>16}] {s['name']}"
        if s.get('new_count'):
            line += f" 新增{s['new_count']}条"
        if s.get('total_items') is not None:
            line += f" (列表{s['total_items']}条)"
        print(line)
    print(f"\n新增条目合计: {len(report['new_items'])}")
    for it in report['new_items']:
        print(f"  [{it['source']}] {it['date']} {it['title'][:50]} {it['url']}")
    print(f"\n明细: {out_file}")


if __name__ == '__main__':
    main()
