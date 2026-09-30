import re, json

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r') as f:
    html = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))
projects = data.get('projects', [])

print(f'Total projects: {len(projects)}')
print('=== EXISTING PROJECTS (company|project|deadline) ===')
for p in projects:
    company = p.get('company', '?')[:8]
    project = p.get('project', '?')[:22]
    deadline = p.get('deadline', '?')[:10]
    print(f'{company}|{project}|{deadline}')
