#!/usr/bin/env python3
"""2026-10-26 千里马批次4（seek_1026_b4）裁决执行：31/32/33/37/38/39/40纳入（7条），
34/35/36不纳入。周老师裁决（23:24）：「31-33纳入，31业务标签增加公司金融，33业务标签改为数据平台，
32-33投标建议改为可关注；37-40纳入且业务标签增加公司金融、投标建议改为可关注；其他不纳入」。
数据一律从 staging_20261017-1102.json 动态取（URL/金额/截止日期），禁手填。
仅落本地工作副本，全批齐审后一次性部署。"""
import json, re
from pathlib import Path

WS_DIR = Path('/Users/zhouhq/Documents/kimi/Workspaces/金融要闻周报')
BOARD = Path('/Users/zhouhq/Documents/kimi/workspace/bidding-daily')
INDEX = BOARD / 'index.html'
REJECTED = BOARD / 'rejected_candidates.json'
STAGING = WS_DIR / 'staging_20261017-1102.json'
DECISION = ('2026-10-26 23:24 周老师seek_1026_b4裁决：31/32/33/37/38/39/40纳入'
            '（31加标签公司金融；33标签改数据平台；32/33/37/38/39/40改可关注）；34/35/36不纳入')

# (staging_id, board_company, region, province, tags, rec)
ADOPT = [
    ('item_4497', '湖南银行', '华中', '湖南', ['信创', '公司金融'], '⭐ ★★☆ 建议投标'),
    ('item_4499', '湖南银行', '华中', '湖南', ['数据服务'], '👀 ★☆☆ 可关注'),
    ('item_4500', '湖南银行', '华中', '湖南', ['数据平台'], '👀 ★☆☆ 可关注'),
    ('item_4508', '屯溪农商银行', '华东', '安徽', ['信创', '公司金融'], '👀 ★☆☆ 可关注'),
    ('item_4509', '中国银行安徽省分行', '华东', '安徽', ['公司金融'], '👀 ★☆☆ 可关注'),
    ('item_4510', '兴业银行', '华东', '福建', ['数据服务', '公司金融'], '👀 ★☆☆ 可关注'),
    ('item_4513', '湖南银行', '华中', '湖南', ['公司金融'], '👀 ★☆☆ 可关注'),
]
REJ_IDS = ['item_4503', 'item_4504', 'item_4505']  # 34/35/36


def main():
    staging = {it['id']: it for it in json.loads(STAGING.read_text(encoding='utf-8'))}
    html = INDEX.read_text(encoding='utf-8')
    m = re.search(r'(<script type="application/json" id="tender-data">)(.*?)(</script>)', html, re.DOTALL)
    if not m:
        raise SystemExit('❌ 找不到 tender-data JSON')
    data = json.loads(m.group(2))
    projects = data['projects']
    next_id = max(p['id'] for p in projects) + 1

    # 防串台：同 project 精确/包含关系拦截（"（第二次）"新一轮并行保留为既定先例，仅拦完全同名）
    for sid, *_ in ADOPT:
        it = staging[sid]
        for p in projects:
            if it['project'] == p.get('project') and it['org'].startswith(p.get('company', '')[:2]):
                raise SystemExit(f"❌ 防串台拦截：看板已存在 {p['company']}/{p['project']}")

    for sid, comp, region, prov, tags, rec in ADOPT:
        it = staging[sid]
        amt = it.get('amount')
        budget = f'{amt}万元' if isinstance(amt, (int, float)) else '-'
        method = it.get('procurement_type') or '其他'
        qm = re.search(r'bid-(\d+)', it.get('source_url') or '')
        src_note = f'；千里马 bid-{qm.group(1)}' if qm else ''
        budget_part = f'，预算{budget}' if budget != '-' else ''
        overview = f"{comp}{it['project']}，{method}{budget_part}{src_note}。"
        projects.append({
            'id': next_id, 'region': region, 'province': prov, 'company': comp,
            'project': it['project'], 'overview': overview,
            'budget': budget, 'deadline': it.get('bid_deadline') or '-',
            'method': method, 'contact': '-',
            'tags': tags, 'rec': rec,
            'url': it.get('source_url') or '', 'source': '千里马招标网', 'date': '2026-10-26',
        })
        print(f"✅ id{next_id} {comp} | {it['project'][:36]} | {tags} | {rec}")
        next_id += 1

    data['total'] = len(projects)
    new_json = json.dumps(data, ensure_ascii=False, indent=2)
    html = html[:m.start(2)] + new_json + html[m.end(2):]
    INDEX.write_text(html, encoding='utf-8')
    print(f'✅ index.html 上板7条（总 {len(projects)} 项）')

    rej = json.loads(REJECTED.read_text(encoding='utf-8'))
    added = 0
    for sid in REJ_IDS:
        it = staging[sid]
        item = {'company': it['org'], 'project': it['project'],
                'deadline': it.get('bid_deadline') or '-',
                'tags': [], 'suggestion': '', 'url': it.get('source_url') or '',
                'source': '千里马Excel候选seek_1026_b4', 'date': '2026-10-26',
                'reject_reason': DECISION}
        if not any(r.get('project') == it['project'] and r.get('date') == '2026-10-26' for r in rej):
            rej.append(item); added += 1
    if added:
        REJECTED.write_text(json.dumps(rej, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'✅ rejected_candidates.json 新增 {added} 条不纳入记录')


if __name__ == '__main__':
    main()
