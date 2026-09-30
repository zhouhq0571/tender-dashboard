import json, re
from datetime import datetime, timedelta

# Read current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract JSON data
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))
projects = data.get('projects', [])

today = datetime(2026, 8, 11).date()
yesterday = today - timedelta(days=1)

# Track changes
deleted = []
marked_expired = []

new_projects = []
for p in projects:
    dl_str = p.get('deadline', '')
    pid = p.get('id')
    
    # Check if should delete (deadline <= 2026-08-09, i.e., 2+ days before today)
    should_delete = False
    if dl_str and dl_str != '-':
        try:
            if ' ' in dl_str and ':' in dl_str:
                dl = datetime.strptime(dl_str, '%Y-%m-%d %H:%M').date()
            else:
                dl = datetime.strptime(dl_str, '%Y-%m-%d').date()
            
            if dl < yesterday:  # deadline <= 2026-08-09
                should_delete = True
                deleted.append({
                    'id': pid,
                    'company': p.get('company'),
                    'project': p.get('project'),
                    'deadline': dl_str
                })
            elif dl == yesterday:  # deadline = 2026-08-10
                # Mark as expired
                if p.get('rec') != '☆☆☆ 已截止':
                    marked_expired.append({
                        'id': pid,
                        'company': p.get('company'),
                        'project': p.get('project')[:40],
                        'deadline': dl_str,
                        'old_rec': p.get('rec')
                    })
                    p['rec'] = '☆☆☆ 已截止'
                new_projects.append(p)
            else:
                new_projects.append(p)
        except:
            new_projects.append(p)
    else:
        new_projects.append(p)

# Reassign IDs sequentially
for i, p in enumerate(new_projects, 1):
    p['id'] = i

# Update metadata
data['projects'] = new_projects
data['version'] = 'v144'
data['date'] = '2026年08月11日'
data['timePeriod'] = '上午'

# Re-serialize JSON
json_str = json.dumps(data, ensure_ascii=False, indent=2)

# Replace JSON in HTML
new_html = re.sub(
    r'<script type="application/json" id="tender-data">.*?</script>',
    f'<script type="application/json" id="tender-data">{json_str}</script>',
    html,
    flags=re.DOTALL
)

# Update cover time
new_html = re.sub(
    r'<div class="cover-meta" id="cover-update-time">.*?</div>',
    '<div class="cover-meta" id="cover-update-time">数据更新时间：2026年08月11日 上午</div>',
    new_html
)

# Update footer time
new_html = re.sub(
    r'<span id="footer-update-time">.*?</span>',
    '<span id="footer-update-time">2026年08月11日 上午</span>',
    new_html
)

# Update title
new_html = re.sub(
    r'<title>.*?</title>',
    '<title>恒生银信招标资讯每日速递 | 2026年08月11日（更新）v144</title>',
    new_html
)

# Write back
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"Deleted projects: {len(deleted)}")
for d in deleted:
    print(f"  ID {d['id']}: {d['company']} - {d['project'][:50]} (deadline: {d['deadline']})")

print(f"\nMarked as expired: {len(marked_expired)}")
for e in marked_expired:
    print(f"  ID {e['id']}: {e['company']} - {e['project']} (deadline: {e['deadline']}, was: {e['old_rec']})")

print(f"\nRemaining projects: {len(new_projects)}")
print(f"Version: {data['version']}")
print(f"Date: {data['date']}")
print(f"TimePeriod: {data['timePeriod']}")
