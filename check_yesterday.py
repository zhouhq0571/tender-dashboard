import json, re
from datetime import datetime, timedelta

html = open('index.html', 'r', encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))
projects = data.get('projects', [])

today = datetime(2026, 8, 11).date()
yesterday = today - timedelta(days=1)

print("Projects with deadline on or before yesterday (2026-08-10):")
for p in projects:
    dl_str = p.get('deadline', '')
    if not dl_str or dl_str == '-':
        continue
    try:
        if ' ' in dl_str and ':' in dl_str:
            dl = datetime.strptime(dl_str, '%Y-%m-%d %H:%M').date()
        else:
            dl = datetime.strptime(dl_str, '%Y-%m-%d').date()
    except:
        continue
    
    if dl <= yesterday:
        print(f"  ID {p['id']}: {p['company']} | {p['project'][:50]}... | deadline: {dl_str} | current rec: {p.get('rec')}")
