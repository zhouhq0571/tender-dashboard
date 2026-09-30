import sys, json, re

html = sys.stdin.read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))

print(f"Version: {data.get('version')}")
print(f"Date: {data.get('date')}")
print(f"Period: {data.get('timePeriod')}")
print(f"Projects: {len(data.get('projects', []))}")
print("---")

for p in data['projects']:
    if '海南' in p.get('company', ''):
        print(f"ID {p['id']}: {p['company']} - {p['project']}")
        print(f"  预算: {p.get('budget')}")
        print(f"  截止: {p.get('deadline')}")
        print(f"  建议: {p.get('rec')}")
        print(f"  标签: {p.get('tags')}")
