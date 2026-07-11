import json, re

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', c, re.DOTALL)
data = json.loads(m.group(1))

# Find project with contact='-' and update it
for p in data['projects']:
    if p.get('contact') == '-':
        print(f"Updating ID {p['id']}: {p['company']} - {p['project']}")
        # Update contact with available info from fetch
        p['contact'] = '联系方式：19*******37（需登录水滴标讯查看完整联系方式）'
        print(f"New contact: {p['contact']}")

# Write back
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_content = c.replace(m.group(1), new_json)

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated index.html")
