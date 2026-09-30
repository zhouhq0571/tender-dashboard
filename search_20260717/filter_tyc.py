import csv, glob, json, re, os
from datetime import datetime

os.chdir('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/search_20260717')

rows_all = []
for f in sorted(glob.glob('tyc_*.csv')):
    kw = f.replace('tyc_','').replace('.csv','')
    with open(f, encoding='utf-8-sig') as fp:
        for r in csv.DictReader(fp):
            r['kw'] = kw
            rows_all.append(r)

print(f'total raw rows: {len(rows_all)}')

# dedup by uuid
seen = {}
for r in rows_all:
    u = r.get('uuid') or r.get('id')
    if u not in seen:
        seen[u] = r
rows = list(seen.values())
print(f'after dedup: {len(rows)}')

def ts2date(ts):
    try:
        return datetime.fromtimestamp(int(ts)/1000).strftime('%Y-%m-%d')
    except Exception:
        return '?'

# financial-institution purchaser patterns
FIN_PAT = re.compile(r'银行|农商|农信|信用社|信托|理财|金科|金融科技|清算|征信|银联|网联|金交所|金融资产|财务公司|消费金融|汽车金融|货币经纪|金租|金融租赁')
# exclude non-target institution types even if matched above
NONFIN_PAT = re.compile(r'证券|基金|保险|期货|大学|学院|学校|医院|政府|委员会|财政局|公安|法院|检察院|税务|海关|移动|联通|电信|电网|电力|烟草|石油|铁路|航空|航天|兵器|中车|中建|中铁|交建|能源|矿业|煤|化工|环保|水利|交通|公交|地铁|城投|交投|文旅|传媒|出版|广播|气象|地震|测绘|地质|林|农业|畜牧|水产|粮|供销|烟草|盐业|邮政|烟草|行政审批|政务|大数据局|机关|部队|军|武警|监狱|戒毒|救助|福利|红十字会|公积金|社保|医保|不动产|住房保障|自然资源|生态环境|住建|城管|市场监管|应急管理|审计|统计|档案|方志|老干部|党校|工会|共青团|妇联|残联|科协|文联|工商联|贸促会|开发区|高新区|园区|新区|街道|镇|乡|村')
# announcement stage exclude
STAGE_EXCLUDE = re.compile(r'中标|成交|结果|已结束|终止|废标|流标|合同公示|验收')

cand, excl = [], []
for r in rows:
    title = r.get('title','')
    purchaser = r.get('purchaser','')
    stage = r.get('stage','')
    typ = r.get('type','')
    prov = r.get('province','')
    pub = ts2date(r.get('publishTime',''))
    link = r.get('link','') or r.get('bidUrl','')
    amt = r.get('bidAmount','')
    winner = r.get('bidWinner','')
    blob = title + '|' + stage + '|' + typ
    reason = None
    if STAGE_EXCLUDE.search(blob):
        reason = f'已结束/中标类({stage or typ})'
    elif not FIN_PAT.search(purchaser):
        reason = '采购人非目标金融机构'
    elif NONFIN_PAT.search(purchaser):
        reason = '证券/基金/保险/非金融机构'
    if reason:
        excl.append((pub, purchaser[:30], title[:55], reason))
    else:
        cand.append({'pub':pub,'purchaser':purchaser,'title':title,'stage':stage,'type':typ,
                     'province':prov,'link':link,'amount':amt,'kw':r['kw'],
                     'content_head': re.sub(r'<[^>]+>',' ',r.get('content',''))[:600]})

print(f'\n=== candidates: {len(cand)} ===')
for i,c in enumerate(sorted(cand, key=lambda x:x['pub'], reverse=True),1):
    print(f"[{i}] {c['pub']} | {c['purchaser'][:26]} | {c['title'][:60]} | {c['stage']}/{c['type']} | {c['province']} | kw={c['kw']}")

print(f'\n=== excluded: {len(excl)} (top 25 shown) ===')
for e in excl[:25]:
    print('X', e[0], '|', e[1], '|', e[2], '|', e[3])

with open('tyc_candidates.json','w') as fp:
    json.dump(cand, fp, ensure_ascii=False, indent=1)
print('\nsaved tyc_candidates.json')
