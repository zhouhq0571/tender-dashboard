#!/usr/bin/env python3
"""每日过期项目分析：删除 delta>=2，标记 delta==1 或今晨已过。"""
import json, re, sys
from datetime import date, datetime

DIR = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily'
html = open(f'{DIR}/index.html').read()
m = re.search(r'<script type="application/json" id="tender-data">\s*(\{.*?\})\s*</script>', html, re.S)
d = json.loads(m.group(1))
today = date(2026, 9, 2)
now_h, now_m = 6, 0

to_delete, to_mark, already = [], [], []
for p in d['projects']:
    dl = (p.get('deadline') or '').strip()
    rec = p.get('rec', '') or ''
    marked = '已截止' in rec
    dm = re.search(r'(\d{4})-(\d{1,2})-(\d{1,2})', dl)
    if not dm:
        continue
    y, mn, dd = map(int, dm.groups())
    delta = (today - date(y, mn, dd)).days
    tm = re.search(r'(\d{1,2}):(\d{2})', dl)
    if delta >= 2:
        to_delete.append((p['id'], p['company'], p['project'][:38], dl, 'marked' if marked else 'UNMARKED'))
    elif delta == 1:
        (already if marked else to_mark).append((p['id'], p['company'], p['project'][:38], dl))
    elif delta == 0 and tm and not marked:
        hh, mm = int(tm.group(1)), int(tm.group(2))
        if (hh, mm) <= (now_h, now_m):
            to_mark.append((p['id'], p['company'], p['project'][:38], dl + ' 今晨已过'))

print('DELETE:')
for x in to_delete: print(' ', x)
print('MARK:')
for x in to_mark: print(' ', x)
print('ALREADY-MARKED(delta=1,keep):')
for x in already: print(' ', x)
print('total:', len(d['projects']))
