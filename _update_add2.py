#!/usr/bin/env python3
import json
import re

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON data
json_match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
if not json_match:
    print("ERROR: Could not find tender-data JSON")
    exit(1)

json_str = json_match.group(1)
data = json.loads(json_str)

print(f"Current version: {data['version']}")
print(f"Current project count: {len(data['projects'])}")

# Update existing GSXT project (ID 42)
gsxt_updated = False
for p in data['projects']:
    if p['id'] == 42:
        p['budget'] = '50万元'
        p['deadline'] = '2026-08-12 09:30'
        p['contact'] = '采购人：黄以德 0571-87214005；代理人：李刚雷 0571-85833957 / 15088746906'
        p['url'] = 'https://www.qianlima.com/bid-620324506.html'
        p['method'] = '竞争性磋商'
        p['overview'] = '杭州工商信托股份有限公司委托浙江省成套招标代理有限公司就接口总线系统改造项目进行竞争性磋商，欢迎对本项目有兴趣并符合供应商资格条件的供应商参加响应。'
        p['rec'] = '🔥 ★★★ 强烈建议投标'
        p['tags'] = ['数据平台']
        gsxt_updated = True
        print(f"Updated ID 42: {p['company']} - {p['project']}")
        break

if not gsxt_updated:
    print("WARNING: ID 42 not found!")

# Check if Tianjin bank project already exists
has_tjbk = any('分级授权审批流程' in p['project'] for p in data['projects'])
print(f"Has Tianjin bank project: {has_tjbk}")

# Add new Tianjin bank project if not exists
if not has_tjbk:
    max_id = max(p['id'] for p in data['projects'])
    new_project = {
        "region": "华北",
        "province": "天津",
        "company": "天津银行",
        "project": "理财资产管理系统分级授权审批流程改造项目",
        "overview": '依托天津银行新版经营授权方案，本次将对理财资产管理系统开展专项改造，明确债券、基金等投资业务的授权范围、审批标准及操作流程，以系统化手段规范业务全流程管控。同步对标监管"一表通"建设规范，迭代优化投资管理、资产信息管理相关功能，提升监管数据报送规范性。服务期限：合同签订后6个月完成系统功能开发、测试工作，实现项目功能投产。提供从验收时间开始一年期的技术支持及维护。',
        "budget": "34.94万元",
        "deadline": "2026-08-21 09:30",
        "method": "公开招标",
        "contact": "招标人：宋伟晓 15122993906；代理：霍晶/张如春/刘昭君/孙旭迪/任立秀 18322773732",
        "tags": ["资产管理"],
        "rec": "🔥 ★★★ 强烈建议投标",
        "url": "https://www.qianlima.com/bid-620415500.html",
        "source": "千里马招标网",
        "id": max_id + 1
    }
    data['projects'].append(new_project)
    print(f"Added new project ID {max_id + 1}: 天津银行理财资产管理系统分级授权审批流程改造项目")

# Update metadata
data['version'] = 'v145'
data['date'] = '2026年08月11日'
data['timePeriod'] = '早上'

print(f"New version: {data['version']}")
print(f"New project count: {len(data['projects'])}")

# Convert back to JSON string
new_json_str = json.dumps(data, ensure_ascii=False, indent=2)

# Replace JSON in content
new_content = content.replace(json_str, new_json_str, 1)

# Update title
new_content = re.sub(r'<title>.*?</title>', '<title>恒生银信招标资讯每日速递 | 2026年08月11日（更新）v145</title>', new_content)

# Update cover time
new_content = re.sub(r'<div class="cover-meta" id="cover-update-time">.*?</div>', '<div class="cover-meta" id="cover-update-time">数据更新时间：2026年08月11日 早上</div>', new_content)

# Update footer time
new_content = re.sub(r'<span id="footer-update-time">.*?</span>', '<span id="footer-update-time">2026年08月11日 早上</span>', new_content)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("SUCCESS: index.html updated")

# Verify by reading back
with open('index.html', 'r', encoding='utf-8') as f:
    verify = f.read()

v_match = re.search(r'"version": "(v\d+)"', verify)
t_match = re.search(r'<title>.*?v(\d+)</title>', verify)
print(f"Verified JSON version: {v_match.group(1) if v_match else 'NOT FOUND'}")
print(f"Verified title version: v{t_match.group(1) if t_match else 'NOT FOUND'}")

json_match2 = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', verify, re.DOTALL)
data2 = json.loads(json_match2.group(1))
print(f"Verified project count: {len(data2['projects'])}")

# Show updated/new projects
for p in data2['projects']:
    if p['id'] in [42, 77]:
        print(f"Project ID {p['id']}: {p['company']} - {p['project']}, budget={p['budget']}, deadline={p['deadline']}")
