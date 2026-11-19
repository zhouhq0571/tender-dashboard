#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-19 组件决策批次（15 条：纳入 13、不纳入 2）上板 id 198-209。
来源：周老师 10:36 组件 submit（run 卡死已取消，主对话接管执行）。
push_no 14（农行浙江银法智管）上游链接缺失暂缓，见汇报。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":198,"company":"兴业银行","project":"2027年理财数据服务项目",
  "overview":"兴业银行2027年理财数据服务项目公开招标（招标编号FJZT-2026-13032），预算33.25万元，投标截止2026-12-09；文件获取及递交详见招标公告。",
  "budget":"33.25万元","deadline":"2026-12-09","method":"公开招标","contact":"代理 福建省中通通信有限公司；联系人 张先生；电话 18060753032；邮箱 jiangjiyu.gyl@chinaccs.cn",
  "region":"华东","province":"福建","tags":["数据服务"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-648722704.html","source":"千里马招标网","date":"2026-11-19"},
 {"id":199,"company":"中银理财","project":"2026年网络安全等级保护测评及信创技术支持服务采购项目",
  "overview":"中银理财2026年网络安全等级保护测评及信创技术支持服务采购项目（招标编号BOCWM-JC-2026026），报名截止2026-11-27，投标截止2026-11-30；公告未披露预算。",
  "budget":"-","deadline":"2026-11-30","method":"公开招标","contact":"代理 北京国际贸易有限公司；联系人 苑经理；电话 010",
  "region":"华北","province":"北京","tags":["风控合规","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648980116.html","source":"千里马招标网","date":"2026-11-19"},
 {"id":200,"company":"兴银理财","project":"投资风控项目五期供应商征集调研",
  "overview":"兴业银行关于兴银理财投资风控项目五期供应商征集调研，报名截止2026-11-25 23:59；征集调研不披露预算。",
  "budget":"-","deadline":"2026-11-25","method":"供应商征集","contact":"兴业银行 项目联系 (021)20567666-671024",
  "region":"华东","province":"福建","tags":["资产管理","风控合规"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_d287e69b16b744d8b1233992b7367fc7&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":201,"company":"兴业银行","project":"企业年金受托管理项目三期（企业年金转移接续）供应商征集调研",
  "overview":"兴业银行关于企业年金受托管理项目三期（企业年金转移接续）供应商征集调研，报名截止2026-11-25 23:59；征集调研不披露预算。",
  "budget":"-","deadline":"2026-11-25","method":"供应商征集","contact":"兴业银行 项目联系 (021)20567666-671024",
  "region":"华东","province":"福建","tags":["大模型应用"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_e6edf4761c0c4d58a0548646b5e01152&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":202,"company":"兴业银行","project":"意图平台工程项目供应商征集调研",
  "overview":"兴业银行关于意图平台工程项目供应商征集调研，报名截止2026-11-25 23:59；征集调研不披露预算。",
  "budget":"-","deadline":"2026-11-25","method":"供应商征集","contact":"兴业银行 项目联系 (021)20567666-671024",
  "region":"华东","province":"福建","tags":["大模型应用"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_d8d9f09e359e488e8acbbfd7d77d4a82&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":203,"company":"建设银行四川省分行","project":"南充市高坪区中医医院综合支付结算系统项目",
  "overview":"建设银行四川省分行南充市高坪区中医医院综合支付结算系统项目公开招标（项目编号JYZX-ZB-SC-2026-00057），预算84.5万元；报名截止2026-11-26 17:00，开标2026-12-10 10:00。",
  "budget":"84.5万元","deadline":"2026-12-10 10:00","method":"公开招标","contact":"代理 建银工程咨询有限责任公司；电话 028-86766001",
  "region":"西南","province":"四川","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_f280acd10dda4e248a20e7c9454718a4&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":204,"company":"广银理财","project":"IT桌面运维外包服务项目",
  "overview":"广银理财IT桌面运维外包服务项目（项目编号CGB-GYLC-2026-012），预算118.35万元，报名截止2026-11-25 17:30，开标2026-12-03 09:30。",
  "budget":"118.35万元","deadline":"2026-12-03 09:30","method":"公开招标","contact":"代理 上海同济工程项目管理咨询有限公司；电话 021-68298828",
  "region":"华东","province":"上海","tags":["运维服务","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_8bc90c1fc1764ac59ca0175a5c3ca3f3&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":205,"company":"广银理财","project":"IT运维外包服务采购项目",
  "overview":"广银理财IT运维外包服务采购项目（项目编号CGB-GYLC-2026-013），报名截止2026-11-25 17:30，开标2026-12-04 09:30；公告未披露预算。",
  "budget":"-","deadline":"2026-12-04 09:30","method":"公开招标","contact":"代理 上海召源商务咨询有限公司；电话 021-68298828",
  "region":"华东","province":"上海","tags":["运维服务","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=guuangfayinghang_33gMeHlvR4wpVUXRTcXRkD&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":206,"company":"青银理财","project":"2027年技术支持人力外包项目",
  "overview":"青银理财2027年技术支持人力外包项目（项目编号QDHX-QY2026322），预算29.66万元，报名截止2026-11-25 16:30，开标2026-11-30 09:30。",
  "budget":"29.66万元","deadline":"2026-11-30 09:30","method":"公开招标","contact":"代理 青岛鸿翔招标有限公司；电话 0532-66015830",
  "region":"华东","province":"山东","tags":["人力外包","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_zhongguozbfwpt_code_8c61dfc8f99aa4998317fe6a643ad40a&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":207,"company":"华夏理财","project":"2026年ESG可持续投资外部数据引入项目供应商征集",
  "overview":"华夏理财2026年ESG可持续投资外部数据引入项目供应商征集，报名截止2026-11-24；征集公告未披露预算。",
  "budget":"-","deadline":"2026-11-24","method":"供应商征集","contact":"联系人 赵女士；邮箱 hxlcjzcg@hxb.com.cn",
  "region":"华北","province":"北京","tags":["数据服务","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648706597.html","source":"千里马招标网","date":"2026-11-19"},
 {"id":208,"company":"中海信托","project":"国产数据库采购",
  "overview":"中海信托国产数据库采购（项目编号ZHXT-2026-085-XJ-KX/01，公开询价），报名截止2026-11-24，开标2026-11-25 09:00；公告未披露预算。",
  "budget":"-","deadline":"2026-11-25 09:00","method":"询价采购","contact":"中海信托 招标单位电话 02123191962",
  "region":"华东","province":"上海","tags":["数据服务","信创"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_bidcnooc_7b93da462bba3256cee9c56e5f7582cb&type=AllBeacon","source":"快查","date":"2026-11-19"},
 {"id":209,"company":"杭州工商信托","project":"信用风险舆情数据采购项目",
  "overview":"杭州工商信托信用风险舆情数据采购项目竞争性磋商（项目编号GSXT2026HWJC217），预算50万元，报名截止2026-11-25 17:00，开标2026-11-25 09:00。",
  "budget":"50万元","deadline":"2026-11-25 09:00","method":"竞争性磋商","contact":"代理 浙江省成套招标代理有限公司；电话 0571-87228017",
  "region":"华东","province":"浙江","tags":["数据服务","风控合规"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_zhaobidezb_5587cd49-f11f-4b1f-bfc4-9511bb929099886b0b9f-f260-452e-b823-940832c3f26c&type=AllBeacon","source":"快查","date":"2026-11-19"},
]

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
print(f"OK: {len(NEW)}条上板 id 198-209，总条目 {data['total']}，total 已同步")
