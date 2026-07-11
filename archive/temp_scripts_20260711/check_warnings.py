import json, re

with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', c, re.DOTALL)
data = json.loads(m.group(1))

# Check for duplicates with different key matching
print("=== 查找重复项目（使用更精确的匹配） ===")
seen = {}
dups = []
for p in data['projects']:
    # Use first 15 chars of project name + company
    key = p.get('company', '') + '|' + p.get('project', '')[:15]
    if key in seen:
        dups.append((seen[key], p['id'], key, p.get('project', '')))
    seen[key] = p['id']

for d in dups:
    print(f"重复: ID {d[0]} vs ID {d[1]} - {d[2]}")
    print(f"  完整名称: {d[3]}")

# Also check with shorter key
print("\n=== 使用更短的项目名匹配 ===")
seen2 = {}
for p in data['projects']:
    key = p.get('company', '') + '|' + p.get('project', '')[:20]
    if key in seen2:
        print(f"可能重复: ID {seen2[key]} vs ID {p['id']} - {key}")
    seen2[key] = p['id']
