# -*- coding: utf-8 -*-
"""2026-09-22 手动入库：邮储银行广东省分行 AI算力设备采购项目"""
import re, json, shutil, config

HTML = 'index.html'
shutil.copy(HTML, HTML + '.bak_v264_20260922_manual')

html = open(HTML, encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))

new_project = {
    "id": 263,
    "region": "华南",
    "province": "广东",
    "company": "邮储银行广东省分行",
    "project": "AI算力设备采购项目",
    "overview": "公开招标选1家供应商，为广东省分行提供一套AI算力设备及配套部署、保修服务，含软硬件产品、部署调试、性能调优、AI模型适配部署及日常运维支撑，交付本地化AI算力平台。预算236万元（含税），合同期1年。要求投标人为制造商或制造商唯一授权代理商，具备2023年以来同类算力设备项目经验；全线上流程，邮银易采平台CA加密递交，投标保证金2.43万元，招标文件500元/套，文件获取截止2026-09-24 17:00。",
    "budget": "236万元",
    "deadline": "2026-10-29 09:30",
    "method": "公开招标",
    "contact": "招标代理 中捷通信：王菲/邝炎滢等 020-38187025；需求咨询 吕先生 13760879009；购买文件 黄小姐 020-83820346",
    "tags": ["大模型应用"],
    "rec": "👀 ★☆☆ 可关注",
    "url": "https://mp.weixin.qq.com/s/o5O-HyQNQwBbebSkaGZxXQ",
    "source": "中国邮政储蓄银行邮银易采平台"
}

if any(p['company'] == new_project['company'] and 'AI算力' in p['project'] for p in data['projects']):
    raise SystemExit('已存在该项目，终止')
assert new_project['id'] == max(p['id'] for p in data['projects']) + 1

data['projects'].append(new_project)
data['projects'] = sorted(data['projects'], key=config.sort_key)
data['version'] = 'v264'
data['date'] = '2026年09月22日'

new_json = m.group(1) + json.dumps(data, ensure_ascii=False, indent=1) + m.group(3)
html = html[:m.start()] + new_json + html[m.end():]
html, n = re.subn(r'v263', 'v264', html)
open(HTML, 'w', encoding='utf-8').write(html)
print(f"OK: 已添加 ID 263，项目总数 {len(data['projects'])}，版本 v264，title替换 {n} 处")
