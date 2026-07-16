#!/usr/bin/env python3
"""2026-07-17 增量合并：删16 + 改5已截止 + id28更新 + 新增10"""
import json, re, sys
sys.path.insert(0, '.')
from config import sort_key

F = 'work_current_projects.json'
d = json.load(open(F, encoding='utf-8'))
ps = d['projects']
base = len(ps)
assert base == 57, f'基准数异常: {base}'

# ---- 1. 删除：15个过期(deadline<2026-07-16) + id14北京农商(无固定截止/不合规) ----
DEL = {4,5,14,15,17,19,23,24,27,34,36,37,38,41,49,55}
ps = [p for p in ps if p['id'] not in DEL]
assert len(ps) == 41, f'删除后应为41，实际{len(ps)}'

# ---- 2. 已截止标记（deadline=07-16，今日07-17）----
for p in ps:
    if p['id'] in {30,31,32,33,51}:
        p['rec'] = '☆☆☆ 已截止'

# ---- 3. 状态变更：id28 江苏银行基金指数数据 → 重新招标 ----
for p in ps:
    if p['id'] == 28:
        p['deadline'] = '2026-07-23 09:00'
        if '重新招标' not in p['overview']:
            p['overview'] += '本项目2026-07-03首次招标，07-13终止后于当日重新发布招标公告。'

# ---- 4. 新增项目 ----
NEW = [
 dict(region='华东', province='福建', company='兴银理财',
      project='理财登记过户（TA）系统产品优化项目',
      overview='对现有理财登记过户（TA）系统进行产品优化升级，最高限价145.89万元（含税），公开招标，地点福州。',
      budget='145.89万元', deadline='2026-08-07 09:30', method='公开招标',
      contact='代理机构：公诚管理咨询有限公司 殷浩楠、陈碧霞、王红兰 18806091031',
      tags=['资产管理'], rec='🔥 ★★★ 强烈建议投标',
      url='https://www.chengezhao.com/cms/post/7/9/793b7422653132bfbe7d5690808d25c9/', source='天眼查'),
 dict(region='华东', province='山东', company='光大理财',
      project='投资交易系统2026年升级项目（三次招标）',
      overview='投资交易系统2026年度升级，招标估价605.76万元。前两次招标（05-18、06-16）流标，本次为第三次招标。',
      budget='605.76万元', deadline='2026-07-24', method='公开招标',
      contact='光大理财 0532-88965671（天眼查工商信息，2025年年报）',
      tags=['资产管理'], rec='🔥 ★★★ 强烈建议投标',
      url='https://yn.qianlima.com/zbcontent-611073216.html', source='千里马'),
 dict(region='华东', province='安徽', company='徽银理财',
      project='IBOR底座及头寸管理建设项目',
      overview='建设IBOR（实时持仓簿记）数据底座及头寸管理能力，支撑资管一体化平台。2026-07-14发布于安徽省招标投标信息网。',
      budget='-', deadline='2026-08-04', method='公开招标',
      contact='徽银理财 0551-65199001（天眼查工商信息，2025年年报）',
      tags=['资产管理', '数据平台'], rec='⭐ ★★☆ 建议投标',
      url='http://gjpt.ahtba.org.cn/biddingBulletin/2026-07-14/80577.html', source='天眼查'),
 dict(region='华东', province='江苏', company='紫金信托',
      project='资产管理信托技术服务供应商资源池项目',
      overview='资产管理信托业务技术服务供应商资源池，为技术开发服务储备供应商，属人力外包类。',
      budget='-', deadline='2026-08-05 09:30', method='公开招标',
      contact='代理机构：江苏省招标中心有限公司 刘欣楠、郭家栋 025-82281929',
      tags=['人力外包', '资产管理'], rec='👀 ★☆☆ 可关注',
      url='https://www.jszbcg.com/#/bulletindetail/TenderBulletin/716985', source='天眼查'),
 dict(region='华南', province='广东', company='华润信托',
      project='2026年实时数据同步平台项目',
      overview='采购实时数据同步平台，含5条链路永久授权、部署实施及1年维保。原06-23公告已终止，07-15重新发布谈判采购公告（编号LX[2026]070002）。',
      budget='-', deadline='2026-07-21 09:30', method='竞争性谈判',
      contact='吕启芳 13689561200 lvqf@crctrust.com',
      tags=['数据平台'], rec='👀 ★☆☆ 可关注',
      url='https://www.szecp.com.cn/first_cggg/2026-07-14/2682026.html', source='天眼查'),
 dict(region='西南', province='贵州', company='华能贵诚信托',
      project='估值系统上交所新竞价新综业改造项目',
      overview='恒生估值核算系统上交所新债券竞价、新综合业务平台相关改造。直接采购，拟定供应商为恒生电子股份有限公司，公示期2026-07-16至07-19。',
      budget='-', deadline='2026-07-19', method='单一来源采购',
      contact='周经理 010-68292029 zhouys@hngtrust.com',
      tags=['资产管理'], rec='⭐ ★★☆ 建议投标',
      url='https://ec.chng.com.cn/channel/home/#/detail?id=12911011', source='天眼查'),
 dict(region='华北', province='北京', company='外贸信托',
      project='开放平台信创改造项目',
      overview='开放平台信创改造。直接采购，拟定供应商为东华软件股份公司，公示期2026-07-15至07-21。',
      budget='-', deadline='2026-07-21', method='单一来源采购',
      contact='王秋兰 13501126634',
      tags=['信创/国产化'], rec='☆☆☆ 不建议',
      url='https://scm.esinochem.com/hpc/index.html#/details?noticeId=2077225020154593282', source='天眼查'),
 dict(region='西南', province='贵州', company='华能贵诚信托',
      project='反洗钱系统升级优化与维保服务项目',
      overview='反洗钱系统升级优化与维保。直接采购，拟定供应商为北京捷软世纪信息技术有限公司，公示期2026-07-15至07-18。',
      budget='-', deadline='2026-07-18', method='单一来源采购',
      contact='周经理 010-68292300',
      tags=['风控合规', '运维服务'], rec='☆☆☆ 不建议',
      url='https://ec.chng.com.cn/channel/home/#/detail?id=12911010', source='天眼查'),
 dict(region='西南', province='贵州', company='华能贵诚信托',
      project='风控百融平台运维服务项目',
      overview='风控百融平台运维服务。直接采购，拟定供应商为百融至信（北京）科技有限公司，公示期2026-07-15至07-18。',
      budget='-', deadline='2026-07-18', method='单一来源采购',
      contact='周经理 010-68292300',
      tags=['运维服务', '风控合规'], rec='☆☆☆ 不建议',
      url='https://ec.chng.com.cn/channel/home/#/detail?id=12911005', source='天眼查'),
 dict(region='西南', province='贵州', company='华能贵诚信托',
      project='金证TA系统运维服务项目',
      overview='金证TA系统运维服务。直接采购，拟定供应商为金证科技股份有限公司，公示期2026-07-16至07-19。',
      budget='-', deadline='2026-07-19', method='单一来源采购',
      contact='周经理 010-68292300',
      tags=['运维服务'], rec='☆☆☆ 不建议',
      url='https://ec.chng.com.cn/channel/home/#/detail?id=12911012', source='天眼查'),
]

# 去重检查：公司+项目名前15字
exist_keys = {(p['company'], p['project'][:15]) for p in ps}
for n in NEW:
    k = (n['company'], n['project'][:15])
    assert k not in exist_keys, f'重复: {k}'
    exist_keys.add(k)
ps.extend(NEW)

# ---- 5. 排序 + 重排ID ----
ps.sort(key=sort_key)
for i, p in enumerate(ps, 1):
    p['id'] = i

# ---- 6. 头部字段 ----
d['projects'] = ps
d['version'] = 'v100'
d['date'] = '2026年07月17日'
d['timePeriod'] = '上午'
d['updateTime'] = '2026年07月17日'
strong = sum(1 for p in ps if p['rec'].startswith('🔥'))
normal = sum(1 for p in ps if p['rec'].startswith('⭐'))
watch = sum(1 for p in ps if p['rec'].startswith('👀'))
expired = sum(1 for p in ps if p['rec'].startswith('☆☆☆'))
d['stats'] = {'total': len(ps), 'strong': strong, 'normal': normal, 'watch': watch, 'expired': expired}

json.dump(d, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
print(f'OK: {base} - 16 + {len(NEW)} = {len(ps)}')
print('stats:', d['stats'])
# 70%保护阈值
assert len(ps) >= int(base * 0.7), '低于70%保护阈值'
print('70%阈值检查通过')
