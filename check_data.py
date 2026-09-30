import re, json, sys
from datetime import datetime, timedelta

html = open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))

print(f"version={data['version']}")
print(f"date={data['date']}")
print(f"timePeriod={data['timePeriod']}")
print(f"projects={len(data['projects'])}")

# Check for expired projects (deadline < yesterday = 2026-08-08)
today = datetime(2026, 8, 9).date()
yesterday = today - timedelta(days=1)
expired = []
for p in data['projects']:
    dl = p.get('deadline', '')
    if dl:
        try:
            if ' ' in dl:
                dl_date = datetime.strptime(dl.split(' ')[0], '%Y-%m-%d').date()
            else:
                dl_date = datetime.strptime(dl, '%Y-%m-%d').date()
            if dl_date < yesterday:
                expired.append((p.get('company',''), p.get('project','')[:30], dl))
        except:
            pass

print(f"expired_count={len(expired)}")
for e in expired:
    print(f"EXPIRED: {e[0]} | {e[1]} | {e[2]}")
