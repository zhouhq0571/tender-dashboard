#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-25 决策组件批次执行：push_no 2/3/7 上板（id 85/86/87）。
来源：「标讯晨报·决策一体」组件 submit（batch 2026-11-25）：2纳入(金市/资金/同业/可关注)、
3纳入(公司金融/建议投标)、7纳入(信创,风控合规/建议投标)；1、4、5、6、8 不纳入仅回写 pending。
防串台：8 条台账 status=待确认，首次执行，无撤回。
详情核验（快查详情页 1 次抓取全部命中）：
- push2 中国银行（编号2640STC75132）：公开招标；报名截止2026-12-08 17:00（与 pending 一致，
  报名截止优先于开标2026-12-16 09:30，沿 id210 口径）；代理 中宝招标(北京)有限公司，
  详情页未披露电话 → contact 挂代理机构名+【联系方式待补】。
- push3 建设银行湖南省分行（编号N_HN260231/01）：预算350.00万→归一350万元；
  报名截止2026-12-02 17:00（同 pending）；联系方式 招标单位 0731-84419053；
  代理 建银工程咨询有限责任公司。快查页"项目地区：海南省"与招采单位湖南省分行矛盾，
  按招采单位归属 华中/湖南。
- push7 北银理财（编号0773-2640GNOCFWCS3305）：竞争性磋商；预算30.00万→归一30万元；
  报名截止2026-11-30 16:00（同 pending）；代理 中金招标有限责任公司 18701390392。
"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":85,"company":"中国银行","project":"中国银行金融工具估值模型和标准初始保证金模型验证咨询项目",
  "overview":"中国银行股份有限公司金融工具估值模型和标准初始保证金模型验证咨询项目公开招标（项目编号2640STC75132），预算未披露；报名2026-11-25 09:00至2026-12-08 17:00，开标2026-12-16 09:30（北京）。采购内容：金融工具估值模型和标准初始保证金（SIMM）模型验证咨询。",
  "budget":"-","deadline":"2026-12-08 17:00","method":"公开招标",
  "contact":"代理 中宝招标(北京)有限公司【联系方式待补】",
  "region":"华北","province":"北京","tags":["金市/资金/同业"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_d22e005280364633903355354c44b747&type=AllBeacon","source":"快查","date":"2026-11-25"},
 {"id":86,"company":"建设银行湖南省分行","project":"湖南**股份有限公司财资一体化平台开发项目软件开发服务采购",
  "overview":"湖南**股份有限公司财资一体化平台开发项目软件开发服务采购公开招标（项目编号N_HN260231/01），预算350万元；报名2026-11-24 09:00至2026-12-02 17:00，开标2026-12-16 09:30。采购内容：财资一体化平台开发项目软件开发服务（建行湖南省分行集采）。",
  "budget":"350万元","deadline":"2026-12-02 17:00","method":"公开招标",
  "contact":"招标单位电话 0731-84419053；代理 建银工程咨询有限责任公司",
  "region":"华中","province":"湖南","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=jianhangcj_2125134140510466048&type=AllBeacon","source":"快查","date":"2026-11-25"},
 {"id":87,"company":"北银理财","project":"北银理财风险底座国产化升级建设项目",
  "overview":"北银理财有限责任公司风险底座国产化升级建设项目竞争性磋商（项目编号0773-2640GNOCFWCS3305），预算30万元；报名2026-11-24至2026-11-30 16:00，开标2026-12-07 09:30（北京）。采购内容：风险底座国产化升级建设（信创改造+风控合规方向）。",
  "budget":"30万元","deadline":"2026-11-30 16:00","method":"竞争性磋商",
  "contact":"代理 中金招标有限责任公司；电话 18701390392",
  "region":"华北","province":"北京","tags":["信创","风控合规"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_c6995d41ef454648bf1c3b1b3fc76374&type=AllBeacon","source":"快查","date":"2026-11-25"},
]

for n in NEW:
    for t in n['tags']:
        assert t in VALID_TAGS, f"非法标签: {t} (id {n['id']})"

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

cores = ['金融工具估值模型', '财资一体化平台', '风险底座国产化']
for core in cores:
    assert not any(core in p['project'] for p in ps), f"板上已有 {core}，禁止重复上板"
assert all(n['url'] not in p.get('url','') for p in ps for n in NEW), "url 重复"
assert all(n['id'] not in {p['id'] for p in ps} for n in NEW), "id 冲突"

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)

new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
out = html[:m.start()] + new_block + html[m.end():]
open('index.html', 'w', encoding='utf-8').write(out)
print(f"OK: 3 条新增（id 85/86/87），总条目 {data['total']}")
