#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""乐采云平台采集脚本（L1 直连层，2026-10-15 上线，L1 第 2 家）

零模型 token：Playwright 过阿里云 WAF（acw_sc__v2）→ 页内 fetch 公告大厅
/announcement/lobby/queryPage（项目采购全量在招公告，含全文）→ 代码预筛
（金融机构 + 业务正向词 + 阶段/后勤噪声）→ 正文抽取投标截止 →
输出 monitor/new_items_lecaiyun_YYYYMMDD_HHMM.json（schema 与 ccb_ibuy_fetch 一致）。

背景：湖州银行 AI 大模型平台、数智化平台两标均经此平台交易；浙江区域
城商行/农商（湖州银行、温州银行、泰隆、稠州、杭州银行等）政采类标高频入口。

2026-10-19 WAF 兜底（周老师批准）：阿里云 WAF 自 10-15 起持续拦截直连，
当且仅当 status == "waf_blocked" 时，自动改用快查官方 API 定向补采
乐采云 niche（湖州/温州/泰隆/稠州/杭州/宁波银行，≤6 次调用/天，占少量
快查额度）；url_id 以 ccgp_lecaiyun 开头者即乐采云平台原始公告，可精确
归因。直连恢复后兜底自动停用（status 不再是 waf_blocked 即不触发）。

L1 失效纪律：连续抓取失败 3 天须在汇报中报失效（降级/维修）。
"""
import hashlib
import json
import re
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ql_subscribe_fetch import TITLE_EXCLUDE  # 复用预筛排除词表

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "monitor"

UA = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 '
      '(KHTML, like Gecko) Chrome/126.0 Safari/537.36')

# 项目采购-在招类公告（ lobbying 页首屏 tab1 的 types，公示/结果类不在此列）
TENDER_TYPES = ["3012", "3020", "2002", "3003", "3011", "3002", "3001",
                "3008", "2001", "10007", "10002", "10012", "20010",
                "200012", "200003", "200026", "200025", "200004", "200002",
                "200005", "200022", "200001", "200006", "200023", "200000",
                "20010", "20012", "20009"]
# 2026-10-18 根治"发布早、周期长"漏采（湖州银行算力服务器 9-30 发布 4 天窗口翻页漏失）：
# 零模型脚本，加页只耗运行时间（~1-2 分钟）不耗 token； lobby 约 100-150 条/天，20 页 ≈ 1980 条覆盖 15 天
PAGES = 20         # 每页 99 条，按日期早停（末条超出回看窗口即停翻）
LOOKBACK_DAYS = 15 # 只保留近 N 天 releasedAt 的条目（与月度复盘 15 天口径对齐）

# 金融机构（招标主体或项目对象须在范围内）
FINANCE = re.compile(
    r'银行|信托|理财|农商|信用社|金融|资产管理|证券|基金|消费金融|金融租赁|AIC')
# 业务正向词：IT/业务相关才保留
POSITIVE = re.compile(
    r'数据|系统|平台|软件|智能|大模型|AI|财富|理财|资管|信创|外包|开发|测试|云|'
    r'数据库|监管|报送|风控|营销|客户|渠道|APP|中台|数字|科技|运维|人力|投顾|'
    r'养老金|托管|估值|TA|直销|钱包|支付|接口|资讯|数字人民币|数币')
# 乐采云特有噪声（平台为全行业采购，后勤/工程/物资占比极高）
LCY_NOISE = re.compile(
    r'体检|物业|餐饮|年金|开户银行|资金专户|存款账户|恒温恒湿|金库|守押|押运|'
    r'清分|宣传|广告|装修|租赁|绿化|车辆|充电桩|停车|搬迁|食材|苗木|'
    r'电梯|空调|办公用品|家具|印刷|监控设备|门禁|档案|洗衣|票务|'
    r'医疗|医院|学院|学校|课时|教材|实训|病房|器械|药品')
# 阶段词：已过阶段直接丢
STAGE_DROP = re.compile(
    r'结果公示|结果公告|中标|成交公告|废标|流标|终止|更正公告|变更公告|候选人公示|'
    r'合同公告|验收|预公示')

DETAIL = 'https://sourcing-lcy.lecaiyun.com/luban/announcement/detail?encryptId='

# 2026-10-19 快查 API 兜底常量（标准 API 独立额度，与 kc_bid_fetch 同 key）
KC_GATEWAY = "https://bizveris.kuaicha365.com"
KC_TOOL_ID = "operation_get_yuqing_bidding_search_plus"
KC_KEY_FILE = BASE / ".kc_apikey"
# 乐采云 niche：浙江区域城商行/农商政采高频入口（与 l1_bank 7家、主 kc 3组词表互补）
KC_FALLBACK_GROUPS = ["湖州银行", "温州银行", "泰隆", "稠州", "杭州银行", "宁波银行"]
KC_WINDOW_DAYS = 4  # 覆盖 WAF 拦截缺口；重复条目由 dedup_filter/标题级去重零成本剔除


def strip_html(s):
    return re.sub(r'<[^>]+>', '', s or '')


def extract_deadline(text):
    """从公告正文抽取投标/响应截止日（YYYY-MM-DD），取第一个匹配。"""
    pats = [
        (r'(?:投标|响应|报价|申请文件)[^\n。；]{0,12}?截止[^\n。；]{0,20}?'
         r'(\d{4})年(\d{1,2})月(\d{1,2})日', 3),
        (r'(\d{4})年(\d{1,2})月(\d{1,2})日[^\n。；]{0,15}?(?:开标|截止)', 3),
        (r'(?:投标|响应|报价)[^\n。；]{0,10}?截止[^0-9]{0,10}(\d{4})-(\d{1,2})-(\d{1,2})', 3),
    ]
    for p, ngroups in pats:
        m = re.search(p, text)
        if m:
            if ngroups == 3:
                y, mo, d = m.group(1), int(m.group(2)), int(m.group(3))
                return f'{y}-{mo:02d}-{d:02d}'
    return ''


def prescreen(title):
    if STAGE_DROP.search(title):
        return False
    if LCY_NOISE.search(title):
        return False
    if not FINANCE.search(title):
        return False
    if not POSITIVE.search(title):
        return False
    for kw in TITLE_EXCLUDE:
        if kw in title:
            return False
    return True


def _norm_title(s):
    return ' '.join((s or '').split())


def _load_seen_title_hashes():
    """加载跨日去重库的标题级 hash（'t:' 前缀），防 WAF 兜底重复上报历史条目。"""
    seen = set()
    f = OUT_DIR / 'seen_hashes.jsonl'
    if f.exists():
        for line in f.read_text(encoding='utf-8').splitlines():
            line = line.strip()
            if line.startswith('t:'):
                seen.add(line)
    return seen


def _load_rejected_projects():
    """已否决项目名集合（≥6字才参与匹配），避免兜底重报用户已砍条目。零模型。"""
    rej, f = set(), BASE / 'rejected_candidates.json'
    if f.exists():
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            for it in (data if isinstance(data, list)
                       else data.get('items') or []):
                p = _norm_title(it.get('project', ''))
                if len(p) >= 6:
                    rej.add(p)
        except Exception:
            pass
    return rej


def kc_api(payload):
    key = KC_KEY_FILE.read_text().strip()
    req = urllib.request.Request(
        f"{KC_GATEWAY}/api_route/gateway/{KC_TOOL_ID}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json",
                 "open-authorization": f"Bearer {key}"},
        method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode())


def kc_fallback(window_days=KC_WINDOW_DAYS):
    """WAF 兜底：快查 API 定向补采乐采云 niche。返回 (kept, total, calls, status)。

    与直连同口径预筛（阶段/后勤噪声、业务正向词、TITLE_EXCLUDE），招标主体由
    tender_names 组词锁定浙江区域银行；url_id 带 ccgp_lecaiyun 前缀者精确归因
    乐采云平台。每条给唯一链接（?n=url_id），避免去重库按首页 URL 折叠条目。
    """
    now = int(time.time())
    start = now - window_days * 86400
    em = re.compile(r'<[^>]+>')
    seen_t = _load_seen_title_hashes()
    rejected = _load_rejected_projects()
    kept, total, calls, status = [], 0, 0, "ok"
    for name in KC_FALLBACK_GROUPS:
        payload = {"type": "招标", "pub_time": start, "pub_time_1": now,
                   "registration_deadline_time": now,
                   "tender_names": name, "page": 1, "page_size": 50,
                   "orders": "pub_time desc"}
        try:
            r = kc_api(payload)
            calls += 1
        except Exception as e:
            status = f"error: {str(e)[:60]}"
            break
        items = (r.get('data') or {}).get('list') or r.get('list') or []
        if isinstance(items, dict):
            items = items.get('list') or []
        total += len(items)
        for it in items:
            title = em.sub('', str(it.get('title')
                                    or it.get('notice_title') or '')).strip()
            hl = it.get('highlight') or {}
            buyer = ''
            if isinstance(hl.get('tender_names'), list) and hl['tender_names']:
                buyer = em.sub('', str(hl['tender_names'][0]))
            if not buyer:
                buyer = str(it.get('tender_names') or it.get('tender_name')
                            or '')
            if not title:
                continue
            # 与直连同口径的标题预筛（FINANCE 由 tender_names 组词承担）
            if STAGE_DROP.search(title) or LCY_NOISE.search(title):
                continue
            if not FINANCE.search(buyer) or not POSITIVE.search(title):
                continue
            if any(kw in title for kw in TITLE_EXCLUDE):
                continue
            t_norm = _norm_title(title)
            th = 't:' + hashlib.md5(t_norm.encode('utf-8')).hexdigest()
            if th in seen_t:
                continue
            if any(rp in t_norm for rp in rejected):
                continue
            url_id = str(it.get('url_id') or '')
            pub = it.get('pub_time') or it.get('index_time') or now
            dl = it.get('registration_deadline_time')
            kept.append({
                'title': (f"{title}（{buyer}）"
                          if buyer and buyer not in title else title),
                'pubdate': datetime.fromtimestamp(pub).strftime('%Y-%m-%d'),
                'deadline': (datetime.fromtimestamp(dl).strftime('%Y-%m-%d')
                             if dl else ''),
                'url': (f"https://www.kuaicha365.com/?n={url_id}"
                        if url_id else "https://www.kuaicha365.com/"),
                'source': '快查',
                'channel': ('乐采云WAF兜底补采'
                            if url_id.startswith('ccgp_lecaiyun')
                            else '乐采云WAF兜底补采-他源'),
                'method': str(it.get('pubnote_type') or ''),
                'budget': it.get('deal_budget_money') or '',
                'url_id': url_id,
            })
        time.sleep(1)
    return kept, total, calls, status


def _ts_ms(it):
    ts = it.get('releasedAt') or it.get('createdAt') or 0
    if isinstance(ts, str):
        try:
            ts = datetime.fromisoformat(ts.replace('Z', '+00:00')).timestamp()
        except ValueError:
            ts = 0
    return ts * 1000 if ts and ts < 1e12 else ts


def main(kc_window=KC_WINDOW_DAYS):
    from playwright.sync_api import sync_playwright
    run_at = datetime.now().strftime('%Y%m%d_%H%M')
    out_path = OUT_DIR / f"new_items_lecaiyun_{run_at}.json"
    result = {"run_at": run_at, "sources": [], "new_items": []}
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(user_agent=UA)
        page = ctx.new_page()
        status, total, kept = "ok", 0, []
        try:
            page.goto('https://sourcing-lcy.lecaiyun.com/luban/xmcg',
                      timeout=60000)
            page.wait_for_timeout(8000)  # 过 WAF +  Lobby 首屏加载
            cutoff_ms = (datetime.now().timestamp()
                         - LOOKBACK_DAYS * 86400) * 1000
            # 2026-10-18 改造：弃用页内 fetch（WAF v2 会无限挂起 XHR），
            # 改 ctx.request（携带浏览器 cookie、可设硬超时），快速失败不拖死任务
            items = []
            for pn in range(1, PAGES + 1):
                try:
                    r = ctx.request.post(
                        'https://sourcing-lcy.lecaiyun.com'
                        '/announcement/lobby/queryPage',
                        data={'district': None,
                              'districtCodeFProvince': '900099',
                              'announcementTypes': TENDER_TYPES,
                              'pageNo': pn, 'pageSize': 99},
                        headers={'Content-Type': 'application/json'},
                        timeout=20000)
                    text = r.text()
                except Exception as e:
                    status = f"error_page{pn}: {str(e)[:60]}"
                    break
                if 'aliyun_waf' in text:
                    # WAF 挑战页：记录状态快速退出，避免挂死每日任务
                    status = "waf_blocked"
                    break
                try:
                    j = json.loads(text)
                except ValueError:
                    status = f"bad_json_page{pn}"
                    break
                data = (j.get('result') or {}).get('data') or []
                items.extend(data)
                # 列表按发布时间倒序：整页最旧一条已超出回看窗口即可停翻
                if len(data) < 99:
                    break
                if data and _ts_ms(data[-1]) < cutoff_ms:
                    break
            total = len(items)
            for it in items:
                ts = _ts_ms(it)
                if ts and ts < cutoff_ms:
                    continue
                title = (it.get('title') or '').strip()
                if not prescreen(title):
                    continue
                text = strip_html(it.get('content', ''))
                kept.append({
                    'title': title,
                    'pubdate': datetime.fromtimestamp(
                        ts / 1000).strftime('%Y-%m-%d') if ts else '',
                    'deadline': extract_deadline(text),
                    'url': DETAIL + it.get('encryptId', ''),
                    'source': '乐采云平台',
                    'channel': it.get('announcementTypeName') or '',
                })
            for k in kept:
                result["new_items"].append(k)
        except Exception as e:
            status = f"error: {str(e)[:80]}"
        result["sources"].append({"name": "乐采云-项目采购公告",
                                  "mode": "fetch", "status": status,
                                  "total_items": total,
                                  "new_count": len(kept)})
        if status == "waf_blocked":
            # 2026-10-19 周老师批准：WAF 持续拦截期间由快查 API 定向补采（≤6 次/天）
            try:
                fb, fb_total, fb_calls, fb_status = kc_fallback(kc_window)
                result["new_items"].extend(fb)
                result["sources"].append({
                    "name": "乐采云WAF兜底-快查API定向补",
                    "mode": "api", "status": fb_status,
                    "total_items": fb_total, "new_count": len(fb),
                    "quota_calls": fb_calls, "window_days": kc_window})
            except Exception as e:
                result["sources"].append({
                    "name": "乐采云WAF兜底-快查API定向补",
                    "mode": "api", "status": f"error: {str(e)[:60]}",
                    "total_items": 0, "new_count": 0, "quota_calls": 0})
        browser.close()
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=1),
                        encoding='utf-8')
    print(f"saved {out_path}")
    for s in result["sources"]:
        print(f"  {s['name']}: {s['status']} 共{s['total_items']}条 "
              f"keep{s['new_count']}")
    for it in result["new_items"]:
        print(" KEEP:", it['title'][:60], '| 截止', it.get('deadline', ''),
              '|', it.get('pubdate', ''))


if __name__ == '__main__':
    main()
