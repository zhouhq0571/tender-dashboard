#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-11-26 批次台账回写：8 条裁决落账。
1纳入(资产管理,运维服务)→id88；2/3/8不纳入；4纳入(公司金融)→id89；
5纳入(公司金融)→id90；6纳入(财富管理,强烈建议投标)→id91；7纳入(资产管理,人力外包)→id92。
"""
import json

DECISIONS = {
 1: ("纳入", ["资产管理","运维服务"], None, 88),
 2: ("不纳入", None, None, None),
 3: ("不纳入", None, None, None),
 4: ("纳入", ["公司金融"], None, 89),
 5: ("纳入", ["公司金融"], None, 90),
 6: ("纳入", ["财富管理"], "强烈建议投标", 91),
 7: ("纳入", ["资产管理","人力外包"], None, 92),
 8: ("不纳入", None, None, None),
}

items = json.load(open('pending_candidates.json', encoding='utf-8'))
pend = {x['push_no']: x for x in items if x.get('status') == '待确认'}
assert set(pend) == set(DECISIONS), f"待确认集合不符: {set(pend)} vs {set(DECISIONS)}"

for no, (dec, tags, rec, bid) in DECISIONS.items():
    x = pend[no]
    x['status'] = dec
    x['decision_date'] = '2026-11-26'
    if tags is not None:
        x['tags'] = '、'.join(tags)
    if rec is not None:
        x['rec'] = rec
    if bid is not None:
        x['board_id'] = bid
    x['decision'] = ('2026-11-26 周老师RC端【候选决策 2026-11-26】原文：'
        '1纳入（标签：资产管理、运维服务）；2不纳入；3不纳入；4纳入（标签：公司金融）；'
        '5纳入（标签：公司金融）；6纳入（标签：财富管理）（建议：强烈建议投标）；'
        '7纳入（标签：资产管理、人力外包）；8不纳入'
        + (f'；上板id{bid}' if bid else ''))

json.dump(items, open('pending_candidates.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
left = [x for x in items if x.get('status') == '待确认']
print(f"回写完成：8 条已裁决，剩余待确认 {len(left)} 条")
