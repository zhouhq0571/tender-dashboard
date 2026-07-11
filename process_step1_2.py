# -*- coding: utf-8 -*-
import json
from datetime import datetime
import re

# 当前时间
now = datetime(2026, 7, 1, 7, 30, 31)
today = now.date()  # 2026-07-01
yesterday = datetime(2026, 6, 30).date()  # 2026-06-30

print(f"当前时间: {now}")
print(f"今天: {today}")
print(f"昨天: {yesterday}")

# 从HTML文件提取JSON数据
html_path = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html'
with open(html_path, 'r', encoding='utf-8') as f:
    html_content = f.read()

# 提取 tender-data JSON
match = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html_content, re.DOTALL)
if not match:
    print("未找到 tender-data JSON")
    exit(1)

data = json.loads(match.group(1))
projects = data.get('projects', [])

print(f"现有项目总数: {len(projects)}")
print(f"版本: {data.get('version', '未知')}")
print(f"日期: {data.get('date', '未知')}")

def parse_deadline(d):
    """解析截止日期，返回日期部分和是否含时间"""
    if not d or d == "-":
        return None, False
    if "另行通知" in d:
        return None, False
    m = re.match(r'(\d{4}-\d{2}-\d{2})', str(d))
    if not m:
        return None, False
    date_part = datetime.strptime(m.group(1), "%Y-%m-%d").date()
    has_time = bool(re.search(r'\d{1,2}:\d{2}', str(d)))
    return date_part, has_time

# 步骤1：删除过期项目（deadline < 昨天）
removed = []
kept = []
for p in projects:
    dl_date, has_time = parse_deadline(p.get('deadline', ''))
    if dl_date is None:
        kept.append(p)
        continue
    if dl_date < yesterday:
        removed.append(p)
    else:
        kept.append(p)

print(f"\n步骤1：删除已过期项目")
print(f"  删除项目数: {len(removed)}")
for p in removed:
    print(f"    - id={p['id']}: {p['company']} | {p['deadline']}")
print(f"  保留项目数: {len(kept)}")

# 步骤2：更新投标建议标记
updated_rec = []
for p in kept:
    dl_date, has_time = parse_deadline(p.get('deadline', ''))
    if dl_date is None:
        continue
    
    old_rec = p['rec']
    new_rec = old_rec
    
    if dl_date == today and has_time:
        # 今天含具体时间
        dl_time = re.search(r'(\d{4}-\d{2}-\d{2})\s+(\d{1,2}):(\d{2})', str(p['deadline']))
        if dl_time:
            dl_hour = int(dl_time.group(2))
            dl_min = int(dl_time.group(3))
            if dl_hour < 7 or (dl_hour == 7 and dl_min <= 30):
                new_rec = "\u2606\u2606\u2606 \u5df2\u622a\u6b62"
    elif dl_date == yesterday and has_time:
        # 昨天含具体时间 -> 已截止
        new_rec = "\u2606\u2606\u2606 \u5df2\u622a\u6b62"
    elif dl_date == yesterday and not has_time:
        # 昨天日期-only -> 已截止
        new_rec = "\u2606\u2606\u2606 \u5df2\u622a\u6b62"
    elif dl_date < today and not has_time:
        # 早于今天的日期-only -> 已截止
        new_rec = "\u2606\u2606\u2606 \u5df2\u622a\u6b62"
    
    if new_rec != old_rec:
        p['rec'] = new_rec
        updated_rec.append((p['id'], p['company'], old_rec, new_rec, p['deadline']))

print(f"\n步骤2：更新投标建议标记")
print(f"  更新项目数: {len(updated_rec)}")
for item in updated_rec:
    print(f"    - id={item[0]}: {item[1]} | {item[2]} -> {item[3]} | deadline={item[4]}")

print(f"\n最终保留项目数: {len(kept)}")

# 保存结果
result = {
    "kept": kept,
    "removed": removed,
    "updated_rec": updated_rec,
    "baseline_count": len(projects),
    "kept_count": len(kept)
}
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/step1_2_result.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("\n结果已保存到 step1_2_result.json")
