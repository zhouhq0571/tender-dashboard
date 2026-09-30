import json, re, sys
from datetime import datetime, timedelta

html = open('index.html', 'r', encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
if not m:
    print("ERROR: Could not find tender-data JSON")
    sys.exit(1)

data = json.loads(m.group(1))
projects = data.get('projects', [])

print(f"Version: {data.get('version')}")
print(f"Date: {data.get('date')}")
print(f"TimePeriod: {data.get('timePeriod')}")
print(f"Total projects: {len(projects)}")
print()

# Check deadlines
today = datetime(2026, 8, 11).date()
yesterday = today - timedelta(days=1)

to_delete = []
to_mark_expired = []
to_keep = []

for p in projects:
    deadline_str = p.get('deadline', '')
    if not deadline_str or deadline_str == '-':
        to_keep.append(p)
        continue
    
    # Parse deadline
    has_time = ' ' in deadline_str and ':' in deadline_str
    try:
        if has_time:
            dl = datetime.strptime(deadline_str, '%Y-%m-%d %H:%M').date()
        else:
            dl = datetime.strptime(deadline_str, '%Y-%m-%d').date()
    except:
        to_keep.append(p)
        continue
    
    # Rule: delete if deadline < yesterday (i.e., deadline <= today - 2 days)
    if dl < yesterday:
        to_delete.append({
            'id': p.get('id'),
            'company': p.get('company'),
            'project': p.get('project')[:40],
            'deadline': deadline_str,
            'reason': f'deadline {dl} < yesterday {yesterday}'
        })
    else:
        to_keep.append(p)

print(f"=== DELETE ({len(to_delete)} projects) ===")
for d in to_delete:
    print(f"  ID {d['id']}: {d['company']} - {d['project']}... | deadline: {d['deadline']}")

print(f"\n=== KEEP ({len(to_keep)} projects) ===")
print(f"  (Projects with deadline >= {yesterday} are kept)")

# Save results
with open('_expired_analysis.json', 'w', encoding='utf-8') as f:
    json.dump({
        'to_delete': to_delete,
        'to_keep_count': len(to_keep),
        'deleted_count': len(to_delete),
        'today': str(today),
        'yesterday': str(yesterday)
    }, f, ensure_ascii=False, indent=2)

print(f"\nSaved analysis to _expired_analysis.json")
