import re, json, sys
from datetime import datetime, timedelta

TODAY = datetime(2026, 8, 7)
YESTERDAY = TODAY - timedelta(days=1)  # 2026-08-06
DELETE_CUTOFF = TODAY - timedelta(days=2)  # 2026-08-05

def parse_deadline(dl_str):
    """解析截止日期，返回datetime或None"""
    if not dl_str or dl_str in ('未披露', '-', '投标截止日期'):
        return None
    # 清理括号内容
    dl_clean = re.sub(r'[（(].*?[）)]', '', str(dl_str)).strip()
    for fmt in ('%Y-%m-%d %H:%M', '%Y-%m-%d'):
        try:
            return datetime.strptime(dl_clean, fmt)
        except ValueError:
            continue
    return None

# 读取HTML
html = open('index.html', 'r', encoding='utf-8').read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.S)
data = json.loads(m.group(1))
projects = data.get('projects', [])

original_count = len(projects)
print(f"原始项目数: {original_count}")
print(f"今天: {TODAY.strftime('%Y-%m-%d')}")
print(f"昨天: {YESTERDAY.strftime('%Y-%m-%d')}")
print(f"删除 cutoff (deadline < {DELETE_CUTOFF.strftime('%Y-%m-%d')}): 删除")
print("-" * 60)

kept = []
deleted = []

for p in projects:
    dl_str = p.get('deadline', '')
    dl_dt = parse_deadline(dl_str)
    
    if dl_dt is None:
        # 无效截止日期，保留但标记
        kept.append(p)
        continue
    
    dl_date = dl_dt.date()
    today_date = TODAY.date()
    yesterday_date = YESTERDAY.date()
    cutoff_date = DELETE_CUTOFF.date()
    
    if dl_date < cutoff_date:
        deleted.append(p)
        print(f"❌ 删除: {p.get('company','?')} | {p.get('project','?')[:35]} | {dl_str}")
    else:
        kept.append(p)

print("-" * 60)
print(f"删除项目数: {len(deleted)}")
print(f"保留项目数: {len(kept)}")

# 备份原始数据
backup_file = f'backup/baseline_v127_{TODAY.strftime("%Y%m%d")}.json'
import os
os.makedirs('backup', exist_ok=True)
with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f"备份已保存: {backup_file}")

# 更新数据
data['projects'] = kept
data['version'] = 'v128'
data['date'] = '2026年08月07日'
data['timePeriod'] = '上午'

# 写回HTML
json_str = json.dumps(data, ensure_ascii=False, indent=2)
new_html = html[:m.start()] + '<script type="application/json" id="tender-data">' + json_str + '</script>' + html[m.end():]

# 更新静态日期文本和时间词
old_date = '2026年08月06日'
new_date = '2026年08月07日'
old_period = '上午'
new_period = '上午'  # 06:00 属于上午

# 更新封面/封底时间
new_html = new_html.replace(f'{old_date} {old_period}', f'{new_date} {new_period}')
# 也替换单独的日期（如果前面没匹配到完整的）
new_html = new_html.replace(old_date, new_date)

# 更新 title
new_html = new_html.replace('2026年08月06日（更新）v127', '2026年08月07日（更新）v128')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"已更新 index.html: version=v128, date=2026年08月07日, count={len(kept)}")
