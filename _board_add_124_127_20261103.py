#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-03 08:13 周老师裁决：候选1-4均纳入，2、3投标建议改"建议投标"。上板 id 124-127。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

NEW = [
 {"id":124,"company":"邮储银行","project":"科技金融深度数据服务采购项目（第2次招标）",
  "overview":"邮储银行科技金融深度数据服务采购项目（第2次招标）公开招标，投标截止2026-11-09；代理机构江苏省招标中心有限公司。",
  "budget":"-","deadline":"2026-11-09","method":"公开招标",
  "contact":"江苏省招标中心有限公司 王潇轩等 13146589358 010-87056688",
  "region":"华北","province":"北京","tags":["数据服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://cg.psbc.com/cms/default/webfile/1ywgg2/20261102/1301961334694346752.html",
  "source":"邮储银行邮银易采平台","date":"2026-11-03"},
 {"id":125,"company":"秦皇岛银行","project":"国库集中电子化支付系统数字人民币建设改造项目",
  "overview":"秦皇岛银行国库集中电子化支付系统数字人民币建设改造项目单一来源采购，预算32.8万元，响应截止2026-11-17。",
  "budget":"32.8万元","deadline":"2026-11-17","method":"单一来源采购",
  "contact":"河北宏信招标有限公司",
  "region":"华北","province":"河北","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-643994685.html","source":"千里马招标网","date":"2026-11-03"},
 {"id":126,"company":"厦门银行","project":"境内人民币支付升级项目（供应商寻源）",
  "overview":"厦门银行境内人民币支付升级项目（供应商寻源）供应商征集，征集截止2026-11-09；公告正文未披露联系方式。",
  "budget":"-","deadline":"2026-11-09","method":"供应商征集","contact":"-",
  "region":"华东","province":"福建","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-643781636.html","source":"千里马招标网","date":"2026-11-03"},
 {"id":127,"company":"北京银行","project":"2026年产业数字金融数字仓单建设项目-供应链系统一期（二次）",
  "overview":"北京银行2026年产业数字金融数字仓单建设项目-供应链系统一期（二次）竞争性磋商，预算53.1万元，响应截止2026-11-16；代理建银工程咨询有限责任公司。",
  "budget":"53.1万元","deadline":"2026-11-16","method":"竞争性磋商",
  "contact":"建银工程咨询有限责任公司 谢鹏 15373337313",
  "region":"华北","province":"北京","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-644027228.html","source":"千里马招标网","date":"2026-11-03"},
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

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)
new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
open('index.html', 'w', encoding='utf-8').write(html[:m.start()] + new_block + html[m.end():])
print(f"OK: 4条上板 id 124-127，板上共 {len(ps)} 条")
