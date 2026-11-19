#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-03 11:06 周老师裁决 shortwin 批次 seek_1103_b2：仅15纳入，
投标建议改"可关注"；11-14不纳入。上板 id 131。
数据来源：暂存库 staging_20261102-1116.json item_6402（动态取值）。
联系方式/预算：千里马VIP详情页直读（qlm-tender 会话 2026-11-03 11:0x 重登后取数）。
真实业主更正：staging org 截断"重庆农村商业银行2027-202"→重庆农村商业银行（详情页 zhaoBiaoUnit 实证）。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

NEW = [
 {"id":131,"company":"重庆农村商业银行","project":"2027-2028年彭博金融终端数据服务采购项目",
  "overview":"重庆农村商业银行2027-2028年彭博金融终端数据服务采购项目单一来源采购公示，采购预算120,076.80美元，公示异议截止2026-11-09；采购部门陈女士023-61111138。",
  "budget":"120,076.80美元","deadline":"2026-11-09","method":"单一来源采购",
  "contact":"重庆农商行采购部 陈女士 023-61111138",
  "region":"西南","province":"重庆","tags":["数据服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"http://www.qianlima.com/zb/detail/20261102_643952883.html","source":"千里马招标网","date":"2026-11-03"},
]

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

keys = {(p['company'], p['project']) for p in ps}
urls = {p.get('url','') for p in ps}
for n in NEW:
    assert (n['company'], n['project']) not in keys, f"重复: {n['company']}{n['project']}"
    assert n['url'] not in urls, f"url重复: {n['url']}"
    assert n['id'] not in {p['id'] for p in ps}, f"id冲突: {n['id']}"
    assert '彭博' in n['project'], f"项目名异常: {n['project']}"

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)
data['version'] = 'v374'
data['date'] = '2026年11月03日'
data['timePeriod'] = '上午'
new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
html = html[:m.start()] + new_block + html[m.end():]
html = re.sub(r'(<title>[^<]*?)v\d+', r'\g<1>v374', html, count=1)
open('index.html', 'w', encoding='utf-8').write(html)
print(f"OK: 1条上板 id 131，板上共 {len(ps)} 条，version v374")
