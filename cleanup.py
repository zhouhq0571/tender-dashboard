import re, json, sys
from datetime import datetime, timedelta

HTML_PATH = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html'

def parse_deadline(dl_str):
    """Parse deadline string to date."""
    if not dl_str or dl_str in ('-', '未披露', '投标截止日期'):
        return None
    try:
        if ' ' in dl_str:
            return datetime.strptime(dl_str.split(' ')[0], '%Y-%m-%d').date()
        else:
            return datetime.strptime(dl_str, '%Y-%m-%d').date()
    except:
        return None

def get_rec_for_deadline(dl_str, original_rec):
    """Determine rec based on deadline vs current time."""
    dl_date = parse_deadline(dl_str)
    if not dl_date:
        return original_rec
    
    today = datetime(2026, 8, 9).date()
    now = datetime(2026, 8, 9, 6, 0)  # Current time: 2026-08-09 06:00
    
    # If deadline date is before yesterday (< today - 1 day), this project should be deleted
    if dl_date < today - timedelta(days=1):
        return 'DELETE'
    
    # If deadline is yesterday or earlier (but not before yesterday), mark as expired
    if dl_date < today:
        return '☆☆☆ 已截止'
    
    # If deadline is today
    if dl_date == today:
        # Check if it has specific time
        if ' ' in dl_str:
            try:
                dl_dt = datetime.strptime(dl_str, '%Y-%m-%d %H:%M')
                if dl_dt < now:
                    return '☆☆☆ 已截止'
                else:
                    # Keep original rec but remove any expired marking
                    if '已截止' in original_rec:
                        return '★☆☆ 可关注'
                    return original_rec
            except:
                pass
        # Date-only: treat as 23:59, so not expired yet today
        if '已截止' in original_rec:
            return '★☆☆ 可关注'
        return original_rec
    
    # Future deadline - keep original rec if not expired
    if '已截止' in original_rec:
        return '★☆☆ 可关注'
    return original_rec

html = open(HTML_PATH).read()
m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))

original_count = len(data['projects'])
kept = []
deleted = []
updated = []

for p in data['projects']:
    dl = p.get('deadline', '')
    new_rec = get_rec_for_deadline(dl, p.get('rec', ''))
    
    if new_rec == 'DELETE':
        deleted.append((p.get('company', ''), p.get('project', '')[:40], dl))
    else:
        if new_rec != p.get('rec', ''):
            updated.append((p.get('company', ''), p.get('project', '')[:40], dl, p.get('rec', ''), new_rec))
            p['rec'] = new_rec
        kept.append(p)

data['projects'] = kept

print(f"原始项目数: {original_count}")
print(f"删除项目数: {len(deleted)}")
print(f"更新状态数: {len(updated)}")
print(f"保留项目数: {len(kept)}")
print()
print("=== 删除的项目 ===")
for d in deleted:
    print(f"  {d[0]} | {d[1]} | {d[2]}")
print()
print("=== 状态更新的项目 ===")
for u in updated:
    print(f"  {u[0]} | {u[1]} | {u[2]} | {u[3]} -> {u[4]}")

# Save cleaned data back to a temp file for later use
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/cleaned_data.json', 'w') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print()
print("清理后的数据已保存到 cleaned_data.json")
