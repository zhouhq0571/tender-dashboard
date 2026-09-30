import json, re

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html') as f:
    html = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))

# Check for companies
companies_to_check = ['湖北银行', '重庆农商', '重庆农村商业银行', '渤海银行', '光大银行']
for c in companies_to_check:
    matches = [p for p in data['projects'] if c in p.get('company', '')]
    print(f"{c}: {len(matches)} projects")
    for m in matches:
        print(f"  - {m.get('project','')[:50]} | {m.get('deadline','')}")
    print()
