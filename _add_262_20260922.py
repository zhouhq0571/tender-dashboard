# -*- coding: utf-8 -*-
"""2026-09-22 手动入库：江苏农商联合银行 数字人民币项目加密机（供应商征集）"""
import re, json, shutil, datetime

HTML = 'index.html'
shutil.copy(HTML, HTML + '.bak_v263_20260922_manual')

html = open(HTML, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))

new_project = {
    "id": 262,
    "region": "华东",
    "province": "江苏",
    "company": "江苏农商联合银行",
    "project": "数字人民币项目加密机采购供应商征集",
    "overview": "数字人民币项目配套加密机纯硬件采购，与数币核心系统、场景业务系统、智能合约系统同步征集，报名截止2026-09-23 17:00，经江苏农商联合银行集中采购管理平台报名。",
    "budget": "-",
    "deadline": "2026-09-23 17:00",
    "method": "供应商征集",
    "contact": "江苏农商联合银行：商务 刘老师 15335183735；业务 何老师 15365129084；报名经江苏农商联合银行集中采购管理平台",
    "tags": ["公司金融"],
    "rec": "⭐ ★★☆ 建议投标",
    "url": "https://mp.weixin.qq.com/s/vQw3qmuzaauUkHam73xNmA",
    "source": "移动支付网"
}

# 去重检查
if any(p['company'] == new_project['company'] and '加密机' in p['project'] for p in data['projects']):
    raise SystemExit('已存在加密机项目，终止')
ids = [p['id'] for p in data['projects']]
assert new_project['id'] == max(ids) + 1, f"ID 不连续: max={max(ids)}"

data['projects'].append(new_project)
data['version'] = 'v263'
data['date'] = '2026年09月22日'

new_json = m.group(1) + json.dumps(data, ensure_ascii=False, indent=1) + m.group(3)
new_html = html[:m.start()] + new_json + html[m.end():]
open(HTML, 'w', encoding='utf-8').write(new_html)
print(f"OK: 已添加 ID 262，项目总数 {len(data['projects'])}，版本 {data['version']}")
