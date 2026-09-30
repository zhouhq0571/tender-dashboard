import json, re, os, sys
from datetime import datetime

html = open('index.html').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
if not m:
    print("ERROR: cannot find tender-data")
    sys.exit(1)

data = json.loads(m.group(1))
projects = data.get('projects', [])

print(f"项目总数: {len(projects)}")
print(f"版本号: {data.get('version', '?')}")
print(f"日期: {data.get('date', '?')}")
print(f"timePeriod: {data.get('timePeriod', '?')}")
print(f"项目ID范围: {min(p['id'] for p in projects)} - {max(p['id'] for p in projects)}")

TODAY = '2026-07-26'
YESTERDAY = '2026-07-25'

to_delete = []
today_yesterday = []
keep = []

for p in projects:
    dl = p.get('deadline', '')
    dl_date = dl.split(' ')[0] if dl else ''
    if dl_date < YESTERDAY:
        to_delete.append(p)
    elif dl_date in (YESTERDAY, TODAY):
        today_yesterday.append(p)
    else:
        keep.append(p)

print(f"\n=== 删除决策 ===")
print(f"待删除项目(deadline < {YESTERDAY}): {len(to_delete)} 个")
for p in to_delete:
    print(f"  id={p['id']:3d} {p['company']:12s} {p['project'][:30]:30s} deadline={p['deadline']}")

print(f"\n保留项目(今天/昨天截止): {len(today_yesterday)} 个")
for p in today_yesterday:
    print(f"  id={p['id']:3d} {p['company']:12s} {p['project'][:30]:30s} deadline={p['deadline']} rec={p.get('rec','')}")

print(f"\n保留项目(未来截止): {len(keep)} 个")

# Save baseline
with open('baseline_before_update.json', 'w') as f:
    json.dump({'projects': projects, 'version': data.get('version'), 'date': data.get('date')}, f, ensure_ascii=False, indent=2)
print(f"\n基准数据已保存到 baseline_before_update.json")

# Save deletion list for reporting
with open('deleted_projects.json', 'w') as f:
    json.dump(to_delete, f, ensure_ascii=False, indent=2)
print(f"删除列表已保存到 deleted_projects.json")
