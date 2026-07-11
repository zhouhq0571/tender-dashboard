import json, re
from collections import Counter

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()
match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', content, re.DOTALL)
data = json.loads(match.group(1))
projects = data.get('projects', [])

print('=== 缺少 ID 的项目 ===')
for i, p in enumerate(projects):
    if 'id' not in p:
        print(f'  idx={i}: {p.get("company", "?")} - {p.get("project", "?")[:50]}')

print('\n=== 重复项目（company+project前15字）===')
seen = {}
for p in projects:
    key = p.get('company', '') + '|' + p.get('project', '')[:15]
    if key in seen:
        print(f'  DUPE: {key} (id {seen[key]} vs {p.get("id", "N/A")})')
    seen[key] = p.get('id', '?')

print('\n=== 完整重复（company+project全名）===')
seen2 = {}
for p in projects:
    key = p.get('company', '') + '|' + p.get('project', '')
    if key in seen2:
        print(f'  DUPE: {key} (id {seen2[key]} vs {p.get("id", "N/A")})')
    seen2[key] = p.get('id', '?')

print('\n=== 投标建议分布 ===')
for rec, cnt in sorted(Counter(p.get('rec', 'N/A') for p in projects).items()):
    print(f'  {rec}: {cnt}')

print('\n=== 大区分布 ===')
for r, cnt in sorted(Counter(p.get('region', 'N/A') for p in projects).items()):
    print(f'  {r}: {cnt}')

print('\n=== 招标方式分布 ===')
for m, cnt in sorted(Counter(p.get('method', 'N/A') for p in projects).items()):
    print(f'  {m}: {cnt}')

print('\n=== 项目名称为空或过短 ===')
for i, p in enumerate(projects):
    proj = p.get('project', '')
    if len(proj) < 5:
        print(f'  idx={i}: {p.get("company", "?")} - "{proj}"')

print('\n=== URL 为空或异常 ===')
for i, p in enumerate(projects):
    url = p.get('url', '')
    if not url or url == '-' or not url.startswith('http'):
        print(f'  idx={i}: {p.get("company", "?")} - url="{url}"')
