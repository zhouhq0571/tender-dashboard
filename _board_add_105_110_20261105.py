#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-05 12:2x 周老师裁决 seek_1105_b1：6纳入（8/9/10/11/18/23，10与18改可关注、23升强烈建议投标），其余18条不纳入。
上板 id 105-110。数据取自千里马JSONL work副本（25字段源），非手填；台账 seek_1105_b1。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

NEW = [
 {"id":106,"company":"广西北部湾银行","project":"大模型应用场景项目(20261009)",
  "overview":"大模型应用场景项目竞争性磋商，响应截止2026-11-13，预算未公布。详见千里马招标网公告。",
  "budget":"-","deadline":"2026-11-13","method":"竞争性磋商",
  "contact":"林经理；电话 0771-6115363；邮箱 bhcg@bankofbbg.com",
  "region":"华南","province":"广西","tags":["大模型应用"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-644445876.html",
  "source":"千里马招标网","date":"2026-11-05"},
 {"id":107,"company":"兴业银行","project":"托管业务可视化项目二期",
  "overview":"托管业务可视化项目二期征集调研，征集截止2026-11-10，预算未公布。详见千里马招标网公告。",
  "budget":"-","deadline":"2026-11-10","method":"供应商征集",
  "contact":"电话 38308999-665021；邮箱 wush@cib.com.cn",
  "region":"华东","province":"浙江","tags":["资产托管"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-644162436.html",
  "source":"千里马招标网","date":"2026-11-05"},
 {"id":108,"company":"北京农商银行","project":"票据集中提回系统信创改造项目",
  "overview":"票据集中提回系统信创改造（征集），征集截止2026-11-09，预算未公布。详见千里马招标网公告。",
  "budget":"-","deadline":"2026-11-09","method":"供应商征集",
  "contact":"冯老师；电话 13581881572；邮箱 jhcw_gyszj@bjrcb.com",
  "region":"华北","province":"北京","tags":["信创","公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-644157086.html",
  "source":"千里马招标网","date":"2026-11-05"},
 {"id":109,"company":"山东农信","project":"市场风险管理信息系统项目",
  "overview":"市场风险管理信息系统竞争性谈判，响应截止2026-11-11，预算未公布。详见千里马招标网公告。",
  "budget":"-","deadline":"2026-11-11","method":"竞争性谈判",
  "contact":"白雅婷；电话 17853157270；邮箱 hyhawb@vip.126.com；代理 海逸恒安项目管理有限公司",
  "region":"华东","province":"山东","tags":["风控合规"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-644792064.html",
  "source":"千里马招标网","date":"2026-11-05"},
 {"id":110,"company":"建信信托","project":"2026-2027年恒生电子系统维护服务采购项目",
  "overview":"2026-2027年恒生电子系统维护服务（单一来源公示），公示截止2026-11-08，预算未公布。详见千里马招标网公告。",
  "budget":"-","deadline":"2026-11-08","method":"单一来源采购",
  "contact":"邮箱 jzcgbgs@ccbtrust.com.cn",
  "region":"华东","province":"安徽","tags":["资产服务信托","运维服务"],"rec":"🔥 ★★★ 强烈建议投标",
  "url":"https://www.qianlima.com/bid-644174080.html",
  "source":"千里马招标网","date":"2026-11-05"},
]

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

keys = {(p['company'], p['project']) for p in ps}
# 防串台：项目名关键词断言 + 板上查重
for n in NEW:
    assert len(n['project']) >= 8, n['id']
    if (n['company'], n['project']) in keys:
        print('SKIP dup:', n['id'], n['project']); continue
    if any(n['project'][:15] in p['project'] or p['project'][:15] in n['project'] for p in ps):
        print('ABORT 疑似串台:', n['id'], n['project']); sys.exit(1)
    ps.append(n)

data['projects'] = sorted(ps, key=sort_key)
# 版本与日期随部署脚本刷新，此处仅写数据
out = json.dumps(data, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(html[:m.start(2)] + out + html[m.end(2):])
print('OK, total =', len(data['projects']))
