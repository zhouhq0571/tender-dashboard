#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-05 08:27 周老师裁决（05:53 晨报批次）：2纳入、1不纳入。上板 id 104（邮储企业法人核验数据）。"""
import re, json, sys
sys.path.insert(0, '.')
from config import sort_key

NEW = [
 {"id":104,"company":"中国邮政储蓄银行","project":"企业法人相关信息核验数据采购项目",
  "overview":"企业法人相关信息核验数据采购项目公开招标，投标截止2026-11-26 09:30，预算未公布。详见中邮邮采平台公告。",
  "budget":"-","deadline":"2026-11-26 09:30","method":"公开招标",
  "contact":"公诚管理咨询有限公司 吴勇强 15145104317 tengmanyue.gcmc.gd@chinaccs.cn",
  "region":"华北","province":"北京","tags":["数据服务"],"rec":"👀 ★☆☆ 可关注",
  "url":"https://cg.psbc.com/cms/default/webfile/1ywgg2/20261104/1302679699696123904.html",
  "source":"中邮邮采易采平台","date":"2026-11-05"},
]

html = open('index.html', encoding='utf-8').read()
m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.S)
data = json.loads(m.group(2))
ps = data['projects']

keys = {(p['company'], p['project']) for p in ps}
for n in NEW:
    if (n['company'], n['project']) in keys:
        print('SKIP dup:', n['id'], n['project']); continue
    ps.append(n)

data['projects'] = sorted(ps, key=sort_key)
out = json.dumps(data, ensure_ascii=False, indent=2)
open('index.html', 'w', encoding='utf-8').write(html[:m.start(2)] + out + html[m.end(2):])
print('OK, total =', len(data['projects']))
