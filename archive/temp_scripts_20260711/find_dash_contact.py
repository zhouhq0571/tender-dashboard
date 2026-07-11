import json, re

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', c, re.DOTALL)
data = json.loads(m.group(1))

# Find project with contact='-'
for p in data['projects']:
    if p.get('contact') == '-':
        print(f"ID: {p['id']}")
        print(f"Company: {p['company']}")
        print(f"Project: {p['project']}")
        print(f"URL: {p['url']}")
        print(f"Contact: {p['contact']}")
        print(f"Source: {p.get('source', '')}")
