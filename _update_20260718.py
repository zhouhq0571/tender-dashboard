#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-07-18 增量更新：删过期5 + 标已截止3 + 新增7（用户已确认）"""
import json, re, io, sys

HTML = 'index.html'
html = io.open(HTML, encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
data = json.loads(m.group(1))
projects = data['projects']
print('更新前项目数:', len(projects))

TODAY = '2026-07-18'
YESTERDAY = '2026-07-17'

# ── 步骤1: 删除过期（deadline 日期 < 昨天）──
deleted = []
kept = []
for p in projects:
    d = p.get('deadline', '')[:10]
    if d < YESTERDAY:
        deleted.append(f"{p['company']}·{p['project'][:20]}({d})")
    else:
        kept.append(p)
projects = kept
print('删除过期', len(deleted), '个:')
for x in deleted: print('  -', x)

# ── 步骤2: 昨天截止 → 标记已截止；今天 date-only → 保持原建议 ──
marked = []
for p in projects:
    d = p.get('deadline', '')
    if d[:10] == YESTERDAY and p.get('rec') != '☆☆☆ 已截止':
        p['rec'] = '☆☆☆ 已截止'
        marked.append(f"{p['company']}·{p['project'][:20]}")
print('标记已截止', len(marked), '个:', marked)

# ── 步骤3: 新增 7 个已确认项目 ──
max_id = max((p.get('id', 0) for p in projects), default=0)
REC = '👀 ★☆☆ 可关注'
new_projects = [
 dict(region='华北', province='天津', company='天津农商',
      project='2026-2028年度信息科技外包人员调用框架采购项目',
      overview='信息科技外包人员调用框架采购，共6包（软件开发、系统分析、测试、运行操作、IT服务、安全服务），框架入围兼投兼中，服务期两年。',
      budget='人月单价6000-32000元', deadline='2026-07-22 09:30', method='公开招标',
      contact='刘经理 13581590765', tags=['人力外包'], rec=REC,
      url='https://www.guoxinzbcg.com/news/815212.html', source='国信招投标平台'),
 dict(region='华北', province='天津', company='天津农商',
      project='重构数据文件交换系统采购项目',
      overview='重构数据文件交换系统采购，划分为1个标段，纸质投标文件递交，开标地点天津市。',
      budget='-', deadline='2026-08-06 09:30', method='公开招标',
      contact='董天 13041093518 / 徐工 18611886439', tags=['数据平台'], rec=REC,
      url='http://www.qgzbcgjypt.com/zhongbiaoxinxi/105231.html', source='国信招标信息平台'),
 dict(region='华东', province='浙江', company='浙江农商联合',
      project='综合领域通用类软件研发人力外包资源池入围',
      overview='与浙江农商数字科技联合征集综合领域通用类软件开发外包人员资源池，含开发、测试、培训、推广、维护，框架协议3年。',
      budget='-', deadline='2026-07-21 09:15', method='框架协议采购',
      contact='0571-87260853', tags=['人力外包'], rec=REC,
      url='https://www.zj96596.com/zj96596/2026-07/13/article_2026071312411159553.shtml', source='浙江农信官网'),
 dict(region='华南', province='广东', company='广州农商',
      project='2026-2028年度流程银行数据录入外包项目',
      overview='两年期流程银行数据录入外包服务，确定2名中标人，要求供应商具备2个以上异地远程录入基地及银行实时性录入案例。',
      budget='167.26万元', deadline='2026-08-04 09:00', method='公开招标',
      contact='潘先生 020-22389241', tags=['人力外包'], rec=REC,
      url='https://www.grcbank.com/grcbank/gywx/cggg/2026070717110988254/index.shtml', source='广州农商行官网'),
 dict(region='华东', province='浙江', company='瑞丰银行',
      project='通用开发人力外包服务采购项目',
      overview='采购软件开发、数据开发、AI开发、UI设计等科技人力外包服务，要求注册资金1000万元以上及3个银行总行级同类案例。',
      budget='-', deadline='2026-07-24 14:00', method='公开招标',
      contact='文先生 0575-81105730', tags=['人力外包'], rec=REC,
      url='https://www.mpaypass.com.cn/news/202607/17091229.html', source='移动支付网'),
 dict(region='西南', province='贵州', company='贵州农商联合银行',
      project='外部金融数据终端项目（二次）',
      overview='采购40个外部金融数据终端账号（其中4个需开通API功能），服务周期1年，全流程电子化招标。',
      budget='152万元', deadline='2026-08-05 13:00', method='公开招标',
      contact='潘老师 18984165007 / 郑老师 18885282681', tags=['金融市场/资金/同业', '数据平台'], rec=REC,
      url='https://www.gznxbank.com/html/xn9999999/detail/59_29022.html', source='贵州农商联合银行官网'),
 dict(region='华北', province='北京', company='华鑫信托',
      project='备份与灾备系统建设项目（2026期）',
      overview='备份与灾备系统一套（备份服务器2台+授权软件+交换机2台）及实施服务，部署于北京生产中心与廊坊灾备中心，质保不少于3年。',
      budget='196万元', deadline='2026-07-21 17:30', method='竞争性谈判',
      contact='王帆 010-68809287', tags=['其他'], rec=REC,
      url='https://zmzb.dlnyzb.com/detail/41502428', source='电力能源招标网'),
]

# 去重检查（机构+项目前15字）
existing_keys = {(p['company'], p['project'][:15]) for p in projects}
added = []
for np in new_projects:
    key = (np['company'], np['project'][:15])
    if key in existing_keys:
        print('!! 重复跳过:', key)
        continue
    max_id += 1
    np['id'] = max_id
    projects.append(np)
    added.append(np['company'] + '·' + np['project'][:20])
print('新增', len(added), '个:', added)

# ── 步骤4: 版本号 + 日期 + timePeriod ──
data['version'] = 'v102'
data['date'] = '2026年07月18日'
data['timePeriod'] = '上午'
data['projects'] = projects
print('更新后项目数:', len(projects))

# 写回 HTML（保持其余部分不动）
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_html = html[:m.start(1)] + '\n' + new_json + '\n' + html[m.end(1):]

# 静态封面/封底时间文本同步
new_html = re.sub(r'(id="cover-update-time"[^>]*>)[^<]*', r'\g<1>数据更新时间：2026年07月18日 上午', new_html)
new_html = re.sub(r'(id="footer-update-time"[^>]*>)[^<]*', r'\g<1>数据更新时间：2026年07月18日 上午', new_html)

io.open(HTML, 'w', encoding='utf-8').write(new_html)
print('index.html 已写入')
