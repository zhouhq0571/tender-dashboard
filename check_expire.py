import re, json, sys, os
from datetime import datetime, timedelta

WORKSPACE_DIR = "/Users/zhouhq/Documents/kimi/workspace/bidding-daily"
HTML_PATH = f"{WORKSPACE_DIR}/index.html"

def load_data():
    with open(HTML_PATH, 'r', encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'<script type="application/json" id="tender-data">(.+?)</script>', html, re.DOTALL)
    return json.loads(m.group(1))

def deadline_date(d):
    try:
        return datetime.strptime(d.strip()[:10], '%Y-%m-%d').date()
    except:
        return None

data = load_data()
print(f"版本: {data.get('version')}")
print(f"日期: {data.get('date')}")
print(f"时间段: {data.get('timePeriod')}")
print(f"项目总数: {len(data['projects'])}")
print()

today = datetime.now().date()
yesterday = today - timedelta(days=1)
before_yesterday = today - timedelta(days=2)

print(f"今天: {today}")
print(f"昨天: {yesterday}")
print()

to_delete = []
to_mark = []
keep = []

for p in data['projects']:
    dd = deadline_date(p.get('deadline', ''))
    if dd is None:
        print(f"  [无效deadline] id={p['id']}: {p['company']} | {p['project']} | deadline='{p.get('deadline','')}'")
        continue
    
    if dd < before_yesterday:
        to_delete.append(p)
    else:
        keep.append(p)
    
    # 标记判断
    dl = p.get('deadline','').strip()
    if ' ' in dl:
        # 含时间
        try:
            dt = datetime.strptime(dl, '%Y-%m-%d %H:%M')
            if dt < datetime.now():
                if '已截止' not in p.get('rec',''):
                    to_mark.append((p['id'], p['company'], p['project'], '已截止'))
        except:
            pass
    else:
        # 仅日期，视为23:59
        if dd < today:
            if '已截止' not in p.get('rec',''):
                to_mark.append((p['id'], p['company'], p['project'], '已截止(日期已过)'))

print(f"\n===== 待删除项目（deadline < {before_yesterday}） =====")
for p in to_delete:
    print(f"  id={p['id']}: {p['company']} | {p['project']} | deadline={p.get('deadline')}")

print(f"\n===== 待标记已截止项目 =====")
for item in to_mark:
    print(f"  id={item[0]}: {item[1]} | {item[2]} | {item[3]}")

print(f"\n===== 保留项目数: {len(keep)} =====")
