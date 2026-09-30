#!/usr/bin/env python3
import json, re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

json_match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
data = json.loads(json_match.group(1))

for p in data['projects']:
    if '接口总线' in p['project'] or '杭州工商信托' in p['company']:
        print(f"ID {p['id']}: {p['company']} - {p['project']}")
        print(f"  Budget: {p['budget']}, Deadline: {p['deadline']}, URL: {p['url']}")
        print()
