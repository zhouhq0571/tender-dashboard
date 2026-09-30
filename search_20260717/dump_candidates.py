import csv, glob, json, re, os
from datetime import datetime

os.chdir('/Users/zhouhq/Documents/kimi/workspace/bidding-daily/search_20260717')

cands = json.load(open('tyc_candidates.json'))
# reload full content from CSVs by uuid via title match
full = {}
for f in sorted(glob.glob('tyc_*.csv')):
    with open(f, encoding='utf-8-sig') as fp:
        for r in csv.DictReader(fp):
            full[r.get('title','')] = r

def clean(html):
    t = re.sub(r'<style.*?</style>', ' ', html or '', flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', t)
    t = re.sub(r'&nbsp;?', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()

KEEP = ['兴银理财理财登记过户','IBOR底座','智慧组合管理平台','财富管理业务渠道对接','恒生估值系统',
        '供应商资源池','开放平台信创改造','反洗钱升级优化','实时数据同步平台','风控百融平台',
        '一体化运维管理平台自动化运维组件','金证TA系统运维','接口监测审计系统','帆软产品技术服务',
        '财务管理系统二期','FICC投研服务','非零内评','Zstack','腾讯会议','日志分析系统扩容','成果互动软件']
for c in cands:
    if not any(k in c['title'] for k in KEEP):
        continue
    r = full.get(c['title'], {})
    txt = clean(r.get('content',''))
    print('='*100)
    print(f"PUB {c['pub']} | {c['purchaser']} | {c['title']}")
    print(f"AMOUNT: {c.get('amount') or '-'} | LINK: {c['link'][:110]}")
    print(txt[:1800])
    print()
