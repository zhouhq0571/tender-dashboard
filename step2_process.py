import json
from datetime import datetime, timedelta
import re

data = json.load(open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/current_data.json'))
projects = data['projects']

today = datetime(2026, 7, 31)
yesterday = today - timedelta(days=1)

deleted_projects = []
remaining_projects = []

for p in projects:
    dl = p['deadline']
    try:
        dl_date = datetime.strptime(dl, '%Y-%m-%d %H:%M')
    except:
        try:
            dl_date = datetime.strptime(dl, '%Y-%m-%d')
        except:
            remaining_projects.append(p)
            continue
    
    if dl_date.date() < yesterday.date():
        deleted_projects.append(p)
    else:
        remaining_projects.append(p)

print(f"Deleted: {len(deleted_projects)} projects")
print(f"Remaining before rec update: {len(remaining_projects)} projects")

# Now update rec for expired projects (deadline date < today, but kept per rules)
# For date-only deadlines: if deadline date < today, mark as expired
# For time deadlines: if deadline datetime < now, mark as expired
now = datetime(2026, 7, 31, 6, 0)

for p in remaining_projects:
    dl = p['deadline']
    try:
        dl_dt = datetime.strptime(dl, '%Y-%m-%d %H:%M')
        if dl_dt < now:
            if '☆☆☆ 已截止' not in p['rec']:
                p['rec'] = '☆☆☆ 已截止'
                print(f"  Updated rec to expired: {p['company']} - {dl}")
    except:
        try:
            dl_date = datetime.strptime(dl, '%Y-%m-%d').date()
            if dl_date < today.date():
                if '☆☆☆ 已截止' not in p['rec']:
                    p['rec'] = '☆☆☆ 已截止'
                    print(f"  Updated rec to expired: {p['company']} - {dl}")
        except:
            pass

# Save updated data
data['projects'] = remaining_projects
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/updated_projects.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\nFinal remaining: {len(remaining_projects)} projects")
print(f"Deleted list saved")
