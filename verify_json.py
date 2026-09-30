#!/usr/bin/env python3
import json, re

HTML_PATH = "/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html"

with open(HTML_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
if not match:
    print("❌ 无法找到 tender-data JSON")
    exit(1)

data = json.loads(match.group(1))
print(f"版本: {data['version']}")
print(f"项目数: {len(data['projects'])}")

ids = [p['id'] for p in data['projects']]
print(f"ID范围: {min(ids)}-{max(ids)}")
print(f"后15个ID: {ids[-15:]}")

from collections import Counter
c = Counter(ids)
dups = {k:v for k,v in c.items() if v > 1}
print(f"重复ID: {dups}")

# 检查必填字段
required = ['id', 'region', 'province', 'company', 'project', 'overview', 'deadline', 'method', 'contact', 'tags', 'rec', 'url']
issues = []
for p in data['projects']:
    for f in required:
        if f not in p or not p.get(f):
            issues.append(f"[id={p.get('id', '?')}] 缺少 {f}")

print(f"\n必填字段问题: {len(issues)}个")
if issues:
    for i in issues[:5]:
        print(f"  {i}")

# 检查region/province一致性
region_province_map = {
    '东北': ['黑龙江', '吉林', '辽宁'],
    '华北': ['内蒙古', '北京', '天津', '河北', '山西'],
    '西北': ['陕西', '甘肃', '宁夏', '青海', '新疆'],
    '华东': ['山东', '江苏', '浙江', '安徽', '福建', '江西', '上海'],
    '华中': ['河南', '湖北', '湖南'],
    '西南': ['重庆', '四川', '贵州', '云南', '西藏'],
    '华南': ['广东', '广西', '海南'],
}

rp_issues = []
for p in data['projects']:
    r, prov = p.get('region', ''), p.get('province', '')
    if r in region_province_map and prov not in region_province_map[r]:
        rp_issues.append(f"[id={p['id']}] {p['company']}: region='{r}' vs province='{prov}'")

print(f"\n大区/省份不一致: {len(rp_issues)}个")
if rp_issues:
    for i in rp_issues[:5]:
        print(f"  {i}")

print("\n✅ 验证完成")
