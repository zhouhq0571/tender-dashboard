#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-16 周老师裁决 seek_1116_b1~b5：纳入19（3/4/8/9/13/15/17/18/27/28/30/32/34/38/40/42/43/47/48），其余31条不纳入。
数据一律从暂存库 item 动态取（URL/金额/截止日期/联系方式/区域），周老师改判 tags/rec 合入；板上 id 184-202。
动作链：落板→fix_sort→health_check→deploy（本脚本只落板）。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

STAGING = '/Users/zhouhq/Documents/kimi/Workspaces/金融要闻周报/staging_20261102-1116.json'

# 周老师终判：no -> (tags, advice)
FINAL = {
    3:  ('大模型应用', '建议投标'),
    4:  ('信创、财富管理', '建议投标'),
    8:  ('公司金融', '可关注'),
    9:  ('公司金融', '可关注'),
    13: ('财富管理', '建议投标'),
    15: ('大模型应用', '可关注'),
    17: ('数据服务', '建议投标'),
    18: ('信创、公司金融', '建议投标'),
    27: ('资产管理', '建议投标'),
    28: ('财富管理', '建议投标'),
    30: ('财富管理', '建议投标'),
    32: ('大模型应用、财富管理', '建议投标'),
    34: ('人力外包、公司金融', '可关注'),
    38: ('财富管理、金市/资金/同业', '建议投标'),
    40: ('公司金融', '建议投标'),
    42: ('人力外包、金市/资金/同业', '可关注'),
    43: ('大模型应用、财富管理', '建议投标'),
    47: ('资产管理', '建议投标'),
    48: ('信创、财富管理', '建议投标'),
}

# 大区映射（config.PROVINCE_ORDER 分段）
REGION_OF = {}
for r, provs in {'东北': ['黑龙江','吉林','辽宁'],
                 '华北': ['内蒙古','北京','天津','河北','山西'],
                 '西北': ['陕西','甘肃','宁夏','青海','新疆'],
                 '华东': ['山东','江苏','浙江','安徽','福建','江西','上海'],
                 '华中': ['河南','湖北','湖南'],
                 '西南': ['重庆','四川','贵州','云南','西藏'],
                 '华南': ['广东','广西','海南']}.items():
    for p in provs:
        REGION_OF[p] = r

REC = {'建议投标': '⭐ ★★☆ 建议投标', '可关注': '👀 ★☆☆ 可关注'}

# ---- 从暂存库动态取数（按 cand50 的 url 匹配）----
cand50 = json.load(open('/tmp/cand50.json'))
staging = json.load(open(STAGING))
sitems = staging if isinstance(staging, list) else staging['items']
by_url = {x.get('source_url'): x for x in sitems if x.get('source_url')}

NEW = []
missing = []
for no in sorted(FINAL):
    c = next(r for r in cand50 if r['no'] == no)
    it = by_url.get(c['url'])
    if not it:
        missing.append((no, c['url'])); continue
    # 二次核对：编号与暂存库条目 assert 项目名关键词（防误落）
    assert c['project'][:10] == it['project'][:10] and c['project'][-10:] == it['project'][-10:], \
        f'#{no} 项目名不匹配: {c["project"]} vs {it["project"]}'
    assert it['type'] == 'bid_tender', f'#{no} 非在招标'
    prov = (it.get('region') or '-').split('-')[0]
    amt = it.get('amount')
    budget = (f'{amt}万元' if isinstance(amt, (int, float)) else (amt or '-'))
    dl = it['bid_deadline']
    NEW.append({
        'company': it['org'], 'project': it['project'],
        'overview': f"{it['project'].split('公司')[-1]}，截止{dl}，预算{ ('未公布' if budget=='-' else budget) }。详见千里马招标网公告。",
        'budget': budget, 'deadline': dl,
        'method': it.get('procurement_type') or '其他',
        'contact': it.get('contact') or '公告未披露',
        'region': REGION_OF.get(prov, '华东'), 'province': prov,
        'tags': [t for t in FINAL[no][0].split('、') if t],
        'rec': REC[FINAL[no][1]],
        'url': it['source_url'], 'source': '千里马招标网', 'date': '2026-11-16',
    })
assert not missing, f'暂存库缺匹配: {missing}'
assert len(NEW) == 19

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']
next_id = max(p['id'] for p in ps) + 1

def core(pj, comp):
    """剥项目名首部的机构前缀（org前缀污染会致15字前缀撞车，11-16实证），再取核心段比较"""
    for pre in (comp, comp.replace('股份有限公司', ''), comp.replace('有限责任公司', ''), comp.replace('有限公司', '')):
        if pre and pj.startswith(pre):
            return pj[len(pre):]
    return pj

keys = {(p['company'], p['project']) for p in ps}
for i, n in enumerate(NEW):
    n['id'] = next_id + i
    assert len(n['project']) >= 8, n['id']
    if (n['company'], n['project']) in keys:
        print('SKIP dup:', n['id'], n['project']); continue
    nc = core(n['project'], n['company'])
    if any(len(core(p['project'], p['company'])) >= 8 and
           (nc[:15] == core(p['project'], p['company'])[:15]) for p in ps):
        print('ABORT 疑似串台:', n['id'], n['project']); sys.exit(1)
    ps.append(n)

data['projects'] = sorted(ps, key=sort_key)
out = json.dumps(data, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(html[:m.start(2)] + out + html[m.end(2):])
print(f'OK 落板 {len(NEW)} 条（id {next_id}-{next_id+len(NEW)-1}），板上总数 = {len(data["projects"])}')
for n in NEW:
    print(' ', n['id'], n['company'][:12], '|', n['project'][:32], '|', n['deadline'], '|', '、'.join(n['tags']), '|', n['rec'][:1])
