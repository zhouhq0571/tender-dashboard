#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-19 decide.html 决策补执行：push_no 14（农行浙江银法智管，第二次）上板 id 210。
来源：周老师 decide.html 指令「【候选决策 2026-11-19】14纳入（标签：公司金融）」。
补链：千里马 VIP bid-648885175（真实公告），报名截止 2026-11-25 优先于开标 2026-12-09。
防串台：push_no 14 台账 status=待确认（10:36 批次暂缓项），本条为首次执行。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":210,"company":"农业银行浙江省分行","project":"银法智管平台与\"一张网\"系统支持服务项目（第二次）",
  "overview":"农业银行浙江省分行银法智管平台与\"一张网\"系统支持服务项目（第二次）公开招标（招标编号A19H999S26105001），预算81万元（不含税）；招标文件发售至2026-11-25（报名截止优先），投标截止2026-12-09 09:30。采购内容：银法智管平台与\"一张网\"系统技术支持服务，确保两系统对接顺畅，促进我行系统与法院系统同步升级优化，服务期2027-01-01至2029-12-31。",
  "budget":"81万元","deadline":"2026-11-25","method":"公开招标",
  "contact":"代理 浙江豪圣建设项目管理有限公司；联系人 赵浣岗、曹剑斌、陈敏娇；电话 0571-56329673、18957165500",
  "region":"华东","province":"浙江","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648885175.html","source":"千里马招标网","date":"2026-11-19"},
]

for n in NEW:
    for t in n['tags']:
        assert t in VALID_TAGS, f"非法标签: {t} (id {n['id']})"

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

# 防串台：project 精确相等即拦截
core = '银法智管'
assert not any(core in p['project'] for p in ps), "板上已有银法智管条目，禁止重复上板"
assert all(n['url'] not in p.get('url','') for p in ps for n in NEW), "url 重复"
assert all(n['id'] not in {p['id'] for p in ps} for n in NEW), "id 冲突"

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)

new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
out = html[:m.start()] + new_block + html[m.end():]
open('index.html', 'w', encoding='utf-8').write(out)
print(f"OK: id 210 上板，总条目 {data['total']}")
