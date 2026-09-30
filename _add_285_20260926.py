# -*- coding: utf-8 -*-
"""2026-09-26 手动入库：华夏银行 2026年信息科技人力资源池项目"""
import re, json, shutil, config

HTML = 'index.html'
shutil.copy(HTML, HTML + '.bak_v272_20260926_manual')

html = open(HTML, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))

new_project = {
    "id": 285,
    "region": "华北",
    "province": "北京",
    "company": "华夏银行",
    "project": "2026年信息科技人力资源池项目（公开招标·入围）",
    "overview": "华夏银行2026年信息科技人力资源池项目，委托建银工程咨询代理，公开招标入围8-10家供应商，覆盖开发、需求与产品设计、测试、运维四个通用技术领域，人员级别含初级至资深专家，服务地点为北京或济南（部分开发和测试人员在济南）。投标人须具备不少于500名技术服务人员（提供投标前4个月内连续3个月社保缴纳证明，代缴不予认可），2023年1月1日至今至少有一个框架资源池类外包服务案例（框架合同+订单/结算单/发票），承诺90%以上人员稳定性，不接受联合体、不得转包分包。2026-09-24至10-09线上报名（材料发邮箱JYZXZBDL@163.com），文件售价300元；投标截止2026-11-03 10:00，北京市海淀区西三环北路甲2号院国防科技园1号楼17层专人递交，不接受邮寄。",
    "budget": "-",
    "deadline": "2026-11-03 10:00",
    "method": "公开招标（入围）",
    "contact": "招标代理 建银工程咨询有限责任公司；报名邮箱 JYZXZBDL@163.com；文件购买 2026-09-24至10-09 9:00-11:00/14:00-17:00",
    "tags": ["人力外包"],
    "rec": "⭐ ★★☆ 建议投标",
    "url": "https://mp.weixin.qq.com/s/NzsQNG_VIhZ2V19V8XMNWQ",
    "source": "银行科技研究社（公众号）",
    "date": "2026-09-26"
}

if any(p['company'] == new_project['company'] and '人力资源池' in p['project'] for p in data['projects']):
    raise SystemExit('已存在该项目，终止')
assert new_project['id'] == max(p['id'] for p in data['projects']) + 1

data['projects'].append(new_project)
data['projects'] = sorted(data['projects'], key=config.sort_key)
data['version'] = 'v273'
data['date'] = '2026年09月26日'

new_json = m.group(1) + json.dumps(data, ensure_ascii=False, indent=1) + m.group(3)
html = html[:m.start()] + new_json + html[m.end():]
html, n = re.subn(r'v272', 'v273', html)
open(HTML, 'w', encoding='utf-8').write(html)
print(f"OK: 已添加 ID 285，项目总数 {len(data['projects'])}，版本 v273，title替换 {n} 处")
