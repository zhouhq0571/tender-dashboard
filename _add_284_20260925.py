# -*- coding: utf-8 -*-
"""2026-09-25 手动入库：武汉农商行 监管报表"一表通"项目配套软硬件资源采购"""
import re, json, shutil, config

HTML = 'index.html'
shutil.copy(HTML, HTML + '.bak_v271_20260925_manual')

html = open(HTML, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))

new_project = {
    "id": 284,
    "region": "华中",
    "province": "湖北",
    "company": "武汉农商行",
    "project": "监管报表“一表通”项目配套软硬件资源采购",
    "overview": "武汉农村商业银行监管报表“一表通”项目配套软硬件资源采购，公开招标，项目编号HBT-106126085-266027，招标控制价298.5875万元（超出按废标处理），合同签订后30个日历天内供货。投标人须近三年内有类似服务器供货业绩（提供合同关键页），不接受联合体投标。招标文件2026-09-23至09-29在湖北省招标股份有限公司“数智云采”平台获取，售价800元。",
    "budget": "298.59万元",
    "deadline": "2026-10-13 09:30",
    "method": "公开招标",
    "contact": "招标代理 湖北省招标股份有限公司（数智云采平台）；开标地点 武汉市武昌中北路108号兴业银行大厦三层",
    "tags": ["数据平台", "信创"],
    "rec": "👀 ★☆☆ 可关注",
    "url": "https://mp.weixin.qq.com/s/rzlv6wOpD34n04vMLQV8Kw",
    "source": "银行科技研究社（公众号）",
    "date": "2026-09-25"
}

if any(p['company'] == new_project['company'] and '一表通' in p['project'] for p in data['projects']):
    raise SystemExit('已存在该项目，终止')
assert new_project['id'] == max(p['id'] for p in data['projects']) + 1

data['projects'].append(new_project)
data['projects'] = sorted(data['projects'], key=config.sort_key)
data['version'] = 'v272'
data['date'] = '2026年09月25日'

new_json = m.group(1) + json.dumps(data, ensure_ascii=False, indent=1) + m.group(3)
html = html[:m.start()] + new_json + html[m.end():]
html, n = re.subn(r'v271', 'v272', html)
open(HTML, 'w', encoding='utf-8').write(html)
print(f"OK: 已添加 ID 284，项目总数 {len(data['projects'])}，版本 v272，title替换 {n} 处")
