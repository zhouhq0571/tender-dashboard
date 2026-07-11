import json, re
from collections import Counter

# 读取当前数据
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(match.group(1))
projects = data.get('projects', [])

print(f'当前项目数: {len(projects)}')

# 检查重复
keys = [f"{p.get('company','')}|{p.get('project','')[:15]}" for p in projects]
dups = {k:v for k,v in Counter(keys).items() if v > 1}
print(f'重复项目: {dups}')

# 显示重复项目详情
for p in projects:
    key = f"{p.get('company','')}|{p.get('project','')[:15]}"
    if key in dups:
        print(f"  ID {p.get('id')}: {p.get('company')} - {p.get('project')[:40]}")

# 检查排序
for i, p in enumerate(projects):
    if p.get('id') != i + 1:
        print(f'排序错误: ID {p.get("id")} 应在位置 {i+1}')
        break
else:
    print('ID排序正确')
