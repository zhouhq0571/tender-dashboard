import re, json, os
from datetime import datetime, timedelta

WORKSPACE_DIR = "/Users/zhouhq/Documents/kimi/workspace/bidding-daily"
HTML_PATH = f"{WORKSPACE_DIR}/index.html"

def load_data():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'<script type="application/json" id="tender-data">(.+?)</script>', html, re.DOTALL)
    return json.loads(m.group(1)), html

def deadline_date(d):
    try:
        return datetime.strptime(d.strip()[:10], '%Y-%m-%d').date()
    except:
        return None

data, html = load_data()
projects = data['projects']
today = datetime.now().date()
before_yesterday = today - timedelta(days=2)

print(f"处理前项目数: {len(projects)}")

# 1. 删除无效deadline项目和过期项目
new_projects = []
deleted = []
for p in projects:
    dd = deadline_date(p.get('deadline', ''))
    if dd is None or dd < before_yesterday:
        deleted.append(p)
        continue
    new_projects.append(p)

print(f"删除项目数: {len(deleted)}")
for p in deleted:
    print(f"  删除 id={p['id']}: {p['company']} | {p['project']} | deadline={p.get('deadline')}")

# 2. 标记已截止项目
marked = []
for p in new_projects:
    dl = p.get('deadline', '').strip()
    dd = deadline_date(dl)
    if dd is None:
        continue
    
    is_expired = False
    if ' ' in dl:
        try:
            dt = datetime.strptime(dl, '%Y-%m-%d %H:%M')
            if dt < datetime.now():
                is_expired = True
        except:
            pass
    else:
        if dd < today:
            is_expired = True
    
    if is_expired and '已截止' not in p.get('rec', ''):
        old_rec = p['rec']
        p['rec'] = '☆☆☆ 已截止'
        marked.append((p['id'], p['company'], p['project'], old_rec, p['rec']))

print(f"\n标记已截止项目数: {len(marked)}")
for item in marked:
    print(f"  id={item[0]}: {item[1]} | {item[2]} | {item[3]} -> {item[4]}")

# 3. 重新分配id
for i, p in enumerate(new_projects, 1):
    p['id'] = i

print(f"\n处理后项目数: {len(new_projects)}")

# 4. 更新JSON数据
data['projects'] = new_projects
data['date'] = '2026年08月06日'
data['timePeriod'] = '上午'
data['version'] = 'v127'

json_str = json.dumps(data, ensure_ascii=False, indent=2)

# 替换HTML中的JSON
new_html = re.sub(
    r'<script type="application/json" id="tender-data">.+?</script>',
    f'<script type="application/json" id="tender-data">{json_str}</script>',
    html, flags=re.DOTALL
)

# 更新封面日期
new_html = new_html.replace('2026年08月05日 早上', '2026年08月06日 上午')
# 更新封底日期
new_html = new_html.replace('2026年08月05日 早上', '2026年08月06日 上午')
# 更新title
new_html = new_html.replace('2026年08月05日（更新）v126', '2026年08月06日（更新）v127')

with open(HTML_PATH, 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"\n已更新 {HTML_PATH}")
print(f"新版本: v127, 日期: 2026年08月06日 上午, 项目数: {len(new_projects)}")
