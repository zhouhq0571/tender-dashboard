import json, re
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
if not match:
    print("ERROR: Cannot parse index.html")
    exit(1)
data = json.loads(match.group(1))
print(f"Version: {data.get('version', 'N/A')}")
print(f"Date: {data.get('date', 'N/A')}")
print(f"TimePeriod: {data.get('timePeriod', 'N/A')}")
print(f"Projects count: {len(data.get('projects', []))}")

# Check ID continuity
projects = data.get('projects', [])
ids = [int(p.get('id', 0)) for p in projects if 'id' in p]
if not ids:
    print("WARNING: No 'id' field found in projects")
else:
    expected = list(range(1, len(projects) + 1))
    is_continuous = sorted(ids) == expected
    print(f"ID continuous: {is_continuous}")
    print(f"ID range: {min(ids)} - {max(ids)}")
    print(f"Expected: 1 - {len(projects)}")
    
# Check for missing id
no_id = [i for i, p in enumerate(projects) if 'id' not in p]
print(f"Projects without 'id': {len(no_id)}")
if no_id:
    for i in no_id[:3]:
        print(f"  idx={i}: {projects[i].get('company','?')} - {projects[i].get('project','?')[:30]}")

# Check rec values
recs = set(p.get('rec', '') for p in projects)
print(f"Unique rec values: {recs}")

# Check tags
tags = set()
for p in projects:
    for t in p.get('tags', []):
        tags.add(t)
print(f"Unique tags: {tags}")

# Check deadline formats
invalid_dl = []
for p in projects:
    dl = p.get('deadline', '')
    if dl == '-' or not dl:
        invalid_dl.append((p.get('company','?'), p.get('project','?')[:20], dl))
print(f"Invalid deadlines: {len(invalid_dl)}")

# Check source field
no_source = [p.get('company','?') for p in projects if not p.get('source')]
print(f"Projects without source: {len(no_source)}")

# Check overview '-' 
dash_overview = [p.get('company','?') for p in projects if p.get('overview') == '-']
print(f"Projects with overview='-': {len(dash_overview)}")

# Check contact '-' 
dash_contact = [p.get('company','?') for p in projects if p.get('contact') == '-']
print(f"Projects with contact='-': {len(dash_contact)}")

# Check duplicate companies+projects
seen = {}
dupes = []
for p in projects:
    key = p.get('company','') + '|' + p.get('project','')[:15]
    if key in seen:
        dupes.append((key, seen[key], p.get('id', '?')))
    seen[key] = p.get('id', '?')
print(f"Duplicates: {len(dupes)}")

# Check region/province consistency
VALID_REGIONS = {'东北', '华北', '西北', '华东', '华中', '西南', '华南'}
region_province_map = {
    '东北': ['黑龙江', '吉林', '辽宁'],
    '华北': ['内蒙古', '北京', '天津', '河北', '山西'],
    '西北': ['陕西', '甘肃', '宁夏', '青海', '新疆'],
    '华东': ['山东', '江苏', '浙江', '安徽', '福建', '江西', '上海'],
    '华中': ['河南', '湖北', '湖南'],
    '西南': ['重庆', '四川', '贵州', '云南', '西藏'],
    '华南': ['广东', '广西', '海南'],
}
region_issues = []
for p in projects:
    r, prov = p.get('region', ''), p.get('province', '')
    if r in region_province_map and prov not in region_province_map[r]:
        region_issues.append((p.get('company','?'), r, prov))
print(f"Region/province issues: {len(region_issues)}")

# Check stale projects
from datetime import datetime, date, timedelta
today = date.today()
cutoff = today - timedelta(days=2)
stale = []
for p in projects:
    rec = p.get('rec', '')
    if '已截止' not in rec:
        continue
    dl = p.get('deadline', '')
    m = re.search(r'(\d{4}-\d{2}-\d{2})', str(dl))
    if m:
        dl_date = datetime.strptime(m.group(1), '%Y-%m-%d').date()
        if dl_date < cutoff:
            stale.append((p.get('company','?'), dl))
print(f"Stale cutoff projects: {len(stale)}")

# Check title
title_match = re.search(r'<title>(.*?)</title>', content)
if title_match:
    print(f"Title: {title_match.group(1)[:60]}")
    print(f"Title contains version: {data.get('version','') in title_match.group(1)}")
    print(f"Title contains date: {data.get('date','') in title_match.group(1)}")
