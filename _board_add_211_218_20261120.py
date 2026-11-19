#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-20 decide.html 批次决策执行：push_no 31/38/39/40/41/42/43/44 上板。
来源：周老师 decide.html 指令「【候选决策 2026-11-20】…」（8 纳入 14 不纳入）。
数据：pending_candidates.json 动态取 + ql_vip_fetch 详情核验（预算/截止/联系方式一致）。
防串台：8 条台账 status=待确认，首次执行；标签/建议按决策括注覆盖。
特殊处理：push_no 42（北京银行测试需求·第二次）板上已有首轮 id 6（bid-645933219，
截止 2026-11-23 已失效）→ 原地更新为第二轮（bid-648428666，截止 2026-12-01），不新增。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key, VALID_TAGS

NEW = [
 {"id":211,"company":"青岛农商银行","project":"青岛农商银行社保资金代收付系统信创改造项目",
  "overview":"青岛农商银行社保资金代收付系统信创改造项目公开招标（招标编号FSCG-2026110017），预算18.7万元；投标截止2026-12-01。采购内容：社保资金代收付系统信创改造。",
  "budget":"18.7万元","deadline":"2026-12-01","method":"公开招标",
  "contact":"代理 青岛鸿翔招标有限公司；联系人 徐晓；电话 0532-66957097；邮箱 hongxiangzhaobiao@126.com",
  "region":"华东","province":"山东","tags":["公司金融","信创"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-648575109.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":212,"company":"杭州工商信托","project":"杭州工商信托股份有限公司债券投资信用评级模型采购项目",
  "overview":"杭州工商信托债券投资信用评级模型采购项目公开招标（招标编号GSXT2026HWJC216），预算50万元；报名及投标截止2026-11-25。采购内容：债券投资信用评级模型。",
  "budget":"50万元","deadline":"2026-11-25","method":"公开招标",
  "contact":"代理 浙江省成套招标代理有限公司；联系人 蒋帅；电话 0571-87228017",
  "region":"华东","province":"浙江","tags":["风控合规","资产管理"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648749418.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":213,"company":"中铁信托","project":"中铁信托有限责任公司资管系统进行反洗钱、信息披露改造线上询价采购",
  "overview":"中铁信托资管系统进行反洗钱、信息披露改造线上询价采购，预算未披露；报价截止2026-11-20。采购内容：资管系统反洗钱、信息披露改造。",
  "budget":"-","deadline":"2026-11-20","method":"询价采购",
  "contact":"联系人 羌女士；电话 15882132060",
  "region":"西南","province":"四川","tags":["资产管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-648590069.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":214,"company":"中铁信托","project":"中铁信托有限责任公司投资者APP电子签名改造等需求线上询价采购",
  "overview":"中铁信托投资者APP电子签名改造等需求线上询价采购，预算未披露；报价截止2026-11-20。采购内容：投资者APP电子签名改造等。",
  "budget":"-","deadline":"2026-11-20","method":"询价采购",
  "contact":"联系人 张先生；电话 028-82570568",
  "region":"西南","province":"四川","tags":["渠道系统"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://www.qianlima.com/bid-648075955.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":215,"company":"华润深国投信托","project":"华润深国投信托有限公司华润信托二代征信报数系统信创改造项目",
  "overview":"华润信托二代征信报数系统信创改造项目竞争性谈判（项目编号LX[2026]110009），预算未披露；响应截止2026-11-23。采购内容：二代征信报数系统信创改造。",
  "budget":"-","deadline":"2026-11-23","method":"竞争性谈判",
  "contact":"联系人 吕启芳；电话 13689561200；邮箱 lvqf@crctrust.com",
  "region":"华南","province":"广东","tags":["风控合规","资产管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-647990611.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":216,"company":"兴业银行","project":"兴业银行关于境外投资理财保费融资及结构性票据升级项目",
  "overview":"兴业银行境外投资理财保费融资及结构性票据升级项目公开招标，预算未披露；报名截止2026-11-25。采购内容：境外投资理财保费融资及结构性票据系统升级。",
  "budget":"-","deadline":"2026-11-25","method":"公开招标",
  "contact":"联系人 吴诗；电话 38308999-665021；邮箱 wush@cib.com.cn",
  "region":"华东","province":"福建","tags":["财富管理"],"rec":"⭐ ★★☆ 建议投标",
  "url":"https://www.qianlima.com/bid-648984994.html","source":"千里马招标网","date":"2026-11-20"},
 {"id":217,"company":"青岛农商银行","project":"青岛农商银行贵金属代销系统黄金积存兑换功能优化项目",
  "overview":"青岛农商银行贵金属代销系统黄金积存兑换功能优化项目公开招标（招标编号FSCG-2026110021），预算16万元；投标截止2026-12-01。采购内容：贵金属代销系统黄金积存兑换功能优化。",
  "budget":"16万元","deadline":"2026-12-01","method":"公开招标",
  "contact":"代理 青岛鸿翔招标有限公司；联系人 徐晓；电话 0532-66957097；邮箱 hongxiangzhaobiao@126.com",
  "region":"华东","province":"山东","tags":["财富管理"],"rec":"🔥 ★★★ 强烈建议投标",
  "url":"https://www.qianlima.com/bid-648573616.html","source":"千里马招标网","date":"2026-11-20"},
]

# push_no 42：板上首轮 id 6 原地更新为第二次公告
UPDATE_ID6 = {
 "project": "北京银行2026年财富管理数字赋能系统业务测试需求项目（第二次）",
 "overview": "北京银行2026年财富管理数字赋能系统业务测试需求项目（第二次）公开招标（招标编号0747-2660SCCZND30/01），预算15.91万元（159120元）；投标截止2026-12-01。采购内容：财富管理数字赋能系统业务测试服务。",
 "budget": "15.91万元", "deadline": "2026-12-01", "method": "公开招标",
 "contact": "代理 中化商务有限公司",
 "url": "https://www.qianlima.com/bid-648428666.html", "date": "2026-11-20",
}

for n in NEW:
    for t in n['tags']:
        assert t in VALID_TAGS, f"非法标签: {t} (id {n['id']})"

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

cores = ['社保资金代收付系统信创改造', '债券投资信用评级模型', '反洗钱、信息披露改造',
         '电子签名改造', '二代征信报数系统信创改造',
         '保费融资及结构性票据升级', '黄金积存兑换功能优化']
for core in cores:
    assert not any(core in p['project'] for p in ps), f"板上已有 {core}，禁止重复上板"
assert all(n['url'] not in p.get('url','') for p in ps for n in NEW), "url 重复"
assert all(n['id'] not in {p['id'] for p in ps} for n in NEW), "id 冲突"

# 防串台：id 6 必须是北京银行测试首轮才允许原地更新
t6 = [p for p in ps if p['id'] == 6]
assert len(t6) == 1 and '财富管理数字赋能系统业务测试' in t6[0]['project'] \
    and t6[0]['url'].endswith('bid-645933219.html'), "id 6 内容不符预期，禁止更新"
t6[0].update(UPDATE_ID6)

ps.extend(NEW)
ps.sort(key=sort_key)
data['total'] = len(ps)

new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
out = html[:m.start()] + new_block + html[m.end():]
open('index.html', 'w', encoding='utf-8').write(out)
print(f"OK: 7 条新增（id 211~217）+ id 6 原地更新为第二次公告，总条目 {data['total']}")
