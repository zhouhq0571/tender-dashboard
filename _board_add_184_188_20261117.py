#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-17 看板候选批次（9 条裁决：纳入 5 条）上板：id 184-188
决策（周老师 09:23）：1、2、5、6、9纳入；2、9标签改公司金融；5、9建议改建议投标；6标签增资产管理；其他不纳入。
联系方式按规则 O-联系方式经 VIP 详情页/公告原文提取（deadline/budget 以 VIP 正文修正）。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":184,"company":"中信信托","project":"估值系统2026年需求建设项目",
  "overview":"中信信托估值系统2026年需求建设项目公开招标（招标编号0733-26505282），预算169.83万元，投标截止2026-12-08；文件获取及递交详见招标公告。",
  "budget":"169.83万元","deadline":"2026-12-08","method":"公开招标","contact":"代理 中信国际招标有限公司；联系人 刘冰；电话 400-903-3175；邮箱 zanxj@ck.citic.com",
  "region":"华北","province":"北京","tags":["资产管理"],"rec":"🔥 ★★★ 强烈建议投标",
  "url":"https://www.qianlima.com/bid-648087043.html","source":"千里马招标网","date":"2026-11-17"},
 {"id":185,"company":"北京银行","project":"数字人民币运营机构筹建项目-头寸管理系统2.0",
  "overview":"北京银行数字人民币运营机构筹建项目-头寸管理系统2.0竞争性磋商（项目编号0773-2640GNOCFWCS3193），预算32.99万元，合同签订后180日内启动上线试运行；文件获取至2026-11-23 16:00（中招联合平台，标书0元+平台服务费500元），响应文件递交截止2026-11-30 14:00（北京银行二层集采中心会议室）。",
  "budget":"32.99万元","deadline":"2026-11-30 14:00","method":"竞争性磋商","contact":"代理 中金招标有限责任公司；联系人 高金婵、柳建林；电话 18701390392；邮箱 cctcof@chinatendering.com.cn",
  "region":"华北","province":"北京","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://login-cpm-xt.bankofbeijing.com.cn/cms/default/webfile/1ywgg1/20261116/1307105618544295936.html","source":"北京银行集中采购管理平台","date":"2026-11-17"},
 {"id":186,"company":"苏州银行","project":"2026年供应链服务平台二期服务采购项目",
  "overview":"苏州银行2026年供应链服务平台二期服务采购项目竞争性磋商（招标编号FUTC-2026-B131），预算200万元，报名截止2026-11-23，投标截止2026-11-27。",
  "budget":"200万元","deadline":"2026-11-27","method":"竞争性磋商","contact":"联系人 林老师；电话 19951223220、13585728489；邮箱 wanghy@cfcpn.com",
  "region":"华东","province":"江苏","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-648207313.html","source":"千里马招标网","date":"2026-11-17"},
 {"id":187,"company":"交银理财","project":"2026年应用系统延续实施外部服务（综合事务管理、需求分析设计、基础资源）",
  "overview":"交银理财2026年应用系统延续实施外部服务（综合事务管理、需求分析设计、基础资源）采购，报名/文件获取截止2026-11-19，公告未披露预算。",
  "budget":"-","deadline":"2026-11-19","method":"其他","contact":"邮箱 qinglu@bankcomm.com（交银理财采购联系）",
  "region":"华东","province":"上海","tags":["人力外包","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648138175.html","source":"千里马招标网","date":"2026-11-17"},
 {"id":188,"company":"青岛农商银行","project":"扫码收单系统架构优化及信创升级建设项目",
  "overview":"青岛农商银行扫码收单系统架构优化及信创升级建设项目公开招标（项目编号QRCB-JC2026086），项目控制价140万元；文件获取2026-11-14至11-20（青岛阳光采购平台免费下载，远程在线开标），投标截止/开标2026-11-25 14:00。",
  "budget":"140万元","deadline":"2026-11-25 14:00","method":"公开招标","contact":"代理 山东海润项目管理有限公司；联系人 吕宁、何雨豪；电话 15254288355；邮箱 sdhrqd@163.com",
  "region":"华东","province":"山东","tags":["公司金融"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.mpaypass.com.cn/news/202611/16180410.html","source":"移动支付网","date":"2026-11-17"},
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
print(f"OK: {len(NEW)}条上板 id 184-188，总条目 {data['total']}，total 已同步")
