#!/usr/bin/env python3
import json, re, datetime

with open('index.html') as f:
    html = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
data = json.loads(m.group(1).strip())

today = datetime.date(2026, 8, 10)
yesterday = today - datetime.timedelta(days=1)

expired = []
for p in data.get('projects', []):
    dl = p.get('deadline', '')
    c = p.get('company', '')
    if dl and dl != '-':
        try:
            dld = datetime.datetime.strptime(dl[:10], '%Y-%m-%d').date()
            if dld < yesterday:
                expired.append((c, p.get('project', '')[:40], dl))
        except:
            pass

print(f"过期项目数: {len(expired)}")
for c, pr, dl in expired:
    print(f"  {c} | {pr} | {dl}")
