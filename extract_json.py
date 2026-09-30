import re, json, sys

fpath = sys.argv[1] if len(sys.argv) > 1 else 'index.html'
html = open(fpath, 'r', encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
if not m:
    print("ERROR: JSON not found")
    sys.exit(1)
data = json.loads(m.group(1))
print(f"version={data.get('version','?')}")
print(f"date={data.get('date','?')}")
print(f"timePeriod={data.get('timePeriod','?')}")
projects = data.get('projects', [])
print(f"count={len(projects)}")
print("-"*60)
for i, p in enumerate(projects):
    print(f"{i+1}. {p.get('company','?')} | {p.get('project','?')[:40]} | {p.get('deadline','?')} | {p.get('rec','?')}")
