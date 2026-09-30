#!/usr/bin/env python3
import json, re
from datetime import datetime, timedelta

# Read index.html
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract JSON data
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
if not m:
    print("ERROR: Could not find tender-data JSON")
    exit(1)

data = json.loads(m.group(1))
projects = data.get('projects', [])

print(f"基准项目数: {len(projects)}")
print(f"版本: {data.get('version', 'N/A')}")
print(f"日期: {data.get('date', 'N/A')}")

today = datetime(2026, 7, 30).date()

keep = []
delete = []
mark_expired = []

for p in projects:
    dl = p.get('deadline', '')
    if not dl:
        keep.append(p)
        continue
    
    # Parse deadline
    dl_date = None
    try:
        if ' ' in dl:
            dl_date = datetime.strptime(dl.split()[0], '%Y-%m-%d').date()
        else:
            dl_date = datetime.strptime(dl, '%Y-%m-%d').date()
    except:
        keep.append(p)
        continue
    
    delta = (today - dl_date).days
    
    if delta >= 2:
        # Delete: deadline is 2+ days before today
        delete.append(p)
    elif delta == 1 or delta == 0:
        # Keep but mark as expired
        p['rec'] = '☆☆☆ 已截止'
        mark_expired.append(p)
        keep.append(p)
    else:
        # Future deadline, keep as-is
        keep.append(p)

print(f"\n过期处理结果:")
print(f"  保留项目: {len(keep)}")
print(f"  删除项目 (deadline <= {today - timedelta(days=2)}): {len(delete)}")
print(f"  标记已截止 (deadline = {today - timedelta(days=1)} 或 {today}): {len(mark_expired)}")

if delete:
    print(f"\n删除项目列表:")
    for p in delete:
        print(f"  - {p.get('company','')} | {p.get('project','')} | deadline: {p.get('deadline','')}")

# Save processed data
with open('work_current_projects.json', 'w', encoding='utf-8') as f:
    json.dump(keep, f, ensure_ascii=False, indent=2)

# Save deleted for reference
with open('deleted_projects_today.json', 'w', encoding='utf-8') as f:
    json.dump(delete, f, ensure_ascii=False, indent=2)

print(f"\n已保存 work_current_projects.json ({len(keep)} 个项目)")
