import json
from datetime import datetime

today_date = datetime(2026, 8, 15).date()

text = open('index.html', 'r', encoding='utf-8').read()
start = text.find('<script type="application/json" id="tender-data">')
start = text.find('{', start)
end = text.find('</script>', start)
json_text = text[start:end].strip()
data = json.loads(json_text)
projects = data.get('projects', [])

def parse_deadline_date(dl):
    if not dl or dl == '-':
        return None
    try:
        return datetime.strptime(dl[:10], '%Y-%m-%d').date()
    except ValueError:
        return None

to_delete = []
to_mark = []
to_keep = []

for p in projects:
    dl = p.get('deadline', '')
    dl_date = parse_deadline_date(dl)
    if not dl_date:
        to_keep.append(p)
        continue
    
    delta_days = (today_date - dl_date).days
    if delta_days >= 2:
        to_delete.append(p)
    elif delta_days == 1:  # 昨天过期 → 标记已截止
        to_mark.append(p)
        p['rec'] = '☆☆☆ 已截止'
        to_keep.append(p)
    else:
        to_keep.append(p)

print(f"删除: {len(to_delete)} 个")
for p in to_delete:
    print(f"  - {p['company']} | {p['project']} | {p['deadline']}")

print(f"\n标记已截止: {len(to_mark)} 个")
for p in to_mark:
    print(f"  - {p['company']} | {p['project']} | {p['deadline']}")

print(f"\n保留: {len(to_keep)} 个")

data['projects'] = to_keep
new_json = json.dumps(data, ensure_ascii=False, indent=2)
new_html = text[:start] + new_json + text[end:]
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("\nindex.html 已更新")
