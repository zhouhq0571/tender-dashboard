#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-16 看板候选批次（11 条裁决：纳入 9 条）上板：id 175-183
决策（周老师 09:33+09:36）：1、2、4、6、7-11纳入（4标签运维服务+财富管理；7-10及11标签改公司金融），3、5不纳入。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":175,"company":"建信理财有限责任公司","project":"交易所固定收益类证券估值数据服务项目供应商公开征集",
  "overview":"建信理财交易所固定收益类证券估值数据服务项目供应商公开征集，征集截止2026-11-18；公告未披露预算。",
  "budget":"-","deadline":"2026-11-18","method":"供应商征集","contact":"-",
  "region":"华南","province":"广东","tags":["数据服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_97f39ec1b8b145369d&type=AllBeacon","source":"快查","date":"2026-11-16"},
 {"id":176,"company":"建信理财有限责任公司","project":"中证估值数据服务项目供应商公开征集",
  "overview":"建信理财中证估值数据服务项目供应商公开征集，征集截止2026-11-18；公告未披露预算。",
  "budget":"-","deadline":"2026-11-18","method":"供应商征集","contact":"-",
  "region":"华南","province":"广东","tags":["数据服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_52bbf7fdeead408092&type=AllBeacon","source":"快查","date":"2026-11-16"},
 {"id":177,"company":"北京银行","project":"2027年代理贵金属交易系统、竞价做市商交易管理系统、积存金业务管理系统维保项目",
  "overview":"北京银行2027年代理贵金属交易系统、竞价做市商交易管理系统、积存金业务管理系统维保项目公开招标，投标截止2026-11-27 14:00；公告未披露预算。",
  "budget":"-","deadline":"2026-11-27 14:00","method":"公开招标","contact":"-",
  "region":"华北","province":"北京","tags":["运维服务","财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://login-cpm-xt.bankofbeijing.com.cn/cms/default/webfile/1ywgg1/20261113/1305986788522721280.html","source":"北京银行集中采购管理平台","date":"2026-11-16"},
 {"id":178,"company":"上海农商银行","project":"智能投研服务采购项目供应商征集",
  "overview":"上海农商银行智能投研服务采购项目供应商征集，征集截止2026-11-19 15:00；公告未披露预算。",
  "budget":"-","deadline":"2026-11-19 15:00","method":"供应商征集","contact":"-",
  "region":"华东","province":"上海","tags":["金市/资金/同业"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.mpaypass.com.cn/news/202611/14100330.html","source":"移动支付网","date":"2026-11-16"},
 {"id":179,"company":"广州农商银行","project":"综合支付系统项目",
  "overview":"广州农商银行综合支付系统项目公开招标，投标截止2026-11-23 09:00；公告未披露预算。",
  "budget":"-","deadline":"2026-11-23 09:00","method":"公开招标","contact":"-",
  "region":"华南","province":"广东","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.mpaypass.com.cn/news/202611/13185211.html","source":"移动支付网","date":"2026-11-16"},
 {"id":180,"company":"兴业银行","project":"数字人民币运营系统信创二期项目供应商征集调研",
  "overview":"兴业银行数字人民币运营系统信创二期项目供应商征集调研，征集截止2026-11-20 23:59；公告未披露预算。",
  "budget":"-","deadline":"2026-11-20 23:59","method":"供应商征集","contact":"-",
  "region":"华东","province":"福建","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.mpaypass.com.cn/news/202611/13185009.html","source":"移动支付网","date":"2026-11-16"},
 {"id":181,"company":"甘肃农商银行","project":"快捷支付数字化运营项目",
  "overview":"甘肃农商银行快捷支付数字化运营项目公开招标，投标截止2026-12-04 09:00；公告未披露预算。",
  "budget":"-","deadline":"2026-12-04 09:00","method":"公开招标","contact":"-",
  "region":"西北","province":"甘肃","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.mpaypass.com.cn/news/202611/13184353.html","source":"移动支付网","date":"2026-11-16"},
 {"id":182,"company":"建设银行深圳市分行","project":"数字人民币统一支付监管分行特色应用产品创新采购项目供应商征集",
  "overview":"建设银行深圳市分行数字人民币统一支付监管分行特色应用产品创新采购项目供应商征集，征集截止2026-11-18 17:00；公告未披露预算。",
  "budget":"-","deadline":"2026-11-18 17:00","method":"供应商征集","contact":"-",
  "region":"华南","province":"广东","tags":["公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.mpaypass.com.cn/news/202611/13183809.html","source":"移动支付网","date":"2026-11-16"},
 {"id":183,"company":"四川银行","project":"跨境业务系统采购项目",
  "overview":"四川银行跨境业务系统采购项目竞争性磋商（项目编号：四川银行集采〔2026〕138号），预算含税395万元/不含税373万元；采购跨境业务系统整体，2027年8月前具备投产上线条件，投产后平稳运行6个月验收，验收合格后一年免费驻场技术服务；门槛：近3年一个国际结算产品实施案例、具备多跨境业务通道整合建设能力，不接受联合体；文件获取11-13至11-19（150元/份，成都现场报名或网络报名），递交截止/开启2026-11-24 10:00（成都天府新谷）。",
  "budget":"395万元","deadline":"2026-11-24 10:00","method":"竞争性磋商","contact":"采购人 向老师 028-63289737；代理 四川公众项目咨询 陶冶张引 15708432070、19208055177",
  "region":"西南","province":"四川","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.mpaypass.com.cn/news/202611/13172814.html","source":"移动支付网","date":"2026-11-16"},
]

# 标签白名单断言
for n in NEW:
    for t in n['tags']:
        assert t in VALID_TAGS, f"非法标签: {t} (id {n['id']})"

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

keys = {(p['company'], p['project']) for p in ps}
urls = {p.get('url','') for p in ps}
for n in NEW:
    assert (n['company'], n['project']) not in keys, f"重复: {n['company']}{n['project']}"
    assert n['url'] not in urls, f"url重复: {n['url']}"
ids = {p['id'] for p in ps}
for n in NEW:
    assert n['id'] not in ids, f"id冲突: {n['id']}"

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)

new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
out = html[:m.start()] + new_block + html[m.end():]
open('index.html', 'w', encoding='utf-8').write(out)
print(f"OK: {len(NEW)}条上板 id 175-183，总条目 {data['total']}，total 已同步")
