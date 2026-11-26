#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-26 决策批次执行：push_no 1/4/5/6/7 上板（id 88-92）。
来源：周老师 RC 端【候选决策 2026-11-26】：1纳入(资产管理,运维服务)、4纳入(公司金融)、
5纳入(公司金融)、6纳入(财富管理/强烈建议投标)、7纳入(资产管理,人力外包)；2/3/8 不纳入仅回写。
防串台：8 条台账 status=待确认，首次执行。
详情核验（快查详情页+千里马原文 1 轮抓取全部命中）：
- push1 建信理财：供应商征集；报名截止2026-12-01（千里马原文"即日起至12月1日00:00"）；
  预算未披露；联系 采购陈老师0755-****8612/需求刘老师0755-****8269（千里马平台打码）。
- push4 建行泰州分行：公开招标；报名截止2026-12-02 12:00；项目地区江苏省；预算/联系未披露。
- push5 建行广西区分行：供应商征集；报名截止2026-12-01 22:00；联系 招标单位0778-2112196；项目地区广西。
- push6 西藏信托：公开招标 编号0701-2640NM03C056；预算91.00万→91万元；报名截止2026-12-02 17:00；
  代理 中技国际招标有限公司 010-81168099；项目实施地北京。
- push7 建信信托：公开招标 编号N_TRBB260049/01；报名截止2026-12-02 16:00；项目地区安徽合肥庐阳区；
  联系 招标单位010-83142309/010-83142265；代理 中信国际招标有限公司。
"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":88,"company":"建信理财","project":"建信理财2026-2027年度建行云运维支持服务项目供应商公开征集",
  "overview":"建信理财有限责任公司2026-2027年度建行云运维支持服务项目供应商公开征集，预算未披露；报名自公告起至2026-12-01。采购内容：建行云运维支持服务（云环境运维保障，2026-2027年度）。报名：邮件至wealthccb.com邮箱+龙集采平台注册。",
  "budget":"-","deadline":"2026-12-01","method":"供应商征集",
  "contact":"采购 陈老师 0755-****8612（千里马打码）；需求 刘老师 0755-****8269（千里马打码）",
  "region":"华北","province":"北京","tags":["资产管理","运维服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-651205222.html","source":"千里马招标网","date":"2026-11-26"},
 {"id":89,"company":"建设银行泰州分行","project":"泰州市住建局小区公共收益资金服务系统项目",
  "overview":"中国建设银行股份有限公司泰州分行泰州市住建局小区公共收益资金服务系统采购项目公开招标，预算未披露；报名截止2026-12-02 12:00（项目地区江苏省）。采购内容：小区公共收益资金服务系统（住建局场景资金管理系统开发/采购）。",
  "budget":"-","deadline":"2026-12-02 12:00","method":"公开招标",
  "contact":"详情页未披露【联系方式待补】",
  "region":"华东","province":"江苏","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_9532488a995940b69ebb63db2e494f68&type=AllBeacon","source":"快查","date":"2026-11-26"},
 {"id":90,"company":"建设银行广西区分行","project":"河池学院宿舍、工资、财务管理及一卡通系统优化升级项目软硬件采购供应商征集",
  "overview":"中国建设银行股份有限公司广西区分行河池学院宿舍、工资、财务管理及一卡通系统优化升级项目软件、硬件产品采购项目供应商征集，预算未披露；报名截止2026-12-01 22:00。采购内容：高校宿舍/工资/财务管理及一卡通系统优化升级的软硬件产品。",
  "budget":"-","deadline":"2026-12-01 22:00","method":"供应商征集",
  "contact":"招标单位 0778-2112196",
  "region":"华南","province":"广西","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_60f9d5fae9f14e0595d9661626d34957&type=AllBeacon","source":"快查","date":"2026-11-26"},
 {"id":91,"company":"西藏信托","project":"西藏信托资产配置系统建设项目",
  "overview":"西藏信托有限公司资产配置系统建设项目公开招标（项目编号0701-2640NM03C056），预算91万元；报名2026-11-25 09:00至2026-12-02 17:00，开标2026-12-07 09:30（北京）。采购内容：资产配置系统建设（财富/资管业务方向核心系统）。",
  "budget":"91万元","deadline":"2026-12-02 17:00","method":"公开招标",
  "contact":"代理 中技国际招标有限公司；电话 010-81168099",
  "region":"华北","province":"北京","tags":["财富管理"],"rec":"🔥 ★★★ 强烈建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_zhongguozbfwpt_code_b8f926a7ecdb00ec2bbdb043a5a612df&type=AllBeacon","source":"快查","date":"2026-11-26"},
 {"id":92,"company":"建信信托","project":"建信信托2027-2028年信息技术开发服务采购项目",
  "overview":"建信信托有限责任公司2027-2028年信息技术开发服务采购项目公开招标（项目编号N_TRBB260049/01），预算未披露；报名2026-11-25 09:00至2026-12-02 16:00，开标2026-12-16 09:00。采购内容：信息技术开发服务（年度开发资源采购，项目地区安徽合肥庐阳区）。",
  "budget":"-","deadline":"2026-12-02 16:00","method":"公开招标",
  "contact":"招标单位 010-83142309 / 010-83142265；代理 中信国际招标有限公司",
  "region":"华东","province":"安徽","tags":["资产管理","人力外包"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=jianhangcj_2125429416247726080&type=AllBeacon","source":"快查","date":"2026-11-26"},
]

for n in NEW:
    for t in n['tags']:
        assert t in VALID_TAGS, f"非法标签: {t} (id {n['id']})"

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

cores = ['建行云运维支持服务', '公共收益资金服务系统', '河池学院宿舍', '资产配置系统建设', '信息技术开发服务采购']
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
print(f"OK: 5 条新增（id 88-92），总条目 {data['total']}")
