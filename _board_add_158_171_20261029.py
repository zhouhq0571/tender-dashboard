#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-29 看板候选批次（14条，周老师"同意，继续"全采纳）上板：id 158-171
结构化改 index.html（tender-data JSON），append 后按 config.sort_key 重排，id 不变。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

NEW = [
 {"id":158,"company":"威海银行","project":"网贷平台信创改造项目",
  "overview":"威海银行网贷平台信创改造项目公开招标，投标截止2026-11-19；公告未披露预算。",
  "budget":"-","deadline":"2026-11-19","method":"公开招标","contact":"-",
  "region":"华东","province":"山东","tags":["信创"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641801840.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":159,"company":"长安银行","project":"内部资金转移定价系统（新建）项目",
  "overview":"长安银行内部资金转移定价系统（新建）项目公开招标，投标截止2026-11-16；公告未披露预算。",
  "budget":"-","deadline":"2026-11-16","method":"公开招标","contact":"-",
  "region":"西北","province":"陕西","tags":["金市/资金/同业"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641947148.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":160,"company":"福建海峡银行","project":"自动化运维平台信创改造项目",
  "overview":"福建海峡银行自动化运维平台信创改造项目公开招标，投标截止2026-11-16；公告未披露预算。",
  "budget":"-","deadline":"2026-11-16","method":"公开招标","contact":"-",
  "region":"华东","province":"福建","tags":["信创","运维服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-641760112.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":161,"company":"中国银行青岛市分行","project":"2026年软网控平台采购项目",
  "overview":"中国银行青岛市分行2026年软网控平台采购项目公开招标，预算33.9万元，投标截止2026-11-16。",
  "budget":"33.9万元","deadline":"2026-11-16","method":"公开招标","contact":"-",
  "region":"华东","province":"山东","tags":["运维服务"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641638648.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":162,"company":"张家口银行","project":"2026年大数据基础平台软硬件扩容项目",
  "overview":"张家口银行2026年大数据基础平台软硬件扩容项目公开招标，投标截止2026-11-17；公告未披露预算。",
  "budget":"-","deadline":"2026-11-17","method":"公开招标","contact":"-",
  "region":"华北","province":"河北","tags":["数据平台"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642043869.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":163,"company":"兴业银行杭州分行","project":"浙江省银行非税收缴及结算平台信创软件采购项目",
  "overview":"兴业银行杭州分行浙江省银行非税收缴及结算平台信创软件采购项目供应商征集，征集截止2026-11-03。",
  "budget":"-","deadline":"2026-11-03","method":"供应商征集","contact":"-",
  "region":"华东","province":"浙江","tags":["信创"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642339301.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":164,"company":"北京农商银行","project":"作业外包处理系统信创改造项目",
  "overview":"北京农商银行作业外包处理系统信创改造项目供应商征集，征集截止2026-10-30。",
  "budget":"-","deadline":"2026-10-30","method":"供应商征集","contact":"-",
  "region":"华北","province":"北京","tags":["信创","人力外包"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-641709820.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":165,"company":"浦发银行苏州分行","project":"2026年EAST校验系统项目",
  "overview":"浦发银行苏州分行2026年EAST校验系统项目供应商征集，征集截止2026-10-30。",
  "budget":"-","deadline":"2026-10-30","method":"供应商征集","contact":"-",
  "region":"华东","province":"江苏","tags":["数据服务"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642592052.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":166,"company":"四川天府银行","project":"新一代国际业务平台系统建设项目（第三次）",
  "overview":"四川天府银行新一代国际业务平台系统建设项目（第三次）公开招标，预算220万元，投标截止2026-11-09。",
  "budget":"220万元","deadline":"2026-11-09","method":"公开招标","contact":"-",
  "region":"西南","province":"四川","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641849100.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":167,"company":"北京农商银行","project":"2026年互联网域名系统更新改造项目",
  "overview":"北京农商银行2026年互联网域名系统更新改造项目供应商征集，征集截止2026-10-30。",
  "budget":"-","deadline":"2026-10-30","method":"供应商征集","contact":"-",
  "region":"华北","province":"北京","tags":["运维服务"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-641715932.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":168,"company":"青岛农商银行","project":"理财H5及前置系统业务优化及信创改造项目",
  "overview":"青岛农商银行理财H5及前置系统业务优化及信创改造项目公开招标，预算67万元，投标截止2026-11-04。",
  "budget":"67万元","deadline":"2026-11-04","method":"公开招标","contact":"-",
  "region":"华东","province":"山东","tags":["信创","财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642295979.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":169,"company":"青岛农商银行","project":"互联网综合服务平台系统信创改造等四项需求项目",
  "overview":"青岛农商银行互联网综合服务平台系统信创改造等四项需求项目公开招标，预算55.8万元，投标截止2026-11-03。",
  "budget":"55.8万元","deadline":"2026-11-03","method":"公开招标","contact":"-",
  "region":"华东","province":"山东","tags":["信创"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642295987.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":170,"company":"建行山东省分行","project":"潍坊分行山东第二医科大学智慧校园财资数据基座与运营治理平台金融服务一体化建设项目",
  "overview":"建行山东省分行潍坊分行山东第二医科大学智慧校园财资数据基座与运营治理平台金融服务一体化建设项目供应商征集，征集截止2026-11-01。",
  "budget":"-","deadline":"2026-11-01","method":"供应商征集","contact":"-",
  "region":"华东","province":"山东","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642187920.html","source":"千里马招标网","date":"2026-10-29"},
 {"id":171,"company":"浦银理财","project":"金融信创技术支撑服务采购",
  "overview":"浦银理财金融信创技术支撑服务采购供应商征集，公示截止2026-11-02。",
  "budget":"-","deadline":"2026-11-02","method":"供应商征集","contact":"-",
  "region":"华东","province":"上海","tags":["信创","财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-642575812.html","source":"千里马招标网","date":"2026-10-29"},
]

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

# 查重：company+project 与 url
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
print(f"OK: {len(NEW)}条上板 id 158-171，总条目 {data['total']}，total 已同步")
