#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-29 15:16 周老师裁决执行：14条候选保留6条（2/6/9/11/12/14），撤8条。
保留条目修订：#6(id163)加标签公司金融；#12(id169)加标签公司金融；
#14(id171)删财富管理加资产管理、建议改可关注。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

REMOVE = [158, 160, 161, 162, 164, 165, 167, 170]  # 候选# 1,3,4,5,7,8,10,13

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

before = len(ps)
ps = [p for p in ps if p['id'] not in REMOVE]
print(f'撤下 {before - len(ps)} 条（id {REMOVE}）')

edits = 0
for p in ps:
    if p['id'] == 163:  # #6 兴业银行杭州分行
        if '公司金融' not in p['tags']:
            p['tags'].append('公司金融'); edits += 1
    elif p['id'] == 169:  # #12 青农商互联网综合服务平台
        if '公司金融' not in p['tags']:
            p['tags'].append('公司金融'); edits += 1
    elif p['id'] == 171:  # #14 浦银理财
        if '财富管理' in p['tags']:
            p['tags'].remove('财富管理'); edits += 1
        if '资产管理' not in p['tags']:
            p['tags'].append('资产管理'); edits += 1
        p['rec'] = '👀 ★☆☆ 可关注'; edits += 1
print(f'修订 {edits} 处')

ps.sort(key=sort_key)
data['projects'] = ps
data['total'] = len(ps)

new_block = m.group(1) + '\n' + json.dumps(data, ensure_ascii=False, indent=2) + '\n' + m.group(3)
open('index.html', 'w', encoding='utf-8').write(html[:m.start()] + new_block + html[m.end():])
print(f'OK: 板上现 {len(ps)} 条，total 已同步')
for p in ps:
    if p['id'] in (159, 163, 166, 168, 169, 171):
        print(p['id'], p['company'], '|', p['project'][:30], '|', p['tags'], '|', p['rec'])
