#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-20 决策组件批次执行：push_no 1/4/5 上板（id 218/219/220）。
来源：决策组件 submit（batch 2026-11-20）：1纳入(数据服务/可关注)、4纳入(财富管理/强烈建议投标)、
5纳入(风控合规,资产管理/建议投标)；2、3、6 不纳入仅回写 pending。
防串台：6 条台账 status=待确认，首次执行；标签按组件修改值（4 资产管理→财富管理，5 增资产管理）。
详情核验：
- push1 泸州银行：ql_vip_fetch+原公告——实为竞争性磋商（pending 误写公开招标，已纠）；
  预算55万元一致；递交/开启 2026-11-26 10:00；联系方式公告脱敏（李先生 0830-****796），挂【联系方式待补】。
- push4 徽银理财（快查详情 GN2026-13-9130）：预算168.04万元；报名截止2026-11-25 17:30（优先于
  开标2026-12-09 14:30，沿 id210 口径），开标写入 overview；代理电话 15255163136/0551-66061273。
- push5 杭州工商信托（快查详情 GSXT2026FWJC215）：竞争性磋商，预算100万元；报名截止2026-11-25 17:00。
  与板上 id212（GSXT2026HWJC216/公开招标/50万）编号、预算、方式均不同→独立项目，非同源重复。
"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":218,"company":"泸州银行","project":"泸州银行2026年-2028年企业征信数据服务（数据库）采购",
  "overview":"泸州银行2026年-2028年企业征信数据服务（数据库）采购，竞争性磋商（邀请4家供应商），预算55万元；响应文件递交截止暨开启2026-11-26 10:00。采购内容：企业征信数据服务（数据库），服务期2026-2028年。",
  "budget":"55万元","deadline":"2026-11-26 10:00","method":"竞争性磋商",
  "contact":"采购人联系人 李先生；电话 0830-****796（公告脱敏）【联系方式待补】",
  "region":"西南","province":"四川","tags":["数据服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-649091898.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":219,"company":"徽银理财","project":"徽银理财账户管理及统一清结算平台建设项目",
  "overview":"徽银理财账户管理及统一清结算平台建设项目公开招标（项目编号GN2026-13-9130），预算168.04万元；报名截止2026-11-25 17:30，开标2026-12-09 14:30（安徽合肥）。采购内容：账户管理及统一清结算平台建设。",
  "budget":"168.04万元","deadline":"2026-11-25 17:30","method":"公开招标",
  "contact":"代理单位电话 15255163136；0551-66061273",
  "region":"华东","province":"安徽","tags":["财富管理"],"rec":"🔥 ★★★ 强烈建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_yzcycgpt_b6122d99b285b541b960a6f5e2610507&type=AllBeacon","source":"快查","date":"2026-11-20"},
 {"id":220,"company":"杭州工商信托","project":"杭州工商信托债券投资信用评级模型管理平台建设项目",
  "overview":"杭州工商信托债券投资信用评级模型管理平台建设项目竞争性磋商（项目编号GSXT2026FWJC215），预算100万元；报名截止2026-11-25 17:00。采购内容：债券投资信用评级模型管理平台建设。（与板上 id212「债券投资信用评级模型采购项目 GSXT2026HWJC216/公开招标/50万」同代理同截止日，编号/预算/方式不同，为两项独立采购）",
  "budget":"100万元","deadline":"2026-11-25","method":"竞争性磋商",
  "contact":"代理 浙江省成套招标代理有限公司；电话 0571-87228017",
  "region":"华东","province":"浙江","tags":["风控合规","资产管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_zhaobidezb_d0feade7-085c-4b12-8503-f02b57998f59657000e9-b33e-4bff-b516-54ef03471c36&type=AllBeacon","source":"快查","date":"2026-11-20"},
]

for n in NEW:
    for t in n['tags']:
        assert t in VALID_TAGS, f"非法标签: {t} (id {n['id']})"

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

cores = ['企业征信数据服务', '账户管理及统一清结算', '信用评级模型管理平台']
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
print(f"OK: 3 条新增（id 218/219/220），总条目 {data['total']}")
