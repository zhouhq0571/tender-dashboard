#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-03 10:49 周老师裁决 shortwin 批次 seek_1103_b1：7、8、10 纳入
（8业务标签改"公司金融"、10改"财富管理"），其余不纳入。上板 id 128-130。
数据来源：暂存库 staging_20261102-1116.json item_6289/6304/6319（动态取值，URL/截止/金额不回填手填）。
联系方式：千里马VIP详情页直读（qlm-tender 会话，2026-11-03 11:xx 重登后取数）。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

NEW = [
 {"id":128,"company":"北京农商银行","project":"理财销售系统信息披露文件功能优化项目",
  "overview":"北京农商银行理财销售系统信息披露文件功能优化项目供应商征集，征集截止2026-11-05；通过行方采购平台在线报名，公告正文未披露电话。",
  "budget":"-","deadline":"2026-11-05","method":"供应商征集","contact":"-",
  "region":"华北","province":"北京","tags":["财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-643309940.html","source":"千里马招标网","date":"2026-11-03"},
 {"id":129,"company":"建设银行徐州分行","project":"徐州地铁数字人民币应用改造信息化项目",
  "overview":"建设银行徐州分行徐州地铁数字人民币应用改造信息化项目供应商征集，征集截止2026-11-06；建行采购平台服务热线400-918-1908。",
  "budget":"-","deadline":"2026-11-06","method":"供应商征集","contact":"建行采购平台 400-918-1908",
  "region":"华东","province":"江苏","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-643000105.html","source":"千里马招标网","date":"2026-11-03"},
 {"id":130,"company":"上海农商银行","project":"中登智能查询系统二代POC",
  "overview":"上海农商银行中登智能查询系统二代POC供应商征集，征集截止2026-11-06；行方集中采购中心021-61899383。",
  "budget":"-","deadline":"2026-11-06","method":"供应商征集","contact":"上海农商银行集中采购中心 021-61899383",
  "region":"华东","province":"上海","tags":["财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642953773.html","source":"千里马招标网","date":"2026-11-03"},
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
    # 项目名关键词防串台
    assert any(kw in n['project'] for kw in ('信息披露','数字人民币','中登')), f"项目名异常: {n['project']}"

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)
# 版本与日期回写
data['version'] = 'v373'
data['date'] = '2026年11月03日'
data['timePeriod'] = '上午'
new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
open('index.html', 'w', encoding='utf-8').write(html[:m.start()] + new_block + html[m.end():])
print(f"OK: 3条上板 id 128-130，板上共 {len(ps)} 条，version v373")
