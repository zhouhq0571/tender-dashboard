#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, re
from datetime import datetime, timedelta

html = open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/index.html').read()

m = re.search(r'<script type="application/json" id="tender-data">(.*?)</script>', html, re.DOTALL)
data = json.loads(m.group(1))

today = datetime(2026, 8, 8).date()
yesterday = today - timedelta(days=1)

print(f'今天是: {today}')
print(f'昨天是: {yesterday}')
print(f'删除条件: deadline < {yesterday} (即 deadline <= {yesterday - timedelta(days=1)})')
print()

to_delete = []
keep = []
for p in data['projects']:
    dl = p['deadline']
    if dl == '-' or not dl:
        keep.append(p)
        continue
    try:
        dl_date = datetime.strptime(dl.split(' ')[0], '%Y-%m-%d').date()
        if dl_date < yesterday:
            to_delete.append(p)
        else:
            keep.append(p)
    except:
        keep.append(p)

print(f'删除: {len(to_delete)} 个')
for p in to_delete:
    print(f"  id={p['id']} | {p['company']} | {p['deadline']} | {p['project'][:50]}")

print()
print(f'保留: {len(keep)} 个')

# 写出清理后的数据
keep.sort(key=lambda p: p.get('id', 0))
for i, p in enumerate(keep, 1):
    p['id'] = i

data['projects'] = keep
with open('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/tender_data_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f'清理后数据已保存到 tender_data_cleaned.json')
print(f'保留项目重新编号: 1 ~ {len(keep)}')
