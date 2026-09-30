#!/usr/bin/env python3
"""2026-09-02 增量更新：删除7个过期项目、标记2个已截止、刷新时间/版本 v197"""
import json, re

DIR = '/Users/zhouhq/Documents/kimi/workspace/bidding-daily'
path = f'{DIR}/index.html'
html = open(path).read()
m = re.search(r'(<script type="application/json" id="tender-data">\s*)\{.*?\}(\s*</script>)', html, re.S)
d = json.loads(m.group(0)[len(m.group(1)): -len(m.group(2))])

DELETE_IDS = {8, 16, 18, 19, 47, 57, 69}
MARK_IDS = {48, 61}

before = len(d['projects'])
deleted = [p for p in d['projects'] if p['id'] in DELETE_IDS]
d['projects'] = [p for p in d['projects'] if p['id'] not in DELETE_IDS]
marked = []
for p in d['projects']:
    if p['id'] in MARK_IDS:
        p['rec'] = '☆☆☆ 已截止'
        marked.append(p)

d['date'] = '2026年09月02日'
d['timePeriod'] = '早上'
d['version'] = 'v197'

print('deleted:', [(p['id'], p['company'], p['project'][:30]) for p in deleted])
print('marked:', [(p['id'], p['company'], p['project'][:30]) for p in marked])
print('count:', before, '->', len(d['projects']))

new_json = json.dumps(d, ensure_ascii=False, indent=2)
new_block = m.group(1) + new_json + m.group(2)
html = html[:m.start()] + new_block + html[m.end():]
open(path, 'w').write(html)
print('written OK')
