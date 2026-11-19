#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-18 看板候选批次（13 条裁决：纳入 9 条）上板：id 189-197
决策（周老师 13:26）：2、3纳入且+公司金融；6-12纳入且+资产管理；10删财富管理；10、12建议投标；其他不纳入。
截止日期修正：pending 多为报名截止，统一以开标时间为准（详情页核实）。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":189,"company":"北京银行","project":"数字人民币运营机构筹建项目-数据湖系统（实时区）",
  "overview":"北京银行数字人民币运营机构筹建项目-数据湖系统（实时区）竞争性磋商（项目编号0747-2660SCCZND69），预算69.52万元，报名截止2026-11-24 17:00，开标2026-11-30 14:00。",
  "budget":"69.52万元","deadline":"2026-11-30 14:00","method":"竞争性磋商","contact":"代理 中化商务有限公司；电话 010-83923581、15120004080",
  "region":"华北","province":"北京","tags":["数据平台","公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648624869.html","source":"千里马招标网","date":"2026-11-18"},
 {"id":190,"company":"北京银行","project":"数字人民币运营机构筹建项目-数据集中处理系统",
  "overview":"北京银行数字人民币运营机构筹建项目-数据集中处理系统竞争性磋商（项目编号BOB-SZJR-20261109077-C），预算36.6万元（含税），合同签订后130日内启动上线试运行；文件获取至2026-11-23（中国通信建设集团，现场或邮寄，500元/份），响应文件递交截止2026-11-30 14:00（北京银行二层集采中心会议室）。",
  "budget":"36.6万元","deadline":"2026-11-30 14:00","method":"竞争性磋商","contact":"代理 中国通信建设集团有限公司；联系人 桑思文、杨洋；电话 13091199083、18010041733；邮箱 sangsiwen.zgtj@chinaccs.cn",
  "region":"华北","province":"北京","tags":["数据平台","公司金融"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://login-cpm-xt.bankofbeijing.com.cn/cms/default/webfile/1ywgg1/20261117/1307379988567162880.html","source":"北京银行集中采购管理平台","date":"2026-11-18"},
 {"id":191,"company":"宁银理财","project":"2027年存储光交硬件维保项目",
  "overview":"宁银理财2027年存储光交硬件维保项目公开招标（项目编号NBGODOZB226316-04），报名截止2026-11-24 17:00，开标2026-12-07 10:00；公告未披露预算。",
  "budget":"-","deadline":"2026-12-07 10:00","method":"公开招标","contact":"代理 宁波国际投资咨询有限公司；电话 0574-55717458、87329207",
  "region":"华东","province":"浙江","tags":["运维服务","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_8060734dc2c04f0aba49476c44827515&type=AllBeacon","source":"快查","date":"2026-11-18"},
 {"id":192,"company":"宁银理财","project":"2027年安全数据管理维保项目",
  "overview":"宁银理财2027年安全数据管理维保项目公开招标（项目编号NBGODOZB226316-02），报名截止2026-11-24 17:00，开标2026-12-07 09:30；公告未披露预算。",
  "budget":"-","deadline":"2026-12-07 09:30","method":"公开招标","contact":"代理 宁波国际投资咨询有限公司；电话 0574-55717458、87329207",
  "region":"华东","province":"浙江","tags":["运维服务","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648497611.html","source":"千里马招标网","date":"2026-11-18"},
 {"id":193,"company":"北银理财","project":"科技管理系统国产化改造与功能优化项目（二次）",
  "overview":"北银理财科技管理系统国产化改造与功能优化项目（二次）竞争性磋商（项目编号0773-2640GNOCFWCS3149），预算44.92万元，报名截止2026-11-23 16:00，开标2026-11-27 14:30。",
  "budget":"44.92万元","deadline":"2026-11-27 14:30","method":"竞争性磋商","contact":"代理 中金招标有限责任公司；电话 18701390392",
  "region":"华北","province":"北京","tags":["信创","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648195571.html","source":"千里马招标网","date":"2026-11-18"},
 {"id":194,"company":"北银理财","project":"2026年监管报送平台国产化及新增功能改造项目（二次）",
  "overview":"北银理财2026年监管报送平台国产化及新增功能改造项目（二次）竞争性磋商（项目编号0773-2643GNOCFWCS2889），预算86.23万元，报名截止2026-11-23 16:00，开标2026-11-27 15:00。",
  "budget":"86.23万元","deadline":"2026-11-27 15:00","method":"竞争性磋商","contact":"代理 中金招标有限责任公司；电话 18701390392",
  "region":"华北","province":"北京","tags":["信创","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_48c7a8fb1e1440a99697e25fedf6f76f&type=AllBeacon","source":"快查","date":"2026-11-18"},
 {"id":195,"company":"北银理财","project":"2026年代销相关改造项目（阶段三）（二次）",
  "overview":"北银理财2026年代销相关改造项目（阶段三）（二次）竞争性磋商（项目编号0773-2640GNOCFWCS3143），预算64万元，报名截止2026-11-23 16:00，开标2026-11-27 13:30。",
  "budget":"64万元","deadline":"2026-11-27 13:30","method":"竞争性磋商","contact":"代理 中金招标有限责任公司；电话 18701390392",
  "region":"华北","province":"北京","tags":["资产管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_9167cc00a52a43acb51f9559d648d8a7&type=AllBeacon","source":"快查","date":"2026-11-18"},
 {"id":196,"company":"中信信托","project":"综合办公系统（OA）2026年需求开发项目",
  "overview":"中信信托综合办公系统（OA）2026年需求开发项目公开招标（项目编号0733-26505399），预算90万元，报名截止2026-12-04 16:00，开标2026-12-08 13:30。",
  "budget":"90万元","deadline":"2026-12-08 13:30","method":"公开招标","contact":"代理 中信国际招标有限公司；招标单位电话 010-59902756",
  "region":"华北","province":"北京","tags":["其他","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_jincaiwang_1406c426331946068f9b9caea68fbd53&type=AllBeacon","source":"快查","date":"2026-11-18"},
 {"id":197,"company":"中原信托","project":"信息系统软件供应商库入围项目",
  "overview":"中原信托信息系统软件供应商库入围项目遴选（项目编号HNZB2026220733），报名2026-11-18至11-24 17:30，开标2026-12-01 09:30；公告未披露预算。",
  "budget":"-","deadline":"2026-12-01 09:30","method":"比选采购","contact":"代理 河南省机电设备招标股份有限公司；电话 0371-86230661",
  "region":"华中","province":"河南","tags":["其他","资产管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.kuaicha365.com/outer/tender-bid/project-process?urlId=ccgp_zhongguozbfwpt_code_c8066d7c50e04ccc42e444e1fd452b35&type=AllBeacon","source":"快查","date":"2026-11-18"},
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
print(f"OK: {len(NEW)}条上板 id 189-197，总条目 {data['total']}，total 已同步")
